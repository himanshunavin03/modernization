"""Read-only integration gate over the frozen KG and current Doctor artifacts."""
import json
from hashlib import sha256
from pathlib import Path

from polaris_modernization.feature_specifications.human_presentation import audit_human_markdown


ROOT=Path(__file__).resolve().parents[1]
FEATURE='feature-doctor-directory-management'
FROZEN='legacy-dashboard-complete-application-demo-v1-2026-09-06-203944'


def read(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))


def verify_doctor_requirements():
    specification=read(f'artifacts/feature-specifications/latest/{FEATURE}.json')
    au=read('artifacts/application-understanding/latest/source-capabilities.json')
    stories=read(f'artifacts/stories/features/{FEATURE}/latest/story-catalog.json')
    acceptance=read(f'artifacts/acceptance-criteria/features/{FEATURE}/latest/acceptance-criteria.json')
    coverage=read('artifacts/feature-specifications/latest/capability-coverage.json')
    assert au['kg_run_id']==FROZEN==specification['upstream_lineage']['kg_run_id']
    au_run=specification['upstream_lineage']['application_understanding_run_id']
    assert read(f'artifacts/application-understanding/runs/{au_run}/source-capabilities.json')==au
    lineage=acceptance['lineage']
    assert lineage['canonical_upstream_kg_run']==FROZEN
    assert lineage['application_understanding_run_id']==au_run
    assert lineage['story_run']==stories['lineage']['story_run']
    archived=ROOT/'artifacts/feature-specifications/runs'/lineage['feature_run']/f'{FEATURE}.json'
    assert sha256(archived.read_bytes()).hexdigest()==lineage['feature_contract_hash']
    assert specification['stories']==stories['stories']
    assert specification['acceptance_criteria']==acceptance['acceptance_criteria']
    requirements={r['id']:r for r in specification['functional_requirements']}
    caps={c['capability_id']:c for c in au['capabilities']}
    included={d['capability_id'] for d in coverage['dispositions'] if d.get('feature_id')==FEATURE and d['scope_status']=='INCLUDED'}
    used={i for r in requirements.values() for i in r['source_capability_ids']}
    assert used==included
    assert {c['capability_id'] for c in caps.values() if c['domain_context']=='doctors' and any(e['stage']=='UI' for e in c['source_evidence'])} <= included
    def semantic_key(s):return (s.get('interaction_id'),s.get('effect_kind'),s.get('observable_result'))
    expected={semantic_key(s) for cid in included for s in caps[cid]['interaction_semantics'] if s.get('observable_result')}
    realized={semantic_key(s) for r in requirements.values() for s in r['interaction_semantics'] if s.get('observable_result')}
    assert expected==realized
    for r in requirements.values():
        allowed={semantic_key(s) for cid in r['source_capability_ids'] for s in caps[cid]['interaction_semantics']}
        assert {semantic_key(s) for s in r['interaction_semantics']}<=allowed
    story_by_id={s['story_id']:s for s in stories['stories']}
    assert {r for s in stories['stories'] for r in s['functional_requirement_ids']}==set(requirements)
    assert {c['story_id'] for c in acceptance['acceptance_criteria']}==set(story_by_id)
    for s in stories['stories']:
        parent=requirements[s['functional_requirement_ids'][0]]
        assert s['interaction_semantics']==parent['interaction_semantics']
        assert s['system_initiated']==parent['system_initiated']
        if s['system_initiated']:assert not s['story_statement'].startswith('As a')
    for c in acceptance['acceptance_criteria']:
        parent=story_by_id[c['story_id']]
        assert c['functional_requirement_ids']==parent['functional_requirement_ids']
        assert (c['interaction_id'],c['effect_kind'],c['then']) in {semantic_key(s) for s in parent['interaction_semantics']}
        assert c['given'] and c['when'] and c['then']
        assert c['effect_id'] and c['lineage_node_ids']
    assert {(c['interaction_id'],c['effect_kind'],c['then']) for c in acceptance['acceptance_criteria']}==realized
    apis={(a['method'],a['route']) for a in specification['capability_api_contracts']}
    assert apis=={('GET','/api/doctors'),('GET','/api/doctors/{id}'),('POST','/api/doctors'),('PUT','/api/doctors'),('DELETE','/api/doctors/{id}'),('GET','/api/users/current/tenant')}
    kinds={s['effect_kind'] for r in requirements.values() for s in r['interaction_semantics']}
    assert {'RECORD_CREATE','RECORD_UPDATE','DESTINATION_STATE','MEDIA_BINDING','MEDIA_RENDER','SELECTION','VALIDATION','VALIDATION_GATE','NAVIGATION','SYSTEM_CONTEXT','COLLECTION_APPEND','COLLECTION_REMOVE','FIXED_ORDER','RENDER','CONFIRMATION'}<=kinds
    for label,method in [('Add','POST'),('Save','PUT')]:
        r=next(r for r in requirements.values() if any(s.get('label')==label for s in r['interaction_semantics']))
        assert r['api_dependencies']==[f'{method} /api/doctors']
    new=next(r for r in requirements.values() if any(s.get('label')=='New doctor' for s in r['interaction_semantics']))
    assert new['api_dependencies']==[]
    markdown=(ROOT/f'artifacts/feature-specifications/latest/{FEATURE}.md').read_text(encoding='utf-8')
    assert not any(audit_human_markdown(markdown).values())
    assert 'numbered pagination' not in markdown.lower()
    for phrase in ('required batch size','NO DATA','Name','profile','automatically','select-all','confirmation'):
        assert phrase.lower() in markdown.lower() or phrase=='required batch size' and 'requested batch size' in markdown
    index=read('artifacts/feature-specifications/latest/feature-specification-index.json')
    row=next(r for r in index['features'] if r['feature_id']==FEATURE)
    assert row['stories']==len(story_by_id) and row['acceptance_criteria']==len(acceptance['acceptance_criteria'])
    return {'feature_run':lineage['feature_run'],'au_run':au_run,'story_run':lineage['story_run'],
        'ac_run':lineage['acceptance_criteria_run'],'fr_count':len(requirements),'story_count':len(story_by_id),
        'ac_count':len(acceptance['acceptance_criteria']),'api_count':len(apis),
        'requirements':[{'id':r['id'],'title':r['title']} for r in requirements.values()],
        'apis':[f'{method} {route}' for method,route in sorted(apis)],
        'source_behavior_count':len(expected),'realized_behavior_count':len(realized),
        'specification_run':row['requirements_run_id']}


def test_current_doctor_requirements_pass_frozen_source_fidelity_and_traceability():
    verify_doctor_requirements()

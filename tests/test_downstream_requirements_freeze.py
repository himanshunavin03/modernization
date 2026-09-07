"""Downstream-only regressions; fixtures are graph records, never source extraction."""
import json
from pathlib import Path

import pytest

from polaris_modernization.application_understanding.interactions import InteractionGraph
from polaris_modernization.capability_completeness import validate_capability_coverage
from polaris_modernization.feature_scope_completeness import build_feature_scope_contract
from polaris_modernization.feature_targeted_generation import generate_targeted_stories, generate_targeted_acceptance_criteria, FeatureLineageError


def node(identity,label,**props):
    return {'id':identity,'name':identity,'label':label,'properties':props,
            'evidence':[{'source_path':'neutral/view.html','line_start':1,'line_end':1}]}


def edge(source,kind,target):
    return {'source':source,'type':kind,'target':target}


def graph_fixture():
    return {'nodes':[node('a','UIAction',text='Same text',expression='alpha()'),node('b','UIAction',text='Same text',expression='beta()'),
        node('ha','FrontendFunction'),node('hb','FrontendFunction'),node('invoke','FrontendInvocation',target_function='then'),
        node('callback','FrontendFunction',anonymous=True),node('helper','FrontendFunction'),
        node('na','Navigation',target='first'),node('nb','Navigation',target='second'),
        node('append','CollectionMutation',operation='push',collection='items')],
        'edges':[edge('a','TRIGGERS','ha'),edge('b','TRIGGERS','hb'),edge('ha','INVOKES','invoke'),
            edge('invoke','PASSES_CALLBACK','callback'),edge('callback','INVOKES','helper'),edge('helper','NAVIGATES','na'),
            edge('ha','MUTATES_COLLECTION','append'),edge('hb','NAVIGATES','nb')]}


def scope(semantics):
    caps=[{'capability_id':'cap-x','domain_context':'neutral','operation_kind':'NAVIGATE','operation_identity':'opaque',
        'source_evidence':[{'node_id':'a','source_path':'neutral/view.html','stage':'UI'}],
        'interaction_semantics':semantics,'confidence':'PROVEN'}]
    dispositions=[{'capability_id':'cap-x','feature_id':'feature-neutral','scope_status':'INCLUDED','downstream_refs':['feature:feature-neutral']}]
    return build_feature_scope_contract('feature-neutral','Neutral Experience',validate_capability_coverage(caps,dispositions))[0]


def test_different_handlers_and_targets_remain_distinct_with_identical_labels():
    index=InteractionGraph(graph_fixture())
    values=[s.model_dump() for anchor,handler in [('a','ha'),('b','hb')] for s in index.semantics(index.nodes[anchor],index.nodes[handler])]
    requirements=scope(values)['functional_requirements']
    assert len(requirements)==2
    target_sets=[{s['navigation_target'] for s in r['interaction_semantics'] if s.get('navigation_target')} for r in requirements]
    assert {'first'} in target_sets and {'second'} in target_sets


def test_same_handler_related_effects_remain_one_interaction():
    index=InteractionGraph(graph_fixture())
    semantics=index.semantics(index.nodes['a'],index.nodes['ha'])
    contract=scope([s.model_dump() for s in semantics])
    assert len(contract['functional_requirements'])==1
    assert {s.effect_kind for s in semantics}=={'NAVIGATION','COLLECTION_APPEND'}
    nav=next(s for s in semantics if s.effect_kind=='NAVIGATION')
    assert nav.lineage_node_ids==['a','ha','invoke','callback','helper','na']
    assert nav.system_event=='the operation completes successfully'


def test_unrelated_callback_and_navigation_cannot_supply_an_outcome():
    graph=graph_fixture();graph['edges']=[e for e in graph['edges'] if e['source']!='ha']
    index=InteractionGraph(graph)
    semantics=index.semantics(index.nodes['a'],index.nodes['ha'])
    assert all(s.observable_result is None for s in semantics)
    assert semantics[0].unresolved_reason


def test_system_prerequisite_is_not_merged_with_user_interaction():
    values=[{'interaction_id':'interaction-user','interaction_type':'ACTION','handler_id':'h1','observable_result':'the first view opens'},
            {'interaction_id':'interaction-system','interaction_type':'SYSTEM','handler_id':'h2','system_initiated':True,'observable_result':'context reaches the dependent request'}]
    reqs=scope(values)['functional_requirements']
    assert len(reqs)==2 and {r['system_initiated'] for r in reqs}=={False,True}


def test_grouping_ignores_labels_routes_and_source_positions():
    index=InteractionGraph(graph_fixture())
    values=[s.model_dump() for a,h in [('a','ha'),('b','hb')] for s in index.semantics(index.nodes[a],index.nodes[h])]
    before={r['interaction_id'] for r in scope(values)['functional_requirements']}
    for value in values:
        value['label']='Unrelated text';value['api_node_ids']=['/arbitrary/route']
        for evidence in value['source_evidence']:evidence['source_path']='elsewhere.txt';evidence['line_start']=10000
    assert {r['interaction_id'] for r in scope(values)['functional_requirements']}==before


def targeted_context(tmp_path,values):
    contract=scope(values);contract['capability_api_contracts']=contract.pop('api_contracts')
    return {'feature':{'feature_id':'feature-neutral','slug':'neutral','name':'Neutral Experience'},'contract':contract,
        'coverage':{'capabilities':[]},'feature_run':'scope-neutral','feature_contract_hash':'neutral-hash',
        'canonical_kg_run':'kg-neutral','contract_path':tmp_path/'artifacts'/'feature-specifications'/'latest'/'feature-neutral.json'}


def test_multiple_effects_generate_multiple_ac_with_exact_lineage_and_no_extra_markdown(tmp_path):
    index=InteractionGraph(graph_fixture());values=[s.model_dump() for s in index.semantics(index.nodes['a'],index.nodes['ha'])]
    context=targeted_context(tmp_path,values)
    stories=generate_targeted_stories(context,tmp_path/'stories')
    ac=generate_targeted_acceptance_criteria(context,stories['path'],tmp_path/'ac')
    assert len(ac['criteria'])==2
    assert {c['effect_id'] for c in ac['criteria']}=={'na','append'}
    assert all(c['interaction_id']==values[0]['interaction_id'] for c in ac['criteria'])
    assert not list(tmp_path.rglob('*.md'))
    assert 'complete the supported' not in stories['stories'][0]['story_statement']


def test_ac_rejects_cross_interaction_outcome_even_if_non_null(tmp_path):
    index=InteractionGraph(graph_fixture());values=[s.model_dump() for s in index.semantics(index.nodes['a'],index.nodes['ha'])]
    context=targeted_context(tmp_path,values);stories=generate_targeted_stories(context,tmp_path/'stories')
    path=stories['path']/'story-catalog.json';catalog=json.loads(path.read_text())
    catalog['stories'][0]['interaction_semantics'][0]['interaction_id']='interaction-unrelated'
    path.write_text(json.dumps(catalog))
    with pytest.raises(FeatureLineageError,match='different interaction'):
        generate_targeted_acceptance_criteria(context,stories['path'],tmp_path/'ac')


def test_graph_with_only_api_and_button_label_cannot_invent_ux():
    g={'nodes':[node('a','UIAction',text='Continue'),node('h','FrontendFunction'),node('api','ApiCall',http_method='GET',normalized_route='/api/records')],
       'edges':[edge('a','TRIGGERS','h'),edge('h','CALLS_API','api')]}
    index=InteractionGraph(g);semantics=index.semantics(index.nodes['a'],index.nodes['h'])
    assert not any(s.observable_result for s in semantics)


def test_same_handler_opposite_guards_select_exact_call_and_callback_paths():
    nodes=[node('neutral/view.html:1:ng-click','UIAction',text='Misleading B',expression='execute()'),
        node('neutral/view.html:2:ng-click','UIAction',text='Misleading A',expression='execute()'),
        node('bind-a','TemplateBinding',attribute='ngClick',expression='execute()',element_identity='neutral/view.html:1:10'),
        node('bind-b','TemplateBinding',attribute='ngClick',expression='execute()',element_identity='neutral/view.html:2:20'),
        node('guard-a','UICondition',condition='!mode',visibility='SHOW',element_identity='neutral/view.html:1:10'),
        node('guard-b','UICondition',condition='mode',visibility='SHOW',element_identity='neutral/view.html:2:20'),
        node('h','FrontendFunction',owner='Neutral',function_name='execute'),
        node('body','StateMutation',owner='Neutral',target='$scope.execute',expression='() => { if (!$scope.mode) { client.left(); } else { client.right(); } }'),
        node('left','FrontendInvocation',target_function='then',target_owner='client.left()'),
        node('right','FrontendInvocation',target_function='then',target_owner='client.right()'),
        node('cb-a','FrontendFunction'),node('cb-b','FrontendFunction'),node('nav-a','Navigation',target='one'),node('nav-b','Navigation',target='two')]
    edges=[edge('h','INVOKES','left'),edge('h','INVOKES','right'),edge('left','PASSES_CALLBACK','cb-a'),edge('right','PASSES_CALLBACK','cb-b'),edge('cb-a','NAVIGATES','nav-a'),edge('cb-b','NAVIGATES','nav-b')]
    index=InteractionGraph({'nodes':nodes,'edges':edges})
    first=index.semantics(nodes[0],index.nodes['h']);second=index.semantics(nodes[1],index.nodes['h'])
    assert {s.navigation_target for s in first if s.navigation_target}=={'one'}
    assert {s.navigation_target for s in second if s.navigation_target}=={'two'}
    assert all('cb-b' not in s.lineage_node_ids for s in first)
    assert all('cb-a' not in s.lineage_node_ids for s in second)


def test_directive_writer_is_joined_to_its_own_instance_binding():
    g={'nodes':[node('usage','DirectiveUsage',element_identity='element-a'),node('binding','DirectiveBinding'),
        node('template','TemplateBinding',element_identity='element-a'),node('other','TemplateBinding',element_identity='element-b'),
        node('callback','FrontendFunction'),node('mutation','StateMutation',expression='reader.result'),
        node('state','BoundState'),node('other-state','BoundState'),node('condition','UICondition',condition='image',visibility='RENDER')],
       'edges':[edge('usage','BINDS_TO','binding'),edge('mutation','MUTATES_BINDING','binding'),edge('callback','MUTATES','mutation'),
        edge('template','BINDS_TO','binding'),edge('other','BINDS_TO','binding'),edge('template','BINDS_STATE','state'),
        edge('other','BINDS_STATE','other-state'),edge('state','CONTROLS_RENDER','condition')]}
    index=InteractionGraph(g);semantics=index.media(index.nodes['usage'])
    assert {s.effect_kind for s in semantics}=={'MEDIA_BINDING','MEDIA_RENDER'}
    assert all('other-state' not in s.lineage_node_ids for s in semantics)


def test_conditional_collection_visibility_uses_recorded_guards_without_api_pagination():
    from polaris_modernization.application_understanding.interactions import recorded_call_guards,condition_event
    assert recorded_call_guards('if (!state.mode) { service.first(); } else { service.second(); }','service.first')==['!state.mode']
    assert recorded_call_guards('if (!state.mode) { service.first(); } else { service.second(); }','service.second')==['state.mode']
    assert condition_event('!$scope.items.length')=='the items collection is empty'
    assert condition_event('batch.length < requestedSize')=='the returned batch contains fewer records than the requested batch size'
    assert condition_event('arbitraryFlag') is None


def test_consolidation_preserves_exact_story_fr_ownership_and_one_human_document(tmp_path):
    from polaris_modernization.feature_specifications.workflow import synchronize_targeted_feature_specification
    from polaris_modernization.feature_specifications.human_presentation import audit_human_markdown
    index=InteractionGraph(graph_fixture())
    values=[s.model_dump() for a,h in [('a','ha'),('b','hb')] for s in index.semantics(index.nodes[a],index.nodes[h])]
    context=targeted_context(tmp_path,values)
    context['contract_path'].parent.mkdir(parents=True)
    context['contract_path'].write_text(json.dumps(context['contract']))
    stories=generate_targeted_stories(context,tmp_path/'stories');ac=generate_targeted_acceptance_criteria(context,stories['path'],tmp_path/'ac')
    result=synchronize_targeted_feature_specification(context,stories['path'],ac['path'],context['contract_path'].parents[1])
    assert all(len(s['functional_requirement_refs'])==1 for s in result['presentation']['jira_stories'])
    assert len(list(context['contract_path'].parent.glob('*.md')))==1
    assert not any(audit_human_markdown((result['path']/'feature-neutral.md').read_text()).values())


def test_scope_refresh_clears_previous_consolidation_lineage(tmp_path):
    from polaris_modernization.feature_scope_completeness import publish_feature_scope_refresh
    source=tmp_path/'latest';source.mkdir()
    (source/'feature-neutral.json').write_text(json.dumps({'feature_id':'feature-neutral','feature_name':'Neutral Experience','generation_lineage':{'feature_contract_hash':'obsolete'},'stories':[{'story_id':'obsolete'}]}))
    (source/'feature-api-contracts.json').write_text(json.dumps({'features':[{'feature_id':'feature-neutral','contracts':[]}]}))
    caps=[{'capability_id':'cap-neutral','domain_context':'neutral','operation_kind':'NAVIGATE','operation_identity':'opaque','source_evidence':[{'node_id':'a','source_path':'neutral/view.html','stage':'UI'}],'confidence':'PROVEN'}]
    coverage=validate_capability_coverage(caps,[{'capability_id':'cap-neutral','feature_id':'feature-neutral','scope_status':'INCLUDED','downstream_refs':['feature:feature-neutral']}])
    result=publish_feature_scope_refresh(source,tmp_path,'feature-neutral',coverage)
    refreshed=json.loads((result['path']/'feature-neutral.json').read_text())
    assert 'generation_lineage' not in refreshed and 'stories' not in refreshed
    assert len(refreshed['functional_requirements'])==1
    assert not list(result['path'].glob('*.md'))


def test_typed_query_metadata_renders_parameter_names_without_python_objects(tmp_path):
    from polaris_modernization.feature_specifications.human_presentation import build_targeted_human_presentation
    index=InteractionGraph(graph_fixture())
    context=targeted_context(tmp_path,[s.model_dump() for s in index.semantics(index.nodes['a'],index.nodes['ha'])])
    context['contract']['capability_api_contracts']=[{'contract_id':'API-1','method':'GET','route':'/api/items','requirement_ids':['FR-01'],'source_capability_ids':['cap-x'],
        'metadata':[{'query_parameters':[{'name':'limit','type':'int'}],'response_type':'Task<List<Item>>'}]}]
    stories=generate_targeted_stories(context,tmp_path/'stories');ac=generate_targeted_acceptance_criteria(context,stories['path'],tmp_path/'ac')
    presentation=build_targeted_human_presentation(context['contract'],{'stories':stories['stories']},{'acceptance_criteria':ac['criteria']})
    assert presentation['api_requirements'][0]['inputs']==[{'name':'limit','location':'Query','description':'Request parameter (int)'}]
    assert presentation['api_requirements'][0]['description']=='Collection of Item records'


FROZEN='legacy-dashboard-complete-application-demo-v1-2026-09-06-203944'


def test_frozen_doctor_au_semantic_gate():
    from polaris_modernization.application_understanding.retrieval import load_approved_graph
    from polaris_modernization.capability_completeness import derive_source_capabilities
    root=Path(__file__).resolve().parents[1]
    approved=load_approved_graph(root/'artifacts'/'knowledge-graph'/'runs'/FROZEN)
    caps=[c for c in derive_source_capabilities(approved['graph']) if c.domain_context=='doctors']
    detail=next(c for c in caps if c.operation_identity=='GET /api/doctors/{PARAM}')
    assert any(s.effect_kind=='DESTINATION_STATE' and any('Route:' in i for i in s.lineage_node_ids) and any('callback@' in i for i in s.lineage_node_ids) for s in detail.interaction_semantics)
    for kind in ('CREATE','UPDATE'):
        cap=next(c for c in caps if c.operation_kind==kind)
        assert any(s.navigation_target=='doctors' and any('callback@' in i for i in s.lineage_node_ids) and any('navigateBack' in i for i in s.lineage_node_ids) for s in cap.interaction_semantics)
        assert {s.label for s in cap.interaction_semantics}==({'Add'} if kind=='CREATE' else {'Save'})
        assert any(s.effect_kind==('RECORD_CREATE' if kind=='CREATE' else 'RECORD_UPDATE') for s in cap.interaction_semantics)
    media=[s for c in caps if c.operation_kind=='UPLOAD' for s in c.interaction_semantics]
    assert {'MEDIA_BINDING','MEDIA_RENDER'} <= {s.effect_kind for s in media}
    tenant=next(c for c in caps if c.operation_identity=='GET /api/users/current/tenant')
    assert all(s.system_initiated for s in tenant.interaction_semantics)
    listing=next(c for c in caps if c.operation_kind=='LIST')
    assert {'COLLECTION_APPEND','RENDER','FIXED_ORDER'} <= {s.effect_kind for s in listing.interaction_semantics}

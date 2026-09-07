"""Propagate interaction/effect identity through approved graph relationships only.

This module does not open application source or interpret API routes as UI behavior.
Graph paths are retained with each effect so downstream stages cannot borrow an
outcome from another handler, callback, route or directive instance.
"""
from __future__ import annotations

from collections import defaultdict, deque
from hashlib import sha256
import re

from polaris_modernization.capability_completeness import InteractionSemantics, SourceCapability, _evidence


def words(value: str) -> str:
    value = re.sub(r"^(?:\$scope\.|\$rootScope\.|scope\.|this\.)", "", value)
    return re.sub(r"[._-]+", " ", re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)).strip().lower()


def describe_semantic(semantic: dict) -> str:
    result=semantic.get('observable_result') or ''
    condition=semantic.get('condition')
    if semantic.get('effect_kind')=='ACTION_VISIBILITY' and condition:
        result += ' when '+(semantic.get('condition_description') or f"{words(condition.lstrip('!'))} is {'inactive' if condition.startswith('!') else 'active'}")
    elif semantic.get('effect_kind')=='VALIDATION_GATE':
        pass
    elif semantic.get('system_event'):
        result += ' when '+semantic['system_event']
    return result[:1].upper()+result[1:].rstrip('.')+'.' if result else ''


def _balanced_end(text: str, start: int, opening: str, closing: str) -> int:
    depth=0;quote=None;position=start
    while position<len(text):
        char=text[position]
        if quote:
            if char=='\\':position+=2;continue
            if char==quote:quote=None
        elif char in "\"'`":quote=char
        elif text.startswith('//',position):
            newline=text.find('\n',position);position=len(text) if newline<0 else newline;continue
        elif text.startswith('/*',position):
            end=text.find('*/',position+2);position=len(text) if end<0 else end+2;continue
        elif char==opening:depth+=1
        elif char==closing:
            depth-=1
            if not depth:return position
        position+=1
    return -1


def recorded_call_guards(expression: str, function_name: str) -> list[str]:
    """Interpret braced guards already recorded in a function-valued KG property.

    No application file, source inventory, parser or extractor is consulted.
    Unsupported syntax yields no guard rather than a guessed association.
    """
    occurrences=[m.start() for m in re.finditer(r'(?<![\w$])'+re.escape(function_name)+r'\s*\(',expression)]
    return _recorded_guards(expression,occurrences)


def _recorded_guards(expression:str,occurrences:list[int]) -> list[str]:
    guards=[]
    for match in re.finditer(r'\bif\s*\(',expression):
        begin=expression.find('(',match.start());end=_balanced_end(expression,begin,'(',')')
        if end<0:continue
        body=end+1
        while body<len(expression) and expression[body].isspace():body+=1
        if body>=len(expression) or expression[body]!='{':continue
        body_end=_balanced_end(expression,body,'{','}')
        if body_end<0:continue
        condition=expression[begin+1:end].strip()
        if any(body<pos<body_end for pos in occurrences):guards.append(condition)
        remaining=expression[body_end+1:]
        alternate=re.match(r'\s*else\s*\{',remaining)
        if alternate:
            other=body_end+1+alternate.end()-1;other_end=_balanced_end(expression,other,'{','}')
            if any(other<pos<other_end for pos in occurrences):
                guards.append(condition[1:] if condition.startswith('!') else '!'+condition)
    return guards


def condition_event(condition:str) -> str | None:
    condition=condition.strip()
    empty=re.fullmatch(r'!\s*(?:\$scope\.|scope\.)?(\w+)\.length',condition)
    if empty:return f'the {words(empty[1])} collection is empty'
    batch=re.fullmatch(r'\w+\.length\s*<\s*\w+',condition)
    if batch:return 'the returned batch contains fewer records than the requested batch size'
    return None


def _condition_key(value:str) -> str:
    return re.sub(r'\s+','',value).replace('$scope.','').replace('scope.','').replace('this.','')


class InteractionGraph:
    def __init__(self, graph: dict):
        self.nodes = {item["id"]: item for item in graph["nodes"]}
        self.forward = defaultdict(list)
        self.reverse = defaultdict(list)
        self.by_label = defaultdict(list)
        self.by_element = defaultdict(list)
        self.by_surface = defaultdict(list)
        self.function_bodies=defaultdict(list)
        self.path_cache={}
        for node in self.nodes.values():
            self.by_label[node["label"]].append(node)
            props = node.get("properties", {})
            if node['label']=='StateMutation' and props.get('target'):
                self.function_bodies[(props.get('owner'),props['target'].split('.')[-1])].append(props.get('expression',''))
            if props.get("element_identity"):
                self.by_element[props["element_identity"]].append(node)
            for evidence in node.get("evidence", []):
                self.by_surface[evidence.get("source_path", "")].append(node)
        for edge in graph["edges"]:
            self.forward[edge["source"]].append(edge)
            self.reverse[edge["target"]].append(edge)

    def targets(self, node_id: str, *types: str):
        return [self.nodes[e["target"]] for e in self.forward[node_id] if e["type"] in types]

    def surface(self, node: dict) -> str:
        return next((e["source_path"] for e in node.get("evidence", []) if e.get("source_path")), "")

    def view_context(self,node:dict) -> str:
        surface=self.surface(node)
        routes={r['name'] for r in self.by_label['Route'] if r.get('properties',{}).get('template') and surface.endswith(r['properties']['template'])}
        return f"the {words(next(iter(routes)))} view is displayed" if len(routes)==1 else 'the interaction view is displayed'

    def path(self, start: str, *, follow_routes: bool = True, action_condition: str | None = None):
        key=(start,follow_routes,action_condition)
        if key not in self.path_cache:
            self.path_cache[key]=tuple(self._walk(start,follow_routes=follow_routes,action_condition=action_condition))
        return self.path_cache[key]

    def _walk(self, start: str, *, follow_routes: bool, action_condition: str | None):
        """Walk explicit calls and callbacks; lexical containment is not execution."""
        root=self.nodes[start];props=root.get('properties',{})
        bodies=self.function_bodies[(props.get('owner'),props.get('function_name'))]
        queue = deque([(start, [start])]); visited = set()
        while queue:
            current, lineage = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            yield self.nodes[current], lineage
            for edge in self.forward[current]:
                target = self.nodes[edge["target"]]
                kind = edge["type"]
                if current==start and action_condition and kind=='INVOKES':
                    tp=target.get('properties',{})
                    function=tp.get('target_owner','').split('(',1)[0].strip() if tp.get('target_function') in {'then','catch','finally'} else tp.get('target_function') or tp.get('function_name')
                    if function:
                        guards=[g for body in bodies for g in recorded_call_guards(body,function)]
                        condition_key=_condition_key(action_condition)
                        opposite=condition_key[1:] if condition_key.startswith('!') else '!'+condition_key
                        if opposite in {_condition_key(g) for g in guards} and condition_key not in {_condition_key(g) for g in guards}:
                            continue
                allowed = kind in {"TRIGGERS", "INVOKES", "PASSES_CALLBACK", "CALLS_API", "MUTATES", "MUTATES_COLLECTION", "NAVIGATES", "REQUIRES_CONFIRMATION", "BINDS_STATE", "CONTROLS_RENDER"}
                allowed |= follow_routes and (kind in {"NAVIGATES_TO", "INITIALIZES_WITH"} or kind == "DEPENDS_ON" and target["label"] == "AngularController")
                # An API mechanism is a dependency, never an instruction to inspect
                # arbitrary backend behavior for a user-visible outcome.
                if allowed and target["id"] not in visited:
                    queue.append((target["id"], [*lineage, target["id"]]))

    def element_nodes(self, action: dict):
        """Resolve exact template binding identity, never nearest source position."""
        props = action.get("properties", {})
        surface = self.surface(action)
        bindings = [n for n in self.by_surface[surface] if n["label"] == "TemplateBinding"
                    and n.get("properties", {}).get("expression") == props.get("expression")
                    and n.get("properties", {}).get("attribute") in {"ngClick", "ng-click"}]
        # UIAction IDs retain the exact template event location. It must agree
        # with the binding's element identity; two calls to one handler may have
        # opposite visibility guards. Never choose the nearest source element.
        event_location=action['name'].rsplit(':',1)[0]
        if ':' in event_location:
            bindings=[n for n in bindings if n['properties']['element_identity'].rsplit(':',1)[0]==event_location]
        if len({b['properties']['element_identity'] for b in bindings})>1:
            return []
        return list({n["id"]: n for b in bindings for n in self.by_element[b["properties"]["element_identity"]]}.values())

    def semantics(self, anchor: dict, handler: dict | None = None, *, system: bool = False):
        props = anchor.get("properties", {})
        start = handler or anchor
        identity = "interaction-" + sha256(f"{anchor['id']}|{start['id']}|{system}".encode()).hexdigest()[:20]
        label = str(props.get("text") or "").strip() or None
        elements = self.element_nodes(anchor) if anchor["label"] == "UIAction" else []
        conditions = [n for n in elements if n["label"] == "UICondition"]
        condition = " and ".join(n["properties"]["condition"] for n in conditions) or None
        traversal = list(self.path(start["id"], follow_routes=False,action_condition=condition))
        api_ids = sorted({n["id"] for n, _ in traversal if n["label"] == "ApiCall"})
        base = dict(interaction_id=identity, interaction_type="SYSTEM" if system else "ACTION",
                    label=label, trigger=props.get("expression") or props.get("event"),
                    system_initiated=system, handler_id=start["id"], condition=condition,
                    context=self.view_context(anchor),
                    api_node_ids=api_ids)
        values = []
        for node, lineage in traversal:
            effect = self.effect(node)
            if not effect:
                continue
            result, effect_kind = effect
            # Mutation of a function-valued binding is registration, not an effect.
            callback_kinds = [self.nodes[i].get("properties", {}).get("target_function") for i in lineage if self.nodes[i]["label"] == "FrontendInvocation"]
            event = "the operation fails" if "catch" in callback_kinds else "the operation completes successfully" if "then" in callback_kinds else None
            values.append(InteractionSemantics(**base, observable_result=result, system_event=event,
                effect_id=node["id"], effect_kind=effect_kind,
                navigation_target=node.get("properties", {}).get("target") if effect_kind == "NAVIGATION" else None,
                state_change=node.get("properties", {}).get("target") if effect_kind == "STATE" else None,
                lineage_node_ids=list(dict.fromkeys([anchor["id"], *lineage])),
                source_evidence=[*_evidence(anchor, "UI" if not system else "FRONTEND"), *_evidence(node, "FRONTEND")]))
        # Mutations and bindings share an exact scoped expression. This is an
        # AU join over graph properties, not a source scan or proximity match.
        for mutation, lineage in traversal:
            if mutation['label']!='StateMutation':
                continue
            mp=mutation.get('properties',{}); target=re.sub(r'^(?:\$scope\.|scope\.)','',mp.get('target',''))
            if mp.get('expression') not in {'true','false'}:
                continue
            for state in self.by_surface[self.surface(anchor)]:
                if state['label']!='BoundState' or state.get('properties',{}).get('expression')!=target:
                    continue
                for render in self.targets(state['id'],'CONTROLS_RENDER'):
                    rp=render['properties']; text=rp.get('text','').strip()
                    if not text:continue
                    active=mp['expression']=='true'; hidden=(rp['visibility']=='HIDE')==active
                    bodies=self.function_bodies[(start.get('properties',{}).get('owner'),start.get('properties',{}).get('function_name'))]
                    guards=[guard for body in bodies for guard in _recorded_guards(body,[m.start() for m in re.finditer(re.escape(mp['target'])+r'\s*=',body)])]
                    events=[event for guard in guards if (event:=condition_event(guard))]
                    values.append(InteractionSemantics(**{**base,'condition':rp['condition']},effect_id=render['id'],effect_kind='RENDER',
                        observable_result=f'the "{text}" {"action" if rp.get("element") in {"button","a"} else "message"} is {"hidden" if hidden else "displayed"}',
                        system_event=' and '.join(events) if events else f'{words(target)} is indicated',
                        lineage_node_ids=[anchor['id'],*lineage,state['id'],render['id']],
                        source_evidence=[*_evidence(mutation,'FRONTEND'),*_evidence(render,'UI')]))
        # A navigation owns its destination's load/model chain, but not other
        # navigation handlers merely hosted by the destination controller.
        for node, lineage in traversal:
            if node["label"] != "Navigation":
                continue
            for route in self.targets(node["id"], "NAVIGATES_TO"):
                for controller in self.targets(route["id"], "DEPENDS_ON"):
                    if controller["label"] != "AngularController":
                        continue
                    for constructor in self.targets(controller["id"], "INITIALIZES_WITH"):
                        for target, nested in self.path(constructor["id"], follow_routes=False):
                            effect = self.effect(target)
                            if target['label']=='StateMutation' and re.fullmatch(r'\w+\.data',str(target.get('properties',{}).get('expression',''))) and re.search(r'\(\s*\)\s*$',str(props.get('expression',''))):
                                # Parameterless navigation does not establish a
                                # selected record for the destination load.
                                continue
                            if effect and effect[1] == "STATE":
                                values.append(InteractionSemantics(**base, effect_id=target["id"], effect_kind="DESTINATION_"+effect[1],
                                    observable_result=effect[0], navigation_target=route["name"],
                                    lineage_node_ids=[anchor["id"], *lineage, route["id"], controller["id"], *nested],
                                    source_evidence=[*_evidence(anchor,"UI"), *_evidence(target,"FRONTEND")]))
        for condition_node in conditions:
            cp = condition_node["properties"]
            condition_description=None
            selection_models={n.get('properties',{}).get('model') for n in self.by_surface[self.surface(anchor)] if n['label']=='UISelection'}
            for mutation in self.by_label['StateMutation']:
                mp=mutation.get('properties',{})
                if _condition_key(mp.get('target',''))==cp['condition'] and '.some(' in mp.get('expression','') and any(model and model in mp['expression'] for model in selection_models):
                    condition_description='at least one record is selected'
            values.append(InteractionSemantics(**{**base, "condition": cp["condition"]},
                condition_description=condition_description,
                effect_id=condition_node["id"], effect_kind="ACTION_VISIBILITY",
                observable_result=f'the "{label}" action is {"hidden" if cp["visibility"] == "HIDE" else "displayed"}',
                lineage_node_ids=[anchor["id"], condition_node["id"]], source_evidence=_evidence(condition_node,"UI")))
        for binding in elements:
            bp=binding.get('properties',{})
            if binding['label']=='TemplateBinding' and bp.get('attribute') in {'ngDisabled','ng-disabled'}:
                values.append(InteractionSemantics(**{**base,'condition':bp['expression']},effect_id=binding['id'],effect_kind='VALIDATION_GATE',
                    observable_result=f'the "{label}" action is disabled while the form is invalid',
                    system_event='the form contains incomplete or invalid input',
                    lineage_node_ids=[anchor['id'],binding['id']],source_evidence=_evidence(binding,'UI')))
        if not values:
            values.append(InteractionSemantics(**base, lineage_node_ids=[anchor["id"], start["id"]],
                source_evidence=_evidence(anchor,"UI" if not system else "FRONTEND"),
                unresolved_reason="No executable path to an observable effect is present in the approved graph."))
        explicit_render_ids={s.effect_id for s in values if s.effect_kind=='RENDER'}
        values=[s for s in values if not(s.effect_kind=='ACTION_VISIBILITY' and s.effect_id in explicit_render_ids)]
        return values

    def effect(self, node: dict):
        p = node.get("properties", {}); kind = node["label"]
        if kind == "Navigation":
            return f"the {words(str(p.get('target', '')))} view opens", "NAVIGATION"
        if kind == "Confirmation":
            return "confirmation is requested before the guarded action proceeds", "CONFIRMATION"
        if kind == "CollectionMutation":
            collection = words(p.get("collection", "records"))
            operation = p.get("operation")
            if operation in {"push", "unshift"}:
                return f"additional {collection} are {'appended after' if operation == 'push' else 'prepended before'} the displayed records", "COLLECTION_APPEND"
            if operation == "splice":
                bodies=[body for (owner,_),values in self.function_bodies.items() if owner==p.get('owner') for body in values]
                removes=re.escape(p.get('collection',''))+r'\.splice\(\s*[^,]+,\s*[1-9]\d*\s*\)'
                if any(re.search(removes,body) for body in bodies):
                    return f"the affected {collection} are removed from the displayed collection", "COLLECTION_REMOVE"
        if kind == "StateMutation":
            expr = str(p.get("expression", "")); target = str(p.get("target", ""))
            if not expr or "=>" in expr or re.search(r"\bfunction\b",expr) or target.startswith("this."):
                return None
            if re.fullmatch(r"\w+\.data", expr) and target.startswith(("$scope.", "scope.")):
                return f"the returned {words(target)} details populate the form", "STATE"
            bindings = self.targets(node["id"], "BINDS_STATE")
            if not bindings:
                return None
            if expr == "[]":
                return f"the {words(target)} collection is initialized empty before loading", "STATE"
            if re.fullmatch(r"\w+\.data", expr):
                return f"the returned {words(target)} details populate the form", "STATE"
            if expr in {"true", "false"}:
                return f"{words(target)} is {'active' if expr == 'true' else 'inactive'}", "STATE"
        if kind == "UICondition":
            text = str(p.get("text", "")).strip()
            if text:
                return f'the "{text}" {"action" if p.get("element") in {"button", "a"} else "message"} is {"hidden" if p.get("visibility") == "HIDE" else "displayed"} when {words(p.get("condition", ""))} is active', "RENDER"
        return None

    def dependency_path(self,start:str,target:str):
        queue=deque([(start,[start])]);seen=set()
        while queue:
            current,path=queue.popleft()
            if current==target:return path
            if current in seen:continue
            seen.add(current)
            for e in self.forward[current]:
                if e['type'] in {'CALLS_API','IMPLEMENTED_BY','HANDLED_BY','INVOKES','PERFORMS'}:
                    queue.append((e['target'],[*path,e['target']]))
        return []

    def media(self, usage: dict):
        """Join directive instances via binding identity, including reverse writers."""
        values = []
        for binding in self.targets(usage["id"], "BINDS_TO"):
            for write in self.reverse[binding["id"]]:
                if write["type"] != "MUTATES_BINDING":
                    continue
                mutation = self.nodes[write["source"]]
                if not mutation.get("properties", {}).get("expression"):
                    continue
                writers = [self.nodes[e["source"]] for e in self.reverse[mutation["id"]] if e["type"] == "MUTATES"]
                for writer in writers:
                    for template in self.reverse[binding["id"]]:
                        node = self.nodes[template["source"]]
                        if node["label"] != "TemplateBinding" or node.get("properties", {}).get("element_identity") != usage.get("properties", {}).get("element_identity",usage['name']):
                            continue
                        for state in self.targets(node["id"], "BINDS_STATE"):
                            result = f"the selected file content updates the {words(state['name'])}"
                            identity = "interaction-"+sha256(f"{writer['id']}|{binding['id']}|{state['id']}".encode()).hexdigest()[:20]
                            common = dict(interaction_id=identity, interaction_type="ACTION", trigger="file selection", label=None,
                                handler_id=writer["id"], context=self.view_context(usage)+' with its file input', effect_kind="MEDIA_BINDING",
                                lineage_node_ids=[usage["id"], binding["id"], writer["id"], mutation["id"],node["id"],state["id"]],
                                source_evidence=[*_evidence(usage,"UI"),*_evidence(mutation,"FRONTEND"),*_evidence(state,"UI")])
                            values.append(InteractionSemantics(**common, effect_id=mutation["id"], observable_result=result, state_change=state["name"]))
                            for condition in self.targets(state["id"], "CONTROLS_RENDER"):
                                cp=condition["properties"]
                                negated=cp["condition"].startswith("!")
                                values.append(InteractionSemantics(**{**common, "effect_kind":"MEDIA_RENDER", "lineage_node_ids":[*common["lineage_node_ids"],condition["id"]]},
                                    effect_id=condition["id"], condition=cp["condition"],
                                    observable_result=(f'the "{cp["text"]}" prompt is shown when no file content is set' if negated and cp.get("text") else f"the {words(state['name'])} preview is displayed when file content is set")))
        return values


def propagate_interactions(graph: dict, capabilities: list[SourceCapability]) -> list[SourceCapability]:
    index = InteractionGraph(graph)
    action_semantics = {}
    for action in index.by_label["UIAction"]:
        handlers = index.targets(action["id"], "TRIGGERS")
        if handlers:
            action_semantics[action["id"]] = [s for handler in handlers for s in index.semantics(action,handler)]
    for capability in capabilities:
        ids = {e.node_id for e in capability.source_evidence}
        capability.api_metadata=[{'node_id':i,**index.nodes[i].get('properties',{})} for i in sorted(ids) if i in index.nodes and index.nodes[i]['label']=='Endpoint']
        actions = [index.nodes[i] for i in ids if i in action_semantics]
        own_api_ids={e.node_id for e in capability.source_evidence if e.stage=='API'}
        if own_api_ids:
            actions=[a for a in actions if any(own_api_ids & set(s.api_node_ids) for s in action_semantics[a['id']])]
        values = [s for action in sorted(actions,key=lambda n:n['id']) for s in action_semantics[action['id']]]
        # UI-only capabilities use their explicit trigger chain as well.
        if values:
            capability.interaction_semantics = values
            if capability.operation_kind in {'CREATE','UPDATE'}:
                persistence=[index.nodes[e.node_id] for e in capability.source_evidence if e.stage=='PERSISTENCE' and e.node_id in index.nodes]
                operations={n.get('properties',{}).get('operation') for n in persistence}
                operation='Add' if capability.operation_kind=='CREATE' else 'Update'
                if {operation,'SaveChangesAsync'} <= operations:
                    for identity in sorted({s.interaction_id for s in values}):
                        templates=[s for s in values if s.interaction_id==identity and s.effect_kind=='NAVIGATION']
                        if not templates:continue
                        semantic=templates[0].model_copy(deep=True)
                        write=next(n for n in persistence if n['properties'].get('operation')==operation)
                        semantic.effect_kind='RECORD_CREATE' if operation=='Add' else 'RECORD_UPDATE';semantic.effect_id=write['id']
                        semantic.navigation_target=None
                        semantic.observable_result='the new record is saved' if operation=='Add' else 'the changes to the selected record are saved'
                        dependency=next((path for api in sorted(own_api_ids) if (path:=index.dependency_path(api,write['id']))),[])
                        semantic.lineage_node_ids=[semantic.lineage_node_ids[0],semantic.handler_id,*dependency]
                        semantic.source_evidence.extend(_evidence(write,'PERSISTENCE'))
                        capability.interaction_semantics.append(semantic)
        elif capability.operation_kind == "UPLOAD":
            surfaces = {e.source_path for e in capability.source_evidence}
            usages = [n for surface in surfaces for n in index.by_surface[surface] if n['label']=="DirectiveUsage" and index.targets(n['id'],"USES_DIRECTIVE")]
            capability.interaction_semantics = [s for n in usages for s in index.media(n)]
        elif capability.operation_kind == "READ" and not actions:
            api_ids={e.node_id for e in capability.source_evidence if e.stage=="API"}
            functions=[index.nodes[e.node_id] for e in capability.source_evidence if e.stage=="FRONTEND" and e.node_id in index.nodes]
            # A promise callback invoking another API establishes a system
            # prerequisite. Match explicit invocation receiver/function identity.
            prerequisites=[]
            for fn in functions:
                fp=fn.get("properties",{})
                for inv in index.by_label["FrontendInvocation"]:
                    ip=inv.get("properties",{})
                    if ip.get("target_function")!="then" or ip.get("target_owner","").strip()!=fp.get("function_name","")+"()" or ip.get("caller_owner")!=fp.get("owner"):
                        continue
                    parents=[index.nodes[e['source']] for e in index.reverse[inv['id']] if e['type']=='INVOKES' and index.nodes[e['source']]['label']=='FrontendFunction']
                    dependent=[n for parent in parents for n in index.targets(parent['id'],'CALLS_API') if n['id'] not in api_ids]
                    if dependent:
                        prerequisites.append((inv,dependent))
            if prerequisites:
                headers=sorted({h for _,deps in prerequisites for n in deps for h in n.get('properties',{}).get('request_header_components',[])})
                context_name=words(headers[0].removesuffix('Id')) if len(headers)==1 else 'prerequisite'
                capability.interaction_semantics=[InteractionSemantics(
                    interaction_id="interaction-"+capability.capability_id, interaction_type="SYSTEM", system_initiated=True,
                    label=f'Automatic {context_name} context',
                    trigger="dependent operation initialization", context="a dependent operation is requested",
                    observable_result=f"the {context_name} context is obtained automatically before the dependent request runs",
                    effect_kind="SYSTEM_CONTEXT", effect_id=capability.capability_id, api_node_ids=sorted(api_ids),
                    lineage_node_ids=[prerequisites[0][0]['id'],*[n['id'] for _,deps in prerequisites for n in deps]],
                    source_evidence=capability.source_evidence)]
            else:
                matching=[]
                for action_id,semantics in action_semantics.items():
                    if any(s.effect_kind=='DESTINATION_STATE' for s in semantics) and any(n['id'] in api_ids for n,_ in index.path(action_id)):
                        matching.extend(semantics)
                if matching:
                    capability.interaction_semantics=matching
        if capability.operation_kind in {'VALIDATE','OTHER'} and not values:
            for semantic in capability.interaction_semantics:
                if semantic.interaction_type=='VALIDATION':
                    field=words(semantic.trigger or 'required input')
                    semantic.interaction_id='interaction-'+capability.capability_id
                    semantic.effect_id=capability.source_evidence[0].node_id
                    semantic.effect_kind='VALIDATION'
                    semantic.context=index.view_context(index.nodes[capability.source_evidence[0].node_id])
                    semantic.state_change=field
                    semantic.trigger=f'the user leaves {field} empty'
                    semantic.observable_result=f'{field} remains invalid until a value is provided'
                    semantic.lineage_node_ids=[e.node_id for e in capability.source_evidence]
                elif semantic.interaction_type=='SELECTION':
                    semantic.interaction_id='interaction-'+capability.capability_id
                    semantic.effect_id=capability.source_evidence[0].node_id
                    semantic.effect_kind='SELECTION'
                    semantic.context='the directory displays selectable records'
                    model=next((index.nodes[e.node_id].get('properties',{}).get('model') for e in capability.source_evidence if e.node_id in index.nodes),None)
                    aggregate=any(re.sub(r'^(?:\$scope\.|scope\.)','',n.get('properties',{}).get('target',''))==model and '.every(' in n.get('properties',{}).get('expression','') for n in index.by_label['StateMutation'])
                    semantic.state_change='all displayed record selections' if aggregate else 'an individual record selection'
                    semantic.trigger='the user toggles the select-all checkbox' if aggregate else 'the user toggles a record checkbox'
                    semantic.observable_result='all displayed record checkboxes reflect the select-all state' if aggregate else 'the chosen record reflects its checkbox selection state'
                    semantic.lineage_node_ids=[e.node_id for e in capability.source_evidence]
        if capability.operation_kind=='LIST' and values:
            extra=[]
            for action in actions:
                for handler in index.targets(action['id'],'TRIGGERS'):
                    constructors=[index.nodes[e['source']] for e in index.reverse[handler['id']] if e['type']=='INVOKES' and index.nodes[e['source']].get('properties',{}).get('function_name')=='constructor']
                    for constructor in constructors:
                        controllers=[index.nodes[e['source']] for e in index.reverse[constructor['id']] if e['type']=='INITIALIZES_WITH']
                        if not controllers:continue
                        semantics=index.semantics(action,handler)
                        for s in semantics:
                            if s.effect_kind=='ACTION_VISIBILITY':continue
                            clone=s.model_copy(deep=True)
                            clone.interaction_id='interaction-initialize-'+handler['id']
                            clone.interaction_type='SYSTEM';clone.system_initiated=True
                            clone.label='Directory presentation';clone.trigger='the directory view opens'
                            clone.context='the directory view is opening'
                            clone.lineage_node_ids=[controllers[0]['id'],constructor['id'],*clone.lineage_node_ids]
                            extra.append(clone)
            capability.interaction_semantics.extend(extra)
            ordering=[index.nodes[e.node_id] for e in capability.source_evidence if e.stage=='PERSISTENCE' and e.node_id in index.nodes]
            for node in {n['id']:n for n in ordering}.values():
                props=node.get('properties',{})
                match=re.search(r'\.OrderBy(Descending)?\(\s*(\w+)\s*=>\s*\2\.(\w+)\s*\)',props.get('expression',''))
                if not match:continue
                for interaction_id in sorted({s.interaction_id for s in capability.interaction_semantics if s.effect_kind=='COLLECTION_APPEND'}):
                    owned=[s for s in capability.interaction_semantics if s.interaction_id==interaction_id]
                    template=owned[0].model_copy(deep=True)
                    template.effect_id=node['id'];template.effect_kind='FIXED_ORDER'
                    template.observable_result=f'records retain fixed {words(match[3])} ordering ({"descending" if match[1] else "ascending"})'
                    template.lineage_node_ids=[*template.lineage_node_ids,node['id']]
                    template.source_evidence.extend(_evidence(node,'PERSISTENCE'))
                    capability.interaction_semantics.append(template)
    return capabilities

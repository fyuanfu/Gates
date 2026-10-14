#!/usr/bin/env python3
"""V1.1 contract reference validator (NOT production reportctl or semantic reviewer)."""
import argparse, hashlib, json, os, pathlib, re, sys
import yaml
from jsonschema import Draft202012Validator, FormatChecker
SCHEMAS = pathlib.Path(__file__).resolve().parent.parent / 'schemas'
FILES = [('brief.yaml','brief'),('inputs/manifest.yaml','sources-manifest'),('evidence.yaml','evidence'),('report-plan.yaml','report-plan'),('design-spec.yaml','design-spec'),('state.json','state'),('reviews/content-review.yaml','content-review'),('qa/results.json','qa-results')]
MARKER = re.compile(r'\{\{claim:(C-[0-9]{3,})\}\}')


def read(path):
    with path.open('r',encoding='utf-8') as f:
        return json.load(f) if path.suffix=='.json' else yaml.safe_load(f)

def safe_path(root, rel):
    if not isinstance(rel,str) or rel.startswith('/') or re.match(r'^[A-Za-z]:',rel) or '..' in pathlib.PurePosixPath(rel).parts: raise ValueError('unsafe path')
    candidate=(root/rel).resolve()
    if not candidate.is_relative_to(root.resolve()):raise ValueError('path escapes project root')
    return candidate

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def validate_project(root,stage='G3'):
    root=pathlib.Path(root).resolve(); issues=[]; objs={}
    def problem(path,reason):issues.append({'path':str(path),'reason':str(reason)})
    for rel,sch in FILES:
        p=root/rel
        if not p.exists():
            if rel in ('qa/results.json',) and stage in ('G1','G2','G3','G4'):continue
            problem(rel,'missing required artifact');continue
        try:
            obj=read(p); objs[sch]=obj
            schema=json.loads((SCHEMAS/(sch+'.schema.json')).read_text(encoding='utf-8'))
            for error in Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(obj):
                problem(f'{rel}:{"/".join(map(str,error.absolute_path))}',error.message)
        except Exception as e:problem(rel,f'unreadable: {e}')
    manifest=objs.get('sources-manifest',{});ev=objs.get('evidence',{});plan=objs.get('report-plan',{})
    if not (isinstance(manifest,dict) and isinstance(ev,dict) and isinstance(plan,dict)):return issues
    srcs=manifest.get('sources',[]); sources=ev.get('sources',[]); evidence=ev.get('evidence',[]);claims=ev.get('claims',[]);sections=plan.get('sections',[])
    collections=[('inputs/manifest.yaml:sources',srcs),('evidence.yaml:sources',sources),('evidence.yaml:evidence',evidence),('evidence.yaml:claims',claims),('report-plan.yaml:sections',sections)]
    for collection,items in collections:
        if not isinstance(items,list):continue
        ids=[it.get('id') for it in items if isinstance(it,dict)]
        if len(ids)!=len(set(ids)):problem(collection,'duplicate id')
    mids={x.get('id') for x in srcs if isinstance(x,dict)}; sids={x.get('id') for x in sources if isinstance(x,dict)}
    if mids != sids:problem('evidence.yaml:sources','manifest source IDs must match evidence source IDs')
    for i,item in enumerate(srcs):
        try:
            for key,hashkey in [('raw_path','original_sha256'),('snapshot_path','snapshot_sha256')]:
                p=safe_path(root,item[key]);expected=item[hashkey]
                if not p.is_file():problem(f'inputs/manifest.yaml:sources/{i}/{key}','missing source file')
                elif digest(p)!=expected:problem(f'inputs/manifest.yaml:sources/{i}/{key}','SHA-256 mismatch')
        except (ValueError,KeyError,TypeError) as e:problem(f'inputs/manifest.yaml:sources/{i}',e)
    evid_byid={x.get('id'):x for x in evidence if isinstance(x,dict)}
    claim_byid={x.get('id'):x for x in claims if isinstance(x,dict)}
    for i,e in enumerate(evidence):
        if e.get('source_ref') not in mids:problem(f'evidence.yaml:evidence/{i}/source_ref','unknown Source ID')
    source_byid={x.get('id'):x for x in srcs if isinstance(x,dict)}
    for i,e_src in enumerate(sources):
        if e_src.get('manifest_ref') not in mids or e_src.get('id')!=e_src.get('manifest_ref'):
            problem(f'evidence.yaml:sources/{i}/manifest_ref','invalid source registry link')
    used_claims={r for sec in sections if isinstance(sec,dict) for r in sec.get('claim_refs',[])}
    for i,c in enumerate(claims):
        evids=c.get('evidence_refs',[]); k=c.get('kind');verification=c.get('verification')
        for e in evids:
            if e not in evid_byid:problem(f'evidence.yaml:claims/{i}/evidence_refs',f'unknown Evidence: {e}')
        result=c.get('verification_result')
        if k=='factual':
            if verification=='not_applicable':problem(f'evidence.yaml:claims/{i}/verification','factual cannot be not_applicable')
            if (stage in ['G2','G3','G4','G5'] and c.get('critical') and verification!='verified') or (stage in ['G3','G4','G5'] and c.get('id') in used_claims and verification!='verified'):
                problem(f'evidence.yaml:claims/{i}/verification','factual claim not verified for gate')
            if verification=='verified':
                if not evids or not result or result.get('verdict')!='verified' or set(result.get('evidence_refs',[]))!=set(evids) or not result.get('source_locations'):
                    problem(f'evidence.yaml:claims/{i}/verification_result','verified factual must have a matching evidence-backed verification result')
                for evidid in evids:
                    if evidid in evid_byid:
                        sr=evid_byid[evidid].get('source_ref')
                        if source_byid.get(sr,{}).get('extraction_status')!='ok':problem(f'evidence.yaml:claims/{i}','cannot verify factual with partial/failed extraction')
        elif k in ('hypothesis','recommendation'):
            if verification!='not_applicable':problem(f'evidence.yaml:claims/{i}/verification','nonfactual must use not_applicable')
            if k=='hypothesis' and not c.get('disclosure'):problem(f'evidence.yaml:claims/{i}/disclosure','hypothesis requires explicit disclosure')
        elif k=='inference' and not evids and not c.get('reason'):
            problem(f'evidence.yaml:claims/{i}','inference requires support or rationale')
    seen_paths=set()
    for i,section in enumerate(sections):
        if not isinstance(section,dict):continue
        pth=section.get('content_path','')
        if pth in seen_paths:problem(f'report-plan.yaml:sections/{i}/content_path','duplicate content path')
        seen_paths.add(pth)
        try:
            p=safe_path(root,pth)
            if not p.is_file():problem(f'report-plan.yaml:sections/{i}/content_path','content file missing');continue
            md=p.read_text(encoding='utf-8')
        except (ValueError,UnicodeError,TypeError) as e:problem(f'report-plan.yaml:sections/{i}/content_path',e);continue
        refs=set(section.get('claim_refs',[]));markers=set(MARKER.findall(md))
        for missing in refs-set(claim_byid):problem(f'report-plan.yaml:sections/{i}/claim_refs',f'unknown claim {missing}')
        for missing in markers-refs:problem(pth,f'body marker not declared in section claim_refs: {missing}')
        for missing in refs-markers:problem(pth,f'section claim_refs not present in body: {missing}')
        for marker in markers:
            if marker not in claim_byid:problem(pth,f'unknown body claim {marker}')
            elif claim_byid[marker].get('kind')=='factual' and claim_byid[marker].get('verification')!='verified' and stage in ('G3','G4','G5'):
                problem(pth,f'unverified factual claim used: {marker}')
    d=objs.get('design-spec',{})
    if isinstance(d,dict):
        for rel in d.get('preview_paths',[]):
            try:
                if not safe_path(root,rel).is_file():problem('design-spec.yaml:preview_paths',f'preview missing: {rel}')
            except ValueError as e:problem('design-spec.yaml:preview_paths',e)
    # This reference validator intentionally does not assert semantic factual coverage or QA completeness.
    return issues

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--project',required=True);parser.add_argument('--gate',choices=['G1','G2','G3','G4','G5'],default='G3')
    args=parser.parse_args();found=validate_project(args.project,args.gate)
    print(json.dumps({'ok':not found,'code':'OK' if not found else 'E_CONTRACT','details':found},ensure_ascii=False,indent=2))
    sys.exit(0 if not found else 4)

#!/usr/bin/env python3
"""Offline, self-reading HTML builder from approved report plan/content.
This is a conservative built-in renderer; frontend-design may replace it with
richer HTML, but must preserve the same claims, evidence and QA gates.
"""
import argparse, html, pathlib, re, json, sys
import yaml
try:import mistune
except ImportError:sys.exit('mistune required: python -m pip install -r requirements.txt')
MARK=re.compile(r'\{\{claim:(C-\d{3,})\}\}')
CSS='''
:root{--bg:BG;--fg:FG;--accent:ACCENT;--base:BASEpx;--space:SPACEpx}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--fg);font-family:FONT;line-height:1.72;font-size:var(--base)}
main{max-width:1020px;margin:0 auto;padding:42px 28px 100px}header{padding:48px 0 32px;border-bottom:2px solid var(--accent)}header h1{font-size:2.35rem;line-height:1.25;margin:0 0 16px}header p{max-width:800px;font-size:1.05rem}
nav{display:flex;flex-wrap:wrap;gap:10px;margin:24px 0 44px}nav a{background:color-mix(in srgb,var(--fg) 5%,var(--bg));border-radius:7px;padding:8px 13px;text-decoration:none;color:var(--fg)}
section{margin:42px 0 64px;padding-top:22px;border-top:1px solid color-mix(in srgb,var(--fg) 15%,var(--bg))}section h2{font-size:1.75rem;line-height:1.35}section .thesis{border-left:5px solid var(--accent);padding:13px 18px;background:color-mix(in srgb,var(--accent) 9%,var(--bg));font-weight:650}
h3{margin-top:1.7em}a{color:var(--accent);overflow-wrap:anywhere}table{width:100%;border-collapse:collapse;margin:1.5em 0;font-size:.94rem}th,td{border:1px solid color-mix(in srgb,var(--fg) 18%,var(--bg));padding:10px;text-align:left;vertical-align:top;overflow-wrap:anywhere}th{background:color-mix(in srgb,var(--fg) 7%,var(--bg))}img,svg{max-width:100%;height:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere}blockquote{border-left:4px solid var(--accent);padding-left:18px;color:color-mix(in srgb,var(--fg) 78%,var(--bg))}.sources{font-size:.88rem}.sources li{padding:5px 0}footer{padding:28px 0;border-top:1px solid #aaa;font-size:.85rem}
@media(max-width:600px){main{padding:22px 16px 56px}header{padding:20px 0}header h1{font-size:1.7rem}section h2{font-size:1.38rem}table{display:block;overflow-x:auto}}
@media print{nav{display:none}section{break-inside:avoid}a{color:inherit}}
'''

def main():
 p=argparse.ArgumentParser();p.add_argument('--project',required=True);a=p.parse_args();root=pathlib.Path(a.project).resolve()
 brief=yaml.safe_load((root/'brief.yaml').read_text('utf-8'))
 plan=yaml.safe_load((root/'report-plan.yaml').read_text('utf-8'))
 design=yaml.safe_load((root/'design-spec.yaml').read_text('utf-8'))
 ev=yaml.safe_load((root/'evidence.yaml').read_text('utf-8'))
 color=design['tokens']['colors'];typo=design['tokens']['typography']
 font=typo['font_family'].replace(';','').replace('{','').replace('}','')
 css=CSS.replace('BG',color['background']).replace('FG',color['text']).replace('ACCENT',color['accent']).replace('BASE',str(typo['body_px'])).replace('SPACE',str(design['tokens']['spacing_base_px'])).replace('FONT',font)
 md=mistune.create_markdown(escape=True,plugins=['table','strikethrough'])
 titles={s['id']:s['title'] for s in ev['sources']}
 source_map={s['id']:s for s in ev['evidence']}
 claims={c['id']:c for c in ev['claims']}
 seen=[];parts=[]
 for s in plan['sections']:
  content=(root/s['content_path']).read_text('utf-8')
  found=MARK.findall(content)
  if set(found)!=set(s['claim_refs']):raise ValueError(f'Claim references mismatch in {s["id"]}')
  for cid in found:
   if cid not in claims or (claims[cid]['kind']=='factual' and claims[cid]['verification']!='verified'):raise ValueError(f'Unknown or unverified claim: {cid}')
   if cid not in seen:seen.append(cid)
  content=MARK.sub(lambda m:f' [<sup>{m.group(1)}</sup>](#ref-{m.group(1)})',content)
  parts.append(f'<section id="{html.escape(s["id"])}"><h2>{html.escape(s["title"])}</h2><p class="thesis">{html.escape(s["key_message"])}</p>{md(content)}</section>')
 refs=[]
 for cid in seen:
  c=claims[cid];evidence=[]
  for ref in c['evidence_refs']:
   e=source_map.get(ref)
   if e:evidence.append(f'{html.escape(titles.get(e["source_ref"],e["source_ref"]))} — {html.escape(e["location"])}')
  refs.append(f'<li id="ref-{cid}"><strong>{html.escape(cid)}</strong>：{html.escape(c["text"])}；依据：{"；".join(evidence) or "无外部证据（推论/建议）"}</li>')
 nav=''.join(f'<a href="#{html.escape(s["id"])}">{html.escape(s["title"])}</a>' for s in plan['sections'])
 rendered=f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(brief["title"])}</title><style>{css}</style></head><body><main><header><h1>{html.escape(brief["title"])}</h1><p>{html.escape(brief["core_thesis"])}</p><p><strong>期望行动：</strong>{html.escape(brief["desired_action"])}</p></header><nav aria-label="目录">{nav}</nav>{"".join(parts)}<section aria-label="来源与依据" class="sources"><h2>来源与依据</h2><ol>{"".join(refs) or "<li>本文未引用可核查事实资料。</li>"}</ol></section><footer>阅读型离线报告 · 所有必需资源已内嵌</footer></main></body></html>'
 dest=root/'output/index.html';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(rendered,'utf-8');print(json.dumps({'output':str(dest),'sections':len(parts),'claims':len(seen)},ensure_ascii=False))
if __name__=='__main__':main()

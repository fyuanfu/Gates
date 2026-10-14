#!/usr/bin/env python3
"""Offline Playwright QA; when unavailable, write blocked rather than fabricate pass."""
import argparse, datetime as dt, hashlib, json, pathlib, re, shutil
UTC=lambda:dt.datetime.now(dt.timezone.utc).isoformat()
VIEWPORTS=[(1440,900),(1280,800),(390,844)]
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(root):
 html=root/'output/index.html'; qa_dir=root/'qa';qa_dir.mkdir(parents=True,exist_ok=True)
 state={'schema_version':'1.1','report_id':root.name,'qa_status':'blocked','html_sha256':hashfile(html) if html.exists() else '0'*64,'tested_at':UTC(),'viewports':[],'findings':[],'checks':[]}
 def check(name,ok,observation):state['checks'].append({'id':name,'status':'pass' if ok else 'fail','oracle':name,'observation':observation})
 if not html.exists():
  state['checks'].append({'id':'html-exists','status':'blocked','oracle':'HTML must exist','observation':'output/index.html not found'})
 else:
  content=html.read_text('utf-8')
  bad=bool(re.search(r'@import|\bfetch\s*\(|\bXMLHttpRequest\b|<iframe\b|<(?:img|script|source|link)\b[^>]*(?:src|href)\s*=\s*["\']https?://',content,re.I))
  check('inline-assets',not bad,'remote auto-resource or network API found' if bad else 'no known automatic remote resources')
  check('claim-markers',not bool(re.search(r'\{\{claim:',content)),'unexpanded claim markers' if '{{claim:' in content else 'none')
  try:
   from playwright.sync_api import sync_playwright
   with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True, executable_path=shutil.which("chromium") or shutil.which("google-chrome"))
    for w,h in VIEWPORTS:
     pg=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1)
     network=[];errors=[]
     pg.on('request',lambda req:network.append(req.url) if not req.url.startswith(('file:','data:','blob:')) else None)
     pg.on('pageerror',lambda err:errors.append(str(err)))
     pg.route('**/*',lambda route:route.abort() if not route.request.url.startswith(('file:','data:','blob:')) else route.continue_())
     pg.goto(html.resolve().as_uri(),wait_until='load')
     width=pg.evaluate('document.documentElement.scrollWidth');inner=pg.evaluate('window.innerWidth')
     visible=pg.locator('main').is_visible() if pg.locator('main').count() else False
     ok=not network and not errors and visible and width<=inner+2
     rel=f'qa/viewport-{w}x{h}.png'; pg.screenshot(path=str(root/rel),full_page=True)
     state['viewports'].append({'width':w,'height':h,'status':'pass' if ok else 'fail','screenshot':rel})
     if not ok:state['findings'].append({'id':f'viewport-{w}','severity':'P1','status':'open','location':rel,'description':f'width={width},viewport={inner},requests={network},errors={errors},main_visible={visible}'})
     pg.close()
    browser.close()
   check('playwright-execution',True,'Chromium launched; screenshots captured')
  except Exception as e:
   state['checks'].append({'id':'playwright-execution','status':'blocked','oracle':'run headless Chromium','observation':str(e)[:300]})
 state['qa_status']='passed' if len(state['viewports'])==len(VIEWPORTS) and all(v['status']=='pass' for v in state['viewports']) and all(c['status']=='pass' for c in state['checks']) else 'blocked' if any(c['status']=='blocked' for c in state['checks']) else 'failed'
 (qa_dir/'results.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf-8')
 (qa_dir/'qa-report.md').write_text(f'# HTML QA\n\nStatus: **{state["qa_status"]}**\n\n'+ '\n'.join(f'- {c["id"]}: {c["status"]} ({c["observation"]})' for c in state['checks']),'utf-8')
 return state
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--project',required=True);a=p.parse_args();res=run(pathlib.Path(a.project).resolve());print(json.dumps({'qa_status':res['qa_status'],'checks':res['checks']},ensure_ascii=False));raise SystemExit(0 if res['qa_status']=='passed' else 4)

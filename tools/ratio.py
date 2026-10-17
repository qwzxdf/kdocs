import glob,re,sys,os
sys.stdout.reconfigure(encoding='utf-8')
rows=[]
for f in glob.glob('docs/graphics/**/*.md',recursive=True):
    s=open(f,encoding='utf-8').read()
    s=re.sub(r'<svg.*?</svg>','',s,flags=re.S)
    s=re.sub(r'<div class="anim.*?</div>','',s,flags=re.S)
    s=re.sub(r'```.*?```','',s,flags=re.S)
    s=re.sub(r'## 参考.*','',s,flags=re.S)
    L=[l for l in s.split('\n') if l.strip()]
    tb=sum(len(l) for l in L if l.startswith('|'))
    tot=sum(len(l) for l in L)
    pr=tot-tb
    rows.append((tb/(tot+1),tb,pr,f.replace('docs/graphics/','')))
rows.sort(key=lambda r:r[3])
for r,tb,pr,f in rows:
    print(f"{r:.2f} {tb:6d} {pr:6d} {f}")

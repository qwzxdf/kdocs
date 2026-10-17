import json,os,re,glob,sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0,'tools')
from rename_titles import T
old=json.load(open('tools/_old_titles.json',encoding='utf-8'))
R='docs/graphics/'
new={os.path.normpath(R+k+'.md'):T[k] for k in old}
oldt={os.path.normpath(R+k+'.md'):old[k] for k in old}
link=re.compile(r'\[([^\]]+)\]\(([^)\s#]+\.md)(#[^)]*)?\)')
n=0
for f in glob.glob('docs/**/*.md',recursive=True):
    s=open(f,encoding='utf-8',newline='').read()
    base=os.path.dirname(f)
    def rep(m):
        global n
        t=m.group(1);p=os.path.normpath(os.path.join(base,m.group(2)))
        if p in new:
            o=oldt[p]
            txt=t.replace('**','')
            if txt==o or txt==o.replace(' ','') :
                n+=1
                return '['+new[p]+']('+m.group(2)+(m.group(3) or '')+')'
        return m.group(0)
    s2=link.sub(rep,s)
    if s2!=s: open(f,'w',encoding='utf-8',newline='').write(s2)
print('links',n)
# .pages
ren={'shadows':'Shadows','ao':'Ambient Occlusion (AO)','gi':'Global Illumination (GI)','reflections':'Reflections','postprocess':'Post-Processing','translucency':'Translucency','water':'Water','terrain':'Terrain','atmosphere':'Sky and Atmosphere'}
for f in glob.glob('docs/graphics/**/.pages',recursive=True):
    s=open(f,encoding='utf-8',newline='').read()
    out=[]
    for line in s.split('\n'):
        m=re.match(r'^(\s*- )(.+?): (\S+?)(\r?)$',line)
        if m and not m.group(3).endswith('.md'):
            d=os.path.join(os.path.dirname(f),m.group(3),'index.md')
            k=os.path.relpath(d,R).replace(chr(92),'/')[:-3]
            if k in T: line=f'{m.group(1)}{T[k]}: {m.group(3)}{m.group(4)}'
        out.append(line)
    open(f,'w',encoding='utf-8',newline='').write('\n'.join(out))

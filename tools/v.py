import sys,re
sys.stdout.reconfigure(encoding='utf-8')
for p in sys.argv[1:]:
    s=open(p,encoding='utf-8').read()
    s=re.sub(r'<svg.*?</svg>','[SVG]',s,flags=re.S)
    s=re.sub(r'<div class="anim.*?</div>','[ANIM]',s,flags=re.S)
    s=re.sub(r'\n---\ntitle.*?\n---\n','\n',s,count=1,flags=re.S)
    s=re.sub(r'## 参考.*','',s,flags=re.S)
    print('=====',p,len(s)); print(s)

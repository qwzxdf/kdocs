import sys,re
sys.stdout.reconfigure(encoding='utf-8')
# 表の位置と、表の直前の文を出す
for p in sys.argv[1:]:
    L=open(p,encoding='utf-8').read()
    L=re.sub(r'<svg.*?</svg>','',L,flags=re.S)
    L=re.sub(r'```.*?```','[code]',L,flags=re.S).split('\n')
    print('=====',p)
    i=0
    while i<len(L):
        if L[i].startswith('|'):
            j=i
            while j<len(L) and L[j].startswith('|'): j+=1
            ctx=[l for l in L[max(0,i-3):i] if l.strip()]
            print('--', ' / '.join(c[:100] for c in ctx[-2:]))
            for l in L[i:j]:
                if not set(l)<=set('|- '): print(l[:230])
            i=j
        else: i+=1

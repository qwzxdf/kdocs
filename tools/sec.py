import sys
def sec(path, start, end, new):
    """start 見出し行の先頭から、end 見出し行の直前までを new に置換。end=None はファイル末まで。"""
    s=open(path,encoding='utf-8',newline='').read()
    nl='\r\n' if '\r\n' in s else '\n'
    s=s.replace('\r\n','\n')
    a=s.index(start)
    b=s.index(end,a+len(start)) if end else len(s)
    old=s[a:b]
    assert not any(k in old for k in ('<svg','<div class="anim','<!-- fig')), 'section contains figure: '+start[:30]
    s=s[:a]+new.strip('\n')+'\n\n'+s[b:]
    open(path,'w',encoding='utf-8',newline='').write(s.replace('\n',nl))
def rep(path, old, new, count=1):
    s=open(path,encoding='utf-8',newline='').read()
    nl='\r\n' if '\r\n' in s else '\n'
    s=s.replace('\r\n','\n')
    assert old in s, old[:40]
    s=s.replace(old,new,count)
    open(path,'w',encoding='utf-8',newline='').write(s.replace('\n',nl))

def tbl(path, header_prefix, new, nth=0):
    """header_prefix で始まる行から続く表（'|' 始まりの連続行）を new に置換。"""
    s=open(path,encoding='utf-8',newline='').read()
    nl='\r\n' if '\r\n' in s else '\n'
    s=s.replace('\r\n','\n')
    L=s.split('\n')
    idx=[i for i,l in enumerate(L) if l.startswith(header_prefix)]
    assert len(idx)>nth, ('no table', header_prefix)
    i=idx[nth]; j=i
    while j<len(L) and L[j].startswith('|'): j+=1
    L[i:j]=new.strip('\n').split('\n')
    open(path,'w',encoding='utf-8',newline='').write(nl.join(L))

"""docs/vs の表を、規則に合わないものだけ箇条書きに直す（残す表は KEEP に (ファイル, 開始行) で書く）。"""
import sys, glob, re
KEEP = {('index.md',9),('index.md',43),('libraries.md',24),('package-managers.md',62),('project-types.md',27),
 ('terms/configuration.md',55),('terms/msvc.md',137),('terms/platform.md',24),('editorconfig.md',59),
 ('editorconfig.md',213),('include-dirs.md',92),('settings.md',83),('profiler.md',179),('terms/project.md',166),
 ('terms/build.md',74),('terms/build.md',101),('tips.md',25),('unit-test.md',25),('errors.md',23),('terms/msvc.md',24)}
def cells(r): return [c.strip() for c in r.strip().strip('|').split('|')]
def run(apply):
    for f in sorted(glob.glob('docs/vs/**/*.md', recursive=True)):
        rel = f[8:].replace(chr(92),'/')
        L = open(f, encoding='utf-8').read().split('\n'); out=[]; i=0; fence=False; ch=False
        while i < len(L):
            if L[i].startswith('```'): fence = not fence
            if not fence and L[i].startswith('|') and (i==0 or not L[i-1].startswith('|')):
                j=i
                while j<len(L) and L[j].startswith('|'): j+=1
                if (rel,i+1) in KEEP: out+=L[i:j]
                else:
                    h=cells(L[i]); rows=[cells(r) for r in L[i+2:j]]
                    if not apply: print(rel,i+1,h)
                    for r in rows:
                        r=r+['']*(len(h)-len(r))
                        if len(r)>len(h): r=r[:len(h)-1]+[' | '.join(r[len(h)-1:])]
                        if len(h)==2: out.append(f"- <strong>{r[0]}</strong>: {r[1]}")
                        else: out.append(f"- <strong>{r[0]}</strong>: "+"。".join((f"{h[k]}: " if h[k] else "")+r[k] for k in range(1,len(r)) if r[k]))
                    ch=True
                i=j
            else: out.append(L[i]); i+=1
        if apply and ch: open(f,'w',encoding='utf-8').write('\n'.join(out))
run(len(sys.argv)>1)

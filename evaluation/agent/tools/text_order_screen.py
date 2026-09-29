#!/usr/bin/env python3
"""Text screen for hidden-order candidates in C/C++ sources (29 Sep 2026; no DiscoPoP, no model).

An innermost `for` loop is a candidate when one statement writes an array element that ANOTHER, textually EARLIER
statement of the same body reads through a different subscript that hides the distance: an index read from an
array (`v[kv[i]]`, "indirect") or a variable offset ("offset"). A split of such a loop in textual order may be
wrong, and whether it is depends on data the text does not show — the ORDER-2 situation of E2-V3. Candidates
are then profiled with DiscoPoP and checked with order_screen.py, which reads the order from what DiscoPoP measured.

    venv/bin/python evaluation/agent/tools/text_order_screen.py DIR [DIR ...]
"""
import re
import sys
from pathlib import Path
from typing import Iterator, List, Tuple
ACC=re.compile(r'([A-Za-z_]\w*(?:->\w+|\.\w+)*)\s*\[((?:[^\[\]]|\[[^\[\]]*\])*)\]')
def loops(s: str) -> Iterator[Tuple[int, str, str]]:
    for m in re.finditer(r'\bfor\s*\(',s):
        j=s.find('(',m.start()); d=0; k=j
        while k<len(s):
            if s[k]=='(': d+=1
            elif s[k]==')':
                d-=1
                if d==0: break
            k+=1
        head=s[j+1:k]; rest=s[k+1:]; lead=len(rest)-len(rest.lstrip()); rest=rest.lstrip()
        if not rest.startswith('{'): continue
        d=0; start=k+1+lead
        for e in range(start,len(s)):
            if s[e]=='{': d+=1
            elif s[e]=='}':
                d-=1
                if d==0: yield m.start(), head, s[start+1:e]; break
def screen(files: List[Path]) -> List[Tuple[str, int, str, str, str, str, str]]:
    out: List[Tuple[str, int, str, str, str, str, str]] = []
    for f in files:
        s=Path(f).read_text(errors='ignore')
        s=re.sub(r'/\*.*?\*/',lambda x:'\n'*x.group(0).count('\n'),s,flags=re.S); s=re.sub(r'//[^\n]*','',s)
        for pos, head, b in loops(s):
            if re.search(r'\bfor\s*\(',b) or len(b)>2500: continue
            ctr=re.findall(r'([A-Za-z_]\w*)\s*(?:\+\+|--|\+=|-=)',head)
            stmts=[x.strip() for x in b.split(';')]
            acc: List[Tuple[int, str, str, str]] = []
            for n,st in enumerate(stmts):
                mm=re.match(r'(.*?)(\+=|-=|\*=|/=|(?<![=!<>])=(?!=))(.*)',st,re.S)
                if not mm: continue
                lhs,op,rhs=mm.groups()
                for a in ACC.finditer(lhs):
                    acc.append((n,'W',a.group(1),a.group(2)))
                    if op!='=': acc.append((n,'R',a.group(1),a.group(2)))
                for a in ACC.finditer(rhs): acc.append((n,'R',a.group(1),a.group(2)))
            def hid(sub: str) -> str:
               
                if '[' in sub: return 'indirect'
                names=set(re.findall(r'[A-Za-z_]\w*',sub))-set(ctr)
                return 'offset' if names else ''
            for (nw,t,x,sw) in acc:
                if t!='W': continue
                for (nr,t2,y,sr) in acc:
                    if t2=='R' and x==y and nw!=nr and (hid(sw) or hid(sr)):
                        out.append((str(f), s[:pos].count('\n')+1, x, sw, sr, 'writer after reader' if nw>nr else 'writer before reader', hid(sw) or hid(sr)))
    return out

def main() -> int:
    files = [p for a in sys.argv[1:] for p in (Path(a).rglob("*") if Path(a).is_dir() else [Path(a)])
             if p.suffix in (".c", ".cc", ".cpp", ".C", ".h", ".hpp", ".cxx")]
    seen = set()
    for h in screen(files):
        f, line, x, sw, sr, order, kind = h
        if sw.replace(" ", "") == sr.replace(" ", "") or order != "writer after reader":
            continue
        if (f, line, x) in seen:
            continue
        seen.add((f, line, x))
        print(f"{f}:{line}  {x}  written [{sw}]  read earlier [{sr}]  ({kind})")
    print(f"{len(seen)} candidate pair(s) in {len(files)} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

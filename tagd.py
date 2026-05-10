#!/usr/bin/env python3
import argparse, os, sys, tempfile
from pathlib import Path

F = ".filetags"
SEP = " -- "

def e(n):
    if any(c in n for c in ' \t"\\') or SEP in n:
        return '"' + n.replace('\\', '\\\\').replace('"', '\\"') + '"'
    return n

def p(l):
    l = l.rstrip('\n\r')
    if not l:
        return None, None
    if l[0] == '"':
        i, c = 1, []
        while i < len(l):
            if l[i] == '\\' and i + 1 < len(l):
                c.append(l[i + 1])
                i += 2
            elif l[i] == '"':
                i += 1
                break
            else:
                c.append(l[i])
                i += 1
        name = ''.join(c)
        rest = l[i:]
        if rest.startswith(SEP):
            return name, rest[len(SEP):]
        return name, rest.lstrip(' \t')
    if SEP in l:
        name, _, comment = l.partition(SEP)
        return name, comment
    return l, ''

def w(d, lines):
    if lines:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=d.parent, delete=False) as t:
            for x in lines:
                t.write(x + '\n')
        os.replace(t.name, d)
    else:
        d.unlink(missing_ok=True)

def cmd_s(args):
    f = Path(args.f).resolve()
    if not f.exists():
        print(f"not found: {f}", file=sys.stderr)
        sys.exit(1)
    d = f.parent / F
    c = ' '.join(args.c)
    lines = []
    if d.exists():
        with open(d, 'r', encoding='utf-8') as h:
            for l in h:
                n, _ = p(l)
                if n == f.name:
                    continue
                lines.append(l.rstrip('\n\r'))
    if c:
        lines.append(f"{e(f.name)}{SEP}{c}")
    w(d, lines)
    print(f"ok {f.name}")

def cmd_g(args):
    f = Path(args.f).resolve()
    d = f.parent / F
    if d.exists():
        with open(d, 'r', encoding='utf-8') as h:
            for l in h:
                n, c = p(l)
                if n == f.name:
                    print(c)
                    return
    print("—")
    sys.exit(1)

def cmd_r(args):
    f = Path(args.f).resolve()
    d = f.parent / F
    if not d.exists():
        return
    lines = []
    with open(d, 'r', encoding='utf-8') as h:
        for l in h:
            n, _ = p(l)
            if n == f.name:
                continue
            lines.append(l.rstrip('\n\r'))
    w(d, lines)

def cmd_m(args):
    o = Path(args.o).resolve()
    q = Path(args.n).resolve()
    d = o.parent / F
    if not d.exists():
        print("no .filetags", file=sys.stderr)
        sys.exit(1)
    lines, found = [], False
    with open(d, 'r', encoding='utf-8') as h:
        for l in h:
            n, c = p(l)
            if n == o.name:
                found = True
                lines.append(f"{e(q.name)}{SEP}{c}")
            else:
                lines.append(l.rstrip('\n\r'))
    if not found:
        print("not found")
        return
    w(d, lines)
    print(f"ok {o.name} -> {q.name}")

def cmd_l(args):
    d = Path(args.d).resolve() / F
    if not d.exists():
        print("empty")
        return
    rows = []
    with open(d, 'r', encoding='utf-8') as h:
        for l in h:
            n, c = p(l)
            if n:
                rows.append((n, c))
    if not rows:
        print("empty")
        return
    wn = max(len(n) for n, _ in rows)
    wc = max(len(c) for _, c in rows) if any(c for _, c in rows) else 7
    wn = max(wn, 4)
    wc = max(wc, 7)
    print("┌" + "─" * (wn + 2) + "┬" + "─" * (wc + 2) + "┐")
    print(f"│ {'file':<{wn}} │ {'comment':<{wc}} │")
    print("├" + "─" * (wn + 2) + "┼" + "─" * (wc + 2) + "┤")
    for n, c in rows:
        print(f"│ {n:<{wn}} │ {c:<{wc}} │")
    print("└" + "─" * (wn + 2) + "┴" + "─" * (wc + 2) + "┘")

def cmd_c(args):
    dr = Path(args.d).resolve()
    f = dr / F
    if not f.exists():
        print("0")
        return
    lines, k = [], 0
    with open(f, 'r', encoding='utf-8') as h:
        for l in h:
            n, _ = p(l)
            if n and not (dr / n).exists():
                k += 1
                continue
            lines.append(l.rstrip('\n\r'))
    w(f, lines)
    print(k)

def main():
    a = argparse.ArgumentParser(prog='tag', add_help=False)
    a.add_argument('-h', '--help', action='store_true')
    a.add_argument('-s', nargs='+', metavar=('file', 'comment'), help='set tag')
    a.add_argument('-g', metavar='file', help='get tag')
    a.add_argument('-r', metavar='file', help='remove tag')
    a.add_argument('-m', nargs=2, metavar=('old', 'new'), help='move tag')
    a.add_argument('-l', nargs='?', metavar='dir', const='.', default=None, help='list tags')
    a.add_argument('-c', nargs='?', metavar='dir', const='.', default=None, help='clean dead tags')
    args = a.parse_args()

    if args.help or not any((args.s, args.g, args.r, args.m, args.l is not None, args.c is not None)):
        print("usage: tag -s file comment | -g file | -r file | -m old new | -l [dir] | -c [dir]")
        sys.exit(0)

    if args.s:
        class A: pass
        o = A(); o.f = args.s[0]; o.c = args.s[1:]; cmd_s(o)
    elif args.g:
        class A: pass
        o = A(); o.f = args.g; cmd_g(o)
    elif args.r:
        class A: pass
        o = A(); o.f = args.r; cmd_r(o)
    elif args.m:
        class A: pass
        o = A(); o.o = args.m[0]; o.n = args.m[1]; cmd_m(o)
    elif args.l is not None:
        class A: pass
        o = A(); o.d = args.l; cmd_l(o)
    elif args.c is not None:
        class A: pass
        o = A(); o.d = args.c; cmd_c(o)

if __name__ == '__main__':
    main()
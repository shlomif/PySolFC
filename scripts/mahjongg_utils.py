#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-

import sys, os, re

alpha = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def decode_layout(layout):
    # decode tile positions
    assert layout[0] == "0"
    assert (len(layout) - 1) % 3 == 0
    tiles = []
    for i in range(1, len(layout), 3):
        n = alpha.find(layout[i])
        level, height = n / 7, n % 7 + 1
        tx = alpha.find(layout[i+1])
        ty = alpha.find(layout[i+2])
        assert n >= 0 and tx >= 0 and ty >= 0
        for tl in range(level, level + height):
            tiles.append((tl, tx, ty))
    tiles.sort()
    return tiles

def encode_layout(layout):
    # encode positions
    s = '0'
    ##layout.sort()
    x_max = max([t[1] for t in layout])
    y_max = max([t[2] for t in layout])
    for x in range(x_max+1):
        for y in range(y_max+1):
            l = [t[0] for t in layout if t[1] == x and t[2] == y]
            if not l:
                continue
            i_0 = i_n = l[0]
            for i in l[1:]:
                if i == i_n+1:
                    i_n = i
                    continue
                s += alpha[i_0*7+(i_n-i_0)] + alpha[x] + alpha[y]
                i_0 = i_n = i
            s += alpha[i_0*7+(i_n-i_0)] + alpha[x] + alpha[y]

##     for tl, tx, ty in layout:
##         s += alpha[tl*7]+alpha[tx]+alpha[ty]
    return s



def parse_kyodai(filename):
    # Kyodai (http://www.kyodai.com/)

    fd = open(filename)
    fd.readline()
    fd.readline()

    s = fd.readline()
    i = 0
    y = 0
    z = 0
    layout = []
    while True:
        ss = s[i:i+34]
        if not ss:
            break
        x = 0
        for c in ss:
            if c == '1':
                layout.append((z, x, y))
            x += 1
        y += 1
        if y == 20:
            y = 0
            z += 1
        i += 34
    layout.sort()
    return normalize(layout)


def parse_ace(filename):
    # Ace of Penguins (http://www.delorie.com/store/ace/)
    l = open(filename).read().replace('\n', '').split(',')
    l.reverse()
    layout = []
    layer = 0
    while True:
        x = int(l.pop())
        if x == 127:
            break
        if x <= 0:
            x = -x
            y, z = int(l.pop()), int(l.pop())
            if layer < z:
                layer = z
        layout.append((z, x, y))
    layout.sort()
    return normalize(layout)


def parse_kmahjongg(filename):
    # KMahjongg
    fd = open(filename)
    fd.readline()
    lines = fd.readlines()
    level = 0
    n = 0
    layout = []
    for s in lines:
        i = 0
        while True:
            i = s.find('1', i)
            if i >= 0:
                layout.append((level, i, n))
                i += 1
            else:
                break
        n += 1
        if n == 16:
            n = 0
            level += 1
    layout.sort()
    return normalize(layout)


def parse_xmahjongg(filename):
    if open(filename).readline().startswith('Kyodai'):
        return parse_kyodai(filename)
    fd = open(filename)
    layout = []
    for s in fd:
        s = s.strip()
        if not s:
            continue
        if s.startswith('#'):
            continue
        row, col, lev = s.split()
        layout.append((int(lev), int(col), int(row)))
    layout.sort()
    return normalize(layout)


def normalize(l):
    minx = min([i[1] for i in l])
    if minx:
        l = [(i[0], i[1]-minx, i[2]) for i in l]
    miny = min([i[2] for i in l])
    if miny:
        l = [(i[0], i[1], i[2]-miny) for i in l]
    return l


if __name__ == '__main__':
    gameid = 5200

    usage = '''usage:
%s TYPE FILE ...
  where TYPE are:
    k | kyodai    - parse kyodai file
    x | xmahjongg - parse xmahjongg file
    m | kmahjongg - parse kmahjongg file
    a | ace       - parse ace of penguins file
''' % sys.argv[0]

    if len(sys.argv) < 3:
        sys.exit(usage)
    if sys.argv[1] in ['k', 'kyodai']:
        parse_func = parse_kyodai
    elif sys.argv[1] in ['x', 'xmahjongg']:
        parse_func = parse_xmahjongg
    elif sys.argv[1] in ['m', 'kmahjongg']:
        parse_func = parse_kmahjongg
    elif sys.argv[1] in ['a', 'ace']:
        parse_func = parse_ace
    else:
        sys.exit(usage)

    for filename in sys.argv[2:]:

        layout = parse_func(filename)
        layout = normalize(layout)

        #print filename, len(layout)

        s = encode_layout(layout)

        # check
        lt = decode_layout(s)
        if lt != layout:
            print '*** ERROR ***'
        else:
            ##print s

            gamename = os.path.split(filename)[1].split('.')[0]
            #classname = gamename.replace(' ', '_')
            #classname = 'Mahjongg_' + re.sub('\W', '', classname)

            ncards = len(layout)

            if ncards != 144:
                print '''r(%d, "%s", ncards=%d, layout="%s")
''' % (gameid, gamename, ncards, s)

            else:
                print '''r(%d, "%s", layout="%s")
''' % (gameid, gamename, s)

            gameid += 1


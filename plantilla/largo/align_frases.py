import json, re

T = json.load(open('/home/claude/largo/timing.json'))
g = {c['id']: c for c in json.load(open('/home/claude/largo/guion.json'))}
for cid, d in T.items():
    words = g[cid]['texto'].split()
    # phrases: split after punctuation
    phrases, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r'[.,:;?!…]$', w):
            phrases.append(cur); cur = []
    if cur: phrases.append(cur)
    pch = [sum(len(w) + 1 for w in p) for p in phrases]
    sp = d['speech']
    sdur = [b - a for a, b in sp]
    rate = sum(pch) / sum(sdur)
    P, S = len(phrases), len(sp)
    INF = 1e18
    cost = [[INF] * (S + 1) for _ in range(P + 1)]
    back = [[None] * (S + 1) for _ in range(P + 1)]
    cost[0][0] = 0
    for i in range(P + 1):
        for j in range(S + 1):
            if cost[i][j] >= INF: continue
            for di in range(1, 5):
                for dj in range(1, 5):
                    ni, nj = i + di, j + dj
                    if ni > P or nj > S: continue
                    ch = sum(pch[i:ni]); du = sum(sdur[j:nj])
                    c = cost[i][j] + (ch / rate - du) ** 2 + 0.3 * (di - 1) + 0.15 * (dj - 1)
                    if c < cost[ni][nj]:
                        cost[ni][nj] = c; back[ni][nj] = (i, j)
    # trace
    i, j = P, S
    groups = []
    while (i, j) != (0, 0):
        pi, pj = back[i][j]
        groups.append((pi, i, pj, j)); i, j = pi, pj
    groups.reverse()
    timed = []
    for pi, i2, pj, j2 in groups:
        ws = [w for p in phrases[pi:i2] for w in p]
        segs = sp[pj:j2]
        tot_sp = sum(b - a for a, b in segs)
        wt = [len(w) + 1 for w in ws]; tw = sum(wt)
        def at(x):
            acc = 0
            for a, b in segs:
                if acc + (b - a) >= x: return a + (x - acc)
                acc += b - a
            return segs[-1][1]
        acc = 0
        for w, k in zip(ws, wt):
            s = at(acc / tw * tot_sp); acc += k; e = at(acc / tw * tot_sp - 1e-4)
            timed.append([w, round(s, 3), round(e, 3)])
    assert len(timed) == len(words), cid
    d['words'] = timed
    print(cid, 'grupos', len(groups), 'costo', round(cost[P][S], 2))
json.dump(T, open('/home/claude/largo/timing.json', 'w'), ensure_ascii=False)

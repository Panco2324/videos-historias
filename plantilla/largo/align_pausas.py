import json, re, subprocess

g = json.load(open('/home/claude/largo/guion.json'))
out = {}
for i, c in enumerate(g, 1):
    f = f'/home/claude/largo/assets/voz{i}.mp3'
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))
    log = subprocess.run(['ffmpeg', '-nostdin', '-i', f, '-af', 'silencedetect=noise=-32dB:d=0.18', '-f', 'null', '-'], capture_output=True, text=True).stderr
    ss = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]
    se = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
    sil = list(zip(ss, se + [dur] * (len(ss) - len(se))))
    # speech intervals
    sp = []
    t = 0.0
    for a, b in sil:
        if a > t + 0.02:
            sp.append((t, a))
        t = b
    if t < dur - 0.02:
        sp.append((t, dur))
    speech_total = sum(b - a for a, b in sp)
    words = c['texto'].split()
    weights = [len(w) + (6 if re.search(r'[.?!…:;]$', w) else 2 if w.endswith(',') else 1) for w in words]
    # punctuation weight approximates the pause; but pauses are already removed, so use plain char weights inside speech
    weights = [len(w) + 1 for w in words]
    tot = sum(weights)
    # also align sentence-ending words to silence starts when counts match
    def speech_to_time(x):
        acc = 0.0
        for a, b in sp:
            if acc + (b - a) >= x:
                return a + (x - acc)
            acc += b - a
        return sp[-1][1]
    timed = []
    acc = 0.0
    for w, wt in zip(words, weights):
        s = speech_to_time(acc / tot * speech_total)
        acc += wt
        e = speech_to_time(acc / tot * speech_total - 1e-4)
        timed.append([w, round(s, 3), round(e, 3)])
    out[c['id']] = {'dur': dur, 'words': timed, 'speech': sp}
    print(c['id'], round(dur, 1), len(sp), 'tramos', len(words), 'palabras')
json.dump(out, open('/home/claude/largo/timing.json', 'w'), ensure_ascii=False)

import json, subprocess, sys
ROOT = '/home/claude/largo'
SF = '/home/claude/videos-historias/plantilla/sfx'
VOL = {'boom': 0.55, 'whoosh': 0.45}
for cid in sys.argv[1:] or [f'c{i}' for i in range(1, 10)]:
    num = int(cid[1:])
    info = json.load(open(f'{ROOT}/proj/{cid}/info.json'))
    dur = info['dur']
    ev = [(k, t) for k, t, _ in info['sfx']]
    # whoosh suave en cada corte de clip
    ev += [('whoosh_soft', s) for _, s, _, _ in info['bg'][1:]]
    inputs = ['-stream_loop', '-1', '-i', f'{SF}/drone.wav', '-stream_loop', '-1', '-i', '/home/claude/videos-historias/plantilla/sfx/musica_suspenso.mp3']
    filt = [f'[0:a]atrim=0:{dur},volume=0.12,afade=t=in:d=1.2,afade=t=out:st={max(dur-1.5,0)}:d=1.5[a0]',
            f'[1:a]atrim={num*7}:{num*7+dur},asetpts=PTS-STARTPTS,volume=0.13,afade=t=in:d=2,afade=t=out:st={max(dur-1.5,0)}:d=1.5[m0]']
    labels = ['[a0]', '[m0]']
    for n, (k, t) in enumerate(ev, 2):
        f = 'whoosh' if k.startswith('whoosh') else 'boom'
        v = 0.18 if k == 'whoosh_soft' else VOL[f]
        inputs += ['-i', f'{SF}/{f}.wav']
        ms = int(max(t, 0) * 1000)
        filt.append(f'[{n}:a]volume={v},adelay={ms}|{ms}[a{n}]')
        labels.append(f'[a{n}]')
    filt.append(''.join(labels) + f'amix=inputs={len(labels)}:normalize=0,atrim=0:{dur},aformat=sample_rates=48000:channel_layouts=stereo[out]')
    out = f'{ROOT}/assets/sfx{num}.wav'
    subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', *inputs, '-filter_complex', ';'.join(filt), '-map', '[out]', out], check=True)
    dst = f'{ROOT}/proj/{cid}/assets/sfx{num}.wav'
    import os
    if not os.path.exists(dst): os.symlink(out, dst)
    print(cid, len(ev), 'efectos')

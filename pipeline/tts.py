import sys, soundfile as sf, numpy as np, json
from kokoro_onnx import Kokoro
k=Kokoro('/home/claude/pipe/models/kokoro-v1.0.int8.onnx','/home/claude/pipe/models/voices-v1.0.bin')
voice=sys.argv[2] if len(sys.argv)>2 else 'bm_george'
lines=[l.strip() for l in open(sys.argv[1]) if l.strip()]
out=[];t=0;meta=[];sr=24000
gap=np.zeros(int(0.28*sr),dtype=np.float32)
for l in lines:
    a,sr=k.create(l,voice=voice,speed=0.95,lang='en-gb')
    meta.append({'text':l,'start':t,'end':t+len(a)/sr}); out+= [a,gap]; t+=len(a)/sr+0.28
sf.write('voice.wav',np.concatenate(out),sr); json.dump(meta,open('timing.json','w'),indent=1)
print(round(t,2))

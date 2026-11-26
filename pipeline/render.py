# usage: render.py workdir scene_map(json list of scene file per line) out.mp4 [W H]
import sys, json, subprocess, math, re
from PIL import Image, ImageDraw, ImageFont
wd=sys.argv[1]; smap=json.loads(sys.argv[2]); out=sys.argv[3]
W=int(sys.argv[4]) if len(sys.argv)>4 else 1080; H=int(sys.argv[5]) if len(sys.argv)>5 else 1920
FPS=30
tm=json.load(open(f'{wd}/timing.json'))
total=tm[-1]['end']+0.6
font=ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', 88 if H>W else 64)
# caption chunks
caps=[]
for t in tm:
    words=t['text'].split(); n=3
    chunks=[' '.join(words[i:i+n]) for i in range(0,len(words),n)]
    if len(chunks)>1 and len(chunks[-1].split())==1: chunks[-2]+=' '+chunks[-1]; chunks.pop()
    L=sum(len(c) for c in chunks); s=t['start']; dur=t['end']-t['start']
    for c in chunks:
        e=s+dur*len(c)/L; caps.append((s,e,c)); s=e
# segments
segs=[]
for i,t in enumerate(tm):
    st=t['start'] if i else 0; en=tm[i+1]['start'] if i+1<len(tm) else total
    segs.append((st,en,smap[i],i))
imgs={}
def get(p):
    if p not in imgs: imgs[p]=Image.open(f'{wd}/{p}').convert('RGB').resize((W,H))
    return imgs[p]
NUM=re.compile(r'\d|minus|thousand|eighteen|seventy|eight|twenty')
def caption(fr,text):
    d=ImageDraw.Draw(fr)
    y=int(H*0.70) if H>W else int(H*0.84)
    words=text.upper().split(); 
    # measure
    sp=d.textlength(' ',font=font); widths=[d.textlength(w,font=font) for w in words]
    tw=sum(widths)+sp*(len(words)-1)
    if tw>W*0.9:
        mid=len(words)//2; lines=[words[:mid],words[mid:]]
    else: lines=[words]
    lh=font.size*1.15; y0=y-lh*len(lines)/2
    for li,lw in enumerate(lines):
        ww=[d.textlength(w,font=font) for w in lw]; t2=sum(ww)+sp*(len(lw)-1); x=(W-t2)/2
        for w,wi in zip(lw,ww):
            col=(255,140,40) if NUM.search(w.lower()) else (255,255,255)
            d.text((x,y0+li*lh),w,font=font,fill=col,stroke_width=9 if H>W else 7,stroke_fill=(0,0,0))
            x+=wi+sp
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',f'{wd}/voice.wav','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest',out],stdin=subprocess.PIPE)
nf=int(total*FPS)
for f in range(nf):
    t=f/FPS
    seg=next(s for s in segs if s[0]<=t<s[1]) if t<segs[-1][1] else segs[-1]
    st,en,img,i=seg; u=(t-st)/max(en-st,0.01)
    z=1.0+0.10*u if i%2==0 else 1.10-0.10*u
    base=get(img); cw,ch=W/z,H/z; cx=W/2+(15*math.sin(i)); cy=H/2
    fr=base.crop((int(cx-cw/2),int(cy-ch/2),int(cx+cw/2),int(cy+ch/2))).resize((W,H),Image.BILINEAR)
    # fade from previous on cut (0.15s)
    c=next((c for c in caps if c[0]<=t<c[1]),None)
    if c: caption(fr,c[2])
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait(); print('ok',out,round(total,1))

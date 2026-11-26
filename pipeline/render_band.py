# render_band.py workdir out.mp4  (needs timing.json, voice.wav, plan.json{hook,imgs})
import sys, json, subprocess, math, re, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
wd,out=sys.argv[1],sys.argv[2]; W,H,FPS=1080,1920,30
tm=json.load(open(f'{wd}/timing.json')); plan=json.load(open(f'{wd}/plan.json'))
total=tm[-1]['end']+0.5
FB='/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
fcap=ImageFont.truetype(FB,84); fhook=ImageFont.truetype(FB,78)
NUM=re.compile(r'\d|minus|thousand|eighteen|seventy|eight|twenty|forty|hundred')
caps=[]
for t in tm:
    w=t['text'].split(); ch=[' '.join(w[i:i+3]) for i in range(0,len(w),3)]
    if len(ch)>1 and len(ch[-1].split())==1: ch[-2]+=' '+ch[-1]; ch.pop()
    L=sum(map(len,ch)); s=t['start']; d=t['end']-t['start']
    for c in ch: e=s+d*len(c)/L; caps.append((s,e,c)); s=e
segs=[]
for i,t in enumerate(tm):
    st=t['start'] if i else 0; en=tm[i+1]['start'] if i+1<len(tm) else total
    segs.append((st,en,plan['imgs'][i],i))
BW=1000; BH=int(BW*9/16); BY=560
cache={}
def prep(p):
    if p in cache: return cache[p]
    im=Image.open(p).convert('RGB')
    bg=im.resize((int(H*im.width/im.height),H)); x=(bg.width-W)//2; bg=bg.crop((x,0,x+W,H)).filter(ImageFilter.GaussianBlur(40))
    bg=Image.blend(bg,Image.new('RGB',(W,H),(6,10,24)),0.55)
    d=ImageDraw.Draw(bg)
    # hook
    words=plan['hook'].split(); lines=[]; cur=''
    for w in words:
        t=(cur+' '+w).strip()
        if d.textlength(t,font=fhook)>W*0.86: lines.append(cur); cur=w
        else: cur=t
    lines.append(cur)
    y=330-len(lines)*45
    for ln in lines:
        tw=d.textlength(ln,font=fhook); d.text(((W-tw)/2,y),ln,font=fhook,fill=(255,255,255),stroke_width=8,stroke_fill=(0,0,0)); y+=92
    big=im.resize((int(BW*1.15),int(BH*1.15)),Image.LANCZOS)
    cache[p]=(bg,big); return cache[p]
mask=Image.new('L',(BW,BH),0); ImageDraw.Draw(mask).rounded_rectangle([0,0,BW,BH],radius=36,fill=255)
def caption(fr,text):
    d=ImageDraw.Draw(fr); words=text.upper().split(); sp=d.textlength(' ',font=fcap)
    tw=sum(d.textlength(w,font=fcap) for w in words)+sp*(len(words)-1)
    lines=[words] if tw<W*0.9 else [words[:len(words)//2],words[len(words)//2:]]
    y0=1380-len(lines)*50
    for li,lw in enumerate(lines):
        t2=sum(d.textlength(w,font=fcap) for w in lw)+sp*(len(lw)-1); x=(W-t2)/2
        for w in lw:
            d.text((x,y0+li*100),w,font=fcap,fill=(255,140,40) if NUM.search(w.lower()) else (255,255,255),stroke_width=9,stroke_fill=(0,0,0)); x+=d.textlength(w,font=fcap)+sp
target_kbps=int((2.85*8*1024)/total)-96
args=['-c:v','libx264','-preset','medium','-b:v',f'{target_kbps}k','-maxrate',f'{int(target_kbps*1.3)}k','-bufsize',f'{target_kbps*2}k','-pix_fmt','yuv420p']
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',f'{wd}/voice.wav',*args,'-c:a','aac','-b:a','96k','-shortest','-movflags','+faststart',out],stdin=subprocess.PIPE)
for f in range(int(total*FPS)):
    t=f/FPS; seg=next((s for s in segs if s[0]<=t<s[1]),segs[-1]); st,en,img,i=seg; u=min(1,(t-st)/max(en-st,.01))
    bg,big=prep(img); fr=bg.copy()
    z=1.0+0.13*u if i%2==0 else 1.13-0.13*u
    cw,chh=big.width/1.15/z*1.0,big.height/1.15/z
    cw=BW*1.15/ (1.0+0.15*((z-1)/0.13)); chh=cw*9/16
    cx,cy=big.width/2+(20*math.sin(i*1.7))*u, big.height/2
    crop=big.crop((int(cx-cw/2),int(cy-chh/2),int(cx+cw/2),int(cy+chh/2))).resize((BW,BH),Image.BILINEAR)
    fr.paste(crop,((W-BW)//2,BY),mask)
    ImageDraw.Draw(fr).rounded_rectangle([(W-BW)//2-3,BY-3,(W+BW)//2+3,BY+BH+3],radius=38,outline=(255,140,40),width=5)
    c=next((c for c in caps if c[0]<=t<c[1]),None)
    if c: caption(fr,c[2])
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait(); print(out, round(total,1), os.path.getsize(out))

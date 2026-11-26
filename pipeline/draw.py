from PIL import Image, ImageDraw, ImageFilter, ImageFont
import random, math
S=2  # supersample
NAVY=(10,16,34); OUT=(0,0,0); OR=(255,122,26); CY=(42,212,255); WH=(245,245,245); ICE=(200,235,255)
def canvas(w=1080,h=1920,seed=1,stars=True):
    im=Image.new('RGB',(w*S,h*S),NAVY); d=ImageDraw.Draw(im)
    # vertical gradient
    for y in range(0,h*S,8):
        f=y/(h*S); c=tuple(int(NAVY[i]*(1-f*0.6)+ (4,6,14)[i]*f*0.6) for i in range(3)); d.rectangle([0,y,w*S,y+8],fill=c)
    if stars:
        r=random.Random(seed)
        for _ in range(140):
            x,y=r.randrange(w*S),r.randrange(h*S); s=r.choice([2,2,3,4])
            d.ellipse([x,y,x+s*S,y+s*S],fill=(200,210,235))
    return im,d
def P(*v): return [int(a*S) for a in v]
def circ(d,cx,cy,r,fill,ow=8,outline=OUT):
    d.ellipse(P(cx-r,cy-r,cx+r,cy+r),fill=fill,outline=outline,width=ow*S)
def glow(im,cx,cy,r,color,blur=60,alpha=180):
    g=Image.new('RGBA',im.size,(0,0,0,0)); gd=ImageDraw.Draw(g)
    gd.ellipse(P(cx-r,cy-r,cx+r,cy+r),fill=color+(alpha,)); g=g.filter(ImageFilter.GaussianBlur(blur*S))
    im.paste(g,(0,0),g)
def void_sun(im,d,cx,cy,r):
    glow(im,cx,cy,r*1.35,OR,blur=50,alpha=230); glow(im,cx,cy,r*1.12,(255,200,80),blur=18,alpha=255)
    d=ImageDraw.Draw(im); circ(d,cx,cy,r,(0,0,0),ow=0); return d
def earth(im,d,cx,cy,r,frozen=False,atmo=False):
    if atmo: glow(im,cx,cy,r*1.18,CY,blur=30,alpha=160); d=ImageDraw.Draw(im)
    circ(d,cx,cy,r,(40,110,210) if not frozen else (150,190,230))
    rr=random.Random(3)
    for i in range(6):
        a=rr.uniform(0,6.28); dist=rr.uniform(0,r*0.6); bx=cx+math.cos(a)*dist; by=cy+math.sin(a)*dist; br=rr.uniform(r*0.15,r*0.3)
        d.ellipse(P(bx-br,by-br*0.7,bx+br,by+br*0.7),fill=(70,170,90) if not frozen else (235,245,255))
    if frozen:
        d.ellipse(P(cx-r*0.7,cy-r,cx+r*0.7,cy-r*0.55),fill=WH)
        d.ellipse(P(cx-r*0.7,cy+r*0.55,cx+r*0.7,cy+r),fill=WH)
    d.ellipse(P(cx-r,cy-r,cx+r,cy+r),outline=OUT,width=8*S); return d
def stick(d,x,y,sc=1.0,coat=OR,mood='neutral',look=(0,-1),frost=False):
    # head
    hr=60*sc; circ(d,x,y,hr,WH,ow=int(7*sc))
    ex=x+look[0]*18*sc; ey=y-10*sc+look[1]*12*sc
    d.ellipse(P(ex-9*sc,ey-12*sc,ex+9*sc,ey+12*sc),fill=OUT)
    if mood=='worried': d.arc(P(x-22*sc,y+22*sc,x+22*sc,y+50*sc),200,340,fill=OUT,width=int(6*sc*S))
    elif mood=='calm': d.arc(P(x-20*sc,y+10*sc,x+20*sc,y+34*sc),20,160,fill=OUT,width=int(6*sc*S))
    # body coat
    bw=78*sc; bt=y+hr-6*sc; bb=bt+170*sc
    d.rounded_rectangle(P(x-bw,bt,x+bw,bb),radius=int(40*sc*S),fill=coat,outline=OUT,width=int(7*sc*S))
    for k in range(1,3): d.line(P(x-bw+8*sc,bt+k*55*sc,x+bw-8*sc,bt+k*55*sc),fill=(200,90,15),width=int(5*sc*S))
    # hood around head
    d.arc(P(x-hr-20*sc,y-hr-20*sc,x+hr+20*sc,y+hr+20*sc),140,40,fill=coat,width=int(22*sc*S))
    # legs
    for dx in (-35,35):
        d.rounded_rectangle(P(x+dx*sc-18*sc,bb-10*sc,x+dx*sc+18*sc,bb+120*sc),radius=int(10*sc*S),fill=(25,25,30),outline=OUT,width=int(5*sc*S))
        d.rounded_rectangle(P(x+dx*sc-30*sc,bb+105*sc,x+dx*sc+24*sc,bb+135*sc),radius=int(10*sc*S),fill=OUT)
    if frost:
        for k in range(7):
            fx=x-hr-10*sc+k*22*sc; d.polygon(P(fx,y-hr-12*sc,fx+16*sc,y-hr-12*sc,fx+8*sc,y-hr+14*sc),fill=ICE)
def finish(im): return im.resize((im.width//S,im.height//S),Image.LANCZOS)

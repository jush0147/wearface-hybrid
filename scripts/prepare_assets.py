#!/usr/bin/env python3
"""Populate a WFF watch-face project with local Samsung Watch8 APK assets.

No APK, Samsung resource image, or extracted binary is distributed with the project.
Inputs must be authentic, locally obtained APK files; this is for local personal use.
"""
from __future__ import annotations
import argparse
import io
import math
from pathlib import Path
import zipfile
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

ROOT=Path(__file__).resolve().parents[1]
DRAW=ROOT / 'watchface/src/main/res/drawable'
DRAW.mkdir(parents=True,exist_ok=True)
S=450


def read_png(z: zipfile.ZipFile, path: str)->Image.Image:
    return Image.open(io.BytesIO(z.read(path))).convert('RGBA')


def save(im, name):
    im.save(DRAW/name, optimize=True)


def font(size):
    for f in ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','C:/Windows/Fonts/arial.ttf','/System/Library/Fonts/Helvetica.ttc'):
        if Path(f).exists():return ImageFont.truetype(f,size)
    return ImageFont.load_default()


def placeholder():
    # All-placeholder content is original, intentionally not a Samsung imitation.
    for face, numfont in [('hour','#F6F7FA'),('minute','#A6B3BC')]:
        for d in range(10):
            im=Image.new('RGBA',(115,147))
            dd=ImageDraw.Draw(im)
            dd.text((57,73),str(d),font=font(128),fill=numfont,anchor='mm',stroke_width=1,stroke_fill='#2D3339')
            save(im,f'{face}_{d}.png')
    dial=Image.new('RGBA',(S,S));d=ImageDraw.Draw(dial)
    for i in range(60):
        theta=2*math.pi*i/60-math.pi/2
        r1=190 if i%5 else 181
        r2=205
        col='#BFC7CA' if i%5==0 else '#77828A'
        d.line((225+math.cos(theta)*r1,225+math.sin(theta)*r1,225+math.cos(theta)*r2,225+math.sin(theta)*r2),fill=col,width=4 if i%5==0 else 2)
    save(dial,'heritage_dial.png')
    for typ,length in [('hour',90),('minute',138)]:
        im=Image.new('RGBA',(52,S));di=ImageDraw.Draw(im)
        di.rounded_rectangle((23,225-length,29,233),radius=2,fill='#F1F4F6')
        save(im,'hand_'+typ+'.png')
    cap=Image.new('RGBA',(28,28));ImageDraw.Draw(cap).ellipse((6,6,22,22),fill='#EDF2F5')
    save(cap,'hand_cap.png')
    print('Generated original generic placeholders (no Samsung assets).')


def from_apks(heritage:Path,digital:Path):
    with zipfile.ZipFile(heritage) as zh,zipfile.ZipFile(digital) as zd:
        a='assets/Heritage_classic/'
        dial=Image.new('RGBA',(480,480))
        # Samsung transparent dial indices are positioned on a 480x480 grid.
        for n in ['heritage_index_min.png','heritage_index_hr.png']:
            dial.alpha_composite(read_png(zh,a+n))
        # Ambient OLED protection: avoid bright full-background fills.
        dial=ImageEnhance.Brightness(dial).enhance(0.73)
        save(dial.resize((S,S),Image.Resampling.LANCZOS),'heritage_dial.png')
        for src,dest in [('heritage_hands_hr_metal_white.png','hand_hour.png'),('heritage_hands_min_metal_white.png','hand_minute.png')]:
            im=read_png(zh,a+'Hands/'+src)
            # The Samsung sprites use a pivot at y=240 in a 480-height image.
            save(im.resize((52,S),Image.Resampling.LANCZOS),dest)
        cap=read_png(zh,a+'Hands/classic_hands_aod_pivot.png')
        save(cap.resize((28,28),Image.Resampling.LANCZOS),'hand_cap.png')
        base='assets/Minimal digital/Minimal digital_num/'
        for n in range(10):
            h=read_png(zd,base+f'Hour/num_hr_base_dark_{n}.png')
            # The factory hour numerals use ~30% opacity over Samsung's own background.
            # On a pure-black WFF scene, normalize alpha so they're readable.
            ha=h.getchannel('A').point(lambda a: min(255,int(a*3.05)))
            h.putalpha(ha)
            m=read_png(zd,base+f'Min/num_min_color_{n}.png')
            # Use the original digit shape, but a cooler grey for the lower row.
            solid=Image.new('RGBA',m.size,(171,187,197,255))
            solid.putalpha(m.getchannel('A').point(lambda a:int(a*0.88)))
            save(h,f'hour_{n}.png')
            save(solid,f'minute_{n}.png')
    print('Extracted 25 local assets from two Samsung APKs.')


def render_previews():
    face=Image.new('RGBA',(S,S),'#000000')
    # Active preview, set mock time 10:28 (runtime uses dynamic clock via WFF).
    active=face.copy()
    for x,y,ch,kind in [(111,65,'1','hour'),(226,65,'0','hour'),(111,238,'2','minute'),(226,238,'8','minute')]:
        img=Image.open(DRAW/f'{kind}_{ch}.png').convert('RGBA')
        active.alpha_composite(img,(x,y))
    active.save(DRAW/'preview.png')
    ambient=face.copy()
    dial=Image.open(DRAW/'heritage_dial.png').convert('RGBA')
    ambient.alpha_composite(dial)
    # Rotate hand images around their true central pivot.
    for hand_name,deg in [('hand_hour',-305),('hand_minute',-168)]:
        im=Image.open(DRAW/f'{hand_name}.png').convert('RGBA')
        layer=Image.new('RGBA',(S,S))
        layer.alpha_composite(im,(199,0))
        layer=layer.rotate(deg,resample=Image.Resampling.BICUBIC,center=(225,225))
        ambient.alpha_composite(layer)
    cap=Image.open(DRAW/'hand_cap.png').convert('RGBA')
    ambient.alpha_composite(cap,(211,211))
    ambient.save(ROOT/'preview_aod.png')
    active.save(ROOT/'preview_active.png')
    pair=Image.new('RGBA',(1000,530),'#161A1E')
    dd=ImageDraw.Draw(pair)
    # Keep the preview screen-sized even though the watch case is omitted.
    pair.alpha_composite(ambient,(30,20));pair.alpha_composite(active,(520,20))
    dd.text((190,486),'AOD / Ambient',font=font(23),fill='#B6C3CC')
    dd.text((650,486),'Wake / Active',font=font(23),fill='#B6C3CC')
    pair.convert('RGB').save(ROOT/'preview_side_by_side.jpg',quality=92)
    print('Updated preview_aod.png / preview_active.png / preview_side_by_side.jpg')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--heritage',type=Path)
    p.add_argument('--digital',type=Path)
    args=p.parse_args()
    if bool(args.heritage) != bool(args.digital): p.error('Provide both --heritage and --digital, or neither for placeholders.')
    if args.heritage:
        from_apks(args.heritage,args.digital)
    else: placeholder()
    render_previews()

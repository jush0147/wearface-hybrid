#!/usr/bin/env python3
"""Offline project linter (NOT an official WFF schema validator)."""
from pathlib import Path
import re
import sys
from lxml import etree
from PIL import Image

root=Path(__file__).resolve().parents[1]
res=root/'watchface/src/main/res'
xml_path=res/'raw/watchface.xml'
xml=etree.parse(str(xml_path)).getroot()
assert xml.tag=='WatchFace'
assert xml.get('width')==xml.get('height')=='450'
assert xml.find('Scene') is not None
assert xml.find('Scene').get('backgroundColor')=='#ff000000'
fonts=xml.findall('./BitmapFonts/BitmapFont')
assert {f.get('name') for f in fonts}=={'samsung_hour','samsung_minute'}
for font in fonts:
    chars=font.findall('Character')
    assert len(chars)==10 and {c.get('name') for c in chars}==set('0123456789')
    for ch in chars:
        r=ch.get('resource')
        assert (res/'drawable'/f'{r}.png').exists(),r
        with Image.open(res/'drawable'/f'{r}.png') as im:
            assert im.size == (115,147),(r,im.size)
for r in ['heritage_dial','hand_hour','hand_minute','hand_cap','preview']:
    assert (res/'drawable'/f'{r}.png').exists(),r

groups={g.get('name'):g for g in xml.findall('./Scene/Group')}
assert groups['wake_digital'].get('alpha')=='255'
assert groups['ambient_analog'].get('alpha')=='0'
assert groups['wake_digital'].find('Variant').attrib=={'mode':'AMBIENT','target':'alpha','value':'0'}
assert groups['ambient_analog'].find('Variant').attrib=={'mode':'AMBIENT','target':'alpha','value':'255'}
assert {x.get('format') for x in groups['wake_digital'].findall('./DigitalClock/TimeText')}=={'hh_10','hh_1','mm_10','mm_1'}
assert len(groups['ambient_analog'].findall('./AnalogClock/HourHand'))==1
assert len(groups['ambient_analog'].findall('./AnalogClock/MinuteHand'))==1
manifest=etree.parse(str(root/'watchface/src/main/AndroidManifest.xml'))
ANDROID='{http://schemas.android.com/apk/res/android}'
app=manifest.find('.//application')
assert app.get(ANDROID+'hasCode')=='false'
prop=app.find("./property[@{%s}name='com.google.wear.watchface.format.version']" % ANDROID[1:-1])
assert prop is not None and prop.get(ANDROID+'value')=='2'
etree.parse(str(res/'xml/watch_face_info.xml'))
etree.parse(str(res/'values/strings.xml'))
print('PASS: basic XML parse, file dependencies, BitmapFont digits, AOD state, dynamic time, manifest.')
print('NOT CHECKED: official WFF XSD, Android APK compilation, Watch8 Classic hardware behavior.')

#!/usr/bin/env python3
"""Smoke guard to reject boot screens and stock Wear OS faces.

Use generated grayscale placeholders to distinguish our face from the green
stock watch face. This is deliberately not a device-rendering certification.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from PIL import Image, ImageStat

p = argparse.ArgumentParser()
p.add_argument("screenshot", type=Path)
p.add_argument("--mode", choices=["interactive", "ambient"], required=True)
p.add_argument("--save-report", type=Path)
args = p.parse_args()

im = Image.open(args.screenshot).convert("RGB")
w, h = im.size
side = min(w, h)
box = im.crop(((w-side)//2, (h-side)//2, (w+side)//2, (h+side)//2))
pixels = list(box.getdata())
neutral = sum(1 for r,g,b in pixels if min(r,g,b) > 105 and max(r,g,b) - min(r,g,b) < 42)
green = sum(1 for r,g,b in pixels if g > 85 and g > r*1.16 and g > b*1.05)
brightness = ImageStat.Stat(box.convert("L")).mean[0]
threshold = 450 if args.mode == "ambient" else 600
passed = neutral >= threshold and green < 1000 and brightness > 1.0
report = (f"{args.mode}: {w}x{h}; neutral-pixels={neutral}; "
          f"green-pixels={green}; brightness={brightness:.2f}; "
          f"placeholder-detected={passed}\n")
print(report.strip())
if args.save_report:
    args.save_report.write_text(report, encoding="utf-8")
if not passed:
    raise SystemExit(1)

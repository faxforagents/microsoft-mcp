#!/usr/bin/env python3
"""Resize the supplied brand mark and derive its white outline."""
import argparse
from pathlib import Path
from PIL import Image, ImageChops

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
source = Image.open(args.source).convert("RGB")
background = source.getpixel((0, 0))
difference = ImageChops.difference(source, Image.new("RGB", source.size, background)).convert("L")
mask = difference.point(lambda value: 255 if value > 25 else 0)
box = mask.getbbox()
if box is None:
    raise SystemExit("Source has no visible brand mark")
mark = source.crop(box)
mark.thumbnail((120, 120), Image.Resampling.LANCZOS)
color = Image.new("RGB", (192, 192), background)
color.paste(mark, ((192 - mark.width) // 2, (192 - mark.height) // 2))
color.save(root / "Color.png")
alpha = mask.crop(box)
alpha.thumbnail((28, 28), Image.Resampling.LANCZOS)
outline = Image.new("RGBA", (32, 32), (255, 255, 255, 0))
shape = Image.new("RGBA", alpha.size, (255, 255, 255, 255))
shape.putalpha(alpha)
outline.paste(shape, ((32 - shape.width) // 2, (32 - shape.height) // 2))
outline.save(root / "Outline.png")
print("Created Color.png (192x192) and Outline.png (32x32, white on transparent).")

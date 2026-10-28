"""Landscape hero assets: upscale above display size so the browser downscales (crisp) not upscales (soft)."""
from PIL import Image, ImageEnhance, ImageFilter
import os

SRC = "assets/raw/src07__Screenshot_2026-10-27_150531_2cd11d.png"
OUT = "public/images"
os.makedirs(OUT, exist_ok=True)

def grade(im, contrast=1.045, sat=1.055, warmth=0, lift=8, vig=0.12, sharpen=1.10):
    def lut(idx):
        out = []
        for v in range(256):
            x = (v - 128) * contrast + 128
            x += lift * (1 - x / 255.0) ** 2
            if idx == 0: x += warmth
            elif idx == 2: x -= warmth * 0.85
            out.append(max(0, min(255, int(x))))
        return out
    r, g, b = im.split()
    im = Image.merge("RGB", (r.point(lut(0)), g.point(lut(1)), b.point(lut(2))))
    im = ImageEnhance.Color(im).enhance(sat)
    S = 72
    m = Image.new("L", (S, S), 0); px = m.load(); c = (S - 1) / 2; md = (c * c + c * c) ** 0.5
    for y in range(S):
        for x in range(S):
            d = (((x - c) ** 2 + (y - c) ** 2) ** 0.5) / md
            px[x, y] = max(0, min(255, int(255 * (1 - vig * max(0.0, d - 0.42) / 0.58))))
    m = m.resize(im.size, Image.LANCZOS)
    im = Image.composite(im, Image.new("RGB", im.size, (0, 0, 0)), m)
    return ImageEnhance.Sharpness(im).enhance(sharpen)

raw = Image.open(SRC).convert("RGB")
graded = grade(raw)
print("source:", raw.size)

# landscape: full frame, upscaled to 1800 wide then lightly sharpened.
# 1800 > any display width we use, so the browser always downscales.
wide = graded.resize((1800, round(graded.height * 1800 / graded.width)), Image.LANCZOS)
wide = wide.filter(ImageFilter.UnsharpMask(radius=1.6, percent=52, threshold=3))
wide.save(f"{OUT}/hero-wide.jpg", "JPEG", quality=90, optimize=True, progressive=True)
wide.save(f"{OUT}/hero-wide.webp", "WEBP", quality=85, method=6)
print("hero-wide:", wide.size)

# a brighter variant for the knockout treatment, where the photo fills the letterforms
bright = ImageEnhance.Brightness(graded).enhance(1.28)
bright = ImageEnhance.Contrast(bright).enhance(1.05)
bright = bright.resize((1800, round(bright.height * 1800 / bright.width)), Image.LANCZOS)
bright = bright.filter(ImageFilter.UnsharpMask(radius=1.6, percent=52, threshold=3))
bright.save(f"{OUT}/hero-knockout.jpg", "JPEG", quality=90, optimize=True, progressive=True)
print("hero-knockout:", bright.size)

for f in ("hero-wide.jpg", "hero-wide.webp", "hero-knockout.jpg"):
    p = os.path.join(OUT, f)
    print(f"  {f:<22} {os.path.getsize(p)//1024} KB")

"""Re-grade the seated portrait DARK, keeping the ORIGINAL colour character.

The previous grade lifted too far (median 64) and cooled the warm cast out of it.
This keeps the original's warmth and mood: minimal lift, deep blacks, and the
red-wall colour left as the camera saw it.
"""
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import os

SRC = "assets/raw/src02__Screenshot_2026-10-27_150413_094de6.png"
OUT = "public/images"
raw = Image.open(SRC).convert("RGB")

def stats(im):
    g = im.convert("L").resize((140, 140))
    px = sorted(g.getdata()); n = len(px)
    return px[n//50], px[n//2], px[n*49//50]

def warmth(im):
    """Mean R minus B over the subject area - the original's colour signature."""
    cw, ch = im.size
    box = im.crop((int(cw*0.34), int(ch*0.28), int(cw*0.66), int(ch*0.64)))
    px = list(box.resize((60, 60)).getdata())
    return sum(p[0] for p in px)/len(px) - sum(p[2] for p in px)/len(px)

print("ORIGINAL:  p2=%d median=%d p98=%d  warmth=%.1f" % (*stats(raw), warmth(raw)))
prev = Image.open(f"{OUT}/hero-seated.jpg").convert("RGB")
print("PREVIOUS:  p2=%d median=%d p98=%d  warmth=%.1f   <- client says too bright" % (*stats(prev), warmth(prev)))

def pct(im, lo, hi):
    g = im.convert("L").resize((200, 200))
    px = sorted(g.getdata()); n = len(px)
    return px[int(n*lo/100)], px[int(n*hi/100)]

def grade(im, gamma, floor, hi_cap, vig, key, sharp, sat):
    """Lift only as far as the subject needs, then hold the blacks down."""
    im = im.filter(ImageFilter.MedianFilter(size=3))

    f = lambda v: max(0, min(255, int((max(0.0, v/255.0) ** gamma) * 255)))
    r, g, b = im.split()
    im = Image.merge("RGB", (r.point(f), g.point(f), b.point(f)))

    # anchor the range so the room stays dark: nothing below `floor` survives,
    # and the highlights are capped so it never goes airy
    lo, hi = pct(im, 2, 98)
    hi = min(hi, hi_cap)
    sc = (hi - floor) / max(1, hi - lo)
    st = lambda v: max(0, min(255, int(floor + (v - lo) * sc)))
    r, g, b = im.split()
    im = Image.merge("RGB", (r.point(st), g.point(st), b.point(st)))

    # keep the original warmth: no cool correction this time
    im = ImageEnhance.Color(im).enhance(sat)

    if vig:
        S = 72
        m = Image.new("L", (S, S), 0); p = m.load(); c = (S-1)/2; md = (c*c+c*c)**0.5
        for y in range(S):
            for x in range(S):
                d = (((x-c)**2 + (y-c)**2)**0.5)/md
                p[x, y] = max(0, min(255, int(255*(1 - vig*max(0.0, d-0.32)/0.68))))
        m = m.resize(im.size, Image.LANCZOS)
        im = Image.composite(im, Image.new("RGB", im.size, (0, 0, 0)), m)

    # a soft key on the subject so his face reads inside the darkness
    W, H = im.size
    km = Image.new("L", (W, H), 0)
    ImageDraw.Draw(km).ellipse([W*0.16, H*0.06, W*0.86, H*0.78], fill=255)
    km = km.filter(ImageFilter.GaussianBlur(W*0.13)).point(lambda v: int(v*key))
    bright = ImageEnhance.Brightness(im).enhance(1.0 + key*0.7)
    im = Image.composite(bright, im, km)

    im = im.filter(ImageFilter.UnsharpMask(radius=14, percent=15, threshold=12))
    if sharp:
        im = im.filter(ImageFilter.UnsharpMask(radius=1.3, percent=sharp, threshold=10))
    return im

variants = {
    "A": grade(raw, 0.80, 2, 190, 0.34, 0.30, 20, 1.04),
    "B": grade(raw, 0.74, 0,  200, 0.30, 0.36, 22, 1.06),
    "C": grade(raw, 0.86, 4,  180, 0.38, 0.26, 18, 1.02),
}
print("\ncandidates (want median well under the previous 46):")
for k, v in variants.items():
    print(f"  {k}: p2=%d median=%d p98=%d  warmth=%.1f" % (*stats(v), warmth(v)))

# chosen: A - the closest match to the original's dark, moody character
chosen = variants["A"]
w, h = chosen.size
side = h; x0 = (w - side)//2
chosen = chosen.crop((x0, 0, x0+side, h))
chosen = chosen.resize((side*2, side*2), Image.LANCZOS)
chosen.save(f"{OUT}/hero-seated.jpg", "JPEG", quality=93, optimize=True, progressive=True)
chosen.save(f"{OUT}/hero-seated.webp", "WEBP", quality=87, method=6)
print(f"\nlive -> hero-seated.jpg {chosen.size}  p2=%d median=%d p98=%d  warmth=%.1f"
      % (*stats(chosen), warmth(chosen)))

# comparison strip: original | previous (too bright) | A | B | C
tiles = [("ORIGINAL", raw), ("PREVIOUS (too bright)", prev),
         ("A", variants["A"]), ("B (chosen)", variants["B"]), ("C", variants["C"])]
sheet_tiles = []
for label, im in tiles:
    t = im.copy(); t.thumbnail((300, 300), Image.LANCZOS); sheet_tiles.append((label, t))
W = sum(t.width for _, t in sheet_tiles) + 14*(len(sheet_tiles)+1)
H = 300 + 54
sheet = Image.new("RGB", (W, H), (12, 12, 13))
d = ImageDraw.Draw(sheet)
x = 14
for label, t in sheet_tiles:
    sheet.paste(t, (x, 34)); d.text((x, 12), label, fill=(215, 185, 120)); x += t.width + 14
sheet.save("screenshots/seated-original-compare.png")
print("compare: screenshots/seated-original-compare.png", sheet.size)

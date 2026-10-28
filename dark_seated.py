"""Re-grade the seated portrait DARKER and less sharp.

Previous version: median luminance 64, p98 246 - too bright and too crunchy.
The original was genuinely moody; the job is to make the subject readable
without flattening the room into daylight.
"""
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import os

SRC = "assets/raw/src02__Screenshot_2026-10-27_150413_094de6.png"
OUT = "public/images"
raw = Image.open(SRC).convert("RGB")
# capture the current live asset BEFORE it is overwritten, so the comparison sheet
# still shows the old "too bright" version
prev_live = Image.open(f"{OUT}/hero-seated.jpg").convert("RGB")

def stats(im):
    g = im.convert("L").resize((140, 140))
    px = sorted(g.getdata()); n = len(px)
    return px[n//50], px[n//2], px[n*49//50]

def pct(im, lo, hi):
    g = im.convert("L").resize((180, 180))
    px = sorted(g.getdata()); n = len(px)
    return px[int(n*lo/100)], px[int(n*hi/100)]

def vignette(im, amount):
    S = 72
    m = Image.new("L", (S, S), 0); p = m.load(); c = (S-1)/2; md = (c*c+c*c)**0.5
    for y in range(S):
        for x in range(S):
            d = (((x-c)**2 + (y-c)**2)**0.5)/md
            p[x, y] = max(0, min(255, int(255*(1 - amount*max(0.0, d-0.34)/0.66))))
    m = m.resize(im.size, Image.LANCZOS)
    return Image.composite(im, Image.new("RGB", im.size, (0, 0, 0)), m)

def key_light(im, amount=0.34, cx=0.50, cy=0.40, rx=0.34, ry=0.38):
    """A soft elliptical lift centred on the subject, so the face reads without
    raising the room. The background stays as dark as the grade left it."""
    W, H = im.size
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse([cx*W - rx*W, cy*H - ry*H, cx*W + rx*W, cy*H + ry*H], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(W * 0.11))
    m = m.point(lambda v: int(v * amount))
    bright = ImageEnhance.Brightness(im).enhance(1.0 + amount * 0.85)
    bright = ImageEnhance.Contrast(bright).enhance(1.03)
    return Image.composite(bright, im, m)

def moody(im, gamma, lift, floor, vig, sharp, sat=1.06, cool=True, key=0.34):
    """Lift just enough to see him, then push the shadows back down so the room stays dark."""
    im = im.filter(ImageFilter.MedianFilter(size=3))

    # gentle lift only
    f = lambda v: max(0, min(255, int((max(0.0, v/255.0) ** gamma) * 255)))
    r, g, b = im.split()
    im = Image.merge("RGB", (r.point(f), g.point(f), b.point(f)))

    # black point: anchor the darkest real tone to `floor` so it is NOT milky
    lo, hi = pct(im, 2, 98)
    lo = max(0, lo - 2)
    sc = (255.0 - floor) / max(1, hi - lo)
    st = lambda v: max(0, min(255, int(floor + (v - lo) * sc)))
    r, g, b = im.split()
    im = Image.merge("RGB", (r.point(st), g.point(st), b.point(st)))

    if cool:
        r, g, b = im.split()
        r = r.point(lambda v: max(0, int(v*0.915)))
        g = g.point(lambda v: max(0, min(255, int(v*0.99))))
        b = b.point(lambda v: min(255, int(v*1.10)))
        im = Image.merge("RGB", (r, g, b))

    im = ImageEnhance.Color(im).enhance(sat)
    if vig:
        im = vignette(im, vig)
    if key:
        im = key_light(im, amount=key)
    # clarity without crunch: large radius only, then a very light pass
    im = im.filter(ImageFilter.UnsharpMask(radius=14, percent=16, threshold=12))
    if sharp:
        im = im.filter(ImageFilter.UnsharpMask(radius=1.3, percent=sharp, threshold=9))
    return im

print("original:      p2=%d median=%d p98=%d" % stats(raw))
print("previous:      p2=2 median=64 p98=246   <- too bright\n")

variants = {
    "a": moody(raw, 0.74, 0, 10, 0.30, 22),
    "b": moody(raw, 0.68, 0, 8,  0.38, 20),
    "c": moody(raw, 0.80, 0, 12, 0.24, 24),
}
print("candidates:")
for k, v in variants.items():
    print(f"  {k}: p2=%d median=%d p98=%d" % stats(v))

# write all three so they can be compared, plus keep the chosen one as the live asset
for k, v in variants.items():
    im = v.resize((v.width*2, v.height*2), Image.LANCZOS)
    im.save(f"screenshots/seated-dark-{k}.jpg", "JPEG", quality=93)

# Option C is the chosen grade: moody background, subject still clearly lit.
# Crop the excess from the sides, then export at 2x.
chosen = variants["c"]
w, h = chosen.size
side = h
x0 = (w - side) // 2
chosen = chosen.crop((x0, 0, x0 + side, h))
chosen = chosen.resize((side*2, side*2), Image.LANCZOS)
chosen.save(f"{OUT}/hero-seated.jpg", "JPEG", quality=93, optimize=True, progressive=True)
chosen.save(f"{OUT}/hero-seated.webp", "WEBP", quality=87, method=6)
print(f"\nlive asset -> hero-seated.jpg {chosen.size}  p2=%d median=%d p98=%d" % stats(chosen))

# the comparison sheet: original | previous (too bright) | a | b | c
tiles = [("ORIGINAL", raw), ("PREVIOUS (too bright)", prev_live)]
for k in ("a", "b", "c"):
    tiles.append((f"OPTION {k.upper()}", variants[k]))
th = 300
sheet_tiles = []
for label, im in tiles:
    t = im.copy(); t.thumbnail((th, th), Image.LANCZOS)
    sheet_tiles.append((label, t))
W = sum(t.width for _, t in sheet_tiles) + 16*(len(sheet_tiles)+1)
H = th + 54
sheet = Image.new("RGB", (W, H), (12, 12, 13))
d = ImageDraw.Draw(sheet)
x = 16
for label, t in sheet_tiles:
    sheet.paste(t, (x, 34))
    d.text((x, 12), label, fill=(215, 185, 120))
    x += t.width + 16
sheet.save("screenshots/seated-dark-compare.png")
print("\ncompare: screenshots/seated-dark-compare.png", sheet.size)

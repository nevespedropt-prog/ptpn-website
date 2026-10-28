"""Second attempt at the seated portrait: lift, then RESTORE the black point.

The first attempt raised everything uniformly, which turned the deep shadows to
flat grey and washed out the red wall. This lifts less and then re-anchors the
tonal range so the image keeps depth and colour.
"""
from PIL import Image, ImageEnhance, ImageFilter
import os

SRC = "assets/raw/src02__Screenshot_2026-10-27_150413_094de6.png"
OUT = "public/images"

raw = Image.open(SRC).convert("RGB")

def stats(im, label):
    g = im.convert("L").resize((140, 140))
    px = sorted(g.getdata()); n = len(px)
    print(f"  {label:<24} p2={px[n//50]:<4} p25={px[n//4]:<4} median={px[n//2]:<4} "
          f"p75={px[n*3//4]:<4} p98={px[n*49//50]:<4}")
    return px

print("source:"); stats(raw, "src02 raw")

def percentiles(im, lo=3, hi=97):
    g = im.convert("L").resize((160, 160))
    px = sorted(g.getdata()); n = len(px)
    return px[int(n*lo/100)], px[int(n*hi/100)]

def recover(im, gamma, sat, clarity):
    im = im.filter(ImageFilter.MedianFilter(size=3))          # tame noise before lifting

    def lut(vals):
        return [max(0, min(255, int((max(0.0, v / 255.0) ** gamma) * 255))) for v in range(256)]

    r, g, b = im.split()
    im = Image.merge("RGB", (r.point(lut(None)), g.point(lut(None)), b.point(lut(None))))

    # re-anchor the range: the darkest real tone goes near-black, the brightest stays open.
    # this is what stops the lift looking milky.
    lo, hi = percentiles(im)
    lo = max(0, lo - 6); hi = min(255, hi + 8)
    scale = 255.0 / max(1, hi - lo)
    def stretch(v):
        return max(0, min(255, int((v - lo) * scale)))
    r, g, b = im.split()
    im = Image.merge("RGB", (r.point(stretch), g.point(stretch), b.point(stretch)))

    im = ImageEnhance.Color(im).enhance(sat)
    # clarity: large-radius unsharp adds local contrast without haloing
    im = im.filter(ImageFilter.UnsharpMask(radius=9, percent=int(clarity*100), threshold=6))
    im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=42, threshold=3))
    return im

print("\ncandidates:")
variants = {}
for gamma, sat, cl in ((0.62, 1.16, 0.22), (0.56, 1.20, 0.28), (0.50, 1.24, 0.34)):
    v = recover(raw, gamma, sat, cl)
    stats(v, f"gamma {gamma} sat {sat}")
    variants[gamma] = v

# pick the middle one and write it out
out = variants[0.56]
wide = out.resize((out.width * 2, out.height * 2), Image.LANCZOS)
wide.save(f"{OUT}/coach-seated-lifted.jpg", "JPEG", quality=92, optimize=True, progressive=True)
wide.save(f"{OUT}/coach-seated-lifted.webp", "WEBP", quality=86, method=6)
print(f"\nwritten: coach-seated-lifted {wide.size}  {os.path.getsize(f'{OUT}/coach-seated-lifted.jpg')//1024} KB")

# three-up comparison: original, first attempt, this attempt
orig = raw.copy(); orig.thumbnail((520, 520), Image.LANCZOS)
prev = Image.open("screenshots/seated-lift-compare.png")
old = prev.crop((prev.width//2 + 10, 10, prev.width, prev.height)).copy()
old.thumbnail((520, 520), Image.LANCZOS)
new = out.copy(); new.thumbnail((520, 520), Image.LANCZOS)
tiles = [("original", orig), ("attempt 1 (washed out)", old), ("attempt 2 (black point restored)", new)]
W = sum(t.width for _, t in tiles) + 20*(len(tiles)+1)
H = max(t.height for _, t in tiles) + 60
sheet = Image.new("RGB", (W, H), (12, 12, 13))
from PIL import ImageDraw
d = ImageDraw.Draw(sheet)
x = 20
for label, t in tiles:
    sheet.paste(t, (x, 40))
    d.text((x, 16), label, fill=(215, 185, 120))
    x += t.width + 20
sheet.save("screenshots/seated-lift-compare2.png")
print("compare: screenshots/seated-lift-compare2.png", sheet.size)

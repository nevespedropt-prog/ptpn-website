"""Recover the underexposed seated portrait.

src02 is ~2 stops under (median 18). A plain brightness bump would blow the
highlights and amplify noise, so this lifts via a curve that raises shadows and
midtones while protecting the top end, denoises first, then grades.
"""
from PIL import Image, ImageEnhance, ImageFilter
import os

SRC = "assets/raw/src02__Screenshot_2026-10-27_150413_094de6.png"
OUT = "public/images"

raw = Image.open(SRC).convert("RGB")
print("source:", raw.size)

def stats(im, label):
    g = im.convert("L").resize((140, 140))
    px = sorted(g.getdata()); n = len(px)
    print(f"  {label:<22} p2={px[n//50]:<4} p25={px[n//4]:<4} median={px[n//2]:<4} "
          f"p75={px[n*3//4]:<4} p98={px[n*49//50]:<4}")

print("before:")
stats(raw, "src02 raw")

def lift(im, gamma=0.46, black=6, protect=0.82, contrast=1.06, sat=1.06, denoise=1):
    """Raise shadows and midtones, roll off the top end, keep it from going milky."""
    if denoise:
        im = im.filter(ImageFilter.MedianFilter(size=3))
    def lut(idx):
        out = []
        for v in range(256):
            x = max(0.0, (v - black) / (255 - black))
            x = x ** gamma                       # strong shadow/midtone lift
            if x > protect:                      # gentle shoulder so highlights hold
                x = protect + (x - protect) * (1 - (x - protect) * 0.85)
            x = (x - 0.5) * contrast + 0.5
            out.append(max(0, min(255, int(x * 255))))
        return out
    r, g, b = im.split()
    im = Image.merge("RGB", (r.point(lut(0)), g.point(lut(1)), b.point(lut(2))))
    return ImageEnhance.Color(im).enhance(sat)

def grade(im, contrast=1.05, sat=0.95, warmth=3, vig=0.18, sharp=1.10):
    im = ImageEnhance.Contrast(im).enhance(contrast)
    im = ImageEnhance.Color(im).enhance(sat)
    if warmth:
        r, g, b = im.split()
        r = r.point(lambda v: min(255, v + warmth))
        b = b.point(lambda v: max(0, v - warmth))
        im = Image.merge("RGB", (r, g, b))
    S = 64
    m = Image.new("L", (S, S), 0); px = m.load(); c = (S-1)/2; md = (c*c + c*c) ** 0.5
    for y in range(S):
        for x in range(S):
            d = (((x-c)**2 + (y-c)**2) ** 0.5) / md
            px[x, y] = max(0, min(255, int(255 * (1 - vig * max(0.0, d - 0.45) / 0.55))))
    m = m.resize(im.size, Image.LANCZOS)
    im = Image.composite(im, Image.new("RGB", im.size, (0, 0, 0)), m)
    return ImageEnhance.Sharpness(im).enhance(sharp)

# try a few lift strengths and report, so the choice is measured not guessed
print("\nlift candidates:")
best = None
for gamma in (0.52, 0.46, 0.40):
    t = lift(raw, gamma=gamma)
    stats(t, f"gamma {gamma}")
    if gamma == 0.46:
        best = t

out = grade(best)
print("\nafter grade:")
stats(out, "final")

wide = out.resize((out.width * 2, out.height * 2), Image.LANCZOS)
wide = wide.filter(ImageFilter.UnsharpMask(radius=1.3, percent=44, threshold=3))
wide.save(f"{OUT}/coach-seated-lifted.jpg", "JPEG", quality=92, optimize=True, progressive=True)
wide.save(f"{OUT}/coach-seated-lifted.webp", "WEBP", quality=86, method=6)
print(f"\ncoach-seated-lifted: {wide.size}  {os.path.getsize(f'{OUT}/coach-seated-lifted.jpg')//1024} KB")

# side by side for review
a = raw.copy(); a.thumbnail((700, 700), Image.LANCZOS)
b = out.copy(); b.thumbnail((700, 700), Image.LANCZOS)
sheet = Image.new("RGB", (a.width + b.width + 30, max(a.height, b.height) + 20), (12, 12, 13))
sheet.paste(a, (10, 10)); sheet.paste(b, (a.width + 20, 10))
sheet.save("screenshots/seated-lift-compare.png")
print("compare: screenshots/seated-lift-compare.png", sheet.size)

"""Logo variants for the fresh directions.

The existing lockup is gold-on-transparent, which only works on dark. Two new
variants:
  ptpn-lockup-duo.png  - gold monogram + near-black wordmark (for cream/ivory)
  ptpn-lockup-ink.png  - entirely near-black (for gold or light fields)
"""
from PIL import Image
import os

SRC = "brand/ptpn-logo-approved.png"
OUT = "public/brand"

src = Image.open(SRC).convert("RGB")
lum = src.convert("L")

# key out the dark background
alpha = lum.point(lambda v: 0 if v <= 26 else (255 if v >= 68 else int((v - 26) * 255 / 42)))
base = src.copy(); base.putalpha(alpha)

# trim to the real content
bb = lum.point(lambda v: 255 if v > 34 else 0).getbbox()
base = base.crop(bb)
print("lockup content:", base.size)

def recolor(im, level):
    """Replace RGB with a flat grey at `level`, keeping alpha."""
    grey = im.convert("L").point(lambda v: level)
    flat = Image.merge("RGB", (grey, grey, grey))
    flat.putalpha(im.split()[-1])
    return flat

# --- duo: monogram stays gold, wordmark goes near-black ---
# the monogram occupied x 325-785 in the ORIGINAL; after trimming to bb (335,225)
# that becomes roughly x 0-450 of the trimmed image.
SPLIT = 452
duo = base.copy()
wm = duo.crop((SPLIT, 0, duo.width, duo.height))
ink_wm = recolor(wm, 20)                       # near-black wordmark
duo.paste(ink_wm, (SPLIT, 0), ink_wm)
duo.save(f"{OUT}/ptpn-lockup-duo.png", "PNG", optimize=True)
print("ptpn-lockup-duo.png:", duo.size)

# --- ink: everything near-black ---
ink = recolor(base, 20)
ink.save(f"{OUT}/ptpn-lockup-ink.png", "PNG", optimize=True)
print("ptpn-lockup-ink.png:", ink.size)

# --- check sheets on the actual backgrounds they will sit on ---
for name, bg in (("duo", (241, 238, 230)), ("ink", (201, 162, 39))):
    im = Image.open(f"{OUT}/ptpn-lockup-{name}.png")
    im.thumbnail((520, 520), Image.LANCZOS)
    t = Image.new("RGB", (im.width + 80, im.height + 60), bg)
    t.paste(im, (40, 30), im)
    t.save(f"screenshots/logo-{name}-check.png")
    print(f"  check sheet on {bg}: screenshots/logo-{name}-check.png")

# contrast check
for name, bg in (("duo", (241, 238, 230)), ("ink", (201, 162, 39))):
    im = Image.open(f"{OUT}/ptpn-lockup-{name}.png")
    a = im.split()[-1]
    px = list(im.convert("L").getdata()); al = list(a.getdata())
    solid = [v for v, k in zip(px, al) if k > 200]
    if solid:
        mean = sum(solid) / len(solid)
        bgl = 0.299*bg[0] + 0.587*bg[1] + 0.114*bg[2]
        ratio = (max(mean, bgl) + 5) / (min(mean, bgl) + 5)
        print(f"  {name}: mark mean lum {mean:.0f} vs bg {bgl:.0f} -> contrast ratio {ratio:.1f}:1 "
              f"{'OK' if ratio >= 3 else 'TOO LOW'}")

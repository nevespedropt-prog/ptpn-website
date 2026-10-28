"""Wordmark-only logo variants.

At nav size the particle-ring monogram reads as noise/clip-art, which drags the
perceived quality of an otherwise editorial layout. A wordmark-only lockup is
cleaner on light and on gold.
"""
from PIL import Image
import os

OUT = "public/brand"
base = Image.open(f"{OUT}/ptpn-lockup-ink.png").convert("RGBA")
print("lockup-ink:", base.size)

# the monogram occupied x 0-452 of the trimmed lockup; the wordmark is to the right
WM = 452
wm = base.crop((WM, 0, base.width, base.height))
bb = wm.split()[-1].getbbox()
wm = wm.crop(bb)
wm.save(f"{OUT}/ptpn-wordmark-ink.png", "PNG", optimize=True)
print("ptpn-wordmark-ink.png:", wm.size)

# a light version for dark backgrounds
src = Image.open("brand/ptpn-logo-approved.png").convert("RGB")
lum = src.convert("L")
alpha = lum.point(lambda v: 0 if v <= 26 else (255 if v >= 68 else int((v - 26) * 255 / 42)))
l = src.copy(); l.putalpha(alpha)
l = l.crop(lum.point(lambda v: 255 if v > 34 else 0).getbbox())
wm2 = l.crop((WM, 0, l.width, l.height))
wm2 = wm2.crop(wm2.split()[-1].getbbox())
wm2.save(f"{OUT}/ptpn-wordmark-gold.png", "PNG", optimize=True)
print("ptpn-wordmark-gold.png:", wm2.size)

# check sheets at nav size, on the backgrounds they will actually sit on
tests = [
    ("ptpn-wordmark-ink", (241, 238, 230), "ivory"),
    ("ptpn-wordmark-ink", (201, 162, 39), "gold"),
    ("ptpn-wordmark-gold", (11, 11, 12), "dark"),
]
tiles = []
for name, bg, label in tests:
    im = Image.open(f"{OUT}/{name}.png").convert("RGBA")
    im.thumbnail((160, 44), Image.LANCZOS)
    t = Image.new("RGB", (300, 150), bg)
    # at nav size
    t.paste(im, (26, 30), im)
    # and at 3x so the shape is legible in review
    big = Image.open(f"{OUT}/{name}.png").convert("RGBA")
    big.thumbnail((240, 66), Image.LANCZOS)
    t.paste(big, (26, 84), big)
    tiles.append((t, label))

W = sum(t.width for t, _ in tiles) + 20 * (len(tiles) + 1)
sheet = Image.new("RGB", (W, 170), (60, 60, 60))
x = 20
for t, label in tiles:
    sheet.paste(t, (x, 10)); x += t.width + 20
sheet.save("screenshots/wordmark-check.png")
print("sheet: screenshots/wordmark-check.png", sheet.size)
print("tiles (left to right):", ", ".join(l for _, l in tiles))

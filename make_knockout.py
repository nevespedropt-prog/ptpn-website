"""Build a knockout fill asset: a gold ramp mapped from luminance, tuned so text
filled with it stays legible on a near-black background.

A raw photo used as a text fill fails whenever a dark region lands under a glyph.
Mapping luminance onto a controlled gold ramp guarantees a minimum brightness.
"""
from PIL import Image, ImageEnhance, ImageFilter
import os

SRC = "assets/raw/src07__Screenshot_2026-10-27_150531_2cd11d.png"
OUT = "public/images"

raw = Image.open(SRC).convert("RGB")
# frame on the subject, matching the hero crop
crop = raw.crop((180, 0, 764, 507))
crop = crop.resize((crop.width * 2, crop.height * 2), Image.LANCZOS)

g = crop.convert("L")
g = ImageEnhance.Contrast(g).enhance(0.72)      # flatten: no deep blacks
g = ImageEnhance.Brightness(g).enhance(1.45)    # lift: floor never goes dark
g = g.filter(ImageFilter.GaussianBlur(0.6))     # smooth so glyphs read as tone

# gold ramp: shadows -> deep gold, midtones -> gold, highlights -> pale champagne.
# the floor is deliberately high so no glyph is ever dark.
STOPS = [
    (0,   (120, 86, 34)),
    (64,  (168, 122, 52)),
    (128, (206, 166, 92)),
    (192, (232, 205, 148)),
    (255, (250, 240, 214)),
]
def ramp(v):
    for i in range(len(STOPS) - 1):
        a, ca = STOPS[i]
        b, cb = STOPS[i + 1]
        if v <= b:
            t = (v - a) / (b - a)
            return tuple(round(ca[k] + (cb[k] - ca[k]) * t) for k in range(3))
    return STOPS[-1][1]

lut = [ramp(v) for v in range(256)]
out = Image.new("RGB", g.size)
out.putdata([lut[v] for v in g.getdata()])

out.save(f"{OUT}/hero-knockout.jpg", "JPEG", quality=92, optimize=True, progressive=True)
print("hero-knockout:", out.size)

# report the luminance range, which is what determines legibility
lum = out.convert("L")
px = list(lum.getdata())
px.sort()
n = len(px)
print(f"  fill luminance: min={px[0]} p5={px[n//20]} median={px[n//2]} p95={px[n*19//20]} max={px[-1]}")
print("  (min should be well above 80 so no glyph area is unreadable)")

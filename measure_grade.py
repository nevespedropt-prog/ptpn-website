"""Measure the real colour shift the grade introduces, rather than trusting a vision opinion."""
from PIL import Image

RAW = "assets/raw"
ED = "assets/edited"

orig = Image.open(f"{RAW}/src03__Screenshot_2026-10-27_150429_3e2137.png").convert("RGB")
grad = Image.open(f"{ED}/coach-03-boxing-gloves.jpg").convert("RGB")
print("orig", orig.size, "grad", grad.size)
if orig.size != grad.size:
    grad = grad.resize(orig.size, Image.LANCZOS)

def patch_mean(im, x0, y0, x1, y1):
    c = im.crop((x0, y0, x1, y1))
    px = list(c.getdata())
    n = len(px)
    return tuple(round(sum(p[i] for p in px) / n, 1) for i in range(3))

# scan a grid to find the most skin-like patch (R>G>B, bright-ish)
best = None
w, h = orig.size
for y in range(40, h - 60, 20):
    for x in range(40, w - 60, 20):
        m = patch_mean(orig, x, y, x + 40, y + 40)
        r, g, b = m
        if r > 95 and r > g > b and (r - b) > 22 and (r - b) < 95:
            score = r
            if best is None or score > best[0]:
                best = (score, x, y, m)

print("\nmost skin-like patch found in the ORIGINAL:", best)
_, x, y, mo = best
mg = patch_mean(grad, x, y, x + 40, y + 40)
print(f"  ORIGINAL skin patch at ({x},{y}) mean RGB = {mo}")
print(f"  GRADED   same patch          mean RGB = {mg}")
print(f"  delta R {mg[0]-mo[0]:+.1f}  G {mg[1]-mo[1]:+.1f}  B {mg[2]-mo[2]:+.1f}")
r_o, g_o, b_o = mo; r_g, g_g, b_g = mg
print(f"  warm/cool ratio (R-B): original {r_o-b_o:.1f} -> graded {r_g-b_g:.1f}  "
      f"(change {(r_g-b_g)-(r_o-b_o):+.1f})")

# whole-image comparison
def whole(im):
    px = list(im.resize((80, 80)).getdata())
    n = len(px)
    return tuple(round(sum(p[i] for p in px) / n, 1) for i in range(3))
wo, wg = whole(orig), whole(grad)
print(f"\nwhole-image mean: original {wo}  graded {wg}  delta {tuple(round(wg[i]-wo[i],1) for i in range(3))}")
lum_o = 0.299 * wo[0] + 0.587 * wo[1] + 0.114 * wo[2]
lum_g = 0.299 * wg[0] + 0.587 * wg[1] + 0.114 * wg[2]
print(f"whole-image luminance: {lum_o:.1f} -> {lum_g:.1f} ({lum_g-lum_o:+.1f})")

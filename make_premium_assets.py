"""Premium hero assets: cinematic grade (deep blacks, restrained colour, natural skin)
plus a tight art-directed crop so the frame is about the man, not the gym clutter.
"""
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import os

SRC = "assets/raw/src07__Screenshot_2026-10-27_150531_2cd11d.png"
OUT = "public/images"
os.makedirs(OUT, exist_ok=True)

raw = Image.open(SRC).convert("RGB")
print("source:", raw.size)

def cine(im, contrast=1.14, sat=0.90, lift=-6, warmth=2, vig=0.30, sharp=1.12):
    """Deep, restrained, filmic. Blacks sink, colour pulls back, highlights roll off."""
    def lut(idx):
        out = []
        for v in range(256):
            x = v / 255.0
            # filmic S-curve: gentle toe, controlled shoulder
            x = x * x * (3 - 2 * x) * 0.55 + x * 0.45
            x = (x - 0.5) * contrast + 0.5
            # sink the blacks without clipping them to mud
            x += lift / 255.0 * (1 - x)
            v2 = max(0.0, min(1.0, x)) * 255
            v2 += warmth if idx == 0 else (-warmth * 0.7 if idx == 2 else 0)
            out.append(max(0, min(255, int(v2))))
        return out
    r, g, b = im.split()
    im = Image.merge("RGB", (r.point(lut(0)), g.point(lut(1)), b.point(lut(2))))
    im = ImageEnhance.Color(im).enhance(sat)
    # vignette: pulls the eye to the centre
    S = 80
    m = Image.new("L", (S, S), 0); px = m.load(); c = (S - 1) / 2; md = (c * c + c * c) ** 0.5
    for y in range(S):
        for x in range(S):
            d = (((x - c) ** 2 + (y - c) ** 2) ** 0.5) / md
            px[x, y] = max(0, min(255, int(255 * (1 - vig * max(0.0, d - 0.35) / 0.65))))
    m = m.resize(im.size, Image.LANCZOS)
    im = Image.composite(im, Image.new("RGB", im.size, (0, 0, 0)), m)
    return ImageEnhance.Sharpness(im).enhance(sharp)

def save(im, name, q=90):
    im.save(f"{OUT}/{name}.jpg", "JPEG", quality=q, optimize=True, progressive=True)
    im.save(f"{OUT}/{name}.webp", "WEBP", quality=84, method=6)
    print(f"  {name}: {im.size}  {os.path.getsize(f'{OUT}/{name}.jpg')//1024} KB")

# ---- 1. wide cinematic frame, upscaled ABOVE display size so browsers downscale ----
wide = cine(raw).resize((1760, round(raw.height * 1760 / raw.width)), Image.LANCZOS)
wide = wide.filter(ImageFilter.UnsharpMask(radius=1.4, percent=44, threshold=4))
save(wide, "hero-cine")

# ---- 2. tight art-directed panel crop: him, minus the clutter ----
# subject centre is ~0.75 across; frame him with breathing room on the left
tight = raw.crop((300, 0, 764, 507))          # 464 x 507
tight = cine(tight, vig=0.36)
# to a 4:5 portrait so it can sit as a tall panel
w, h = tight.size
tw = int(h * 4 / 5)
x0 = w - tw                                   # anchor right: keeps him, drops left clutter
panel = tight.crop((x0, 0, x0 + tw, h))
panel = panel.resize((panel.width * 2, panel.height * 2), Image.LANCZOS)
panel = panel.filter(ImageFilter.UnsharpMask(radius=1.3, percent=40, threshold=4))
save(panel, "hero-panel")

# ---- 3. square-ish crop for the gallery plate ----
plate = cine(raw.crop((264, 0, 764, 507)), vig=0.32)
pw, ph = plate.size
side = min(pw, ph)
plate = plate.crop(((pw - side) // 2, 0, (pw - side) // 2 + side, side))
plate = plate.resize((plate.width * 2, plate.height * 2), Image.LANCZOS)
save(plate, "hero-plate")

print("\nluminance check (premium grade should have real blacks and clean highlights):")
for n in ("hero-cine", "hero-panel", "hero-plate"):
    g = Image.open(f"{OUT}/{n}.jpg").convert("L")
    px = sorted(g.resize((160, 160)).getdata())
    print(f"  {n:<12} p2={px[len(px)//50]:<4} median={px[len(px)//2]:<4} p98={px[len(px)*49//50]}")

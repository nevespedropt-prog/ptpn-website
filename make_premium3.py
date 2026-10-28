"""Premium hero assets, take 3 - back on the deadlift (best-exposed frame, median 84).

The lesson from take 2: my cine() grade was crushing the image (median 84 -> 1).
This version is deliberately gentle and VERIFIES the output stays in range.
Adds fine grain, which reads as filmic and also masks upscaling softness.
"""
from PIL import Image, ImageEnhance, ImageFilter
import random

SRC = "assets/edited/coach-07-deadlift.jpg"      # 764x507, median 84 - the best-exposed frame
OUT = "public/images"

src = Image.open(SRC).convert("RGB")
print("source:", src.size)

def lum_stats(im):
    g = im.convert("L").resize((160, 160))
    px = sorted(g.getdata()); n = len(px)
    return px[n//50], px[n//2], px[n*49//50]

print("source stats: p2=%d median=%d p98=%d" % lum_stats(src))

def grade(im, contrast=1.06, sat=0.94, lift=4, warmth=3, vig=0.16, sharp=1.08):
    """Gentle. Contrast barely moves, blacks are LIFTED not sunk, vignette is light."""
    def lut(idx):
        out = []
        for v in range(256):
            x = v / 255.0
            x = (x - 0.5) * contrast + 0.5          # gentle contrast, no S-curve crush
            x += lift / 255.0                        # lift, uniformly
            v2 = max(0.0, min(1.0, x)) * 255
            v2 += warmth if idx == 0 else (-warmth * 0.7 if idx == 2 else 0)
            out.append(max(0, min(255, int(v2))))
        return out
    r, g, b = im.split()
    im = Image.merge("RGB", (r.point(lut(0)), g.point(lut(1)), b.point(lut(2))))
    im = ImageEnhance.Color(im).enhance(sat)
    S = 64
    m = Image.new("L", (S, S), 0); px = m.load(); c = (S - 1) / 2; md = (c * c + c * c) ** 0.5
    for y in range(S):
        for x in range(S):
            d = (((x - c) ** 2 + (y - c) ** 2) ** 0.5) / md
            px[x, y] = max(0, min(255, int(255 * (1 - vig * max(0.0, d - 0.45) / 0.55))))
    m = m.resize(im.size, Image.LANCZOS)
    im = Image.composite(im, Image.new("RGB", im.size, (0, 0, 0)), m)
    return ImageEnhance.Sharpness(im).enhance(sharp)

def grain(im, amount=7):
    """Fine luminance grain - filmic, and it disguises upscaling."""
    random.seed(7)
    n = im.size[0] * im.size[1]
    noise = Image.new("L", im.size)
    noise.putdata([128 + random.randint(-amount, amount) for _ in range(n)])
    return Image.blend(im, Image.merge("RGB", (noise, noise, noise)), 0.045)

def save(im, name, q=92):
    im.save(f"{OUT}/{name}.jpg", "JPEG", quality=q, optimize=True, progressive=True)
    im.save(f"{OUT}/{name}.webp", "WEBP", quality=86, method=6)
    print(f"  {name:<16} {str(im.size):<14} p2={lum_stats(im)[0]:<4} median={lum_stats(im)[1]:<4} p98={lum_stats(im)[2]}")

print("\nbuilding:")

# 1. full-bleed cinematic: upscaled 2.3x, grain masks the softness
wide = grade(src, vig=0.20)
wide = wide.resize((1760, round(src.height * 1760 / src.width)), Image.LANCZOS)
wide = wide.filter(ImageFilter.UnsharpMask(radius=1.6, percent=52, threshold=3))
save(grain(wide, 8), "hero-cine")

# 2. crisp plate at 2x (displays ~760px, so it is genuinely sharp)
plate = grade(src, vig=0.22)
plate = plate.resize((plate.width * 2, plate.height * 2), Image.LANCZOS)
plate = plate.filter(ImageFilter.UnsharpMask(radius=1.3, percent=46, threshold=3))
save(grain(plate, 6), "hero-plate2")

# 3. tall crop for a portrait panel (him + kettlebell, right of frame)
tall = grade(src.crop((360, 0, 764, 507)), vig=0.26)
tall = tall.resize((tall.width * 2, tall.height * 2), Image.LANCZOS)
tall = tall.filter(ImageFilter.UnsharpMask(radius=1.3, percent=44, threshold=3))
save(grain(tall, 6), "hero-tall")

# monogram, softened for background use
mono = Image.open("public/brand/ptpn-monogram.png").convert("RGBA")
soft = mono.filter(ImageFilter.GaussianBlur(9))
a = soft.split()[-1].point(lambda v: int(v * 0.92))
soft.putalpha(a)
soft.save("public/brand/ptpn-monogram-soft.png", "PNG", optimize=True)
print(f"  ptpn-monogram-soft.png  {soft.size}")

print("\nany median below 40 means the grade is crushing the image again.")

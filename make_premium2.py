"""Premium hero assets, take 2.

Key change: the photograph is presented in a PANEL at a size the source supports
(~700px display) instead of being stretched full-bleed, which is what made it look soft.
Also: a softened monogram for background use, so it reads as an embossed seal
instead of a noisy sticker.
"""
from PIL import Image, ImageEnhance, ImageFilter
import os

COACH = "assets/edited/coach-02-portrait-wide.jpg"   # eye contact, strong posture, best lit
OUT = "public/images"
os.makedirs(OUT, exist_ok=True)

src = Image.open(COACH).convert("RGB")
print("source:", src.size)

def cine(im, contrast=1.12, sat=0.92, lift=-8, warmth=2, vig=0.26, sharp=1.10):
    def lut(idx):
        out = []
        for v in range(256):
            x = v / 255.0
            x = x * x * (3 - 2 * x) * 0.5 + x * 0.5
            x = (x - 0.5) * contrast + 0.5
            x += lift / 255.0 * (1 - x)
            v2 = max(0.0, min(1.0, x)) * 255
            v2 += warmth if idx == 0 else (-warmth * 0.7 if idx == 2 else 0)
            out.append(max(0, min(255, int(v2))))
        return out
    r, g, b = im.split()
    im = Image.merge("RGB", (r.point(lut(0)), g.point(lut(1)), b.point(lut(2))))
    im = ImageEnhance.Color(im).enhance(sat)
    S = 70
    m = Image.new("L", (S, S), 0); px = m.load(); c = (S - 1) / 2; md = (c * c + c * c) ** 0.5
    for y in range(S):
        for x in range(S):
            d = (((x - c) ** 2 + (y - c) ** 2) ** 0.5) / md
            px[x, y] = max(0, min(255, int(255 * (1 - vig * max(0.0, d - 0.4) / 0.6))))
    m = m.resize(im.size, Image.LANCZOS)
    im = Image.composite(im, Image.new("RGB", im.size, (0, 0, 0)), m)
    return ImageEnhance.Sharpness(im).enhance(sharp)

def save(im, name, q=92):
    im.save(f"{OUT}/{name}.jpg", "JPEG", quality=q, optimize=True, progressive=True)
    im.save(f"{OUT}/{name}.webp", "WEBP", quality=86, method=6)
    print(f"  {name}: {im.size}  {os.path.getsize(f'{OUT}/{name}.jpg')//1024} KB")

# ---- 1. tall portrait plate: centre on him, 2x so it stays crisp at ~460px display ----
tall = src.crop((190, 0, 546, 512))                     # 356 x 512, him centred
tall = cine(tall, vig=0.30)
tall = tall.resize((tall.width * 2, tall.height * 2), Image.LANCZOS)
tall = tall.filter(ImageFilter.UnsharpMask(radius=1.3, percent=42, threshold=4))
save(tall, "hero-portrait")

# ---- 2. wide bleed: 16:9, displayed near 1:1 so no softness ----
wide = src.crop((0, 20, 733, 432))                      # 733 x 412
wide = cine(wide, vig=0.28)
wide = wide.resize((wide.width * 2, wide.height * 2), Image.LANCZOS)
wide = wide.filter(ImageFilter.UnsharpMask(radius=1.2, percent=38, threshold=4))
save(wide, "hero-bleed")

# ---- 3. monogram for background use: softened so the particle ring reads as tone ----
mono = Image.open("public/brand/ptpn-monogram.png").convert("RGBA")
soft = mono.filter(ImageFilter.GaussianBlur(9))
# pull the alpha back a touch so it layers quietly
a = soft.split()[-1].point(lambda v: int(v * 0.92))
soft.putalpha(a)
soft.save("public/brand/ptpn-monogram-soft.png", "PNG", optimize=True)
print(f"  ptpn-monogram-soft.png: {soft.size}  {os.path.getsize('public/brand/ptpn-monogram-soft.png')//1024} KB")

print("\nluminance (want real blacks, clean highlights, subject well lit):")
for n in ("hero-portrait", "hero-bleed"):
    g = Image.open(f"{OUT}/{n}.jpg").convert("L").resize((120, 120))
    px = sorted(g.getdata())
    print(f"  {n:<14} p2={px[len(px)//50]:<4} median={px[len(px)//2]:<4} p98={px[len(px)*49//50]}")

"""Create the hero deadlift image: portrait-friendly crop, graded, exported at web sizes."""
from PIL import Image, ImageDraw, ImageEnhance
import os

SRC = "assets/raw/src07__Screenshot_2026-10-27_150531_2cd11d.png"
OUT = "public/images"
os.makedirs(OUT, exist_ok=True)

def grade(im, contrast=1.045, sat=1.055, warmth=0, lift=8, vig=0.14, sharpen=1.08):
    def lut(idx):
        out = []
        for v in range(256):
            x = (v - 128) * contrast + 128
            x += lift * (1 - x / 255.0) ** 2
            if idx == 0: x += warmth
            elif idx == 2: x -= warmth * 0.85
            out.append(max(0, min(255, int(x))))
        return out
    r, g, b = im.split()
    im = Image.merge("RGB", (r.point(lut(0)), g.point(lut(1)), b.point(lut(2))))
    im = ImageEnhance.Color(im).enhance(sat)
    S = 72
    m = Image.new("L", (S, S), 0); px = m.load(); c = (S - 1) / 2; md = (c * c + c * c) ** 0.5
    for y in range(S):
        for x in range(S):
            d = (((x - c) ** 2 + (y - c) ** 2) ** 0.5) / md
            px[x, y] = max(0, min(255, int(255 * (1 - vig * max(0.0, d - 0.42) / 0.58))))
    m = m.resize(im.size, Image.LANCZOS)
    im = Image.composite(im, Image.new("RGB", im.size, (0, 0, 0)), m)
    return ImageEnhance.Sharpness(im).enhance(sharpen)

raw = Image.open(SRC).convert("RGB")
print("source:", raw.size)

# subject sits right of centre (mirror reflection on the left). Crop to a
# portrait-friendly box that keeps him centred with some gym context.
BOX = (300, 0, 764, 507)
crop = raw.crop(BOX)
print("crop:", crop.size, "aspect", round(crop.width / crop.height, 3))
graded = grade(crop)

# preview with a 4:5 guide so the cover-crop is predictable
prev = graded.copy()
w, h = prev.size
target_w = int(h * 4 / 5)
x0 = (w - target_w) // 2
d = ImageDraw.Draw(prev)
d.rectangle([x0, 0, x0 + target_w - 1, h - 1], outline=(215, 185, 120), width=2)
prev = prev.resize((w * 2, h * 2), Image.LANCZOS)
prev.save("screenshots/hero-crop-check.png")
print("4:5 guide box:", (x0, 0, x0 + target_w, h), "->", target_w, "x", h)

# the 4:5 box verified to contain his whole body (his centre is ~0.75 across)
X0, X1 = 29, 434
hero = graded.crop((X0, 0, X1, graded.height))
# 2x so the browser downscales rather than stretches a phone-resolution source
hero = hero.resize((hero.width * 2, hero.height * 2), Image.LANCZOS)
hero.save(f"{OUT}/hero-deadlift.jpg", "JPEG", quality=92, optimize=True, progressive=True)
hero.save(f"{OUT}/hero-deadlift.webp", "WEBP", quality=88, method=6)
print("hero-deadlift:", hero.size)

# also keep the full graded frame for other uses
graded.save(f"{OUT}/coach-07-deadlift-frame.jpg", "JPEG", quality=92, optimize=True, progressive=True)
print("coach-07-deadlift-frame:", graded.size)

# keep a clear name for the deadlift shot too
g = grade(Image.open("assets/raw/src07__Screenshot_2026-10-27_150531_2cd11d.png").convert("RGB"))
g.save("assets/edited/coach-07-deadlift.jpg", "JPEG", quality=92, optimize=True, progressive=True)
g.save("public/images/coach-07-deadlift.jpg", "JPEG", quality=92, optimize=True, progressive=True)
print("coach-07-deadlift:", g.size)

"""Crop, clean and export the PTPN image set."""
from PIL import Image, ImageEnhance, ImageDraw
import os

RAW = "assets/raw"
OUT = "assets/edited"
os.makedirs(OUT, exist_ok=True)

def load(name):
    return Image.open(os.path.join(RAW, name)).convert("RGB")

def trim_uniform_border(im, tol=8):
    """Remove flat borders (letterbox bars, screenshot edges) from all four sides."""
    w, h = im.size
    col = im.convert("L").resize((1, h), Image.BOX)
    rows = [col.getpixel((0, y)) for y in range(h)]
    rowm = im.convert("L").resize((w, 1), Image.BOX)
    cols = [rowm.getpixel((x, 0)) for x in range(w)]

    top = 0
    while top < h - 1 and rows[top] < 24:
        top += 1
    bot = h
    while bot > 1 and rows[bot - 1] < 24:
        bot -= 1
    left = 0
    while left < w - 1 and cols[left] < 24:
        left += 1
    right = w
    while right > 1 and cols[right - 1] < 24:
        right -= 1
    if right - left < 40 or bot - top < 40:
        return im
    return im.crop((left, top, right, bot))

def enhance(im, contrast=1.07, colour=1.06, sharp=1.18, bright=1.02):
    im = ImageEnhance.Contrast(im).enhance(contrast)
    im = ImageEnhance.Color(im).enhance(colour)
    im = ImageEnhance.Brightness(im).enhance(bright)
    return ImageEnhance.Sharpness(im).enhance(sharp)

def export(im, name, max_long=1600, quality=92):
    im = im.copy()
    im.thumbnail((max_long, max_long), Image.LANCZOS)
    p = os.path.join(OUT, name)
    im.save(p, "JPEG", quality=quality, optimize=True, progressive=True)
    im.save(p.replace(".jpg", ".webp"), "WEBP", quality=88, method=6)
    return im.size

log = []

# ---------- 1. Coach photos: src01..src07 ----------
COACH = {
    "src01__Screenshot_2026-10-27_150008_9102df.png": "coach-01-portrait-seated.jpg",
    "src02__Screenshot_2026-10-27_150413_094de6.png": "coach-02-portrait-wide.jpg",
    "src03__Screenshot_2026-10-27_150429_3e2137.png": "coach-03-boxing-gloves.jpg",
    "src04__Screenshot_2026-10-27_150444_752e1e.png": "coach-04-kettlebell-squat.jpg",
    "src05__Screenshot_2026-10-27_150502_62d097.png": "coach-05-battle-ropes.jpg",
    "src06__Screenshot_2026-10-27_150513_b1ca10.png": "coach-06-battle-ropes-close.jpg",
    "src07__Screenshot_2026-10-27_150531_2cd11d.png": "coach-07-kettlebell-mirror.jpg",
}
for src, dst in COACH.items():
    im = enhance(trim_uniform_border(load(src)))
    log.append(("coach", dst, export(im, dst)))

# ---------- 2. Client: three-panel progression (src11) ----------
im11 = enhance(trim_uniform_border(load("src11__Screenshot 2026-10-27 144738.png")))
log.append(("client", "client-03-progression.jpg", export(im11, "client-03-progression.jpg", max_long=1800)))

# ---------- 3. Client: two-file BEFORE/AFTER pair -> one composition ----------
before = trim_uniform_border(load("src12__Screenshot 2026-10-27 144759.png"))
after = trim_uniform_border(load("src13__Screenshot 2026-10-27 144819.png"))

# the BEFORE/AFTER wordmarks sit in the bottom ~20%; crop them off and
# lay on our own labels in brand style instead
before = before.crop((0, 0, before.width, int(before.height * 0.80)))
after = after.crop((0, 0, after.width, int(after.height * 0.80)))
before = enhance(before); after = enhance(after)

TARGET_H = 900
def fit_h(im, h):
    return im.resize((max(1, int(im.width * h / im.height)), h), Image.LANCZOS)
before = fit_h(before, TARGET_H)
after = fit_h(after, TARGET_H)

GAP, PAD, LABEL = 18, 40, 78
W = PAD * 2 + before.width + GAP + after.width
H = PAD * 2 + TARGET_H + LABEL
comp = Image.new("RGB", (W, H), (17, 17, 18))
comp.paste(before, (PAD, PAD))
comp.paste(after, (PAD + before.width + GAP, PAD))

d = ImageDraw.Draw(comp)
def label(x, y, text, accent):
    d.rectangle([x, y, x + 92, y + 3], fill=accent)
    d.text((x, y + 14), text, fill=(244, 240, 232))
label(PAD, PAD + TARGET_H + 18, "BEFORE", (185, 138, 66))
label(PAD + before.width + GAP, PAD + TARGET_H + 18, "AFTER", (215, 185, 120))
log.append(("client", "client-04-before-after.jpg", export(comp, "client-04-before-after.jpg", max_long=2000)))

# ---------- 4. Client collages carrying another brand's logo: NOT processed ----------
HELD = {
    "src09__Screenshot 2026-10-27 144619.png": "carries MAMBA ONLINE COACHING logo + 33% FAT / 5% FAT / 58KG overlays",
    "src10__Screenshot 2026-10-27 144721.png": "carries MAMBA logo, @mamba_Studios handle, '1 YEAR TRANSFORMATION -20KG' overlay",
}

print(f"{'kind':<8} {'file':<34} {'exported size'}")
for kind, name, size in log:
    print(f"{kind:<8} {name:<34} {size[0]}x{size[1]}")
print("\nHELD BACK (another brand's branding baked in):")
for k, v in HELD.items():
    print(f"  {k}\n     {v}")
print("\nfiles in assets/edited:")
for f in sorted(os.listdir(OUT)):
    print("  ", f, os.path.getsize(os.path.join(OUT, f)) // 1024, "KB")

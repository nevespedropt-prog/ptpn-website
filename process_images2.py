"""PTPN image finishing: consistent house grade, clean crops, branded before/after composition."""
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
import os

RAW, OUT = "assets/raw", "assets/edited"
os.makedirs(OUT, exist_ok=True)

FONT_BOLD = None
for cand in [r"C:/Windows/Fonts/seguisb.ttf", r"C:/Windows/Fonts/arialbd.ttf",
             r"C:/Windows/Fonts/segoeuib.ttf", r"C:/Windows/Fonts/arial.ttf"]:
    if os.path.exists(cand):
        FONT_BOLD = cand
        break
print("label font:", FONT_BOLD)

def load(n):
    return Image.open(os.path.join(RAW, n)).convert("RGB")

# ---------------- house grade ----------------
def grade(im, contrast=1.045, sat=1.055, warmth=0, lift=8, vig=0.14, sharpen=1.08):
    def lut(idx):
        out = []
        for v in range(256):
            x = (v - 128) * contrast + 128
            x += lift * (1 - x / 255.0) ** 2          # open up the shadows
            if idx == 0:   x += warmth                 # warm the highlights
            elif idx == 2: x -= warmth * 0.85          # pull blue back
            out.append(max(0, min(255, int(x))))
        return out
    r, g, b = im.split()
    im = Image.merge("RGB", (r.point(lut(0)), g.point(lut(1)), b.point(lut(2))))
    im = ImageEnhance.Color(im).enhance(sat)
    if vig:
        S = 72
        m = Image.new("L", (S, S), 0)
        px = m.load()
        c = (S - 1) / 2
        md = (c * c + c * c) ** 0.5
        for y in range(S):
            for x in range(S):
                d = (((x - c) ** 2 + (y - c) ** 2) ** 0.5) / md
                px[x, y] = max(0, min(255, int(255 * (1 - vig * max(0.0, d - 0.42) / 0.58))))
        m = m.resize(im.size, Image.LANCZOS)
        im = Image.composite(im, Image.new("RGB", im.size, (0, 0, 0)), m)
    if sharpen:
        im = ImageEnhance.Sharpness(im).enhance(sharpen)
    return im

def strip_letterbox(im):
    w, h = im.size
    col = im.convert("L").resize((1, h), Image.BOX)
    rows = [col.getpixel((0, y)) for y in range(h)]
    top = 0
    while top < h - 1 and rows[top] < 24:
        top += 1
    bot = h
    while bot > 1 and rows[bot - 1] < 24:
        bot -= 1
    return im.crop((0, top, w, bot))

def export(im, name, max_long=1800, quality=92):
    im = im.copy()
    im.thumbnail((max_long, max_long), Image.LANCZOS)
    im.save(os.path.join(OUT, name), "JPEG", quality=quality, optimize=True, progressive=True)
    im.save(os.path.join(OUT, name.replace(".jpg", ".webp")), "WEBP", quality=88, method=6)
    return im.size

def tracked(d, xy, text, font, fill, track=6):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + track
    return x

# ---------------- 1. coach photos ----------------
COACH = {
    "src01__Screenshot_2026-10-27_150008_9102df.png": "coach-01-portrait-seated.jpg",
    "src02__Screenshot_2026-10-27_150413_094de6.png": "coach-02-portrait-wide.jpg",
    "src03__Screenshot_2026-10-27_150429_3e2137.png": "coach-03-boxing-gloves.jpg",
    "src04__Screenshot_2026-10-27_150444_752e1e.png": "coach-04-kettlebell-squat.jpg",
    "src05__Screenshot_2026-10-27_150502_62d097.png": "coach-05-battle-ropes.jpg",
    "src06__Screenshot_2026-10-27_150513_b1ca10.png": "coach-06-battle-ropes-close.jpg",
    "src07__Screenshot_2026-10-27_150531_2cd11d.png": "coach-07-kettlebell-mirror.jpg",
}
sizes = []
for src, dst in COACH.items():
    im = grade(strip_letterbox(load(src)))
    sizes.append((dst, export(im, dst)))

# ---------------- 2. client progression ----------------
im11 = grade(strip_letterbox(load("src11__Screenshot 2026-10-27 144738.png")))
sizes.append(("client-03-progression.jpg", export(im11, "client-03-progression.jpg", max_long=1900)))

# ---------------- 3. client before/after ----------------
# wordmark rows measured from the pixel mask: BEFORE 359..428 of 446, AFTER 419..488 of 548
b = strip_letterbox(load("src12__Screenshot 2026-10-27 144759.png")).crop((0, 0, 328, 352))
a = strip_letterbox(load("src13__Screenshot 2026-10-27 144819.png")).crop((0, 0, 315, 410))
b, a = grade(b), grade(a)

PH = 880
def fit_h(im, h):
    return im.resize((max(1, round(im.width * h / im.height)), h), Image.LANCZOS)
b, a = fit_h(b, PH), fit_h(a, PH)

GAP, PADX, PADT, PADB, CAP = 16, 46, 46, 34, 92
W = PADX * 2 + b.width + GAP + a.width
H = PADT + PH + CAP + PADB
comp = Image.new("RGB", (W, H), (17, 17, 18))
comp.paste(b, (PADX, PADT))
comp.paste(a, (PADX + b.width + GAP, PADT))

d = ImageDraw.Draw(comp)
# thin gold hairline inside each panel
for x0, w in ((PADX, b.width), (PADX + b.width + GAP, a.width)):
    d.rectangle([x0, PADT, x0 + w - 1, PADT + PH - 1], outline=(58, 52, 38), width=1)

fb = ImageFont.truetype(FONT_BOLD, 30) if FONT_BOLD else ImageFont.load_default()
cap_y = PADT + PH + 26
for x0, txt, col in ((PADX, "BEFORE", (185, 138, 66)),
                     (PADX + b.width + GAP, "AFTER", (215, 185, 120))):
    d.rectangle([x0, cap_y, x0 + 30, cap_y + 2], fill=col)
    tracked(d, (x0, cap_y + 12), txt, fb, col, track=7)

sizes.append(("client-04-before-after.jpg", export(comp, "client-04-before-after.jpg", max_long=2000)))

# ---------------- 4. before/after of the grade, for review ----------------
raw_p = strip_letterbox(load("src03__Screenshot_2026-10-27_150429_3e2137.png"))
grd_p = grade(raw_p)
rw, rh = raw_p.size
sheet = Image.new("RGB", (rw * 2 + 30, rh + 40), (12, 12, 13))
sheet.paste(raw_p, (10, 30)); sheet.paste(grd_p, (rw + 20, 30))
dd = ImageDraw.Draw(sheet)
dd.text((10, 8), "ORIGINAL", fill=(160, 156, 148))
dd.text((rw + 20, 8), "GRADED", fill=(215, 185, 120))
sheet.save("screenshots/grade-compare.png")

print(f"\n{'file':<34} size")
for n, s in sizes:
    print(f"{n:<34} {s[0]}x{s[1]}")
print("\nexports in assets/edited:", len([f for f in os.listdir(OUT) if f.endswith('.jpg')]), "jpg")

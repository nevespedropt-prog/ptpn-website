"""Measure exactly where the BEFORE / AFTER wordmarks sit, so crops remove all of them."""
from PIL import Image

RAW = "assets/raw"

def load(p):
    return Image.open(f"{RAW}/{p}").convert("RGB")

def scan(im, label, gold_only=False):
    w, h = im.size
    px = im.load()
    hits = []
    for y in range(h):
        bright = 0
        for x in range(0, w, 2):
            r, g, b = px[x, y]
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum > 195:
                if gold_only:
                    if r > g > b and (r - b) > 30:
                        bright += 1
                else:
                    bright += 1
        frac = bright / (w / 2)
        if frac > 0.03:
            hits.append((y, round(frac, 3)))
    print(f"\n{label}  {im.size}")
    if not hits:
        print("   no bright text rows found")
        return None
    # group contiguous
    runs = []
    for y, f in hits:
        if runs and y - runs[-1][1] <= 6:
            runs[-1][1] = y
        else:
            runs.append([y, y])
    for a, b in runs:
        print(f"   bright rows {a:>4}..{b:<4}  ({b-a+1}px,  from bottom: {im.height-b}px .. {im.height-a}px)")
    return runs

b12 = load("src12__Screenshot 2026-10-27 144759.png")
b13 = load("src13__Screenshot 2026-10-27 144819.png")

# strip the known letterbox first so coordinates are in content space
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
    return im.crop((0, top, w, bot)), top, h - bot

c12, t12, b12pad = strip_letterbox(b12)
c13, t13, b13pad = strip_letterbox(b13)
print(f"letterbox removed: src12 top {t12} bottom {b12pad} -> {c12.size}")
print(f"letterbox removed: src13 top {t13} bottom {b13pad} -> {c13.size}")

scan(c12, "BEFORE (white wordmark, neutral bright)", gold_only=False)
scan(c13, "AFTER (gold wordmark)", gold_only=True)

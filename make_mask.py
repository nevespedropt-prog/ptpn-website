"""Show exactly which pixels are the bright wordmark, as a black/white mask."""
from PIL import Image, ImageDraw

RAW = "assets/raw"

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

def mask_panel(im, label, thr=200):
    g = im.convert("L")
    m = g.point(lambda v: 255 if v > thr else 0).convert("RGB")
    # ruler on the left
    canvas = Image.new("RGB", (m.width + 120, m.height), (0, 0, 0))
    canvas.paste(m, (120, 0))
    d = ImageDraw.Draw(canvas)
    for y in range(0, m.height, 25):
        major = (y % 100 == 0)
        d.line([(120 - (24 if major else 10), y), (120, y)],
               fill=(255, 60, 60) if major else (90, 90, 90), width=2 if major else 1)
        if major:
            d.text((4, y - 6), f"y={y}", fill=(120, 255, 120))
            d.line([(120, y), (canvas.width, y)], fill=(60, 0, 0), width=1)
    d.text((124, 4), label, fill=(120, 255, 120))
    return canvas

b12 = strip_letterbox(Image.open(f"{RAW}/src12__Screenshot 2026-10-27 144759.png").convert("RGB"))
b13 = strip_letterbox(Image.open(f"{RAW}/src13__Screenshot 2026-10-27 144819.png").convert("RGB"))

m1 = mask_panel(b12, "BEFORE bright mask")
m2 = mask_panel(b13, "AFTER bright mask")
W = max(m1.width, m2.width)
sheet = Image.new("RGB", (W, m1.height + m2.height + 30), (0, 0, 0))
sheet.paste(m1, (0, 10))
sheet.paste(m2, (0, m1.height + 24))
sheet.save("screenshots/mask-text.png")
print("mask sheet:", sheet.size, "| BEFORE", b12.size, "| AFTER", b13.size)

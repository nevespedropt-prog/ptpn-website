"""Overlay a pixel ruler on the lower part of the two client photos so crop rows can be read exactly."""
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

def ruler(im, label, frac=0.55, scale=2):
    w, h = im.size
    start = int(h * (1 - frac))
    crop = im.crop((0, start, w, h))
    crop = crop.resize((crop.width * scale, crop.height * scale), Image.LANCZOS)
    canvas = Image.new("RGB", (crop.width + 150, crop.height), (10, 10, 11))
    canvas.paste(crop, (150, 0))
    d = ImageDraw.Draw(canvas)
    for y_src in range(start, h, 10):
        y_can = (y_src - start) * scale
        major = (y_src % 50 == 0)
        d.line([(150 - (26 if major else 12), y_can), (150, y_can)],
               fill=(215, 185, 120) if major else (90, 88, 84), width=2 if major else 1)
        if major:
            d.text((6, y_can - 7), f"y={y_src}", fill=(244, 240, 232))
            d.line([(150, y_can), (canvas.width, y_can)], fill=(215, 185, 120, 90), width=1)
    # mark the bottom edge
    d.line([(150, crop.height - 1), (canvas.width, crop.height - 1)], fill=(255, 80, 80), width=3)
    d.text((6, crop.height - 18), f"bottom y={h-1}", fill=(255, 120, 120))
    d.text((160, 6), label, fill=(215, 185, 120))
    return canvas

b12 = strip_letterbox(Image.open(f"{RAW}/src12__Screenshot 2026-10-27 144759.png").convert("RGB"))
b13 = strip_letterbox(Image.open(f"{RAW}/src13__Screenshot 2026-10-27 144819.png").convert("RGB"))
print("content sizes:", b12.size, b13.size)

r1 = ruler(b12, "BEFORE", 0.5)
r2 = ruler(b13, "AFTER", 0.5)
W = max(r1.width, r2.width)
sheet = Image.new("RGB", (W, r1.height + r2.height + 40), (12, 12, 13))
sheet.paste(r1, (0, 20))
sheet.paste(r2, (0, r1.height + 34))
sheet.save("screenshots/ruler-text.png")
print("ruler sheet:", sheet.size)

"""Ruler overlay on the top and bottom strips of the two MAMBA-branded client collages."""
from PIL import Image, ImageDraw

RAW = "assets/raw"
JOBS = [("src09__Screenshot 2026-10-27 144619.png", "COLLAGE A"),
        ("src10__Screenshot 2026-10-27 144721.png", "COLLAGE B")]

def ruler(im, label, y0, y1, scale=2, side=140):
    crop = im.crop((0, y0, im.width, y1))
    crop = crop.resize((crop.width * scale, crop.height * scale), Image.LANCZOS)
    canvas = Image.new("RGB", (crop.width + side, crop.height), (10, 10, 11))
    canvas.paste(crop, (side, 0))
    d = ImageDraw.Draw(canvas)
    for y_src in range(y0, y1, 10):
        y_can = (y_src - y0) * scale
        major = (y_src % 50 == 0)
        d.line([(side - (30 if major else 12), y_can), (side, y_can)],
               fill=(215, 185, 120) if major else (80, 78, 74), width=2 if major else 1)
        if major:
            d.text((4, y_can - 7), f"y={y_src}", fill=(120, 255, 120))
            d.line([(side, y_can), (canvas.width, y_can)], fill=(70, 20, 20), width=1)
    d.text((side + 6, 4), label, fill=(215, 185, 120))
    return canvas

panels = []
for f, lbl in JOBS:
    im = Image.open(f"{RAW}/{f}").convert("RGB")
    w, h = im.size
    print(lbl, f, im.size)
    panels.append(ruler(im, f"{lbl} — TOP", 0, int(h * 0.28)))
    panels.append(ruler(im, f"{lbl} — BOTTOM", int(h * 0.74), h))

W = max(p.width for p in panels)
H = sum(p.height for p in panels) + 16 * (len(panels) + 1)
sheet = Image.new("RGB", (W, H), (12, 12, 13))
y = 16
for p in panels:
    sheet.paste(p, (0, y)); y += p.height + 16
sheet.save("screenshots/mamba-rulers.png")
print("ruler sheet:", sheet.size)

"""Locate the real content box inside the white canvas, then show the branding strips."""
from PIL import Image, ImageDraw

RAW = "assets/raw"
A = Image.open(f"{RAW}/src09__Screenshot 2026-10-27 144619.png").convert("RGB")
B = Image.open(f"{RAW}/src10__Screenshot 2026-10-27 144721.png").convert("RGB")

def content_bbox(im, white=246):
    w, h = im.size
    col = im.convert("L").resize((1, h), Image.BOX)
    rows = [col.getpixel((0, y)) for y in range(h)]
    rowm = im.convert("L").resize((w, 1), Image.BOX)
    cols = [rowm.getpixel((x, 0)) for x in range(w)]
    top = 0
    while top < h - 1 and rows[top] > white: top += 1
    bot = h
    while bot > 1 and rows[bot - 1] > white: bot -= 1
    left = 0
    while left < w - 1 and cols[left] > white: left += 1
    right = w
    while right > 1 and cols[right - 1] > white: right -= 1
    return (left, top, right, bot)

for name, im in (("A", A), ("B", B)):
    bb = content_bbox(im)
    print(f"{name} {im.size} -> content box {bb}  size {(bb[2]-bb[0], bb[3]-bb[1])}")

ca = A.crop(content_bbox(A))
cb = B.crop(content_bbox(B))
print("cropped:", ca.size, cb.size)

TW = 500
def strip(im, y0, y1, label):
    c = im.crop((0, y0, im.width, y1))
    c = c.resize((TW, max(1, round(c.height * TW / c.width))), Image.LANCZOS)
    canvas = Image.new("RGB", (TW, c.height + 20), (12, 12, 13))
    canvas.paste(c, (0, 20))
    ImageDraw.Draw(canvas).text((4, 4), label, fill=(215, 185, 120))
    return canvas

hA, hB = ca.size[1], cb.size[1]
parts = [
    strip(ca, 0, int(hA * 0.24), f"COLLAGE A top (y0-{int(hA*0.24)})"),
    strip(ca, int(hA * 0.78), hA, f"COLLAGE A bottom (y{int(hA*0.78)}-{hA})"),
    strip(cb, 0, int(hB * 0.24), f"COLLAGE B top (y0-{int(hB*0.24)})"),
    strip(cb, int(hB * 0.78), hB, f"COLLAGE B bottom (y{int(hB*0.78)}-{hB})"),
]
H = sum(p.height for p in parts) + 10 * (len(parts) + 1)
sheet = Image.new("RGB", (TW + 20, H), (10, 10, 11))
y = 10
for p in parts:
    sheet.paste(p, (10, y)); y += p.height + 10
sheet.save("screenshots/mamba-strips.png")
print("strips sheet:", sheet.size)

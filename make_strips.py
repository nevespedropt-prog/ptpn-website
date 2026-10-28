"""Compact visual of the four branding strips, small enough for reliable review."""
from PIL import Image, ImageDraw

RAW = "assets/raw"
A = Image.open(f"{RAW}/src09__Screenshot 2026-10-27 144619.png").convert("RGB")
B = Image.open(f"{RAW}/src10__Screenshot 2026-10-27 144721.png").convert("RGB")
print("A", A.size, "B", B.size)

# corner + edge pixel samples to detect solid bars
for name, im in (("A", A), ("B", B)):
    w, h = im.size
    print(f"{name} corners: TL{im.getpixel((2,2))} TR{im.getpixel((w-3,2))} "
          f"BL{im.getpixel((2,h-3))} BR{im.getpixel((w-3,h-3))}  mid-top{im.getpixel((w//2,2))} "
          f"mid-bottom{im.getpixel((w//2,h-3))}")

TW = 520
def strip(im, y0, y1, label):
    c = im.crop((0, y0, im.width, y1))
    c = c.resize((TW, max(1, round(c.height * TW / c.width))), Image.LANCZOS)
    canvas = Image.new("RGB", (TW, c.height + 22), (12, 12, 13))
    canvas.paste(c, (0, 22))
    ImageDraw.Draw(canvas).text((4, 5), label, fill=(215, 185, 120))
    return canvas

parts = [
    strip(A, 0, 170, "COLLAGE A - TOP strip (y 0-170)"),
    strip(A, 440, 594, "COLLAGE A - BOTTOM strip (y 440-594)"),
    strip(B, 0, 170, "COLLAGE B - TOP strip (y 0-170)"),
    strip(B, 440, 595, "COLLAGE B - BOTTOM strip (y 440-595)"),
]
H = sum(p.height for p in parts) + 10 * (len(parts) + 1)
sheet = Image.new("RGB", (TW + 20, H), (10, 10, 11))
y = 10
for p in parts:
    sheet.paste(p, (10, y)); y += p.height + 10
sheet.save("screenshots/mamba-strips.png")
print("strips sheet:", sheet.size)

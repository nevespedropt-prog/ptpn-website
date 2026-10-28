"""Extract the PTPN monogram (the circular gold seal) as a transparent PNG,
for use as a large faded background element. Icon only - no wordmark.
"""
from PIL import Image, ImageFilter, ImageEnhance
import os

SRC = "brand/ptpn-logo-approved.png"     # the approved raster lockup
OUT = "public/brand"
os.makedirs(OUT, exist_ok=True)

src = Image.open(SRC).convert("RGB")
print("lockup:", src.size)

# the monogram is the leftmost element; content box of the lockup is (335,225,1361,667)
# and the monogram occupies roughly the first 440px of that.
box = (325, 215, 785, 677)
mono = src.crop(box)
print("monogram crop:", mono.size)

# key out the dark background by luminance (same technique as the lockup)
lum = mono.convert("L")
alpha = lum.point(lambda v: 0 if v <= 26 else (255 if v >= 68 else int((v - 26) * 255 / 42)))
out = mono.copy()
out.putalpha(alpha)

# trim to the actual mark
hard = lum.point(lambda v: 255 if v > 34 else 0)
bb = hard.getbbox()
pad = 4
bb = (max(0, bb[0] - pad), max(0, bb[1] - pad), min(out.width, bb[2] + pad), min(out.height, bb[3] + pad))
out = out.crop(bb)
print("trimmed:", out.size)

# upscale for use at very large sizes (a background seal can be 1200px+)
big = out.resize((out.width * 3, out.height * 3), Image.LANCZOS)
big = ImageEnhance.Sharpness(big).enhance(1.15)
big.save(f"{OUT}/ptpn-monogram.png", "PNG", optimize=True)
print("ptpn-monogram.png:", big.size, os.path.getsize(f"{OUT}/ptpn-monogram.png") // 1024, "KB")

# a pre-blurred glow copy, so the background seal can be layered for depth
glow = big.filter(ImageFilter.GaussianBlur(28))
glow = ImageEnhance.Brightness(glow).enhance(1.5)
glow.save(f"{OUT}/ptpn-monogram-glow.png", "PNG", optimize=True)
print("ptpn-monogram-glow.png:", glow.size)

# verify the key worked: report alpha coverage and corner alpha
a = big.split()[-1]
px = list(a.getdata())
opaque = sum(1 for v in px if v > 200)
print(f"alpha: {opaque/len(px)*100:.1f}% of pixels are solid, "
      f"corners={a.getpixel((2,2))},{a.getpixel((a.width-3,2))},{a.getpixel((2,a.height-3))}")

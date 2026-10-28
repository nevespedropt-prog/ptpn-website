"""Prepare assets for the Resend-style hero.

1. The seated portrait: recovered from 2 stops under, graded, cropped to the
   panel aspect the layout needs. (Placeholder resolution - HD version to come.)
2. A refined 3D monogram: more surface grain and a more directional light, so it
   reads as machined metal rather than plastic.
"""
from PIL import Image, ImageChops, ImageFilter, ImageDraw, ImageEnhance
import random, os

OUT = "public/images"
BRAND = "public/brand"

# ---------------- 1. the seated portrait ----------------
raw = Image.open("assets/raw/src02__Screenshot_2026-10-27_150413_094de6.png").convert("RGB")
print("seated source:", raw.size)

def percentiles(im, lo=3, hi=97):
    g = im.convert("L").resize((160, 160))
    px = sorted(g.getdata()); n = len(px)
    return px[int(n*lo/100)], px[int(n*hi/100)]

im = raw.filter(ImageFilter.MedianFilter(size=3))
GAMMA = 0.56
r, g, b = im.split()
f = lambda v: max(0, min(255, int((max(0.0, v/255.0) ** GAMMA) * 255)))
im = Image.merge("RGB", (r.point(f), g.point(f), b.point(f)))
lo, hi = percentiles(im)
lo = max(0, lo-6); hi = min(255, hi+8)
scale = 255.0 / max(1, hi-lo)
st = lambda v: max(0, min(255, int((v-lo)*scale)))
r, g, b = im.split()
im = Image.merge("RGB", (r.point(st), g.point(st), b.point(st)))
im = ImageEnhance.Color(im).enhance(1.20)
im = im.filter(ImageFilter.UnsharpMask(radius=9, percent=28, threshold=6))
im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=42, threshold=3))

# crop: trim the excess from each side while keeping the gym context
w, h = im.size
target = 1.0                                  # square panel
if w / h > target:
    nw = int(h * target); x0 = (w - nw) // 2
    im = im.crop((x0, 0, x0 + nw, h))
else:
    nh = int(w / target); y0 = max(0, (h - nh) // 2)
    im = im.crop((0, y0, w, y0 + nh))

im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
# final sharpening pass after the upscale, where it actually helps
im = im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=62, threshold=3))
im.save(f"{OUT}/hero-seated.jpg", "JPEG", quality=93, optimize=True, progressive=True)
im.save(f"{OUT}/hero-seated.webp", "WEBP", quality=87, method=6)
g = im.convert("L").resize((140, 140)); px = sorted(g.getdata()); n = len(px)
print(f"hero-seated: {im.size}  p2={px[n//50]} median={px[n//2]} p98={px[n*49//50]}  "
      f"{os.path.getsize(f'{OUT}/hero-seated.jpg')//1024} KB")

# ---------------- 2. refined 3D monogram ----------------
mono = Image.open(f"{BRAND}/ptpn-monogram.png").convert("RGBA")
DEPTH, PAD = 30, 110
W, H = mono.width + DEPTH + PAD*2, mono.height + DEPTH + PAD*2
canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ox, oy = PAD, PAD
alpha = mono.split()[-1]

# rim glow
g1 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
g1.paste(Image.new("RGBA", mono.size, (215, 185, 120, 255)), (ox, oy), alpha)
g1 = g1.filter(ImageFilter.GaussianBlur(50))
g1.putalpha(g1.split()[-1].point(lambda v: int(v * 0.42)))
canvas = Image.alpha_composite(canvas, g1)

# extrusion
for i in range(DEPTH, 0, -1):
    t = i / DEPTH
    face = Image.new("RGBA", mono.size, (int(104-58*t), int(78-42*t), int(33-18*t), 255))
    face.putalpha(alpha.point(lambda v: int(v * (0.99 - 0.24*t))))
    canvas.alpha_composite(face, (ox+i, oy+i))

# contact shadow
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sh.paste(Image.new("RGBA", mono.size, (0, 0, 0, 255)), (ox+DEPTH//2, oy+DEPTH//2+8), alpha)
sh = sh.filter(ImageFilter.GaussianBlur(34))
sh.putalpha(sh.split()[-1].point(lambda v: int(v * 0.5)))
canvas = Image.alpha_composite(canvas, sh)

# top face: brushed metal with visible grain
face = mono.convert("RGB")
random.seed(5)
streak = Image.new("L", (face.width, 1))
streak.putdata([128 + random.randint(-30, 30) for _ in range(face.width)])
streak = streak.resize(face.size, Image.BILINEAR).filter(ImageFilter.GaussianBlur(0.35))
streak = Image.merge("RGB", (streak, streak, streak))
face = Image.blend(face, streak, 0.14)

# directional light: bright at the top-left, falling to the bottom-right
grad = Image.new("L", face.size, 0)
d = ImageDraw.Draw(grad)
for y in range(face.height):
    d.line([(0, y), (face.width, y)], fill=int(255 - 165 * (y / face.height)))
grad = grad.filter(ImageFilter.GaussianBlur(46))
grad = Image.merge("RGB", (grad, grad, grad))
face = Image.blend(face, grad, 0.34)
face = ImageEnhance.Brightness(face).enhance(1.16).convert("RGBA")
face.putalpha(alpha)
canvas.alpha_composite(face, (ox, oy))

# fine grain across the whole object so it is not clinically smooth
mask = Image.new("L", canvas.size, 0)
mask.paste(alpha, (ox, oy))
n = canvas.width * canvas.height
noise = Image.new("L", canvas.size)
noise.putdata([128 + random.randint(-16, 16) for _ in range(n)])
noise = noise.filter(ImageFilter.GaussianBlur(0.4))
noise_rgb = Image.merge("RGB", (noise, noise, noise)).convert("RGBA")
noise_rgb.putalpha(mask.point(lambda v: int(v * 0.5)))
canvas = Image.blend(canvas, Image.alpha_composite(canvas, noise_rgb), 0.10)

# bevel
rim_tl = ImageChops.subtract(alpha, ImageChops.offset(alpha, 4, 4)).filter(ImageFilter.GaussianBlur(1.0))
hi = Image.new("RGBA", mono.size, (255, 246, 220, 255)); hi.putalpha(rim_tl.point(lambda v: int(v*0.9)))
canvas.alpha_composite(hi, (ox, oy))
rim_br = ImageChops.subtract(alpha, ImageChops.offset(alpha, -4, -4)).filter(ImageFilter.GaussianBlur(1.3))
lo_ = Image.new("RGBA", mono.size, (34, 22, 4, 255)); lo_.putalpha(rim_br.point(lambda v: int(v*0.75)))
canvas.alpha_composite(lo_, (ox, oy))

# specular
spec = Image.new("L", mono.size, 0)
d = ImageDraw.Draw(spec)
d.ellipse([-int(mono.width*0.30), -int(mono.height*0.70),
           int(mono.width*0.66), int(mono.height*0.28)], fill=110)
spec = ImageChops.multiply(spec.filter(ImageFilter.GaussianBlur(52)), alpha)
sp = Image.new("RGBA", mono.size, (255, 252, 242, 255)); sp.putalpha(spec)
canvas.alpha_composite(sp, (ox, oy))

canvas.save(f"{BRAND}/ptpn-3d.png", "PNG", optimize=True)
small = canvas.copy(); small.thumbnail((720, 720), Image.LANCZOS)
small.save(f"{BRAND}/ptpn-3d-720.png", "PNG", optimize=True)
print(f"ptpn-3d.png {canvas.size} / ptpn-3d-720.png {small.size}")

bg = Image.new("RGB", (small.width+160, small.height+160), (5, 5, 6))
bg.paste(small, (80, 80), small)
bg.save("screenshots/monogram-3d-check2.png")
print("preview: screenshots/monogram-3d-check2.png")

"""Render the PTPN monogram as a high-fidelity 3D object.

Resend's hero object reads premium because it is a real render: extruded depth,
bevelled edges, a brushed-metal top face, specular highlights and a rim glow.
This builds the same treatment for the brand mark, composited from the actual
logo asset so it stays on-brand.

Layers, back to front:
  1. outer rim glow
  2. extruded side faces (deepest first), shaded dark bronze
  3. contact shadow
  4. top face with brushed-metal texture
  5. bevel: bright top-left rim, dark bottom-right rim
  6. specular highlight, upper left
"""
from PIL import Image, ImageChops, ImageFilter, ImageDraw, ImageEnhance
import random

SRC = "public/brand/ptpn-monogram.png"
OUT = "public/brand"

mono = Image.open(SRC).convert("RGBA")
print("monogram:", mono.size)

DEPTH = 34          # extrusion depth in px
PAD = 120           # room for glow and shadow

W, H = mono.width + DEPTH + PAD * 2, mono.height + DEPTH + PAD * 2
canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ox, oy = PAD, PAD

alpha = mono.split()[-1]
luma = mono.convert("L")

# ---------- 1. outer rim glow ----------
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gsil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gsil.paste(Image.new("RGBA", mono.size, (215, 185, 120, 255)), (ox, oy), alpha)
glow = gsil.filter(ImageFilter.GaussianBlur(46))
glow.putalpha(glow.split()[-1].point(lambda v: int(v * 0.55)))
canvas = Image.alpha_composite(canvas, glow)

# ---------- 2. extrusion: side faces, deepest drawn first ----------
for i in range(DEPTH, 0, -1):
    t = i / DEPTH                      # 0 at the top face, 1 at the deepest point
    # side faces are dark bronze, darker the deeper they go
    r = int(96 - 52 * t)
    g = int(72 - 38 * t)
    b = int(30 - 16 * t)
    a = alpha.point(lambda v: int(v * (0.98 - 0.22 * t)))
    face = Image.new("RGBA", mono.size, (r, g, b, 255))
    face.putalpha(a)
    canvas.alpha_composite(face, (ox + i, oy + i))

# ---------- 3. contact shadow ----------
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sh.paste(Image.new("RGBA", mono.size, (0, 0, 0, 255)), (ox + DEPTH // 2, oy + DEPTH // 2 + 10), alpha)
sh = sh.filter(ImageFilter.GaussianBlur(30))
sh.putalpha(sh.split()[-1].point(lambda v: int(v * 0.45)))
canvas = Image.alpha_composite(canvas, sh)

# ---------- 4. top face with a brushed-metal treatment ----------
face = mono.copy()

# brushed metal: fine horizontal streaks, low contrast
random.seed(11)
streak = Image.new("L", (face.width, 1))
streak.putdata([128 + random.randint(-26, 26) for _ in range(face.width)])
streak = streak.resize(face.size, Image.BILINEAR).filter(ImageFilter.GaussianBlur(0.4))
streak = Image.merge("RGB", (streak, streak, streak))
face = Image.blend(face.convert("RGB"), streak, 0.10).convert("RGBA")
face.putalpha(alpha)

# a light gradient across the top face: lit from the upper left
grad = Image.new("L", face.size, 0)
d = ImageDraw.Draw(grad)
for y in range(face.height):
    for_x = int(255 - 150 * (y / face.height))
    d.line([(0, y), (face.width, y)], fill=for_x)
grad = grad.filter(ImageFilter.GaussianBlur(40))
grad = Image.merge("RGB", (grad, grad, grad))
lit = Image.blend(face.convert("RGB"), grad, 0.28)
lit = ImageEnhance.Brightness(lit).enhance(1.12)
lit = lit.convert("RGBA"); lit.putalpha(alpha)
canvas.alpha_composite(lit, (ox, oy))

# ---------- 5. bevel ----------
# bright rim along the top-left edges
rim_tl = ImageChops.subtract(alpha, ImageChops.offset(alpha, 4, 4))
rim_tl = rim_tl.filter(ImageFilter.GaussianBlur(1.1))
hi = Image.new("RGBA", mono.size, (255, 244, 214, 255)); hi.putalpha(rim_tl.point(lambda v: int(v * 0.85)))
canvas.alpha_composite(hi, (ox, oy))

# dark rim along the bottom-right edges, where the face turns away from the light
rim_br = ImageChops.subtract(alpha, ImageChops.offset(alpha, -4, -4))
rim_br = rim_br.filter(ImageFilter.GaussianBlur(1.4))
lo = Image.new("RGBA", mono.size, (40, 26, 6, 255)); lo.putalpha(rim_br.point(lambda v: int(v * 0.7)))
canvas.alpha_composite(lo, (ox, oy))

# ---------- 6. specular highlight, upper left ----------
spec = Image.new("L", mono.size, 0)
d = ImageDraw.Draw(spec)
d.ellipse([-int(mono.width*0.35), -int(mono.height*0.75),
           int(mono.width*0.72), int(mono.height*0.32)], fill=120)
spec = spec.filter(ImageFilter.GaussianBlur(58))
spec = ImageChops.multiply(spec, alpha)
sp = Image.new("RGBA", mono.size, (255, 252, 240, 255)); sp.putalpha(spec)
canvas.alpha_composite(sp, (ox, oy))

canvas.save(f"{OUT}/ptpn-3d.png", "PNG", optimize=True)
print("ptpn-3d.png:", canvas.size)

# a version sized for the hero
hero = canvas.copy()
hero.thumbnail((1400, 1400), Image.LANCZOS)
hero.save(f"{OUT}/ptpn-3d-1400.png", "PNG", optimize=True)
print("ptpn-3d-1400.png:", hero.size)

# preview on the Resend-style background
bg = Image.new("RGB", (canvas.width + 200, canvas.height + 200), (5, 5, 6))
prev = canvas.copy()
prev.thumbnail((900, 900), Image.LANCZOS)
bg.paste(prev, ((bg.width - prev.width)//2, (bg.height - prev.height)//2), prev)
bg.save("screenshots/monogram-3d-check.png")
print("preview: screenshots/monogram-3d-check.png", bg.size)

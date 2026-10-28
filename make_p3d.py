"""Isolate the P letterform from the monogram and render it as a clean 3D object.

The particle ring is what makes the mark look like clip-art at large size
("digital static"). Stripping it leaves the letterform, which is what actually
works as a 3D object. Also re-grades the seated portrait: the red walls were
casting too warm, and the sharpening was too aggressive.
"""
from PIL import Image, ImageChops, ImageFilter, ImageDraw, ImageEnhance
import random, os

BRAND, OUT = "public/brand", "public/images"

# ---------------- 1. isolate the P ----------------
mono = Image.open(f"{BRAND}/ptpn-monogram.png").convert("RGBA")
alpha = mono.split()[-1]
w, h = mono.size
cx, cy = w / 2, h / 2
print("monogram:", mono.size)

def crop_circle(frac, label):
    m = Image.new("L", (w, h), 0)
    r = frac * min(w, h)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(3))
    a = ImageChops.multiply(alpha, m)
    out = mono.copy(); out.putalpha(a)
    bb = a.point(lambda v: 255 if v > 40 else 0).getbbox()
    out = out.crop(bb)
    out.save(f"screenshots/p-only-{label}.png")
    print(f"  frac {frac}: {out.size}")
    return out

print("isolating the P:")
p40 = crop_circle(0.40, "40")
p44 = crop_circle(0.44, "44")

# the letterform should be a single solid mass; report how much survives
for frac, im in ((0.40, p40), (0.44, p44)):
    a = im.split()[-1]
    px = list(a.getdata())
    print(f"  frac {frac}: {sum(1 for v in px if v > 200)/len(px)*100:.1f}% solid pixels")

P = p40                                   # the tighter crop keeps only the letterform
P.save(f"{BRAND}/ptpn-p.png", "PNG", optimize=True)

# ---------------- 2. render the P as a 3D object ----------------
def render3d(src, depth, glow_a, grain_a, name):
    a = src.split()[-1]
    W = src.width + depth + 220
    H = src.height + depth + 220
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ox = oy = 110

    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gl.paste(Image.new("RGBA", src.size, (215, 185, 120, 255)), (ox, oy), a)
    gl = gl.filter(ImageFilter.GaussianBlur(52))
    gl.putalpha(gl.split()[-1].point(lambda v: int(v * glow_a)))
    canvas = Image.alpha_composite(canvas, gl)

    for i in range(depth, 0, -1):
        t = i / depth
        f = Image.new("RGBA", src.size, (int(108-62*t), int(80-44*t), int(34-19*t), 255))
        f.putalpha(a.point(lambda v: int(v * (0.99 - 0.26*t))))
        canvas.alpha_composite(f, (ox+i, oy+i))

    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", src.size, (0, 0, 0, 255)), (ox+depth//2, oy+depth//2+6), a)
    sh = sh.filter(ImageFilter.GaussianBlur(30))
    sh.putalpha(sh.split()[-1].point(lambda v: int(v * 0.42)))
    canvas = Image.alpha_composite(canvas, sh)

    # top face: brushed metal + directional light
    face = src.convert("RGB")
    random.seed(9)
    st = Image.new("L", (face.width, 1))
    st.putdata([128 + random.randint(-34, 34) for _ in range(face.width)])
    st = st.resize(face.size, Image.BILINEAR).filter(ImageFilter.GaussianBlur(0.35))
    face = Image.blend(face, Image.merge("RGB", (st, st, st)), 0.16)

    grad = Image.new("L", face.size, 0)
    d = ImageDraw.Draw(grad)
    for y in range(face.height):
        d.line([(0, y), (face.width, y)], fill=int(255 - 175 * (y / face.height)))
    grad = grad.filter(ImageFilter.GaussianBlur(50))
    face = Image.blend(face, Image.merge("RGB", (grad, grad, grad)), 0.38)
    face = ImageEnhance.Brightness(face).enhance(1.18).convert("RGBA")
    face.putalpha(a)
    canvas.alpha_composite(face, (ox, oy))

    # grain over the object only
    mask = Image.new("L", (W, H), 0); mask.paste(a, (ox, oy))
    n = W * H
    nz = Image.new("L", (W, H))
    nz.putdata([128 + random.randint(-18, 18) for _ in range(n)])
    nz = nz.filter(ImageFilter.GaussianBlur(0.35))
    nzr = Image.merge("RGB", (nz, nz, nz)).convert("RGBA")
    nzr.putalpha(mask.point(lambda v: int(v * 0.55)))
    canvas = Image.blend(canvas, Image.alpha_composite(canvas, nzr), grain_a)

    # bevel + specular
    rt = ImageChops.subtract(a, ImageChops.offset(a, 5, 5)).filter(ImageFilter.GaussianBlur(1.1))
    hi = Image.new("RGBA", src.size, (255, 248, 226, 255)); hi.putalpha(rt.point(lambda v: int(v*0.95)))
    canvas.alpha_composite(hi, (ox, oy))
    rb = ImageChops.subtract(a, ImageChops.offset(a, -5, -5)).filter(ImageFilter.GaussianBlur(1.5))
    lo = Image.new("RGBA", src.size, (30, 19, 3, 255)); lo.putalpha(rb.point(lambda v: int(v*0.8)))
    canvas.alpha_composite(lo, (ox, oy))

    sp = Image.new("L", src.size, 0)
    d = ImageDraw.Draw(sp)
    d.ellipse([-int(src.width*0.28), -int(src.height*0.66),
               int(src.width*0.62), int(src.height*0.26)], fill=105)
    sp = ImageChops.multiply(sp.filter(ImageFilter.GaussianBlur(54)), a)
    spl = Image.new("RGBA", src.size, (255, 253, 244, 255)); spl.putalpha(sp)
    canvas.alpha_composite(spl, (ox, oy))

    canvas.save(f"{BRAND}/{name}.png", "PNG", optimize=True)
    sm = canvas.copy(); sm.thumbnail((760, 760), Image.LANCZOS)
    sm.save(f"{BRAND}/{name}-760.png", "PNG", optimize=True)
    print(f"  {name}.png {canvas.size}")
    return canvas

print("\nrendering 3D:")
mark = render3d(P, 30, 0.40, 0.10, "ptpn-p-3d")

bg = Image.new("RGB", (mark.width + 200, mark.height + 200), (5, 5, 6))
bg.paste(mark, (100, 100), mark)
bg.save("screenshots/p-3d-check.png")
print("preview: screenshots/p-3d-check.png")

# ---------------- 3. re-grade the seated portrait ----------------
raw = Image.open("assets/raw/src02__Screenshot_2026-10-27_150413_094de6.png").convert("RGB")
im = raw.filter(ImageFilter.MedianFilter(size=3))
r, g, b = im.split()
f = lambda v: max(0, min(255, int((max(0.0, v/255.0) ** 0.56) * 255)))
im = Image.merge("RGB", (r.point(f), g.point(f), b.point(f)))

gg = im.convert("L").resize((160, 160)); px = sorted(gg.getdata()); n = len(px)
lo, hi = px[int(n*0.03)] - 6, px[int(n*0.97)] + 8
sc = 255.0 / max(1, hi - lo)
st = lambda v: max(0, min(255, int((v - lo) * sc)))
r, g, b = im.split()
im = Image.merge("RGB", (r.point(st), g.point(st), b.point(st)))

# correct the warm cast from the red walls, and pull saturation back
r, g, b = im.split()
r = r.point(lambda v: max(0, int(v * 0.965)))
g = g.point(lambda v: max(0, min(255, int(v * 0.995))))
b = b.point(lambda v: min(255, int(v * 1.045)))
im = Image.merge("RGB", (r, g, b))
im = ImageEnhance.Color(im).enhance(1.06)
im = im.filter(ImageFilter.UnsharpMask(radius=10, percent=20, threshold=8))
im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=26, threshold=4))   # gentler

w, h = im.size
side = h
x0 = (w - side) // 2
im = im.crop((x0, 0, x0 + side, h)).resize((side*2, side*2), Image.LANCZOS)
im = im.filter(ImageFilter.UnsharpMask(radius=1.5, percent=34, threshold=4))
im.save(f"{OUT}/hero-seated.jpg", "JPEG", quality=93, optimize=True, progressive=True)
im.save(f"{OUT}/hero-seated.webp", "WEBP", quality=87, method=6)

# measure the skin tone shift so the warmth fix is verified, not assumed
def skin_shift(img):
    px = list(img.convert("RGB").resize((100, 100)).getdata())
    r = sum(p[0] for p in px)/len(px); b = sum(p[2] for p in px)/len(px)
    return r - b
print(f"\nhero-seated: {im.size}")
print(f"  R-B shift: before {skin_shift(raw):.1f}  after {skin_shift(im):.1f}  (lower = less orange)")
g2 = im.convert("L").resize((140,140)); p2 = sorted(g2.getdata()); m2 = len(p2)
print(f"  p2={p2[m2//50]} median={p2[m2//2]} p98={p2[m2*49//50]}")

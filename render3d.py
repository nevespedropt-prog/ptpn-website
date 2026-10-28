"""Render the P as a genuinely 3D-shaded object, in pure Python (PIL only).

Previous attempts stacked offset copies, which cannot produce correct bevels.
This does an actual shading pass:
  1. distance transform of the letterform -> height field (a rounded bevel that
     flattens into a plateau, like a real machined/chamfered part)
  2. surface normals from the height gradient
  3. Blinn-Phong lighting: directional key light + ambient + specular
  4. gold albedo with a brushed-metal anisotropy, modulated by the shading
Plus a re-grade of the seated portrait with a proper cool correction.
"""
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance, ImageChops
import math, random, os

BRAND, OUT = "public/brand", "public/images"

# ================= 1. height field from the letterform =================
src = Image.open(f"{BRAND}/ptpn-p.png").convert("RGBA")
WORK = 760
src = src.resize((WORK, WORK), Image.LANCZOS)
a = src.split()[-1]
w = h = WORK
print(f"rendering at {w}x{h}")

apx = list(a.getdata())
inside = [v > 110 for v in apx]

# chamfer distance transform (two passes)
INF = 1e9
d = [0.0 if inside[i] else INF for i in range(w*h)]
for y in range(h):
    row = y*w
    for x in range(w):
        i = row + x
        if d[i] == 0.0: continue
        m = d[i]
        if x > 0: m = min(m, d[i-1] + 1.0)
        if y > 0:
            m = min(m, d[i-w] + 1.0)
            if x > 0: m = min(m, d[i-w-1] + 1.414)
            if x < w-1: m = min(m, d[i-w+1] + 1.414)
        d[i] = m
for y in range(h-1, -1, -1):
    row = y*w
    for x in range(w-1, -1, -1):
        i = row + x
        m = d[i]
        if x < w-1: m = min(m, d[i+1] + 1.0)
        if y < h-1:
            m = min(m, d[i+w] + 1.0)
            if x < w-1: m = min(m, d[i+w+1] + 1.414)
            if x > 0: m = min(m, d[i+w-1] + 1.414)
        d[i] = m
print("  distance transform done")

BEVEL = 16.0                       # bevel width in px
H = [min(v, BEVEL) / BEVEL for v in d]   # 0 at the edge, 1 on the plateau

# ================= 2. normals + 3. lighting =================
# key light from the upper-left, slightly toward the viewer
Lx, Ly, Lz = -0.46, -0.60, 0.66
ln = math.sqrt(Lx*Lx + Ly*Ly + Lz*Lz)
Lx, Ly, Lz = Lx/ln, Ly/ln, Lz/ln
# half-vector against the view direction (0,0,1)
hx, hy, hz = Lx, Ly, Lz + 1.0
hn = math.sqrt(hx*hx + hy*hy + hz*hz)
hx, hy, hz = hx/hn, hy/hn, hz/hn

STRENGTH = 9.0                     # how steeply the height falls at the edge
SHIN = 26.0
out = Image.new("RGB", (w, h), (0, 0, 0))
opx = [None] * (w*h)
random.seed(4)
# brushed-metal albedo: fine horizontal streaks in gold
base_r, base_g, base_b = 198, 160, 84

for y in range(h):
    row = y*w
    for x in range(w):
        i = row + x
        if not inside[i]:
            continue
        xm, xp = (x-1 if x > 0 else x), (x+1 if x < w-1 else x)
        ym, yp = (y-1 if y > 0 else y), (y+1 if y < h-1 else y)
        dx = (H[row+xp] - H[row+xm]) * STRENGTH
        dy = (H[yp*w+x] - H[ym*w+x]) * STRENGTH
        nx, ny, nz = -dx, -dy, 1.0
        nn = math.sqrt(nx*nx + ny*ny + nz*nz)
        nx, ny, nz = nx/nn, ny/nn, nz/nn

        diff = max(0.0, nx*Lx + ny*Ly + nz*Lz)
        spec = max(0.0, nx*hx + ny*hy + nz*hz) ** SHIN

        # albedo with brushed streaks + a little per-pixel variation
        streak = 1.0 + 0.055 * math.sin(y * 1.7 + x * 0.05) + random.uniform(-0.028, 0.028)
        # edge darkening (ambient occlusion where the surface curves away)
        ao = 0.55 + 0.45 * (H[i] ** 0.65)

        lit = (0.24 + 0.92 * diff) * ao
        r = base_r * streak * lit + spec * 255
        g = base_g * streak * lit + spec * 246
        b = base_b * streak * lit + spec * 226
        opx[i] = (min(255, int(r)), min(255, int(g)), min(255, int(b)))
print("  shading done")

out.putdata([p if p else (0, 0, 0) for p in opx])
top = out.convert("RGBA")
top.putalpha(a)

# ================= extrusion (the side wall) =================
DEPTH = 26
PAD = 120
W = w + DEPTH + PAD*2
Hh = h + DEPTH + PAD*2
canvas = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
ox = oy = PAD

# rim glow
gl = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
gl.paste(Image.new("RGBA", (w, h), (215, 185, 120, 255)), (ox, oy), a)
gl = gl.filter(ImageFilter.GaussianBlur(54))
gl.putalpha(gl.split()[-1].point(lambda v: int(v * 0.38)))
canvas = Image.alpha_composite(canvas, gl)

# side wall: the silhouette repeated, shaded so it darkens with depth
sil = Image.new("L", (w, h), 0); sil.paste(a, (0, 0))
for i in range(DEPTH, 0, -1):
    t = i / DEPTH
    f = Image.new("RGBA", (w, h), (int(112-66*t), int(83-48*t), int(35-20*t), 255))
    f.putalpha(sil.point(lambda v: int(v * (0.99 - 0.28*t))))
    canvas.alpha_composite(f, (ox+i, oy+i))

# contact shadow
sh = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
sh.paste(Image.new("RGBA", (w, h), (0, 0, 0, 255)), (ox+DEPTH//2, oy+DEPTH//2+6), a)
sh = sh.filter(ImageFilter.GaussianBlur(32))
sh.putalpha(sh.split()[-1].point(lambda v: int(v * 0.45)))
canvas = Image.alpha_composite(canvas, sh)

canvas.alpha_composite(top, (ox, oy))
canvas.save(f"{BRAND}/ptpn-p-3d.png", "PNG", optimize=True)
sm = canvas.copy(); sm.thumbnail((780, 780), Image.LANCZOS)
sm.save(f"{BRAND}/ptpn-p-3d-780.png", "PNG", optimize=True)
print(f"  ptpn-p-3d.png {canvas.size}")

bg = Image.new("RGB", (canvas.width+180, canvas.height+180), (5, 5, 6))
bg.paste(canvas, (90, 90), canvas)
bg.save("screenshots/p-3d-check2.png")
print("  preview: screenshots/p-3d-check2.png")

# ================= 4. the seated portrait, re-graded =================
raw = Image.open("assets/raw/src02__Screenshot_2026-10-27_150413_094de6.png").convert("RGB")

def skin_rb(img):
    """Average R-B over the central subject area only (not the red walls)."""
    im = img.convert("RGB")
    cw, ch = im.size
    box = im.crop((int(cw*0.36), int(ch*0.30), int(cw*0.64), int(ch*0.62)))
    px = list(box.resize((60, 60)).getdata())
    return sum(p[0] for p in px)/len(px) - sum(p[2] for p in px)/len(px)

print(f"\nseated portrait - subject R-B before: {skin_rb(raw):.1f}")

im = raw.filter(ImageFilter.MedianFilter(size=3))
r, g, b = im.split()
f = lambda v: max(0, min(255, int((max(0.0, v/255.0) ** 0.58) * 255)))
im = Image.merge("RGB", (r.point(f), g.point(f), b.point(f)))

gg = im.convert("L").resize((160, 160)); px = sorted(gg.getdata()); n = len(px)
lo, hi = px[int(n*0.03)] - 6, px[int(n*0.97)] + 8
sc = 255.0 / max(1, hi - lo)
st = lambda v: max(0, min(255, int((v - lo) * sc)))
r, g, b = im.split()
im = Image.merge("RGB", (r.point(st), g.point(st), b.point(st)))

# cool correction: this is the fix for the orange cast
r, g, b = im.split()
r = r.point(lambda v: max(0, int(v * 0.905)))
g = g.point(lambda v: max(0, min(255, int(v * 0.985))))
b = b.point(lambda v: min(255, int(v * 1.115)))
im = Image.merge("RGB", (r, g, b))
im = ImageEnhance.Color(im).enhance(1.02)
im = im.filter(ImageFilter.UnsharpMask(radius=12, percent=18, threshold=10))   # local contrast only

w2, h2 = im.size
side = h2
x0 = (w2 - side)//2
im = im.crop((x0, 0, x0+side, h2)).resize((side*2, side*2), Image.LANCZOS)
# one light sharpen, high threshold so flat areas are untouched and no halos form
im = im.filter(ImageFilter.UnsharpMask(radius=1.3, percent=38, threshold=7))
im.save(f"{OUT}/hero-seated.jpg", "JPEG", quality=93, optimize=True, progressive=True)
im.save(f"{OUT}/hero-seated.webp", "WEBP", quality=87, method=6)
print(f"subject R-B after: {skin_rb(im):.1f}  (want it lower than before)")
print(f"hero-seated: {im.size}")

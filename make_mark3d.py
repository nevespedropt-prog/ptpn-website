"""Extract the P mark from the new logo file and render it as a 3D object.

The supplied file is 481x475 with a solid dark-grey background and no alpha.
Keying it out needs to handle two cases: bright gold (luminance key) and the
darker bronze shadow side (saturation key), otherwise holes appear in the mark.
"""
from PIL import Image, ImageFilter, ImageDraw, ImageChops
import math, random, os

SRC = "00PHOTOS/PTPN Logo2.png"
BRAND = "public/brand"

im = Image.open(SRC).convert("RGB")
w, h = im.size
print("source:", im.size)

# ---- key out the flat grey background ----
r, g, b = im.split()
lum = im.convert("L")
mx = ImageChops.lighter(ImageChops.lighter(r, g), b)
mn = ImageChops.darker(ImageChops.darker(r, g), b)
sat = ImageChops.subtract(mx, mn)          # 0 for neutral grey, high for gold

def ramp(v, lo, hi):
    if v <= lo: return 0
    if v >= hi: return 255
    return int((v - lo) * 255 / (hi - lo))

lum_a = lum.point(lambda v: ramp(v, 34, 88))       # catches the bright gold
sat_a = sat.point(lambda v: ramp(v, 11, 38))       # catches the dark bronze side
alpha = ImageChops.lighter(lum_a, sat_a)

# clean stray specks in the background, then soften the edge
alpha = alpha.filter(ImageFilter.MedianFilter(size=3))
alpha = alpha.point(lambda v: 0 if v < 26 else v)

keyed = im.copy(); keyed.putalpha(alpha)
bb = alpha.point(lambda v: 255 if v > 30 else 0).getbbox()
print("content bbox:", bb)
keyed = keyed.crop(bb)
print("keyed:", keyed.size)

a = keyed.split()[-1]
px = list(a.getdata())
print(f"  alpha: {sum(1 for v in px if v > 200)/len(px)*100:.1f}% solid, "
      f"corners={a.getpixel((1,1))},{a.getpixel((a.width-2,1))}")

keyed.save(f"{BRAND}/ptpn-mark-keyed.png", "PNG", optimize=True)

# ---- the P alone (drop the particle ring) ----
# Radial profile of the keyed mark: the letterform reaches ~0.61 of the half-width,
# then there is a clean gap to ~0.73, then the particle ring. Cut inside the gap.
w2, h2 = keyed.size
cx, cy = w2/2, h2/2
m = Image.new("L", (w2, h2), 0)
rad = 0.66 * (min(w2, h2) / 2)
ImageDraw.Draw(m).ellipse([cx-rad, cy-rad, cx+rad, cy+rad], fill=255)
m = m.filter(ImageFilter.GaussianBlur(2))
p_alpha = ImageChops.multiply(a, m)
p_only = keyed.copy(); p_only.putalpha(p_alpha)
pbb = p_alpha.point(lambda v: 255 if v > 40 else 0).getbbox()
p_only = p_only.crop(pbb)
p_only.save(f"{BRAND}/ptpn-mark-p.png", "PNG", optimize=True)
print("P only:", p_only.size)

# preview both on the dark background
prev = Image.new("RGB", (keyed.width + p_only.width + 90, max(keyed.height, p_only.height) + 60), (5,5,6))
prev.paste(keyed, (30, 30), keyed)
prev.paste(p_only, (keyed.width + 60, 30), p_only)
prev.save("screenshots/mark-keyed-check.png")
print("preview: screenshots/mark-keyed-check.png", prev.size)

# ---- 3D render (distance-field bevel + Blinn-Phong, same shader as before) ----
def render3d(src_img, work, depth, bevel, strength, shin, name, glow=0.38):
    src_img = src_img.resize((work, work), Image.LANCZOS)
    al = src_img.split()[-1]
    ww = hh = work
    apx = list(al.getdata())
    inside = [v > 110 for v in apx]

    INF = 1e9
    d = [0.0 if inside[i] else INF for i in range(ww*hh)]
    for y in range(hh):
        row = y*ww
        for x in range(ww):
            i = row + x
            if d[i] == 0.0: continue
            m_ = d[i]
            if x > 0: m_ = min(m_, d[i-1] + 1.0)
            if y > 0:
                m_ = min(m_, d[i-ww] + 1.0)
                if x > 0: m_ = min(m_, d[i-ww-1] + 1.414)
                if x < ww-1: m_ = min(m_, d[i-ww+1] + 1.414)
            d[i] = m_
    for y in range(hh-1, -1, -1):
        row = y*ww
        for x in range(ww-1, -1, -1):
            i = row + x
            m_ = d[i]
            if x < ww-1: m_ = min(m_, d[i+1] + 1.0)
            if y < hh-1:
                m_ = min(m_, d[i+ww] + 1.0)
                if x < ww-1: m_ = min(m_, d[i+ww+1] + 1.414)
                if x > 0: m_ = min(m_, d[i+ww-1] + 1.414)
            d[i] = m_

    Hh = [min(v, bevel)/bevel for v in d]
    Lx, Ly, Lz = -0.46, -0.60, 0.66
    ln = math.sqrt(Lx*Lx+Ly*Ly+Lz*Lz); Lx, Ly, Lz = Lx/ln, Ly/ln, Lz/ln
    hx, hy, hz = Lx, Ly, Lz+1.0
    hn = math.sqrt(hx*hx+hy*hy+hz*hz); hx, hy, hz = hx/hn, hy/hn, hz/hn

    out = Image.new("RGB", (ww, hh), (0,0,0))
    opx = [None]*(ww*hh)
    random.seed(4)
    br, bg_, bb_ = 200, 162, 86
    for y in range(hh):
        row = y*ww
        for x in range(ww):
            i = row+x
            if not inside[i]: continue
            xm, xp = (x-1 if x > 0 else x), (x+1 if x < ww-1 else x)
            ym, yp = (y-1 if y > 0 else y), (y+1 if y < hh-1 else y)
            dx = (Hh[row+xp] - Hh[row+xm]) * strength
            dy = (Hh[yp*ww+x] - Hh[ym*ww+x]) * strength
            nx, ny, nz = -dx, -dy, 1.0
            nn = math.sqrt(nx*nx+ny*ny+nz*nz); nx, ny, nz = nx/nn, ny/nn, nz/nn
            diff = max(0.0, nx*Lx+ny*Ly+nz*Lz)
            ndh = max(0.0, nx*hx+ny*hy+nz*hz)
            spec = ndh ** shin                  # tight highlight
            sheen = (ndh ** 7.0) * 0.16         # broad metallic sheen
            streak = 1.0 + 0.05*math.sin(y*1.7 + x*0.05) + random.uniform(-0.025, 0.025)
            ao = 0.56 + 0.44*(Hh[i]**0.65)
            lit = (0.20 + 0.88*diff)*ao
            opx[i] = (min(255,int(br*streak*lit + spec*330 + sheen*210)),
                      min(255,int(bg_*streak*lit + spec*315 + sheen*186)),
                      min(255,int(bb_*streak*lit + spec*280 + sheen*140)))
    out.putdata([p if p else (0,0,0) for p in opx])
    top = out.convert("RGBA"); top.putalpha(al)

    PAD = 110
    W = ww + depth + PAD*2; H = hh + depth + PAD*2
    canvas = Image.new("RGBA", (W, H), (0,0,0,0))
    ox = oy = PAD

    gl = Image.new("RGBA", (W, H), (0,0,0,0))
    gl.paste(Image.new("RGBA", (ww, hh), (215,185,120,255)), (ox, oy), al)
    gl = gl.filter(ImageFilter.GaussianBlur(52))
    gl.putalpha(gl.split()[-1].point(lambda v: int(v*glow)))
    canvas = Image.alpha_composite(canvas, gl)

    sil = Image.new("L", (ww, hh), 0); sil.paste(al, (0,0))
    for i in range(depth, 0, -1):
        t = i/depth
        f = Image.new("RGBA", (ww, hh), (int(112-66*t), int(83-48*t), int(35-20*t), 255))
        f.putalpha(sil.point(lambda v: int(v*(0.99-0.28*t))))
        canvas.alpha_composite(f, (ox+i, oy+i))

    sh = Image.new("RGBA", (W, H), (0,0,0,0))
    sh.paste(Image.new("RGBA", (ww, hh), (0,0,0,255)), (ox+depth//2, oy+depth//2+6), al)
    sh = sh.filter(ImageFilter.GaussianBlur(30))
    sh.putalpha(sh.split()[-1].point(lambda v: int(v*0.45)))
    canvas = Image.alpha_composite(canvas, sh)

    canvas.alpha_composite(top, (ox, oy))
    canvas.save(f"{BRAND}/{name}.png", "PNG", optimize=True)
    small = canvas.copy(); small.thumbnail((820, 820), Image.LANCZOS)
    small.save(f"{BRAND}/{name}-820.png", "PNG", optimize=True)
    print(f"  {name}.png {canvas.size}")
    return canvas

print("\n3D renders:")
full = render3d(keyed, 560, 24, 14, 9.0, 46.0, "mark-3d-full")
ponly = render3d(p_only, 500, 22, 15, 9.0, 46.0, "mark-3d-p")

for nm, c in (("full", full), ("p", ponly)):
    b2 = Image.new("RGB", (c.width+160, c.height+160), (5,5,6))
    b2.paste(c, (80, 80), c)
    b2.save(f"screenshots/mark-3d-{nm}.png")
print("previews: screenshots/mark-3d-full.png, screenshots/mark-3d-p.png")

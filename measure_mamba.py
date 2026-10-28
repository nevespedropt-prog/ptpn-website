"""Find the rows occupied by the MAMBA branding strips, from pixel brightness."""
from PIL import Image

RAW = "assets/raw"
JOBS = [("src09__Screenshot 2026-10-27 144619.png", "COLLAGE A"),
        ("src10__Screenshot 2026-10-27 144721.png", "COLLAGE B")]

def profile(im, label, y0, y1, thr=215):
    w = im.size[0]
    px = im.load()
    print(f"\n{label}  region y {y0}..{y1}  (thr={thr})")
    rows = []
    for y in range(y0, y1):
        c = 0
        for x in range(0, w, 2):
            r, g, b = px[x, y]
            if 0.299 * r + 0.587 * g + 0.114 * b > thr:
                c += 1
        rows.append((y, round(c / (w / 2), 3)))
    # group runs where fraction > 0.015
    runs = []
    for y, f in rows:
        if f > 0.015:
            if runs and y - runs[-1][1] <= 4:
                runs[-1][1] = y
            else:
                runs.append([y, y])
    for a, b in runs:
        print(f"   bright-text rows {a:>4}..{b:<4}  height {b-a+1:>3}px   peak density "
              f"{max(f for yy, f in rows if a <= yy <= b)}")
    if not runs:
        print("   none found")
    return runs

for f, lbl in JOBS:
    im = Image.open(f"{RAW}/{f}").convert("RGB")
    w, h = im.size
    print(f"\n=== {lbl}  {f}  {w}x{h} ===")
    profile(im, f"{lbl} TOP", 0, int(h * 0.26))
    profile(im, f"{lbl} BOTTOM", int(h * 0.72), h)

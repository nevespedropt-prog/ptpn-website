"""Print row luminance profiles so the white margins and branding rows are unambiguous."""
from PIL import Image

RAW = "assets/raw"
for name, f in (("A", "src09__Screenshot 2026-10-27 144619.png"),
                ("B", "src10__Screenshot 2026-10-27 144721.png")):
    im = Image.open(f"{RAW}/{f}").convert("RGB")
    w, h = im.size
    g = im.convert("L")
    col = g.resize((1, h), Image.BOX)
    rows = [col.getpixel((0, y)) for y in range(h)]
    print(f"\n=== COLLAGE {name}  {w}x{h} ===")
    print("TOP 0..90:")
    for y in range(0, min(90, h), 3):
        print(f"   y={y:>3}  mean={rows[y]:>3}", "WHITE" if rows[y] > 240 else "")
    print("BOTTOM last 90:")
    for y in range(max(0, h - 90), h, 3):
        print(f"   y={y:>3}  mean={rows[y]:>3}", "WHITE" if rows[y] > 240 else "")

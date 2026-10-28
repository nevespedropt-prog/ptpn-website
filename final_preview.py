"""Final review sheet of the edited set."""
from PIL import Image, ImageDraw
import glob, os

files = sorted(glob.glob("assets/edited/*.jpg"))
TH = 400
cols = 3
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (TH + 16) + 16, rows * (TH + 42) + 16), (14, 14, 16))
d = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    im = Image.open(f)
    im.thumbnail((TH, TH), Image.LANCZOS)
    x = 16 + (i % cols) * (TH + 16)
    y = 16 + (i // cols) * (TH + 42)
    sheet.paste(im, (x + (TH - im.width) // 2, y))
    d.text((x + 2, y + TH + 8), os.path.basename(f)[:42], fill=(215, 185, 120))
sheet.save("screenshots/final-preview.png")
print("preview:", sheet.size, "| images:", len(files))

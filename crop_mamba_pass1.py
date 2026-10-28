"""First-pass crop of the two MAMBA-branded collages: remove top banner and bottom bar."""
from PIL import Image, ImageDraw

RAW = "assets/raw"
A = Image.open(f"{RAW}/src09__Screenshot 2026-10-27 144619.png").convert("RGB")
B = Image.open(f"{RAW}/src10__Screenshot 2026-10-27 144721.png").convert("RGB")

# COLLAGE A: 599x594, no white margin. Top banner rows ~30-68, bottom labels ~516-546
A_CROP = (0, 76, 599, 510)
# COLLAGE B: 594x595, white margin to y=24. Top banner below that, bottom bar near the end
B_CROP = (0, 92, 591, 468)

a = A.crop(A_CROP)
b = B.crop(B_CROP)
print("A:", A.size, "->", a.size)
print("B:", B.size, "->", b.size)

TH = 560
def fit(im):
    im = im.copy(); im.thumbnail((TH, TH), Image.LANCZOS); return im

ta, tb = fit(a), fit(b)
sheet = Image.new("RGB", (ta.width + tb.width + 60, max(ta.height, tb.height) + 50), (12, 12, 13))
d = ImageDraw.Draw(sheet)
sheet.paste(ta, (20, 36)); sheet.paste(tb, (ta.width + 40, 36))
d.text((20, 12), "COLLAGE A cropped", fill=(215, 185, 120))
d.text((ta.width + 40, 12), "COLLAGE B cropped", fill=(215, 185, 120))
sheet.save("screenshots/mamba-crop-pass1.png")
print("preview:", sheet.size)

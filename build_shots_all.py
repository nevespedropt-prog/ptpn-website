import subprocess, os, glob
from PIL import Image

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "screenshots")
os.makedirs(OUT, exist_ok=True)

def shoot(page, out, w, h, budget=14000):
    url = "file:///" + page.replace("\\", "/").replace(" ", "%20")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--no-first-run", "--no-default-browser-check", "--force-device-scale-factor=1",
                    f"--virtual-time-budget={budget}", f"--window-size={w},{h}",
                    f"--user-data-dir={os.path.join(ROOT,'.cr')}", f"--screenshot={out}", url],
                   capture_output=True, timeout=300)

def trim(path, pad=28):
    im = Image.open(path).convert("RGB"); w, h = im.size
    bg = im.getpixel((w // 2, h - 8)); px = im.load()
    for y in range(h - 1, 0, -1):
        if any(abs(px[x, y][0] - bg[0]) > 7 or abs(px[x, y][1] - bg[1]) > 7 or abs(px[x, y][2] - bg[2]) > 7
               for x in range(0, w, 17)):
            if y < h - pad:
                im.crop((0, 0, w, y + pad)).save(path)
            break
    return Image.open(path).size

for d in sorted(glob.glob(os.path.join(ROOT, "sketches", "*"))):
    name = os.path.basename(d)
    page = os.path.join(d, "index.html")
    if not os.path.exists(page):
        continue
    hero = os.path.join(OUT, f"{name}-hero.png")
    full = os.path.join(OUT, f"{name}-full.png")
    shoot(page, hero, 1440, 1050)
    shoot(page, full, 1440, 13000, budget=16000)
    size = trim(full)
    im = Image.open(full).convert("RGB"); w, h = im.size
    for i, y in enumerate(range(0, h, 1500), 1):
        if y + 300 > h:
            break
        im.crop((0, y, w, min(h, y + 1600))).save(os.path.join(OUT, f"{name}-crop{i}.png"))
    print(f"{name:16} hero {Image.open(hero).size}  full {size}")

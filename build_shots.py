import subprocess, os, sys
from PIL import Image
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(ROOT, "screenshots")
os.makedirs(OUT, exist_ok=True)

def shoot(page, out, w, h, budget=9000):
    url = "file:///" + page.replace("\\", "/").replace(" ", "%20")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--no-first-run", "--no-default-browser-check", "--force-device-scale-factor=1",
        f"--virtual-time-budget={budget}", f"--window-size={w},{h}",
        f"--user-data-dir={os.path.join(ROOT,'.cr')}", f"--screenshot={out}", url],
        capture_output=True, timeout=180)
    return os.path.exists(out)

def trim(path, pad=28):
    im = Image.open(path).convert("RGB"); w,h = im.size
    bg = im.getpixel((w//2, h-8))
    last = 0
    px = im.load()
    for y in range(h-1, 0, -1):
        row = [px[x,y] for x in range(0, w, 17)]
        if any(abs(c[0]-bg[0])>7 or abs(c[1]-bg[1])>7 or abs(c[2]-bg[2])>7 for c in row):
            last = y; break
    if last and last < h-pad:
        im.crop((0,0,w,min(h,last+pad))).save(path)
    return Image.open(path).size

for name in ["003-flow","004-drift","005-pulse"]:
    page = os.path.join(ROOT,"sketches",name,"index.html")
    hero = os.path.join(OUT, f"{name}-hero.png")
    full = os.path.join(OUT, f"{name}-full.png")
    shoot(page, hero, 1440, 1050)
    shoot(page, full, 1440, 9000, budget=12000)
    print(name, "hero", Image.open(hero).size, "full ->", trim(full))

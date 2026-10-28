"""Zoom into the actual rendered eyebrow text so the question is settled by pixels, not opinion."""
import asyncio, base64, io, json, os, subprocess, time, urllib.request, shutil, tempfile
from PIL import Image

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
ROOT = r"C:/Users/User/OneDrive/Desktop/PTPN website"
URL = "file:///" + os.path.join(ROOT, "hero-options", "fresh-a.html").replace("\\", "/")
PORT = 9977

async def run():
    import websockets
    prof = os.path.join(tempfile.gettempdir(), "cr-zoom")
    shutil.rmtree(prof, ignore_errors=True)
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
                             "--no-default-browser-check", f"--remote-debugging-port={PORT}",
                             f"--user-data-dir={prof}", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ws = None
    for _ in range(70):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=1) as r:
                ws = json.load(r)["webSocketDebuggerUrl"]
            break
        except Exception:
            time.sleep(0.4)
    async with websockets.connect(ws, max_size=90_000_000) as conn:
        c = [0]
        async def send(m, p=None, s=None):
            c[0] += 1
            msg = {"id": c[0], "method": m, "params": p or {}}
            if s: msg["sessionId"] = s
            await conn.send(json.dumps(msg))
            while True:
                g = json.loads(await conn.recv())
                if g.get("id") == c[0]: return g
        t = await send("Target.createTarget", {"url": "about:blank"})
        a = await send("Target.attachToTarget", {"targetId": t["result"]["targetId"], "flatten": True})
        sid = a["result"]["sessionId"]
        await send("Page.enable", {}, sid); await send("Runtime.enable", {}, sid)
        await send("Emulation.setDeviceMetricsOverride",
                   {"width": 1440, "height": 950, "deviceScaleFactor": 1, "mobile": False}, sid)
        await send("Page.navigate", {"url": URL}, sid)
        await asyncio.sleep(3.2)

        r = await send("Runtime.evaluate", {"expression": """(() => {
            const eb = document.querySelector('.eyebrow');
            const em = document.querySelector('h1 em');
            const g = el => { const b = el.getBoundingClientRect();
              return {x:Math.round(b.x), y:Math.round(b.y), w:Math.round(b.width), h:Math.round(b.height),
                      color:getComputedStyle(el).color, size:getComputedStyle(el).fontSize}; };
            return JSON.stringify({eyebrow:g(eb), em:g(em), bg:getComputedStyle(document.body).backgroundColor});
        })()""", "returnByValue": True}, sid)
        info = json.loads(r["result"]["result"]["value"])
        print("eyebrow:", info["eyebrow"])
        print("h1 em  :", info["em"])
        print("body bg:", info["bg"])

        shot = await send("Page.captureScreenshot",
                          {"format": "png", "captureBeyondViewport": True,
                           "clip": {"x": 0, "y": 0, "width": 1440, "height": 950, "scale": 1}}, sid)
        im = Image.open(io.BytesIO(base64.b64decode(shot["result"]["data"]))).convert("RGB")

        # crop the eyebrow with padding and zoom 4x
        e = info["eyebrow"]
        pad = 8
        box = (max(0, e["x"]-pad), max(0, e["y"]-pad),
               min(1440, e["x"]+e["w"]+pad), min(950, e["y"]+e["h"]+pad))
        crop = im.crop(box)
        crop = crop.resize((crop.width*4, crop.height*4), Image.NEAREST)
        crop.save(f"{ROOT}/screenshots/zoom-eyebrow.png")
        print("zoom crop:", crop.size, "-> screenshots/zoom-eyebrow.png")

        # measure: darkest text pixels vs the surrounding background
        px = list(crop.getdata())
        lum = sorted(0.299*p[0]+0.587*p[1]+0.114*p[2] for p in px)
        dark = lum[:max(1, len(lum)//20)]          # darkest 5% = the glyph cores
        bg = lum[-max(1, len(lum)//5):]            # brightest 20% = the paper
        fg = sum(dark)/len(dark); bgl = sum(bg)/len(bg)
        print(f"\nmeasured glyph luminance: {fg:.0f}   paper: {bgl:.0f}")
        print(f"measured contrast ratio: {(max(fg,bgl)+5)/(min(fg,bgl)+5):.2f}:1")
        await send("Browser.close", {})
    try: proc.wait(timeout=10)
    except Exception: proc.kill()

asyncio.run(run())

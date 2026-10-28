import asyncio, base64, json, os, subprocess, time, urllib.request, shutil, tempfile
from PIL import Image

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
PAGE = "file:///C:/Users/User/OneDrive/Desktop/PTPN%20website/sketches/006-cinematic-data/index.html"
OUT = r"C:/Users/User/OneDrive/Desktop/PTPN website/screenshots"
PORT = 9337

async def shoot(width, height, path, label):
    import websockets
    prof = os.path.join(tempfile.gettempdir(), f"cr-cdp-shot-{width}")
    shutil.rmtree(prof, ignore_errors=True)
    p = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
                          "--no-default-browser-check", f"--remote-debugging-port={PORT}",
                          f"--user-data-dir={prof}", "about:blank"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ws = None
    for _ in range(60):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=1) as r:
                ws = json.load(r)["webSocketDebuggerUrl"]
            break
        except Exception:
            time.sleep(0.4)
    async with websockets.connect(ws, max_size=60_000_000) as w:
        i = [0]
        async def send(m, pr=None, s=None):
            i[0] += 1; msg = {"id": i[0], "method": m, "params": pr or {}}
            if s: msg["sessionId"] = s
            await w.send(json.dumps(msg))
            while True:
                g = json.loads(await w.recv())
                if g.get("id") == i[0]: return g
        t = await send("Target.createTarget", {"url": "about:blank"})
        a = await send("Target.attachToTarget", {"targetId": t["result"]["targetId"], "flatten": True})
        sid = a["result"]["sessionId"]
        await send("Page.enable", {}, sid); await send("Runtime.enable", {}, sid)
        await send("Emulation.setDeviceMetricsOverride",
                   {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": width < 900}, sid)
        await send("Page.navigate", {"url": PAGE}, sid)
        await asyncio.sleep(3.5)
        m = await send("Page.getLayoutMetrics", {}, sid)
        css = m["result"]["cssContentSize"]
        full_h = int(css["height"]) + 20
        await send("Emulation.setDeviceMetricsOverride",
                   {"width": width, "height": full_h, "deviceScaleFactor": 1, "mobile": width < 900}, sid)
        await asyncio.sleep(1.5)
        shot = await send("Page.captureScreenshot",
                          {"format": "png", "captureBeyondViewport": True,
                           "clip": {"x": 0, "y": 0, "width": width, "height": full_h, "scale": 1}}, sid)
        data = base64.b64decode(shot["result"]["data"])
        open(path, "wb").write(data)
        im = Image.open(path).convert("RGB"); w, h = im.size
        px = im.load()
        bgs = {(0x11,0x11,0x12),(0x17,0x17,0x18),(0x1b,0x1b,0x1c),(0x0e,0x0e,0x0f),
               (0x14,0x14,0x14),(0x13,0x13,0x13),(0x0d,0x0d,0x0e),(0x1e,0x1e,0x20),(0x14,0x14,0x15)}
        def near_bg(c, tol=5):
            return any(abs(c[0]-b[0])<=tol and abs(c[1]-b[1])<=tol and abs(c[2]-b[2])<=tol for b in bgs)
        rightmost = 0
        for y in range(0, h, 2):
            for x in range(w-1, max(w-30,0), -1):
                if not near_bg(px[x,y]):
                    rightmost = max(rightmost, x); break
        print(f"{label:<22} viewport={width}  image={w}x{h}  cssHeight={int(css['height'])}  "
              f"rightmost content x={rightmost}  (right margin = {w-1-rightmost}px)")
        await send("Browser.close", {})
    try: p.wait(timeout=10)
    except Exception: p.kill()

async def main():
    await shoot(390, 844, os.path.join(OUT, "006-phone-full.png"), "iPhone 390")
    await shoot(360, 800, os.path.join(OUT, "006-android-full.png"), "Android 360")
    await shoot(768, 1024, os.path.join(OUT, "006-tablet-full.png"), "Tablet 768")
    await shoot(1440, 900, os.path.join(OUT, "006-cinematic-data-full.png"), "Desktop 1440")
    await shoot(1440, 900, os.path.join(OUT, "006-cinematic-data-hero.png"), "Desktop hero-only")

asyncio.run(main())

import asyncio, base64, json, os, subprocess, time, urllib.request, shutil, tempfile
from PIL import Image

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
PAGE = "file:///C:/Users/User/OneDrive/Desktop/PTPN%20website/sketches/006-cinematic-data/index.html"
OUT = r"C:/Users/User/OneDrive/Desktop/PTPN website/screenshots"

async def shoot(port, width, height, path, label, clip_h=None):
    import websockets
    prof = os.path.join(tempfile.gettempdir(), f"cr-cdp-shot-{width}-{clip_h}")
    shutil.rmtree(prof, ignore_errors=True)
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
                             "--no-default-browser-check", f"--remote-debugging-port={port}",
                             f"--user-data-dir={prof}", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ws_url = None
    for _ in range(60):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1) as resp:
                ws_url = json.load(resp)["webSocketDebuggerUrl"]
            break
        except Exception:
            time.sleep(0.4)
    async with websockets.connect(ws_url, max_size=80_000_000) as conn:
        counter = [0]
        async def send(method, params=None, session=None):
            counter[0] += 1
            msg = {"id": counter[0], "method": method, "params": params or {}}
            if session:
                msg["sessionId"] = session
            await conn.send(json.dumps(msg))
            while True:
                got = json.loads(await conn.recv())
                if got.get("id") == counter[0]:
                    return got

        t = await send("Target.createTarget", {"url": "about:blank"})
        a = await send("Target.attachToTarget", {"targetId": t["result"]["targetId"], "flatten": True})
        sid = a["result"]["sessionId"]
        await send("Page.enable", {}, sid)
        await send("Runtime.enable", {}, sid)

        mobile = width < 900
        await send("Emulation.setDeviceMetricsOverride",
                   {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": mobile}, sid)
        await send("Page.navigate", {"url": PAGE}, sid)
        await asyncio.sleep(3.5)

        metrics = await send("Page.getLayoutMetrics", {}, sid)
        css_h = int(metrics["result"]["cssContentSize"]["height"]) + 20
        clip_height = min(clip_h, css_h) if clip_h else css_h

        await send("Emulation.setDeviceMetricsOverride",
                   {"width": width, "height": clip_height, "deviceScaleFactor": 1, "mobile": mobile}, sid)
        await asyncio.sleep(1.2)
        shot = await send("Page.captureScreenshot",
                          {"format": "png", "captureBeyondViewport": True,
                           "clip": {"x": 0, "y": 0, "width": width, "height": clip_height, "scale": 1}}, sid)
        open(path, "wb").write(base64.b64decode(shot["result"]["data"]))

        img = Image.open(path).convert("RGB")
        iw, ih = img.size
        px = img.load()
        bgs = [(0x11,0x11,0x12),(0x17,0x17,0x18),(0x1b,0x1b,0x1c),(0x0e,0x0e,0x0f),
               (0x14,0x14,0x14),(0x13,0x13,0x13),(0x0d,0x0d,0x0e),(0x1e,0x1e,0x20)]
        def near_bg(c, tol=7):
            return any(abs(c[0]-b[0])<=tol and abs(c[1]-b[1])<=tol and abs(c[2]-b[2])<=tol for b in bgs)
        rightmost = 0
        for y in range(0, ih, 2):
            for x in range(iw - 1, -1, -1):
                if not near_bg(px[x, y]):
                    if x > rightmost:
                        rightmost = x
                    break
        print(f"{label:<20} viewport={width:<5} image={iw}x{ih}  cssHeight={int(metrics['result']['cssContentSize']['height'])}  "
              f"rightmost content x={rightmost}  right margin={iw-1-rightmost}px")
        await send("Browser.close", {})
    try:
        proc.wait(timeout=10)
    except Exception:
        proc.kill()

async def main():
    await shoot(9341, 390, 844,  os.path.join(OUT, "006-phone-full.png"),  "iPhone 390")
    await shoot(9342, 360, 800,  os.path.join(OUT, "006-android-full.png"), "Android 360")
    await shoot(9343, 768, 1024, os.path.join(OUT, "006-tablet-full.png"),  "Tablet 768")
    await shoot(9344, 1440, 900, os.path.join(OUT, "006-cinematic-data-full.png"), "Desktop full")
    await shoot(9345, 1440, 900, os.path.join(OUT, "006-cinematic-data-hero.png"), "Desktop hero", clip_h=1050)

asyncio.run(main())

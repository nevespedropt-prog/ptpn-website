"""Measure how visible the background monogram actually is at a range of opacities.

Renders the hero with the seal hidden as a baseline, then at several opacities,
and reports the real luminance lift. Picks a value that is clearly visible
but still an atmospheric element rather than a graphic.
"""
import asyncio, base64, io, json, os, subprocess, time, urllib.request, shutil, tempfile
from PIL import Image

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
ROOT = r"C:/Users/User/OneDrive/Desktop/PTPN website"
URL = "file:///" + os.path.join(ROOT, "hero-options", "premium-2.html").replace("\\", "/")
OUT = os.path.join(ROOT, "screenshots")
PORT = 9944

async def run():
    import websockets
    prof = os.path.join(tempfile.gettempdir(), "cr-seal")
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
    assert ws, "CDP unreachable"
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
        await asyncio.sleep(3.5)

        async def shot(op):
            await send("Runtime.evaluate",
                       {"expression": f"""(() => {{
                          const s = document.querySelector('.seal');
                          s.style.opacity = '{op}';
                          const r = s.getBoundingClientRect();
                          return JSON.stringify({{x: Math.round(r.x), y: Math.round(r.y),
                                                  w: Math.round(r.width), h: Math.round(r.height)}});
                       }})()""", "returnByValue": True}, sid)
            await asyncio.sleep(0.4)
            r = await send("Page.captureScreenshot",
                           {"format": "png", "captureBeyondViewport": True,
                            "clip": {"x": 0, "y": 0, "width": 1440, "height": 950, "scale": 1}}, sid)
            return Image.open(io.BytesIO(base64.b64decode(r["result"]["data"]))).convert("L")

        # find the seal box once
        r = await send("Runtime.evaluate",
                       {"expression": """(() => { const r = document.querySelector('.seal').getBoundingClientRect();
                          return JSON.stringify({x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height)}); })()""",
                        "returnByValue": True}, sid)
        box = json.loads(r["result"]["result"]["value"])
        print("seal box:", box)

        base = await shot(0)
        base_a = list(base.getdata())
        print(f"\n{'opacity':<9} {'mean lift':<11} {'p99 lift':<10} visible?")
        best = None
        for op in (0.10, 0.18, 0.24, 0.30, 0.38, 0.48):
            im = await shot(op)
            a = list(im.getdata())
            diffs = [b - x for b, x in zip(a, base_a)]
            diffs.sort()
            mean = sum(diffs) / len(diffs)
            p99 = diffs[int(len(diffs) * 0.99)]
            verdict = ("invisible" if p99 < 12 else
                       "too faint" if p99 < 25 else
                       "GOOD" if p99 <= 75 else "too strong")
            print(f"{op:<9} {mean:<11.1f} {p99:<10} {verdict}")
            if op == 0.30:
                Image.open(io.BytesIO(base64.b64decode(
                    (await send("Page.captureScreenshot",
                                {"format": "png", "captureBeyondViewport": True,
                                 "clip": {"x": 0, "y": 0, "width": 1440, "height": 950, "scale": 1}},
                                sid))["result"]["data"]))).save(f"{OUT}/seal-op{int(op*100)}.png")
            if verdict == "GOOD" and best is None:
                best = op
        print(f"\nfirst GOOD opacity: {best}")
        await send("Browser.close", {})
    try: proc.wait(timeout=10)
    except Exception: proc.kill()

asyncio.run(run())

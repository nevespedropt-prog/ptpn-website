"""Measure the rendered contrast of the small labels, on real pixels."""
import asyncio, base64, io, json, os, subprocess, time, urllib.request, shutil, tempfile
from PIL import Image

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
ROOT = r"C:/Users/User/OneDrive/Desktop/PTPN website"
URL = "file:///" + os.path.join(ROOT, "hero-options", "front-page.html").replace("\\", "/")
PORT = 9744

TARGETS = [(".strip dd", "strip label"), (".hero__facts span", "hero fact"),
           (".card__meta", "card meta"), (".eyebrow", "eyebrow")]

async def run():
    import websockets
    prof = os.path.join(tempfile.gettempdir(), "cr-contrast")
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
    async with websockets.connect(ws, max_size=200_000_000) as conn:
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
                   {"width": 1440, "height": 950, "deviceScaleFactor": 2, "mobile": False}, sid)
        await send("Page.navigate", {"url": URL}, sid)
        await asyncio.sleep(4.0)

        print(f"{'target':<16} {'css colour':<22} {'glyph lum':>10} {'bg lum':>8} {'ratio':>7}  verdict")
        print("-" * 82)
        for sel, label in TARGETS:
            # absolute page coordinates, so no scrolling is involved at all
            r = await send("Runtime.evaluate", {"expression": f"""(() => {{
                const el = document.querySelector('{sel}');
                if (!el) return 'null';
                const b = el.getBoundingClientRect();
                return JSON.stringify({{x:Math.round(b.x), y:Math.round(b.y + window.scrollY),
                    w:Math.round(b.width), h:Math.round(b.height),
                    c:getComputedStyle(el).color}});
            }})()""", "returnByValue": True}, sid)
            v = r["result"]["result"]["value"]
            if v == "null":
                print(f"{label:<16} not found"); continue
            info = json.loads(v)
            pad = 8
            y0 = max(0, info["y"] - pad)
            hh = info["h"] + pad * 2
            # capture that band of the page directly, at 2x, beyond the viewport
            shot = await send("Page.captureScreenshot",
                              {"format": "png", "captureBeyondViewport": True,
                               "clip": {"x": 0, "y": y0, "width": 1440, "height": hh, "scale": 2}}, sid)
            im = Image.open(io.BytesIO(base64.b64decode(shot["result"]["data"]))).convert("L")
            # crop horizontally to just the element
            x0 = max(0, info["x"] * 2)
            x1 = min(im.width, (info["x"] + info["w"]) * 2)
            crop = im.crop((x0, 0, x1, im.height))
            crop.resize((crop.width, crop.height), Image.NEAREST).save(
                f"screenshots/contrast-{label.replace(' ','-')}.png")
            px = sorted(crop.getdata())
            n = len(px)
            # the design is LIGHT text on a DARK ground, so pick the glyph pixels by
            # which ones are closest to the specified CSS colour - not simply the darkest
            cssLum = 0.299*int(info["c"].split("(")[1].split(",")[0]) \
                   + 0.587*int(info["c"].split(",")[1]) \
                   + 0.114*int(info["c"].split(",")[2].split(")")[0])
            by_dist = sorted(px, key=lambda v: abs(v - cssLum))
            k = max(1, n // 40)
            glyph = sum(by_dist[:k]) / k                       # closest to the intended colour
            bg = sum(px[-max(1, n//8):]) / max(1, n//8) if cssLum < 128 else sum(px[:max(1, n//8)]) / max(1, n//8)
            ratio = (max(glyph, bg) + 5) / (min(glyph, bg) + 5)
            v2 = "PASS" if ratio >= 4.5 else ("marginal" if ratio >= 3.5 else "FAILS")
            print(f"{label:<16} {info['c']:<22} {glyph:>10.0f} {bg:>8.0f} {ratio:>7.2f}  {v2}  (cssLum {cssLum:.0f})")
        await send("Browser.close", {})
    try: proc.wait(timeout=10)
    except Exception: proc.kill()

asyncio.run(run())

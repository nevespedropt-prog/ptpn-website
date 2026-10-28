"""Capture the mixed page as scroll frames.

A scroll-driven page cannot be represented by one flat full-page shot: pinning
and horizontal scrubbing only exist at particular scroll positions. So this walks
the page and captures a viewport frame at each step.
"""
import asyncio, base64, io, json, os, subprocess, time, urllib.request, shutil, tempfile
from PIL import Image, ImageDraw

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
ROOT = r"C:/Users/User/OneDrive/Desktop/PTPN website"
URL = "file:///" + os.path.join(ROOT, "hero-options", "mix.html").replace("\\", "/")
OUT = os.path.join(ROOT, "screenshots")
PORT = 9955
FRAMES = 9

async def run():
    import websockets
    prof = os.path.join(tempfile.gettempdir(), "cr-mix")
    shutil.rmtree(prof, ignore_errors=True)
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
                             "--no-default-browser-check", f"--remote-debugging-port={PORT}",
                             f"--user-data-dir={prof}", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ws = None
    for _ in range(80):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=1) as r:
                ws = json.load(r)["webSocketDebuggerUrl"]
            break
        except Exception:
            time.sleep(0.4)
    assert ws, "CDP unreachable"

    async with websockets.connect(ws, max_size=300_000_000) as conn:
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
        await send("Page.enable", {}, sid)
        await send("Runtime.enable", {}, sid)
        await send("Emulation.setDeviceMetricsOverride",
                   {"width": 1440, "height": 900, "deviceScaleFactor": 1, "mobile": False}, sid)
        await send("Page.navigate", {"url": URL}, sid)
        await asyncio.sleep(6.0)

        libs = await send("Runtime.evaluate", {"expression":
            "JSON.stringify({gsap: !!window.gsap, st: !!window.ScrollTrigger, lenis: !!window.Lenis})",
            "returnByValue": True}, sid)
        print("libraries:", libs["result"]["result"]["value"])

        info = await send("Runtime.evaluate", {"expression":
            "JSON.stringify({h: document.documentElement.scrollHeight, "
            "pinned: !!document.querySelector('.pinned'), steps: document.querySelectorAll('.step').length, "
            "faces: document.querySelectorAll('.sface').length})", "returnByValue": True}, sid)
        d = json.loads(info["result"]["result"]["value"])
        print(f"page height {d['h']}  steps {d['steps']}  screens {d['faces']}")

        maxscroll = d["h"] - 900
        frames = []
        for i in range(FRAMES):
            y = int(maxscroll * i / (FRAMES - 1))
            await send("Runtime.evaluate", {"expression":
                f"window.scrollTo(0, {y}); 'ok'", "returnByValue": True}, sid)
            await asyncio.sleep(1.6)
            real = await send("Runtime.evaluate", {"expression": "window.scrollY", "returnByValue": True}, sid)
            shot = await send("Page.captureScreenshot", {"format": "png"}, sid)
            im = Image.open(io.BytesIO(base64.b64decode(shot["result"]["data"]))).convert("RGB")
            frames.append((y, im))
            print(f"  frame {i+1}/{FRAMES}  target y={y}  actual y={real['result']['result']['value']}")

        # save a contact sheet plus the individual frames
        cols, tw = 3, 440
        th = int(tw * 900 / 1440)
        rows = (len(frames) + cols - 1) // cols
        sheet = Image.new("RGB", (cols*(tw+14)+14, rows*(th+30)+14), (10, 10, 11))
        dr = ImageDraw.Draw(sheet)
        for i, (y, im) in enumerate(frames):
            r, cc = divmod(i, cols)
            x = 14 + cc*(tw+14); yy = 14 + r*(th+30)
            thumb = im.copy(); thumb.thumbnail((tw, th), Image.LANCZOS)
            sheet.paste(thumb, (x, yy))
            dr.text((x, yy+thumb.height+7), f"scroll y={y}", fill=(215, 185, 120))
            im.save(f"{OUT}/mix-frame-{i+1}.png")
        sheet.save(f"{OUT}/mix-contact.png")
        print(f"\n-> mix-contact.png {sheet.size}")
        print(f"-> mix-frame-1..{len(frames)}.png (1440x900 each)")
        await send("Browser.close", {})
    try: proc.wait(timeout=10)
    except Exception: proc.kill()

asyncio.run(run())

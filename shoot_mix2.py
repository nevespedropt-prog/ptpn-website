"""Capture mix2 as scroll frames AND verify the pinned phone actually stays put.

The last version looked pinned in a screenshot but wasn't. So this measures the
phone's viewport position at several scroll depths inside the pinned section:
if it holds a constant top, the pin works.
"""
import asyncio, base64, io, json, os, subprocess, time, urllib.request, shutil, tempfile
from PIL import Image, ImageDraw

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
ROOT = r"C:/Users/User/OneDrive/Desktop/PTPN website"
NAME = "mix2.html"
URL = "file:///" + os.path.join(ROOT, "hero-options", NAME).replace("\\", "/")
OUT = os.path.join(ROOT, "screenshots")
PORT = 9966
FRAMES = 10

async def run():
    import websockets
    prof = os.path.join(tempfile.gettempdir(), "cr-mix2")
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
        await send("Page.enable", {}, sid); await send("Runtime.enable", {}, sid)
        await send("Emulation.setDeviceMetricsOverride",
                   {"width": 1440, "height": 900, "deviceScaleFactor": 1, "mobile": False}, sid)
        await send("Page.navigate", {"url": URL}, sid)
        await asyncio.sleep(7.5)          # let the intro curtain finish

        libs = await send("Runtime.evaluate", {"expression":
            "JSON.stringify({gsap:!!window.gsap,st:!!window.ScrollTrigger,"
            "lenis:!!window.Lenis,locked:document.body.classList.contains('locked'),"
            "lines:document.querySelectorAll('.split-h .mask').length})", "returnByValue": True}, sid)
        print("state:", libs["result"]["result"]["value"])

        geo = await send("Runtime.evaluate", {"expression":
            "JSON.stringify({h:document.documentElement.scrollHeight,"
            "pinTop:Math.round(document.getElementById('pinned').getBoundingClientRect().top+window.scrollY),"
            "pinH:Math.round(document.getElementById('pinned').getBoundingClientRect().height)})",
            "returnByValue": True}, sid)
        g = json.loads(geo["result"]["result"]["value"])
        print(f"page {g['h']}  pinned section y={g['pinTop']} h={g['pinH']}")

        # --- PIN VERIFICATION: sample the phone's viewport top inside the pinned section ---
        print("\npin check (phone viewport top should stay ~constant):")
        pin_tops = []
        for frac in (0.15, 0.3, 0.45, 0.6, 0.75, 0.9):
            y = int(g["pinTop"] + g["pinH"] * frac - 450)
            await send("Runtime.evaluate", {"expression": f"window.scrollTo(0,{y});'ok'", "returnByValue": True}, sid)
            await asyncio.sleep(0.9)
            r = await send("Runtime.evaluate", {"expression":
                "JSON.stringify({top:Math.round(document.getElementById('phone').getBoundingClientRect().top),"
                "active:[...document.querySelectorAll('.step')].findIndex(s=>s.classList.contains('active')),"
                "face:[...document.querySelectorAll('.sface')].findIndex(f=>f.classList.contains('on'))})",
                "returnByValue": True}, sid)
            d = json.loads(r["result"]["result"]["value"])
            pin_tops.append(d["top"])
            print(f"  at {int(frac*100):>3}% of section: phone top={d['top']:>4}  active step={d['active']}  screen={d['face']}")
        # the sticky range ends before the section does, so the last sample is
        # legitimately released. Judge only the samples still inside the pin.
        inside = [t for t in pin_tops if 80 <= t <= 420]
        spread = (max(inside) - min(inside)) if len(inside) > 1 else 999
        print(f"  -> {len(inside)}/{len(pin_tops)} samples inside the sticky range, spread {spread}px")
        print(f"  -> {'PIN WORKS' if spread < 40 else 'PIN FAILED'}"
              + f"  (released samples: {[t for t in pin_tops if t not in inside]})")

        # --- capture frames ---
        maxscroll = g["h"] - 900
        frames = []
        for i in range(FRAMES):
            y = int(maxscroll * i / (FRAMES - 1))
            await send("Runtime.evaluate", {"expression": f"window.scrollTo(0,{y});'ok'", "returnByValue": True}, sid)
            await asyncio.sleep(1.5)
            shot = await send("Page.captureScreenshot", {"format": "png"}, sid)
            im = Image.open(io.BytesIO(base64.b64decode(shot["result"]["data"]))).convert("RGB")
            frames.append((y, im))

        cols, tw = 2, 620
        th = int(tw * 900 / 1440)
        rows = (len(frames) + cols - 1) // cols
        sheet = Image.new("RGB", (cols*(tw+16)+16, rows*(th+30)+16), (10, 10, 11))
        dr = ImageDraw.Draw(sheet)
        for i, (y, im) in enumerate(frames):
            r_, cc = divmod(i, cols)
            x = 16 + cc*(tw+16); yy = 16 + r_*(th+30)
            thumb = im.copy(); thumb.thumbnail((tw, th), Image.LANCZOS)
            sheet.paste(thumb, (x, yy))
            dr.text((x, yy+thumb.height+7), f"y={y}", fill=(215,185,120))
            im.save(f"{OUT}/mix2-frame-{i+1}.png")
        sheet.save(f"{OUT}/mix2-contact.png")
        print(f"\n-> mix2-contact.png {sheet.size}")
        await send("Browser.close", {})
    try: proc.wait(timeout=10)
    except Exception: proc.kill()

asyncio.run(run())

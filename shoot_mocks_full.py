"""Full-page capture for the three mockups."""
import asyncio, base64, io, json, os, subprocess, time, urllib.request, shutil, tempfile
from PIL import Image

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
ROOT = r"C:/Users/User/OneDrive/Desktop/PTPN website"
OUT = os.path.join(ROOT, "screenshots")

CHECK = r"""
(() => {
  const vw = document.documentElement.clientWidth;
  const off = [];
  document.querySelectorAll('body *').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width === 0) return;
    if (r.right > vw + 1) off.push(el.tagName + '.' + (el.className||'').toString().slice(0,22) + ' r=' + Math.round(r.right));
  });
  return JSON.stringify({
    vw, doc: document.documentElement.scrollWidth, h: document.documentElement.scrollHeight,
    n: off.length, off: off.slice(0,6),
    bad: [...document.images].filter(i=>!i.naturalWidth).map(i=>i.getAttribute('src')),
    fonts: [...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family).slice(0,6)
  });
})()
"""

async def shoot(port, name, width, height):
    import websockets
    url = "file:///" + os.path.join(ROOT, "hero-options", name).replace("\\", "/")
    prof = os.path.join(tempfile.gettempdir(), f"cr-m-{port}")
    shutil.rmtree(prof, ignore_errors=True)
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
                             "--no-default-browser-check", f"--remote-debugging-port={port}",
                             f"--user-data-dir={prof}", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ws = None
    for _ in range(70):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1) as r:
                ws = json.load(r)["webSocketDebuggerUrl"]
            break
        except Exception:
            time.sleep(0.4)
    if not ws:
        print(f"FAIL {name}: CDP unreachable"); proc.kill(); return
    try:
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
                       {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": width < 900}, sid)
            await send("Page.navigate", {"url": url}, sid)
            await asyncio.sleep(5.0)

            # force all scroll reveals on, so the capture is not full of blank sections
            await send("Runtime.evaluate", {"expression":
                "document.querySelectorAll('.rv').forEach(e=>e.classList.add('in'));"
                "document.querySelectorAll('.bars i[data-w]').forEach(b=>b.style.width=b.dataset.w+'%');"
                "document.querySelectorAll('[data-count]').forEach(n=>n.textContent=parseFloat(n.dataset.count).toLocaleString('en-GB')+(n.dataset.suffix||''));"
                "document.getElementById('prog') && (document.getElementById('prog').style.width='100%');"
                "true;", "returnByValue": True}, sid)
            await asyncio.sleep(2.0)

            r = await send("Runtime.evaluate", {"expression": CHECK, "returnByValue": True}, sid)
            d = json.loads(r["result"]["result"]["value"])
            print(f"\n=== {name}  {width}px ===")
            print(f"  viewport {d['vw']}  document {d['doc']} x {d['h']}")
            print(f"  overflow {d['n']}" + (f"  {d['off']}" if d['n'] else "  none"))
            print(f"  broken images: {d['bad'] if d['bad'] else 'none'}")
            print(f"  fonts loaded: {d['fonts']}")

            shot = await send("Page.captureScreenshot",
                              {"format": "png", "captureBeyondViewport": True,
                               "clip": {"x": 0, "y": 0, "width": width, "height": d["h"], "scale": 1}}, sid)
            full = Image.open(io.BytesIO(base64.b64decode(shot["result"]["data"]))).convert("RGB")
            p = f"{OUT}/mock-{name.split('-')[1]}-full.png"
            full.save(p, "PNG", optimize=True)
            print(f"  -> {os.path.basename(p)} {full.size}")
            await send("Browser.close", {})
    except Exception as e:
        print(f"FAIL {name}: {type(e).__name__} {e}")
    try: proc.wait(timeout=10)
    except Exception: proc.kill()

async def main():
    for i, n in enumerate(["mock-1-evolution.html", "mock-2-momentum.html", "mock-3-system.html"]):
        await shoot(9900 + i, n, 1440, 950)

asyncio.run(main())

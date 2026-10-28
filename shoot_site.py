"""Screenshot and responsive-check the built PTPN site via CDP (honours the emulated viewport)."""
import asyncio, base64, json, os, subprocess, time, urllib.request, shutil, tempfile, sys

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
ROOT = r"C:/Users/User/OneDrive/Desktop/PTPN website"
PAGE = "file:///" + ROOT.replace(" ", "%20") + "/dist/index.html"
OUT = os.path.join(ROOT, "screenshots")
os.makedirs(OUT, exist_ok=True)

OVERFLOW_JS = r"""
(() => {
  const vw = document.documentElement.clientWidth;
  const off = [];
  document.querySelectorAll('body *').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width === 0) return;
    if (r.right > vw + 1) off.push(el.tagName + '.' + (el.className||'').toString().slice(0,34) + ' r=' + Math.round(r.right));
  });
  return JSON.stringify({ vw, doc: document.documentElement.scrollWidth, n: off.length, off: off.slice(0,6) });
})()
"""

async def shoot(port, width, height, path, label, clip_h=None, check=False):
    import websockets
    prof = os.path.join(tempfile.gettempdir(), f"cr-ptpn-{width}-{clip_h}")
    shutil.rmtree(prof, ignore_errors=True)
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
                             "--no-default-browser-check", f"--remote-debugging-port={port}",
                             f"--user-data-dir={prof}", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ws_url = None
    for _ in range(60):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1) as r:
                ws_url = json.load(r)["webSocketDebuggerUrl"]
            break
        except Exception:
            time.sleep(0.4)
    if not ws_url:
        print("CDP unreachable"); proc.kill(); return
    async with websockets.connect(ws_url, max_size=90_000_000) as conn:
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
        mobile = width < 900
        await send("Emulation.setDeviceMetricsOverride",
                   {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": mobile}, sid)
        await send("Page.navigate", {"url": PAGE}, sid)
        await asyncio.sleep(3.0)

        if check:
            r = await send("Runtime.evaluate", {"expression": OVERFLOW_JS, "returnByValue": True}, sid)
            d = json.loads(r["result"]["result"]["value"])
            ok = "OK  " if d["doc"] <= d["vw"] and d["n"] == 0 else "FAIL"
            print(f"{ok} {label:<18} viewport={d['vw']:<5} docScrollWidth={d['doc']:<5} overflowing={d['n']:<3} {d['off']}")

        m = await send("Page.getLayoutMetrics", {}, sid)
        css_h = int(m["result"]["cssContentSize"]["height"]) + 20
        ch = min(clip_h, css_h) if clip_h else css_h
        await send("Emulation.setDeviceMetricsOverride",
                   {"width": width, "height": ch, "deviceScaleFactor": 1, "mobile": mobile}, sid)
        await asyncio.sleep(1.0)
        shot = await send("Page.captureScreenshot",
                          {"format": "png", "captureBeyondViewport": True,
                           "clip": {"x": 0, "y": 0, "width": width, "height": ch, "scale": 1}}, sid)
        open(path, "wb").write(base64.b64decode(shot["result"]["data"]))
        if not check:
            print(f"     {label:<18} -> {path.split(os.sep)[-1]}  {width}x{ch}")
        await send("Browser.close", {})
    try: proc.wait(timeout=10)
    except Exception: proc.kill()

async def main():
    base = 9400
    await shoot(base + 0, 1440, 900, os.path.join(OUT, "site-hero.png"), "Desktop hero", clip_h=1050)
    await shoot(base + 1, 1440, 900, os.path.join(OUT, "site-full.png"), "Desktop full")
    await shoot(base + 2, 390, 844, os.path.join(OUT, "site-phone.png"), "Phone 390")
    for i, (w, h, lbl) in enumerate([(390, 844, "iPhone"), (360, 800, "Android"),
                                     (768, 1024, "Tablet"), (1024, 768, "Small laptop"),
                                     (1440, 900, "Desktop")]):
        await shoot(base + 10 + i, w, h, os.path.join(OUT, "_tmp.png"), lbl, clip_h=100, check=True)

asyncio.run(main())

import asyncio, json, os, subprocess, time, urllib.request, shutil, tempfile
from PIL import Image

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
PAGE = "file:///C:/Users/User/OneDrive/Desktop/PTPN%20website/sketches/006-cinematic-data/index.html"
OUT = r"C:/Users/User/OneDrive/Desktop/PTPN website/screenshots"
PORT = 9351

JS = r"""
(() => {
  const pick = ['#packages', '.tblwrap', '.packcards', '.pcard', '#measure', '#how', '#coach', '#app', '#blog', '#enquire', 'footer', '.quote-stage', '.trans'];
  const out = {};
  pick.forEach(sel => {
    const e = document.querySelector(sel);
    if (e) { const b = e.getBoundingClientRect();
      out[sel] = { top: Math.round(b.top + window.scrollY), h: Math.round(b.height), w: Math.round(b.width),
                   display: getComputedStyle(e).display }; }
  });
  return JSON.stringify(out, null, 1);
})()
"""

async def main():
    import websockets
    prof = os.path.join(tempfile.gettempdir(), "cr-cdp-map"); shutil.rmtree(prof, ignore_errors=True)
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
                             "--no-default-browser-check", f"--remote-debugging-port={PORT}",
                             f"--user-data-dir={prof}", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ws_url = None
    for _ in range(60):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=1) as resp:
                ws_url = json.load(resp)["webSocketDebuggerUrl"]
            break
        except Exception:
            time.sleep(0.4)
    async with websockets.connect(ws_url, max_size=40_000_000) as conn:
        c = [0]
        async def send(m, p=None, s=None):
            c[0] += 1; msg = {"id": c[0], "method": m, "params": p or {}}
            if s: msg["sessionId"] = s
            await conn.send(json.dumps(msg))
            while True:
                g = json.loads(await conn.recv())
                if g.get("id") == c[0]: return g
        t = await send("Target.createTarget", {"url": "about:blank"})
        a = await send("Target.attachToTarget", {"targetId": t["result"]["targetId"], "flatten": True})
        sid = a["result"]["sessionId"]
        await send("Page.enable", {}, sid); await send("Runtime.enable", {}, sid)
        await send("Emulation.setDeviceMetricsOverride", {"width": 390, "height": 844, "deviceScaleFactor": 1, "mobile": True}, sid)
        await send("Page.navigate", {"url": PAGE}, sid)
        await asyncio.sleep(3.5)
        r = await send("Runtime.evaluate", {"expression": JS, "returnByValue": True}, sid)
        data = json.loads(r["result"]["result"]["value"])
        print(json.dumps(data, indent=1))
        await send("Browser.close", {})
    try: proc.wait(timeout=10)
    except Exception: proc.kill()

asyncio.run(main())

# crop the pricing block precisely
try:
    im = Image.open(os.path.join(OUT, "006-phone-full.png")).convert("RGB")
    top = 0
    import json as _j
    # recompute from the printed map is manual; crop a generous band instead
except Exception as e:
    print("crop skipped:", e)

"""Full-page capture: the entire front page top to bottom, plus a scaled overview."""
import asyncio, base64, io, json, os, subprocess, time, urllib.request, shutil, tempfile
from PIL import Image

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
ROOT = r"C:/Users/User/OneDrive/Desktop/PTPN website"
URL = "file:///" + os.path.join(ROOT, "hero-options", "front-page.html").replace("\\", "/")
OUT = os.path.join(ROOT, "screenshots")
PORT = 9700

CHECK = r"""
(() => {
  const vw = document.documentElement.clientWidth;
  const off = [];
  document.querySelectorAll('body *').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width === 0) return;
    if (r.right > vw + 1) off.push(el.tagName + '.' + (el.className||'').toString().slice(0,24) + ' r=' + Math.round(r.right));
  });
  const imgs = [...document.images].map(i => ({s:i.getAttribute('src'), ok:i.naturalWidth>0}));
  return JSON.stringify({
    vw, doc: document.documentElement.scrollWidth,
    h: document.documentElement.scrollHeight,
    n: off.length, off: off.slice(0,8),
    bad: imgs.filter(i => !i.ok).map(i => i.s),
    sections: [...document.querySelectorAll('section, footer.site')].map(s => ({
      cls: (s.className||'').toString() || s.tagName.toLowerCase(),
      top: Math.round(s.getBoundingClientRect().top + window.scrollY),
      h: Math.round(s.getBoundingClientRect().height)
    }))
  });
})()
"""

async def run(width, height, tag):
    import websockets
    prof = os.path.join(tempfile.gettempdir(), f"cr-full-{tag}")
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
                   {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": width < 900}, sid)
        await send("Page.navigate", {"url": URL}, sid)
        await asyncio.sleep(4.5)

        r = await send("Runtime.evaluate", {"expression": CHECK, "returnByValue": True}, sid)
        d = json.loads(r["result"]["result"]["value"])
        print(f"\n=== {tag}  {width}px ===")
        print(f"  viewport {d['vw']}  document {d['doc']} x {d['h']}")
        print(f"  horizontal overflow: {d['n']}" + (f"  {d['off']}" if d['n'] else "  none"))
        print(f"  broken images: {d['bad'] if d['bad'] else 'none'}")
        print(f"  {'section':<28} {'top':>7} {'height':>7}")
        for s in d["sections"]:
            print(f"  {s['cls'][:28]:<28} {s['top']:>7} {s['h']:>7}")

        shot = await send("Page.captureScreenshot",
                          {"format": "png", "captureBeyondViewport": True,
                           "clip": {"x": 0, "y": 0, "width": width, "height": d["h"], "scale": 1}}, sid)
        full = Image.open(io.BytesIO(base64.b64decode(shot["result"]["data"])))
        p = f"{OUT}/front-page-{tag}.png"
        full.convert("RGB").save(p, "PNG", optimize=True)
        print(f"  -> {os.path.basename(p)}  {full.size}")

        # a scaled overview, readable in one look
        ov = full.convert("RGB").copy()
        ov.thumbnail((680, 20000), Image.LANCZOS)
        ov.save(f"{OUT}/front-page-{tag}-overview.png")
        print(f"  -> front-page-{tag}-overview.png  {ov.size}")
        await send("Browser.close", {})
    try: proc.wait(timeout=10)
    except Exception: proc.kill()

asyncio.run(run(1440, 950, "desktop"))

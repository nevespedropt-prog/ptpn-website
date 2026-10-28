import asyncio, json, os, subprocess, time, urllib.request, shutil, tempfile

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
PAGE = "file:///C:/Users/User/OneDrive/Desktop/PTPN%20website/sketches/006-cinematic-data/index.html"
PORT = 9336

JS = r"""
(() => {
  const r = (sel) => { const e = document.querySelector(sel); if (!e) return null;
    const b = e.getBoundingClientRect();
    return {l:Math.round(b.left), r:Math.round(b.right), w:Math.round(b.width), sw:e.scrollWidth}; };
  return JSON.stringify({
    innerWidth: window.innerWidth,
    clientWidth: document.documentElement.clientWidth,
    docScrollWidth: document.documentElement.scrollWidth,
    bodyScrollWidth: document.body.scrollWidth,
    dpr: window.devicePixelRatio,
    wrap: r('.wrap'),
    heroGrid: r('.hero-grid'),
    heroCopy: r('.hero-copy'),
    h1: r('h1'),
    h1em: r('h1 em'),
    lede: r('.hero-copy .lede'),
    eyebrow: r('.eyebrow'),
    panel: r('.panel'),
    proofGrid: r('.proof-grid'),
    footer: r('footer'),
    fbot: r('.fbot')
  }, null, 1);
})()
"""

async def main():
    import websockets
    prof = os.path.join(tempfile.gettempdir(), "cr-cdp-geom"); shutil.rmtree(prof, ignore_errors=True)
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
    async with websockets.connect(ws, max_size=30_000_000) as w:
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
                   {"width": 390, "height": 844, "deviceScaleFactor": 2, "mobile": True}, sid)
        await send("Page.navigate", {"url": PAGE}, sid)
        await asyncio.sleep(3)
        r = await send("Runtime.evaluate", {"expression": JS, "returnByValue": True}, sid)
        print(r["result"]["result"]["value"])
        await send("Browser.close", {})
    try: p.wait(timeout=10)
    except Exception: p.kill()

asyncio.run(main())

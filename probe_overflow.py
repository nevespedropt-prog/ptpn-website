import asyncio, json, os, subprocess, sys, time, urllib.request, shutil, tempfile

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
PAGE = "file:///C:/Users/User/OneDrive/Desktop/PTPN%20website/sketches/006-cinematic-data/index.html"
PORT = 9333

JS = r"""
(() => {
  const vw = document.documentElement.clientWidth;
  const offenders = [];
  document.querySelectorAll('body *').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width === 0) return;
    if (r.right > vw + 1) {
      offenders.push({
        tag: el.tagName,
        cls: (el.className && el.className.toString ? el.className.toString() : '').slice(0, 44),
        right: Math.round(r.right),
        w: Math.round(r.width),
        sw: el.scrollWidth,
        ov: getComputedStyle(el).overflowX
      });
    }
  });
  // keep only the outermost few of each class to avoid noise
  return JSON.stringify({
    vw,
    docScrollWidth: document.documentElement.scrollWidth,
    bodyScrollWidth: document.body.scrollWidth,
    count: offenders.length,
    offenders: offenders.slice(0, 30)
  }, null, 1);
})()
"""

async def main():
    import websockets
    prof = os.path.join(tempfile.gettempdir(), "cr-cdp-probe")
    shutil.rmtree(prof, ignore_errors=True)
    p = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
                          "--no-default-browser-check", f"--remote-debugging-port={PORT}",
                          f"--user-data-dir={prof}", "about:blank"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ws_url = None
    for _ in range(60):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=1) as r:
                ws_url = json.load(r)["webSocketDebuggerUrl"]
            break
        except Exception:
            time.sleep(0.4)
    if not ws_url:
        print("FAILED to reach CDP"); p.kill(); return

    async with websockets.connect(ws_url, max_size=30_000_000) as ws:
        i = [0]
        async def send(method, params=None, session=None):
            i[0] += 1
            msg = {"id": i[0], "method": method, "params": params or {}}
            if session:
                msg["sessionId"] = session
            await ws.send(json.dumps(msg))
            while True:
                got = json.loads(await ws.recv())
                if got.get("id") == i[0]:
                    return got

        t = await send("Target.createTarget", {"url": "about:blank"})
        tid = t["result"]["targetId"]
        a = await send("Target.attachToTarget", {"targetId": tid, "flatten": True})
        sid = a["result"]["sessionId"]
        await send("Page.enable", {}, sid)
        await send("Runtime.enable", {}, sid)

        for w, h, label in [(390, 844, "iPhone 390"), (360, 800, "Android 360"), (768, 1024, "Tablet 768")]:
            await send("Emulation.setDeviceMetricsOverride",
                       {"width": w, "height": h, "deviceScaleFactor": 2, "mobile": True}, sid)
            await send("Page.navigate", {"url": PAGE}, sid)
            await asyncio.sleep(3.0)
            r = await send("Runtime.evaluate", {"expression": JS, "returnByValue": True}, sid)
            data = json.loads(r["result"]["result"]["value"])
            print(f"\n=== {label} ===")
            print(f"viewport {data['vw']}  docScrollWidth {data['docScrollWidth']}  bodyScrollWidth {data['bodyScrollWidth']}")
            print(f"elements past right edge: {data['count']}")
            seen = set()
            for o in data["offenders"]:
                key = (o["tag"], o["cls"])
                if key in seen:
                    continue
                seen.add(key)
                print(f"   {o['tag']:<8} .{o['cls']:<46} right={o['right']:<6} w={o['w']:<6} scrollW={o['sw']:<6} overflowX={o['ov']}")

        await send("Browser.close", {})
    try:
        p.wait(timeout=10)
    except Exception:
        p.kill()

asyncio.run(main())

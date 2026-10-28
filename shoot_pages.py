"""Render the three premium hero options at desktop and phone widths with overflow checks."""
import asyncio, base64, json, os, subprocess, time, urllib.request, shutil, tempfile

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
ROOT = r"C:/Users/User/OneDrive/Desktop/PTPN website"
OUT = os.path.join(ROOT, "screenshots")

CHECK_JS = r"""
(() => {
  const vw = document.documentElement.clientWidth;
  const off = [];
  document.querySelectorAll('body *').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width === 0) return;
    if (r.right > vw + 1) off.push(el.tagName + '.' + (el.className||'').toString().slice(0,26) + ' r=' + Math.round(r.right));
  });
  const imgs = [...document.images].map(i => ({src: i.getAttribute('src'), ok: i.naturalWidth > 0}));
  const h1 = document.querySelector('h1');
  const r = h1 ? h1.getBoundingClientRect() : null;
  return JSON.stringify({
    vw, doc: document.documentElement.scrollWidth, n: off.length, off: off.slice(0,6),
    imgs, h1: r ? {w: Math.round(r.width), h: Math.round(r.height), fs: getComputedStyle(h1).fontSize} : null
  });
})()
"""

async def shoot(port, url, width, height, path, label):
    import websockets
    prof = os.path.join(tempfile.gettempdir(), f"cr-p-{width}-{os.path.basename(path)}")
    shutil.rmtree(prof, ignore_errors=True)
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
                             "--no-default-browser-check", f"--remote-debugging-port={port}",
                             f"--user-data-dir={prof}", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ws_url = None
    for _ in range(70):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1) as r:
                ws_url = json.load(r)["webSocketDebuggerUrl"]
            break
        except Exception:
            time.sleep(0.4)
    if not ws_url:
        print(f"FAIL {label}: CDP unreachable"); proc.kill(); return
    try:
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
            await send("Emulation.setDeviceMetricsOverride",
                       {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": width < 900}, sid)
            await send("Page.navigate", {"url": url}, sid)
            await asyncio.sleep(3.5)
            r = await send("Runtime.evaluate", {"expression": CHECK_JS, "returnByValue": True}, sid)
            if "value" not in r.get("result", {}).get("result", {}):
                print(f"FAIL {label}: eval {json.dumps(r.get('result'))[:200]}")
            else:
                d = json.loads(r["result"]["result"]["value"])
                bad = [i for i in d["imgs"] if not i["ok"]]
                ok = "OK  " if d["doc"] <= d["vw"] and not bad else "FAIL"
                print(f"{ok} {label:<22} vw={d['vw']:<5} doc={d['doc']:<5} over={d['n']:<3} "
                      f"imgs={len(d['imgs'])-len(bad)}/{len(d['imgs'])} h1={d['h1']}")
                if bad: print("     BROKEN:", bad)
                if d["off"]: print("     OVERFLOW:", d["off"])
            m = await send("Page.getLayoutMetrics", {}, sid)
            ch = min(int(m["result"]["cssContentSize"]["height"]) + 10, height)
            shot = await send("Page.captureScreenshot",
                              {"format": "png", "captureBeyondViewport": True,
                               "clip": {"x": 0, "y": 0, "width": width, "height": ch, "scale": 1}}, sid)
            open(path, "wb").write(base64.b64decode(shot["result"]["data"]))
            print(f"     -> {os.path.basename(path)}  {width}x{ch}")
            await send("Browser.close", {})
    except Exception as e:
        print(f"FAIL {label}: {type(e).__name__} {e}")
    try: proc.wait(timeout=10)
    except Exception: proc.kill()

async def main():
    for i, x in enumerate(["1", "2", "3", "4"]):
        url = "file:///" + os.path.join(ROOT, "hero-options", f"page-{x}.html").replace("\\", "/").replace(" ", "%20")
        await shoot(9800 + i, url, 1440, 950, os.path.join(OUT, f"page-{x}-desktop.png"), f"Page {x} desktop")
        await shoot(9810 + i, url, 390, 900, os.path.join(OUT, f"page-{x}-phone.png"), f"Page {x} phone")

asyncio.run(main())

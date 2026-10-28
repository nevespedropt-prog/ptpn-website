"""Find eyebrow type settings that actually RENDER dark enough.

Thin small type never reaches its specified colour: the strokes are narrower than
a pixel, so anti-aliasing blends every pixel toward the background. This renders
a row per candidate and measures the achieved contrast on cream.
"""
import asyncio, base64, io, json, os, subprocess, time, urllib.request, shutil, tempfile
from PIL import Image

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
ROOT = r"C:/Users/User/OneDrive/Desktop/PTPN website"
PORT = 9988
BONE = (241, 238, 230)
INK = "#3d2b08"

# (label, font-family, size, weight, letter-spacing)
CANDIDATES = [
    ("mono 12/500 .20em", "mono", 12, 500, ".20em"),
    ("mono 13/600 .16em", "mono", 13, 600, ".16em"),
    ("mono 14/600 .16em", "mono", 14, 600, ".16em"),
    ("sans 12/600 .18em", "sans", 12, 600, ".18em"),
    ("sans 13/700 .16em", "sans", 13, 700, ".16em"),
    ("sans 14/700 .14em", "sans", 14, 700, ".14em"),
    ("sans 13/600 .16em", "sans", 13, 600, ".16em"),
]

rows = "\n".join(
    f'<div class="row"><span class="eyebrow" data-i="{i}" '
    f'style="font-family:{ {"mono":"\'IBM Plex Mono\',monospace","sans":"\'Archivo\',sans-serif"}[f] };'
    f'font-size:{s}px;font-weight:{w};letter-spacing:{ls}">Personal training · Enfield</span></div>'
    for i, (_, f, s, w, ls) in enumerate(CANDIDATES)
)

HTML = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#f1eee6;padding:0}}
.row{{height:46px;display:flex;align-items:center;padding-left:40px}}
.eyebrow{{text-transform:uppercase;color:{INK}}}
</style></head><body>{rows}</body></html>"""

async def run():
    import websockets
    path = os.path.join(tempfile.gettempdir(), "eyebrow-sweep.html")
    open(path, "w", encoding="utf-8").write(HTML)
    prof = os.path.join(tempfile.gettempdir(), "cr-sweep")
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
    async with websockets.connect(ws, max_size=90_000_000) as conn:
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
                   {"width": 900, "height": 46*len(CANDIDATES)+20, "deviceScaleFactor": DPR, "mobile": False}, sid)
        await send("Page.navigate", {"url": "file:///" + path.replace("\\", "/")}, sid)
        await asyncio.sleep(3.0)
        shot = await send("Page.captureScreenshot",
                          {"format": "png", "captureBeyondViewport": True,
                           "clip": {"x": 0, "y": 0, "width": 900, "height": 46*len(CANDIDATES), "scale": DPR}}, sid)
        im = Image.open(io.BytesIO(base64.b64decode(shot["result"]["data"]))).convert("L")
        print(f"\n=== deviceScaleFactor {DPR} ({'retina' if DPR==2 else 'standard 1x monitor'}) - {im.size} ===")
        print(f"{'candidate':<22} {'min':<6} {'p1':<6} {'contrast(min)':<14} verdict")
        print("-" * 68)
        for i, (label, *_rest) in enumerate(CANDIDATES):
            row = im.crop((0, i*46*DPR, 900*DPR, (i+1)*46*DPR))
            px = sorted(row.getdata())
            n = len(px)
            mn, p1 = px[0], px[n//100]
            bg = 241
            ratio = (bg + 5) / (mn + 5)
            v = "PASS" if ratio >= 4.5 else ("marginal" if ratio >= 3.5 else "FAILS")
            print(f"{label:<22} {mn:<6} {p1:<6} {ratio:<14.2f} {v}")
        await send("Browser.close", {})
    try: proc.wait(timeout=10)
    except Exception: proc.kill()

for DPR in (1, 2):
    asyncio.run(run())

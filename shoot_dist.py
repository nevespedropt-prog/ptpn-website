"""Verify the promoted (built) site renders: hero, pinned phone, overflow, images."""
import asyncio, base64, io, json, os, subprocess, time, urllib.request, shutil, tempfile
from PIL import Image, ImageDraw

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
OUT = r"C:/Users/User/OneDrive/Desktop/PTPN website/screenshots"
URL = "http://127.0.0.1:8098/"
PORT = 9977

async def run():
    import websockets
    prof = os.path.join(tempfile.gettempdir(), "cr-dist")
    shutil.rmtree(prof, ignore_errors=True)
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
                             f"--remote-debugging-port={PORT}", f"--user-data-dir={prof}", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ws = None
    for _ in range(80):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=1) as r:
                ws = json.load(r)["webSocketDebuggerUrl"]; break
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
        await send("Emulation.setDeviceMetricsOverride", {"width":1440,"height":900,"deviceScaleFactor":1,"mobile":False}, sid)
        await send("Page.navigate", {"url": URL}, sid)
        await asyncio.sleep(8)

        probe = await send("Runtime.evaluate", {"expression": """JSON.stringify((()=>{
          const imgs=[...document.images];
          const broken=imgs.filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.src.split('/').pop());
          const de=document.documentElement;
          const over=[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>de.clientWidth+2).slice(0,5).map(e=>e.tagName+'.'+(e.className||'').toString().slice(0,30));
          const css=!![...document.styleSheets].find(s=>s.href&&s.href.includes('_astro'));
          const fonts=getComputedStyle(document.querySelector('h1')).fontFamily;
          return {imgs:imgs.length,broken,sw:de.scrollWidth,cw:de.clientWidth,sh:de.scrollHeight,css,h2:!!document.querySelector('#app .phone'),faq:!!document.querySelector('#contact'),pk:!!document.querySelector('#packages'),ov:over,fonts};
        })())""", "returnByValue": True}, sid)
        print("desktop:", probe["result"]["result"]["value"])

        shot = await send("Page.captureScreenshot", {"format":"png"}, sid)
        open(f"{OUT}/dist-hero.png","wb").write(base64.b64decode(shot["result"]["data"]))
        await send("Runtime.evaluate", {"expression":"document.querySelector('#app').scrollIntoView();'ok'","returnByValue":True}, sid)
        await asyncio.sleep(2.5)
        shot = await send("Page.captureScreenshot", {"format":"png"}, sid)
        open(f"{OUT}/dist-app.png","wb").write(base64.b64decode(shot["result"]["data"]))
        await send("Runtime.evaluate", {"expression":"document.querySelector('#contact').scrollIntoView();'ok'","returnByValue":True}, sid)
        await asyncio.sleep(2)
        shot = await send("Page.captureScreenshot", {"format":"png"}, sid)
        open(f"{OUT}/dist-contact.png","wb").write(base64.b64decode(shot["result"]["data"]))

        # phone width
        await send("Emulation.setDeviceMetricsOverride", {"width":390,"height":844,"deviceScaleFactor":1,"mobile":True}, sid)
        await send("Runtime.evaluate", {"expression":"window.scrollTo(0,0);'ok'","returnByValue":True}, sid)
        await asyncio.sleep(2)
        probe = await send("Runtime.evaluate", {"expression":"""JSON.stringify({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth})""","returnByValue":True}, sid)
        print("phone 390:", probe["result"]["result"]["value"])
        shot = await send("Page.captureScreenshot", {"format":"png"}, sid)
        open(f"{OUT}/dist-phone.png","wb").write(base64.b64decode(shot["result"]["data"]))
        await send("Browser.close", {})
    try: proc.wait(timeout=10)
    except Exception: proc.kill()

    # contact sheet
    names = ["dist-hero.png","dist-app.png","dist-contact.png","dist-phone.png"]
    ims = [Image.open(f"{OUT}/{n}").convert("RGB") for n in names]
    tw = 620
    ths = [im.resize((tw, int(im.height*tw/im.width)), Image.LANCZOS) for im in ims]
    sheet = Image.new("RGB", (tw*2+24, max(t.height for t in ths[:2]) + max(t.height for t in ths[2:]) + 60), (10,10,11))
    dr = ImageDraw.Draw(sheet)
    pos = [(8,8),(tw+16,8),(8,ths[0].height+30),(tw+16,ths[0].height+30)]
    for n,t,(x,y) in zip(names,ths,pos):
        sheet.paste(t,(x,y)); dr.text((x,y-0),n,fill=(215,185,120))
    sheet.save(f"{OUT}/dist-sheet.png")
    print("-> dist-sheet.png", sheet.size)

asyncio.run(run())

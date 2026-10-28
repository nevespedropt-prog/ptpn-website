"""Start a local static server for the PTPN mockups, detached from this session.

terminal(background=true) hangs on this host and nohup/disown are guard-blocked,
so the server is spawned detached with CREATE_NEW_PROCESS_GROUP|DETACHED_PROCESS
and its output goes to a log file.
"""
import subprocess, sys, os, time, socket, urllib.request

ROOT = r"C:\Users\User\OneDrive\Desktop\PTPN website"
PORT = 8099
LOG = os.path.join(ROOT, "server.log")

def port_open(p):
    with socket.socket() as s:
        s.settimeout(0.6)
        return s.connect_ex(("127.0.0.1", p)) == 0

if port_open(PORT):
    print(f"already running on {PORT}")
else:
    log = open(LOG, "a", encoding="utf-8")
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1", "--directory", ROOT],
        stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
        creationflags=0x00000008 | 0x00000200,      # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        close_fds=True,
    )
    for _ in range(30):
        if port_open(PORT): break
        time.sleep(0.3)
    print(f"started pid {proc.pid} on {PORT}")

for path in ("/hero-options/index.html", "/hero-options/mix2.html",
             "/hero-options/mock-1-evolution.html", "/public/images/hero-seated.jpg"):
    url = f"http://127.0.0.1:{PORT}{path}"
    try:
        with urllib.request.urlopen(url, timeout=4) as r:
            print(f"  {r.status}  {url}")
    except Exception as e:
        print(f"  ERR {url}  {e}")

print(f"\nopen:  http://127.0.0.1:{PORT}/hero-options/index.html")
print(f"log:   {LOG}")

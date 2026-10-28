import glob, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

SEL = [
    ("<option>30 minutes · 12 sessions · £32.50 each</option>", "<option>Express · twelve 30-minute sessions · £32.50 each</option>"),
    ("<option>One hour · 4 sessions · £54 each</option>", "<option>Ignition · four one-hour sessions · £54 each</option>"),
    ("<option>One hour · 8 sessions · £48 each</option>", "<option>Momentum · eight one-hour sessions · £48 each</option>"),
    ("<option>One hour · 12 sessions · £40 each</option>", "<option>Signature · twelve one-hour sessions · £40 each</option>"),
    ("<option>Small group · £60 per month</option>", "<option>Duo · small group · £60 per month</option>"),
]

FAQ_SHORT = ("Packages start at £32.50 a session for a twelve-session 30-minute pack. Full-hour packs are £54 a session for four sessions, £48 for eight, and £40 for twelve. Small group training is £60 a month for a minimum of two people training at least once a week.",
             "Packages start at £32.50 a session for Express, a twelve-session 30-minute pack. The one-hour packs are Ignition at £54 a session for four sessions, Momentum at £48 for eight, and Signature at £40 for twelve. Duo, the small group option, is £60 a month for a minimum of two people training at least once a week.")

FAQ_LONG = ("Packages start at £32.50 a session for a twelve-session 30-minute pack. Full-hour packs are £54 a session for four sessions, £48 for eight, and £40 for twelve. Small group training is £60 a month for a minimum of two people training at least once a week. All prices are per session and paid in person.",
            "Packages start at £32.50 a session for Express, a twelve-session 30-minute pack. The one-hour packs are Ignition at £54 a session for four sessions, Momentum at £48 for eight, and Signature at £40 for twelve. Duo, the small group option, is £60 a month for a minimum of two people training at least once a week. All prices are per session and paid in person.")

FAQ = [FAQ_SHORT, FAQ_LONG]

def edit(path, pairs, css=None, css_anchor=None):
    s = open(path, encoding="utf-8").read()
    missing = []
    for old, new in pairs:
        if old not in s:
            missing.append(old[:60])
            continue
        s = s.replace(old, new)
    if css and css_anchor and css not in s:
        s = s.replace(css_anchor, css_anchor + css, 1)
    open(path, "w", encoding="utf-8").write(s)
    print(("OK   " if not missing else "MISS "), path, ("| MISSING: " + str(missing) if missing else ""))

# 001 cinematic
edit("sketches/001-cinematic/index.html", SEL + FAQ + [
    ('<span class="len">30 minutes</span>', '<span class="len">Express</span>'),
    ('<div class="total">12 sessions · £390 total</div>', '<div class="total">Twelve 30-minute sessions · £390 total</div>'),
    ('<span class="len">One hour · 4 sessions</span>', '<span class="len">Ignition</span>'),
    ('<div class="total">4 sessions · £216 total</div>', '<div class="total">Four one-hour sessions · £216 total</div>'),
    ('<span class="len">One hour · 12 sessions</span>', '<span class="len">Signature</span>'),
    ('<div class="total">12 sessions · £480 total</div>', '<div class="total">Twelve one-hour sessions · £480 total</div>'),
    ('<span class="len">One hour · 8 sessions</span>', '<span class="len">Momentum</span>'),
    ('<div class="total">8 sessions · £384 total</div>', '<div class="total">Eight one-hour sessions · £384 total</div>'),
    ('<b>Small group personal training</b>', '<b>Duo · small group personal training</b>'),
])

# 002 data
edit("sketches/002-data/index.html", SEL + FAQ + [
    ('<th>30 minutes<br>12 sessions</th>', '<th>Express<br>12 × 30 min</th>'),
    ('<th>One hour<br>4 sessions</th>', '<th>Ignition<br>4 × 60 min</th>'),
    ('<th class="hl">One hour<br>12 sessions</th>', '<th class="hl">Signature<br>12 × 60 min</th>'),
    ('<th>One hour<br>8 sessions</th>', '<th>Momentum<br>8 × 60 min</th>'),
    ('Small group personal training is separate: £60 per month, minimum two people, minimum one session a week.',
     'Duo, the small group option, is separate: £60 per month, minimum two people, minimum one session a week.'),
])

# 003 flow
edit("sketches/003-flow/index.html", SEL + FAQ + [
    ('<div class="nm"><h3>30 minutes <span class="tag">Entry</span></h3><span>Twelve sessions</span></div>',
     '<div class="nm"><h3>Express <span class="tag">Entry</span></h3><span>Twelve 30-minute sessions</span></div>'),
    ('<div class="nm"><h3>One hour</h3><span>Four sessions</span></div>',
     '<div class="nm"><h3>Ignition</h3><span>Four one-hour sessions</span></div>'),
    ('<div class="nm"><h3>One hour</h3><span>Eight sessions</span></div>',
     '<div class="nm"><h3>Momentum</h3><span>Eight one-hour sessions</span></div>'),
    ('<div class="nm"><h3>One hour <span class="tag">Best value</span></h3><span>Twelve sessions</span></div>',
     '<div class="nm"><h3>Signature <span class="tag">Best value</span></h3><span>Twelve one-hour sessions</span></div>'),
    ('<div><h3>Small group personal training</h3>', '<div><h3>Duo · small group personal training</h3>'),
])

# 004 drift
edit("sketches/004-drift/index.html", SEL + FAQ + [
    ('<span class="tag">Entry</span><h3>30 minutes</h3><div class="pr">£32.50<small> / session</small></div><div class="tt">12 sessions · £390 total</div>',
     '<span class="tag">Entry</span><h3>Express</h3><div class="pr">£32.50<small> / session</small></div><div class="tt">Twelve 30-minute sessions · £390 total</div>'),
    ('<span class="tag">&nbsp;</span><h3>One hour</h3><div class="pr">£54<small> / session</small></div><div class="tt">4 sessions · £216 total</div>',
     '<span class="tag">&nbsp;</span><h3>Ignition</h3><div class="pr">£54<small> / session</small></div><div class="tt">Four one-hour sessions · £216 total</div>'),
    ('<span class="tag">Best value</span><h3>One hour</h3><div class="pr">£40<small> / session</small></div><div class="tt">12 sessions · £480 total</div>',
     '<span class="tag">Best value</span><h3>Signature</h3><div class="pr">£40<small> / session</small></div><div class="tt">Twelve one-hour sessions · £480 total</div>'),
    ('<span class="tag">&nbsp;</span><h3>One hour</h3><div class="pr">£48<small> / session</small></div><div class="tt">8 sessions · £384 total</div>',
     '<span class="tag">&nbsp;</span><h3>Momentum</h3><div class="pr">£48<small> / session</small></div><div class="tt">Eight one-hour sessions · £384 total</div>'),
    ('<div><h3>Small group personal training</h3>', '<div><h3>Duo · small group personal training</h3>'),
])

# 005 pulse
PNAME_CSS = "\n.pname{display:block;font-size:19px;font-weight:500;color:var(--gold-light);letter-spacing:-.025em;margin-bottom:5px}"
edit("sketches/005-pulse/index.html", SEL + FAQ + [
    ('<span class="len">30 minutes · 12 sessions</span>', '<span class="pname">Express</span><span class="len">Twelve 30-minute sessions</span>'),
    ('<span class="len">One hour · 4 sessions</span>', '<span class="pname">Ignition</span><span class="len">Four one-hour sessions</span>'),
    ('<span class="len">One hour · 12 sessions</span>', '<span class="pname">Signature</span><span class="len">Twelve one-hour sessions</span>'),
    ('<span class="len">One hour · 8 sessions</span>', '<span class="pname">Momentum</span><span class="len">Eight one-hour sessions</span>'),
    ('<div><h3>Small group personal training</h3>', '<div><h3>Duo · small group personal training</h3>'),
], css=PNAME_CSS, css_anchor=".pack .len{font-size:15px;color:var(--muted);font-weight:400}")

bad = {}
for f in glob.glob("sketches/*/index.html"):
    s = open(f, encoding="utf-8").read()
    hits = [o for o in ["30 minutes · 12 sessions", "One hour · 4 sessions", "One hour · 8 sessions",
                        "One hour · 12 sessions", "<h3>One hour", "<h3>30 minutes"] if o in s]
    if hits:
        bad[f] = hits
print("\nstale package wording remaining:", bad if bad else "NONE")
for n in ["Express", "Ignition", "Momentum", "Signature", "Duo"]:
    counts = {f.split(os.sep)[1]: open(f, encoding="utf-8").read().count(n) for f in sorted(glob.glob("sketches/*/index.html"))}
    print(f"{n:10}", counts)

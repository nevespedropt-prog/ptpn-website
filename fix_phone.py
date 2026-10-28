import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
F = "sketches/006-cinematic-data/index.html"
s = open(F, encoding="utf-8").read()
edits = []

def rep(old, new, label, count=1):
    global s
    got = s.count(old)
    assert got == count, f"{label}: expected {count} match(es), found {got}"
    s = s.replace(old, new)
    edits.append(label)

# 1. burger must not shrink when the flex row is tight
rep(".links{display:none}.burger{display:block}",
    ".links{display:none}.burger{display:block;flex:0 0 46px}",
    "burger flex-shrink guard")

# 2. phone nav: drop the long CTA + login link, they live in the hero and footer
rep("@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}",
    """@media(max-width:700px){
  .navcta{display:none}
  nav{height:74px}
  nav img{width:142px}
}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}""",
    "phone nav rules")

# 3. phone pricing: stacked cards instead of a sideways-scrolling table
rep("""@media(max-width:640px){
  .case,.meas,.steps,.trans,.posts,.fgrid,.f2,.tiles{grid-template-columns:1fr}
  .proof-grid{grid-template-columns:1fr}
  .proof-grid div{border-right:0}
  section{padding:72px 0}
  .quote-stage{padding:34px 26px}
  .phones{flex-direction:column;align-items:center}
}""",
    """.packcards{display:none}
@media(max-width:640px){
  .case,.meas,.steps,.trans,.posts,.fgrid,.f2,.tiles{grid-template-columns:1fr}
  .proof-grid{grid-template-columns:1fr}
  .proof-grid div{border-right:0}
  section{padding:72px 0}
  .quote-stage{padding:34px 26px}
  .phones{flex-direction:column;align-items:center}
  .tblwrap{display:none}
  .packcards{display:grid;gap:14px}
  .pcard{background:var(--card);border:1px solid var(--line);padding:26px 22px}
  .pcard.best{border-color:var(--gold-deep);background:linear-gradient(180deg,#1f1d18,#1b1b1c)}
  .pcard .nm2{font-family:var(--display);font-size:21px;font-weight:800;color:var(--gold-light);letter-spacing:-.02em}
  .pcard.best .nm2{color:var(--gold)}
  .pcard .len2{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
  .pcard .pr2{font-family:var(--mono);font-size:30px;color:var(--gold);margin:12px 0 2px;letter-spacing:-.02em}
  .pcard .pr2 small{font-size:12px;color:var(--muted)}
  .pcard .tt2{font-family:var(--mono);font-size:11.5px;color:var(--muted);padding-bottom:16px;border-bottom:1px solid var(--line);margin-bottom:16px}
  .pcard ul{list-style:none;display:grid;gap:9px;margin-bottom:20px}
  .pcard li{font-size:14.5px;color:#cdc8bf;padding-left:18px;position:relative}
  .pcard li::before{content:"";position:absolute;left:0;top:8px;width:8px;height:8px;border:1px solid var(--gold-deep);transform:rotate(45deg)}
  .pcard .btn{width:100%}
  .duo{padding:24px 22px;gap:18px}
  .duo .pr{margin-left:0}
}""",
    "phone pricing cards css")

# 4. the card markup itself, shown only on phones
CARDS = """    <div class="packcards">
      <div class="pcard">
        <span class="nm2">Express</span><span class="len2">Twelve 30-minute sessions</span>
        <div class="pr2">£32.50 <small>/ session</small></div>
        <div class="tt2">£390 total</div>
        <ul><li>Focused, high-density training</li><li>Full programme included</li><li>App access included</li></ul>
        <a href="#enquire" class="btn btn-ghost">Free consultation</a>
      </div>
      <div class="pcard">
        <span class="nm2">Ignition</span><span class="len2">Four one-hour sessions</span>
        <div class="pr2">£54 <small>/ session</small></div>
        <div class="tt2">£216 total</div>
        <ul><li>Ideal to trial coaching</li><li>Full programme included</li><li>App access included</li></ul>
        <a href="#enquire" class="btn btn-ghost">Free consultation</a>
      </div>
      <div class="pcard best">
        <span class="nm2">Signature</span><span class="len2">Twelve one-hour sessions</span>
        <div class="pr2">£40 <small>/ session</small></div>
        <div class="tt2">£480 total</div>
        <ul><li>Lowest per-session rate</li><li>Full programme included</li><li>App access included</li></ul>
        <a href="#enquire" class="btn btn-primary">Free consultation</a>
      </div>
      <div class="pcard">
        <span class="nm2">Momentum</span><span class="len2">Eight one-hour sessions</span>
        <div class="pr2">£48 <small>/ session</small></div>
        <div class="tt2">£384 total</div>
        <ul><li>Committed but flexible</li><li>Full programme included</li><li>App access included</li></ul>
        <a href="#enquire" class="btn btn-ghost">Free consultation</a>
      </div>
    </div>
"""
rep('    <div class="duo">', CARDS + '    <div class="duo">', "phone pricing cards markup")

open(F, "w", encoding="utf-8").write(s)
print("applied:", edits)
print("file size:", len(s), "bytes")

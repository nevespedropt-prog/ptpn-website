import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
F = "sketches/006-cinematic-data/index.html"
s = open(F, encoding="utf-8").read()

OLD = """.packcards{display:none}
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
}"""

NEW = """.packcards{display:none}
.pcard{background:var(--card);border:1px solid var(--line);padding:26px 22px}
.pcard.best{border-color:var(--gold-deep);background:linear-gradient(180deg,#1f1d18,#1b1b1c)}
.pcard .nm2{font-family:var(--display);font-size:21px;font-weight:800;color:var(--gold-light);letter-spacing:-.02em;display:block}
.pcard.best .nm2{color:var(--gold)}
.pcard .len2{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.pcard .pr2{font-family:var(--mono);font-size:30px;color:var(--gold);margin:12px 0 2px;letter-spacing:-.02em}
.pcard .pr2 small{font-size:12px;color:var(--muted)}
.pcard .tt2{font-family:var(--mono);font-size:11.5px;color:var(--muted);padding-bottom:16px;border-bottom:1px solid var(--line);margin-bottom:16px}
.pcard ul{list-style:none;display:grid;gap:9px;margin-bottom:20px}
.pcard li{font-size:14.5px;color:#cdc8bf;padding-left:18px;position:relative}
.pcard li::before{content:"";position:absolute;left:0;top:8px;width:8px;height:8px;border:1px solid var(--gold-deep);transform:rotate(45deg)}
.pcard .btn{width:100%}

/* below the comparison table's natural width, switch to stacked cards
   rather than making anyone scroll a pricing table sideways */
@media(max-width:880px){
  .tblwrap{display:none}
  .packcards{display:grid;gap:14px}
}
@media(max-width:640px){
  .case,.meas,.steps,.trans,.posts,.fgrid,.f2,.tiles{grid-template-columns:1fr}
  .proof-grid{grid-template-columns:1fr}
  .proof-grid div{border-right:0}
  section{padding:72px 0}
  .quote-stage{padding:34px 26px}
  .phones{flex-direction:column;align-items:center}
  .duo{padding:24px 22px;gap:18px}
  .duo .pr{margin-left:0}
}"""

assert s.count(OLD) == 1, f"anchor not found exactly once (found {s.count(OLD)})"
s = s.replace(OLD, NEW)
open(F, "w", encoding="utf-8").write(s)
print("refactored: pcard styles hoisted, table swap moved to 880px")

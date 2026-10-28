"""Recolour the three mockups from light/white to black + gold.

Colour values are injected via @TOKENS@ rather than %-formatting, because CSS is
full of literal % signs (height:100%, border-radius:50%) that break %-style
interpolation. Idempotent: re-running skips anything already applied.
"""
import os, sys

ROOT = "hero-options"
FAILS = []
GOLD, GOLD_LIGHT, GOLD_DEEP = "#d7b978", "#f1dda9", "#a67c2e"

def T(s):
    return s.replace("@G@", GOLD).replace("@GL@", GOLD_LIGHT).replace("@GD@", GOLD_DEEP)

def edit(path, pairs, label):
    p = os.path.join(ROOT, path)
    out = open(p, encoding="utf-8").read()
    applied = skipped = 0
    for old, new in pairs:
        old, new = T(old), T(new)
        if old in out:
            out = out.replace(old, new); applied += 1
        elif new in out:
            skipped += 1
        else:
            FAILS.append(f"{label}: NOT FOUND -> {old[:90]}")
    open(p, "w", encoding="utf-8").write(out)
    print(f"  {label}: {applied} applied, {skipped} already done, {len(pairs)} total")

# ================================================================ MOCK 1
edit("mock-1-evolution.html", [
    ("--paper:#ffffff; --ink:#000000; --ink-2:#1a1a1a; --muted:#6b6b6b; --rule:#e2e2e2;\n  --bone:#f6f5f2; --gold:#a67c2e;",
     "--paper:#08080a; --ink:#f4f1ea; --ink-2:#d9d5cc; --muted:#8d8d93; --rule:#1e1e22;\n  --bone:#0e0e11; --gold:@G@;"),
    ("header.solid{background:rgba(255,255,255,.94);backdrop-filter:blur(12px);border-bottom:1px solid var(--rule)}",
     "header.solid{background:rgba(8,8,10,.88);backdrop-filter:blur(14px);border-bottom:1px solid var(--rule)}"),
    ("header:not(.solid) .nav img{filter:invert(1) brightness(2)}", "header:not(.solid) .nav img{filter:none}"),
    ("background:var(--ink); color:#fff; border:1px solid var(--ink);",
     "background:@G@; color:#0b0a06; border:1px solid @G@;"),
    (".btn:hover{background:#fff;color:var(--ink)}", ".btn:hover{background:@GL@;border-color:@GL@}"),
    (".btn--ghost{background:transparent;color:var(--ink);border-color:var(--ink)}",
     ".btn--ghost{background:transparent;color:var(--ink);border-color:rgba(215,185,120,.45)}"),
    (".btn--ghost:hover{background:var(--ink);color:#fff}",
     ".btn--ghost:hover{background:@G@;color:#0b0a06;border-color:@G@}"),
    (".btn--light{background:#fff;color:var(--ink);border-color:#fff}",
     ".btn--light{background:@G@;color:#0b0a06;border-color:@G@}"),
    (".btn--light:hover{background:transparent;color:#fff;border-color:#fff}",
     ".btn--light:hover{background:transparent;color:@GL@;border-color:@GL@}"),
    ("background:linear-gradient(180deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,.12) 34%,rgba(0,0,0,.72) 100%)",
     "background:linear-gradient(180deg,rgba(5,5,6,.74) 0%,rgba(5,5,6,.30) 30%,rgba(5,5,6,.94) 100%)"),
    ("font-family:var(--serif);font-size:19px;font-weight:600;color:#c9c9c9;white-space:nowrap;",
     "font-family:var(--serif);font-size:19px;font-weight:600;color:rgba(215,185,120,.44);white-space:nowrap;"),
    ("padding:26px 0;overflow:hidden;background:var(--paper)}",
     "padding:26px 0;overflow:hidden;background:var(--bone)}"),
    (".method__row:hover{background:var(--bone);padding-left:20px}",
     ".method__row:hover{background:#101013;padding-left:20px}"),
    (".statement{position:relative;background:var(--ink);color:#fff;padding:150px 0;overflow:hidden}",
     ".statement{position:relative;background:#0c0c0f;color:#fff;padding:150px 0;overflow:hidden;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}"),
    ("footer{border-top:1px solid var(--rule);padding:64px 0 40px;background:var(--bone)}",
     "footer{border-top:1px solid var(--rule);padding:64px 0 40px;background:#0b0b0e}"),
], "Mock 1 Evolution")

# ================================================================ MOCK 2
edit("mock-2-momentum.html", [
    ("--paper:#ffffff; --ink:#1c2127; --ink-2:#3a4149; --muted:#7a828b;\n  --line:#e6e8eb; --soft:#f6f7f8; --mint:#dff3e6; --gold:#c8a24a;",
     "--paper:#08080a; --ink:#f4f1ea; --ink-2:#cfcbc2; --muted:#8d8d93;\n  --line:#1e1e22; --soft:#111114; --mint:#1a1f1a; --gold:@G@;"),
    ("header{position:sticky;top:0;z-index:60;background:rgba(255,255,255,.86);",
     "header{position:sticky;top:0;z-index:60;background:rgba(8,8,10,.86);"),
    ("  background:var(--ink);color:#fff;border:1px solid var(--ink);",
     "  background:@G@;color:#0b0a06;border:1px solid @G@;"),
    (".btn:hover{transform:translateY(-2px);box-shadow:0 14px 30px -12px rgba(28,33,39,.4)}",
     ".btn:hover{transform:translateY(-2px);box-shadow:0 14px 34px -12px rgba(215,185,120,.35);background:@GL@}"),
    (".btn--ghost{background:#fff;color:var(--ink);border-color:var(--line)}",
     ".btn--ghost{background:transparent;color:var(--ink);border-color:rgba(215,185,120,.4)}"),
    (".btn--ghost:hover{border-color:var(--ink)}", ".btn--ghost:hover{border-color:@G@;color:@GL@}"),
    ("background:radial-gradient(closest-side,rgba(200,162,74,.09),transparent 70%);pointer-events:none}",
     "background:radial-gradient(closest-side,rgba(215,185,120,.13),transparent 70%);pointer-events:none}"),
    ("background:linear-gradient(180deg,#2b3038,#14181d);\n  box-shadow:0 50px 90px -40px rgba(28,33,39,.5), 0 0 0 1px rgba(0,0,0,.25);",
     "background:linear-gradient(180deg,#26262c,#131316);\n  box-shadow:0 50px 100px -40px rgba(0,0,0,.95), 0 0 0 1px rgba(215,185,120,.16);"),
    (".screen{border-radius:34px;background:#fff;overflow:hidden;", ".screen{border-radius:34px;background:#0c0c0f;overflow:hidden;"),
    ("color:#2f7a4f;background:var(--mint);padding:5px 9px;border-radius:999px;text-transform:uppercase}",
     "color:#7fd39c;background:rgba(127,211,156,.1);padding:5px 9px;border-radius:999px;text-transform:uppercase}"),
    (".pilldot i{width:5px;height:5px;border-radius:50%;background:#2f7a4f;display:block}",
     ".pilldot i{width:5px;height:5px;border-radius:50%;background:#7fd39c;display:block}"),
    (".sidecard{width:270px;background:#fff;border:1px solid var(--line);border-radius:22px;padding:20px;\n  box-shadow:0 30px 60px -34px rgba(28,33,39,.34)}",
     ".sidecard{width:270px;background:#0e0e11;border:1px solid var(--line);border-radius:22px;padding:20px;\n  box-shadow:0 30px 70px -34px rgba(0,0,0,.9)}"),
    (".card{border:1px solid var(--line);border-radius:22px;padding:26px;background:#fff;",
     ".card{border:1px solid var(--line);border-radius:22px;padding:26px;background:#0c0c0f;"),
    (".card:hover{transform:translateY(-5px);box-shadow:0 26px 50px -30px rgba(28,33,39,.32);border-color:#d8dbe0}",
     ".card:hover{transform:translateY(-5px);box-shadow:0 26px 60px -30px rgba(0,0,0,.9);border-color:rgba(215,185,120,.4)}"),
    (".mini{margin-top:20px;border:1px solid var(--line);border-radius:16px;overflow:hidden;background:var(--soft)}",
     ".mini{margin-top:20px;border:1px solid var(--line);border-radius:16px;overflow:hidden;background:#0a0a0c}"),
    ("gap:6px;padding:9px 12px;background:#fff;border-bottom:1px solid var(--line)}",
     "gap:6px;padding:9px 12px;background:#111114;border-bottom:1px solid var(--line)}"),
    (".mini__bar i{width:7px;height:7px;border-radius:50%;background:#dfe2e6;display:block}",
     ".mini__bar i{width:7px;height:7px;border-radius:50%;background:#2a2a30;display:block}"),
    ("padding:7px 0;border-bottom:1px solid #eceef1}", "padding:7px 0;border-bottom:1px solid #1b1b1f}"),
    (".bars .b{height:7px;border-radius:99px;background:var(--soft);overflow:hidden}",
     ".bars .b{height:7px;border-radius:99px;background:#1b1b20;overflow:hidden}"),
    ("background:linear-gradient(90deg,#c8a24a,#e6cf94);", "background:linear-gradient(90deg,@GD@,@GL@);"),
    ("border-radius:50%;background:var(--mint);color:#2f7a4f;",
     "border-radius:50%;background:rgba(215,185,120,.14);color:@G@;"),
    (".quote{border:1px solid var(--line);border-radius:22px;padding:28px;display:flex;flex-direction:column;background:#fff}",
     ".quote{border:1px solid var(--line);border-radius:22px;padding:28px;display:flex;flex-direction:column;background:#0c0c0f}"),
    ("border-radius:50%;background:var(--soft);display:block;flex:0 0 34px}",
     "border-radius:50%;background:linear-gradient(140deg,@GD@,@GL@);display:block;flex:0 0 34px}"),
    (".band{background:var(--soft);border-top:1px solid var(--line);",
     ".band{background:#0a0a0c;border-top:1px solid var(--line);"),
    (".chat{margin-top:14px;background:var(--soft);border-radius:14px;",
     ".chat{margin-top:14px;background:#111114;border:1px solid var(--line);border-radius:14px;"),
], "Mock 2 Momentum")

# ================================================================ MOCK 3
edit("mock-3-system.html", [
    ("--paper:#ffffff; --ink:#333333; --ink-2:#1f1f1f; --muted:#6b7280;\n  --navy:#0b345d; --yellow:#ffed42; --yellow-deep:#f2dd1a;\n  --line:#e5e7eb; --soft:#fafafa;",
     "--paper:#08080a; --ink:#d9d5cc; --ink-2:#f4f1ea; --muted:#8d8d93;\n  --navy:@G@; --yellow:@G@; --yellow-deep:@GL@;\n  --line:#1e1e22; --soft:#0e0e11;"),
    ("background:var(--yellow);color:var(--navy);border:0;cursor:pointer;",
     "background:@G@;color:#0b0a06;border:0;cursor:pointer;"),
    (".btn:hover{background:var(--yellow-deep);transform:translateY(-2px);box-shadow:0 12px 26px -12px rgba(11,52,93,.4)}",
     ".btn:hover{background:@GL@;transform:translateY(-2px);box-shadow:0 12px 30px -12px rgba(215,185,120,.4)}"),
    (".btn--navy{background:var(--navy);color:#fff}",
     ".btn--navy{background:transparent;color:var(--ink);border:1px solid rgba(215,185,120,.45)}"),
    (".btn--navy:hover{background:#082848;box-shadow:0 12px 26px -12px rgba(11,52,93,.5)}",
     ".btn--navy:hover{background:rgba(215,185,120,.1);border-color:@G@;color:@GL@;box-shadow:none}"),
    ("header{position:sticky;top:0;z-index:60;background:rgba(255,255,255,.95);backdrop-filter:blur(10px);",
     "header{position:sticky;top:0;z-index:60;background:rgba(8,8,10,.9);backdrop-filter:blur(12px);"),
    (".nav ul a:hover{color:var(--navy)}", ".nav ul a:hover{color:@G@}"),
    (".progress{position:fixed;top:0;left:0;height:3px;background:var(--yellow);",
     ".progress{position:fixed;top:0;left:0;height:3px;background:linear-gradient(90deg,@GD@,@GL@);"),
    ("background:var(--soft);font-family:var(--display);font-size:21px;font-weight:500;",
     "background:#0e0e11;font-family:var(--display);font-size:21px;font-weight:500;"),
    ("padding:26px 30px;border-left:4px solid var(--yellow);", "padding:26px 30px;border-left:4px solid @G@;"),
    (".compare .col-good{background:#fffdf0}", ".compare .col-good{background:rgba(215,185,120,.07)}"),
    (".compare .col-good strong{display:block;font-family:var(--display);font-weight:700;color:var(--navy);",
     ".compare .col-good strong{display:block;font-family:var(--display);font-weight:700;color:@GL@;"),
    (".compare .x{color:#c2410c;font-weight:500}", ".compare .x{color:#b06a4a;font-weight:500}"),
    (".compare .tick{color:#15803d;font-weight:500}", ".compare .tick{color:#7fb98c;font-weight:500}"),
    (".pillar{border:1px solid var(--line);border-radius:8px;padding:28px;background:#fff;",
     ".pillar{border:1px solid var(--line);border-radius:8px;padding:28px;background:#0c0c0f;"),
    (".pillar:hover{transform:translateY(-4px);box-shadow:0 22px 44px -26px rgba(11,52,93,.28)}",
     ".pillar:hover{transform:translateY(-4px);box-shadow:0 22px 50px -26px rgba(0,0,0,.9);border-color:rgba(215,185,120,.4)}"),
    ("letter-spacing:.18em;color:var(--navy);font-weight:500}", "letter-spacing:.18em;color:@G@;font-weight:500}"),
    (".proof{background:var(--navy);color:#fff;padding:80px 0}",
     ".proof{background:#0c0c0f;color:#fff;padding:80px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}"),
    (".quote{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.14);",
     ".quote{background:rgba(215,185,120,.05);border:1px solid rgba(215,185,120,.2);"),
    ("summary::after{content:\"+\";font-size:22px;color:var(--navy);", "summary::after{content:\"+\";font-size:22px;color:@G@;"),
    (".cta__box{border:1px solid var(--line);border-radius:8px;padding:32px;background:#fff}",
     ".cta__box{border:1px solid rgba(215,185,120,.24);border-radius:8px;padding:32px;background:#0c0c0f}"),
    ("border-radius:4px;background:var(--yellow);color:var(--navy);", "border-radius:4px;background:@G@;color:#0b0a06;"),
    ("border-radius:5px;font-family:var(--body);font-size:16px;margin-bottom:12px\"",
     "border-radius:5px;font-family:var(--body);font-size:16px;margin-bottom:12px;background:#111114;color:#f4f1ea\""),
    ("border-radius:5px;font-family:var(--body);font-size:16px;min-height:96px;resize:vertical\"",
     "border-radius:5px;font-family:var(--body);font-size:16px;min-height:96px;resize:vertical;background:#111114;color:#f4f1ea\""),
    (".sticky{position:fixed;left:0;right:0;bottom:0;z-index:70;background:rgba(255,255,255,.97);backdrop-filter:blur(12px);",
     ".sticky{position:fixed;left:0;right:0;bottom:0;z-index:70;background:rgba(8,8,10,.94);backdrop-filter:blur(14px);"),
], "Mock 3 System")

print()
if FAILS:
    print("!! UNMATCHED REPLACEMENTS:")
    for f in FAILS: print("   " + f)
    sys.exit(1)
print("all replacements matched")

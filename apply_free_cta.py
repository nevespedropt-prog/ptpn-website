import glob, os, re

os.chdir(os.path.dirname(os.path.abspath(__file__)))

FAQ_FREE = ('\n      <details><summary>Is the first session free?</summary><p>Yes. I offer a free consultation '
            'with no obligation. We talk through your goal, your training history and what has stopped you before, '
            'and you leave with a clear idea of what working together would look like. There is no charge and no '
            'pressure to book anything.</p></details>')

NAV_RE = re.compile(r'(<a href="#enquire" class="btn btn-primary" style="min-height:4[0-9]px;padding:0 2[0-9]px;font-size:1[0-9.]+px">)Enquire(</a>)')

total = 0
for f in sorted(glob.glob("sketches/*/index.html")):
    s = open(f, encoding="utf-8").read()
    before = s
    n = {}

    s, n["hero"] = re.subn(r'>Enquire about coaching<', '>Book a free consultation<', s)
    s, n["nav"] = NAV_RE.subn(r'\1Free consultation\2', s)
    s, n["notclient"] = re.subn(r'>Not a client yet\?<', '>Book a free consultation<', s)
    s, n["faq"] = re.subn(r'</details>', '</details>' + FAQ_FREE, s, count=1)

    # enquiry form intro mentions the free consultation
    s, n["enq"] = re.subn(
        r'Answer a few questions and I will come back to you with the package that fits and the next available session\.',
        'Answer a few questions and I will come back to arrange your free consultation and suggest the package that fits.',
        s)
    s, n["enq2"] = re.subn(
        r'Answer a few questions and I will come back with the package that fits\.',
        'Answer a few questions and I will come back to arrange your free consultation.',
        s)

    # 006 proof bar: swap one stat for the free consultation
    s, n["proof"] = re.subn(
        r'<div><b>1-2-1</b><span>Private coaching</span></div>',
        '<div><b>Free</b><span>First consultation</span></div>', s)

    open(f, "w", encoding="utf-8").write(s)
    total += 1
    print(f"{os.path.basename(os.path.dirname(f)):20}", {k: v for k, v in n.items() if v})

print("\nfiles touched:", total)
print("\n--- leftovers check ---")
for f in sorted(glob.glob("sketches/*/index.html")):
    s = open(f, encoding="utf-8").read()
    left = []
    if "Enquire about coaching" in s:
        left.append("hero CTA")
    if ">Not a client yet?<" in s:
        left.append("not-a-client CTA")
    print(f"{os.path.basename(os.path.dirname(f)):20}", left if left else "clean")

print("\n--- 006 CTA inventory ---")
s = open("sketches/006-cinematic-data/index.html", encoding="utf-8").read()
for m in re.finditer(r'>([^<>]{3,40})</a>', s):
    t = m.group(1).strip()
    if t and not t.startswith("http") and len(t) < 40 and "\n" not in t:
        print("  ", t)
print("\nfree-consultation mentions in 006:", s.lower().count("free consultation"))

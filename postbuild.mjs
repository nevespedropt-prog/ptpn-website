// postbuild: rewrite root-absolute internal URLs to relative, per page depth.
// Lets one build work at BOTH a domain root (www.ptpn.co.uk) and the GitHub
// Pages subpath (/ptpn-website/) — without site/path coupling.
import { readdirSync, readFileSync, writeFileSync, statSync } from 'node:fs';
import path from 'node:path';

const DIST = 'dist';
const INTERNAL = /^(\/_astro\/|\/brand\/|\/images\/|\/blog\/|\/fonts\/)/;

function htmlFiles(dir) {
  const out = [];
  for (const e of readdirSync(dir)) {
    const p = path.join(dir, e);
    if (statSync(p).isDirectory()) out.push(...htmlFiles(p));
    else if (e.endsWith('.html')) out.push(p);
  }
  return out;
}

let changed = 0;
for (const f of htmlFiles(DIST)) {
  let relDir = path.dirname(path.relative(DIST, f));
  if (relDir === '.') relDir = '';
  const depth = relDir === '' ? 0 : relDir.split(path.sep).length;
  const up = '../'.repeat(depth) || './';
  let s = readFileSync(f, 'utf8');
  const before = s;
  s = s.replace(/(src|href)="(\/(?:_astro|brand|images|blog|fonts)\/[^"]*)"/g,
    (_, attr, target) => `${attr}="${(depth ? up : './') + target.slice(1)}"`);
  // canonical/og keep absolute domain URLs; do not touch
  if (s !== before) { writeFileSync(f, s); changed++; }
}
console.log(`postbuild: relativized internal URLs in ${changed} html files`);

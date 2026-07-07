#!/usr/bin/env python3
"""Apply the canonical mega-menu <header> to every page, so nav is edited in ONE place.
Run from the website/ root:  python3 scripts/apply-header.py
Also converts the homepage from inline <style> to the shared stylesheet.
"""
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

CANON_HEADER = '''<header class="site-header">
    <div class="wrap header-inner">
      <a href="/" class="brand" aria-label="Southern Perfection Fabrication — home"><span class="brand-mark" aria-hidden="true"></span><span class="brand-text">SOUTHERN&nbsp;PERFECTION</span></a>
      <nav class="nav" aria-label="Primary"><details class="nav-disclosure"><summary aria-label="Menu">Menu</summary>
        <ul class="mega">
          <li class="mega-item"><span class="mega-top">What We Build</span>
            <ul class="mega-panel">
              <li><a href="/returnable-steel-racks/">Returnable Steel Racks</a></li>
              <li><a href="/dunnage/">Dunnage &amp; Foam Inserts</a></li>
              <li><a href="/wip-carts/">WIP Carts &amp; Dollies</a></li>
              <li><a href="/rack-repair-refurbishment/">Rack Repair &amp; Refurbishment</a></li>
            </ul>
          </li>
          <li class="mega-item"><a class="mega-top" href="/industries/">Industries</a>
            <ul class="mega-panel">
              <li><a href="/industries/automotive/">Automotive OEM &amp; Tier-1</a></li>
              <li><a href="/industries/aerospace-defense/">Aerospace &amp; Defense</a></li>
              <li><a href="/industries/ev-battery/">EV / Battery</a></li>
              <li><a href="/industries/heavy-equipment/">Heavy Equipment &amp; Ag</a></li>
              <li><a href="/industries/">General Industrial</a></li>
              <li><a href="/industries/">View all industries &rarr;</a></li>
            </ul>
          </li>
          <li class="mega-item"><a class="mega-top" href="/capabilities/">Capabilities</a>
            <ul class="mega-panel">
              <li><a href="/capabilities/">Contract Metal Fabrication</a></li>
              <li><a href="/capabilities/">Quality &mdash; ISO 9001 / CAGE</a></li>
              <li><a href="/capabilities/">Design &amp; Engineering</a></li>
            </ul>
          </li>
          <li class="mega-item"><a class="mega-top" href="/managed-programs/">Managed Programs</a></li>
          <li class="mega-item"><span class="mega-top">Company</span>
            <ul class="mega-panel">
              <li><a href="/about/">About</a></li>
              <li><a href="/contact/">Contact</a></li>
            </ul>
          </li>
        </ul>
      </details></nav>
      <div class="header-cta"><a href="tel:+14789564442" class="phone">478-956-4442</a><a href="/#rfq" class="btn btn-spark">Start an RFQ</a></div>
    </div>
  </header>'''

header_re = re.compile(r'<header class="site-header">.*?</header>', re.DOTALL)
style_re  = re.compile(r'<!-- CSS inlined.*?-->\s*', re.DOTALL)
style_block_re = re.compile(r'<style>.*?</style>', re.DOTALL)

changed = []
for f in ROOT.rglob('*.html'):
    if 'docs' in f.parts:
        continue
    html = f.read_text()
    new = header_re.sub(lambda m: CANON_HEADER, html, count=1)
    if f.name == 'index.html' and f.parent == ROOT:
        new = style_re.sub('', new)
        new = style_block_re.sub('<link rel="stylesheet" href="/assets/styles.css">', new, count=1)
    if new != html:
        f.write_text(new)
        changed.append(str(f.relative_to(ROOT)))

print(f"Updated {len(changed)} files:")
for c in sorted(changed):
    print(" -", c)

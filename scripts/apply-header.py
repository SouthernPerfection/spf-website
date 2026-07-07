#!/usr/bin/env python3
"""Apply the canonical grouped mega-menu <header> to every page — nav edited in ONE place.
Run from website/ root:  python3 scripts/apply-header.py
Also converts the homepage from inline <style> to the shared stylesheet.
"""
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

CANON_HEADER = '''<header class="site-header">
    <div class="wrap header-inner">
      <a href="/" class="brand" aria-label="Southern Perfection Fabrication — home"><span class="brand-mark" aria-hidden="true"></span><span class="brand-text">SOUTHERN&nbsp;PERFECTION</span></a>
      <nav class="nav" aria-label="Primary">
        <input type="checkbox" id="nav-toggle" class="nav-cb" aria-hidden="true" tabindex="-1">
        <label for="nav-toggle" class="nav-burger">Menu</label>
        <ul class="mega">
          <li class="mega-item"><span class="mega-top">What We Build</span>
            <div class="mega-panel"><div class="mega-cols">
              <div class="mega-col"><p class="mega-h">Returnable Racks</p><ul>
                <li><a href="/returnable-steel-racks/">Returnable Steel Racks</a></li>
                <li><a href="/engine-racks/">Engine Racks</a></li>
                <li><a href="/bumper-racks/">Bumper Racks</a></li>
                <li><a href="/coil-racks/">Coil Racks</a></li>
                <li><a href="/tire-racks/">Tire Racks</a></li>
              </ul></div>
              <div class="mega-col"><p class="mega-h">Containers &amp; Pallets</p><ul>
                <li><a href="/returnable-containers/">Returnable Steel Containers</a></li>
                <li><a href="/steel-pallets/">Steel Pallets</a></li>
                <li><a href="/wip-carts/">WIP Carts &amp; Dollies</a></li>
              </ul></div>
              <div class="mega-col"><p class="mega-h">Dunnage &amp; Service</p><ul>
                <li><a href="/dunnage/">Dunnage</a></li>
                <li><a href="/custom-foam-inserts/">Custom Foam Inserts</a></li>
                <li><a href="/rack-repair-refurbishment/">Rack Repair &amp; Refurb</a></li>
              </ul></div>
            </div></div>
          </li>
          <li class="mega-item"><a class="mega-top" href="/industries/">Industries</a>
            <div class="mega-panel"><div class="mega-cols">
              <div class="mega-col"><p class="mega-h">Who We Serve</p><ul>
                <li><a href="/industries/automotive/">Automotive OEM &amp; Tier-1</a></li>
                <li><a href="/industries/aerospace-defense/">Aerospace &amp; Defense</a></li>
                <li><a href="/industries/ev-battery/">EV / Battery</a></li>
                <li><a href="/industries/heavy-equipment/">Heavy Equipment &amp; Ag</a></li>
                <li><a href="/industries/general-industrial/">General Industrial</a></li>
                <li><a href="/industries/">View all industries &rarr;</a></li>
              </ul></div>
            </div></div>
          </li>
          <li class="mega-item"><a class="mega-top" href="/capabilities/">Capabilities</a>
            <div class="mega-panel"><div class="mega-cols">
              <div class="mega-col"><p class="mega-h">Fabrication</p><ul>
                <li><a href="/capabilities/design-engineering/">Design &amp; Engineering</a></li>
                <li><a href="/capabilities/laser-cutting/">Laser Cutting</a></li>
                <li><a href="/capabilities/robotic-welding/">Robotic Welding</a></li>
                <li><a href="/capabilities/cnc-machining/">CNC Machining</a></li>
              </ul></div>
              <div class="mega-col"><p class="mega-h">Finishing &amp; Quality</p><ul>
                <li><a href="/capabilities/forming/">Forming</a></li>
                <li><a href="/capabilities/powder-coating/">Powder Coating</a></li>
                <li><a href="/capabilities/quality-inspection/">CMM Inspection &amp; Quality</a></li>
                <li><a href="/capabilities/">All Capabilities &rarr;</a></li>
              </ul></div>
            </div></div>
          </li>
          <li class="mega-item"><a class="mega-top" href="/managed-programs/">Managed Programs</a></li>
          <li class="mega-item"><span class="mega-top">Resources</span>
            <div class="mega-panel"><div class="mega-cols">
              <div class="mega-col"><ul>
                <li><a href="/case-studies/">Case Studies</a></li>
                <li><a href="/returnable-vs-expendable-packaging/">Returnable vs. Expendable</a></li>
              </ul></div>
            </div></div>
          </li>
          <li class="mega-item"><span class="mega-top">Company</span>
            <div class="mega-panel"><div class="mega-cols">
              <div class="mega-col"><ul>
                <li><a href="/about/">About</a></li>
                <li><a href="/contact/">Contact</a></li>
              </ul></div>
            </div></div>
          </li>
        </ul>
      </nav>
      <div class="header-cta"><a href="tel:+14789564442" class="phone">478-956-4442</a><a href="/#rfq" class="btn btn-spark">Start an RFQ</a></div>
    </div>
  </header>'''

header_re = re.compile(r'<header class="site-header"[^>]*>.*?</header>', re.DOTALL)
style_comment_re = re.compile(r'<!-- CSS inlined.*?-->\s*', re.DOTALL)
style_block_re = re.compile(r'<style>.*?</style>', re.DOTALL)

changed = []
for f in ROOT.rglob('*.html'):
    if 'docs' in f.parts:
        continue
    html = f.read_text()
    new = header_re.sub(lambda m: CANON_HEADER, html, count=1)
    if f.name == 'index.html' and f.parent == ROOT:
        new = style_comment_re.sub('', new)
        new = new.replace('<style>', '<link rel="stylesheet" href="/assets/styles.css"><style>', 1) if '<style>' in new and 'assets/styles.css' not in new else new
        new = style_block_re.sub('', new, count=1) if '<style>' in new else new
    if new != html:
        f.write_text(new)
        changed.append(str(f.relative_to(ROOT)))

print(f"Updated {len(changed)} files:")
for c in sorted(changed):
    print(" -", c)

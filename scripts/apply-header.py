#!/usr/bin/env python3
"""Apply the canonical grouped mega-menu <header> to every page — nav edited in ONE place.
Run from website/ root:  python3 scripts/apply-header.py
Also converts the homepage from inline <style> to the shared stylesheet.
"""
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

CANON_HEADER = '''<header class="site-header">
    <div class="wrap header-inner">
      <a href="/" class="brand" aria-label="Southern Perfection Fabrication — home"><img src="/assets/logo.png" alt="Southern Perfection Fabrication" class="brand-logo" width="102" height="42"></a>
      <nav class="nav" aria-label="Primary">
        <input type="checkbox" id="nav-toggle" class="nav-cb" aria-hidden="true" tabindex="-1">
        <label for="nav-toggle" class="nav-burger">Menu</label>
        <ul class="mega">
          <li class="mega-item"><span class="mega-top">What We Build</span>
            <div class="mega-panel"><div class="mega-cols">
              <div class="mega-col"><p class="mega-h">Returnable Packaging</p><ul>
                <li><a href="/automotive-racks/">Automotive Racks</a></li>
                <li><a href="/stack-racks/">Stack Racks</a></li>
                <li><a href="/steel-pallets/">Steel Pallets</a></li>
                <li><a href="/returnable-containers/">Industrial Metal Containers</a></li>
              </ul></div>
              <div class="mega-col"><p class="mega-h">Material Handling</p><ul>
                <li><a href="/industrial-carts/">Industrial Carts</a></li>
                <li><a href="/industrial-dollies/">Industrial Dollies</a></li>
                <li><a href="/kanban-flow-racks/">Kanban Flow Racks</a></li>
                <li><a href="/steel-cable-reels/">Steel Cable Reels</a></li>
              </ul></div>
              <div class="mega-col"><p class="mega-h">Custom &amp; Service</p><ul>
                <li><a href="/weldments-frames/">Weldments &amp; Frames</a></li>
                <li><a href="/guards-platforms/">Guards &amp; Platforms</a></li>
                <li><a href="/dunnage/">Dunnage</a></li>
                <li><a href="/custom-foam-inserts/">Custom Foam Inserts</a></li>
                <li><a href="/rack-repair-refurbishment/">Rack Repair &amp; Refurb</a></li>
              </ul></div>
              <div class="mega-col"><p class="mega-h">Custom Manufacturing</p><ul>
                <li><a href="/capabilities/">Contract Manufacturing</a></li>
                <li><a href="/industrial-structures/">Industrial Structures</a></li>
                <li><a href="/high-volume-manufacturing/">High-Volume</a></li>
                <li><a href="/guards-platforms/">Machine Guards</a></li>
                <li><a href="/sheet-metal-fabrication/">Sheet Metal</a></li>
                <li><a href="/capabilities/laser-cutting/">Laser Cutting</a></li>
              </ul></div>
            </div></div>
          </li>
          <li class="mega-item"><a class="mega-top" href="/industries/">Industries</a>
            <div class="mega-panel"><div class="mega-cols">
              <div class="mega-col"><p class="mega-h">Transportation &amp; Mobility</p><ul>
                <li><a href="/industries/automotive/">Automotive OEM &amp; Tier-1</a></li>
                <li><a href="/industries/ev-battery/">EV / Battery</a></li>
                <li><a href="/industries/aerospace-defense/">Aerospace &amp; Defense</a></li>
                <li><a href="/industries/transportation-trailer/">Transportation &amp; Trailer</a></li>
              </ul></div>
              <div class="mega-col"><p class="mega-h">Heavy &amp; Process</p><ul>
                <li><a href="/industries/heavy-equipment/">Heavy Equipment &amp; Off-Highway</a></li>
                <li><a href="/industries/mining-aggregate/">Mining &amp; Aggregate</a></li>
                <li><a href="/industries/chemical-processing/">Chemical Processing</a></li>
                <li><a href="/industries/energy-power/">Energy &amp; Power Generation</a></li>
              </ul></div>
              <div class="mega-col"><p class="mega-h">Distribution &amp; Consumer</p><ul>
                <li><a href="/industries/food-beverage-dairy/">Food, Beverage &amp; Dairy</a></li>
                <li><a href="/industries/packaging-paper/">Packaging &amp; Paper</a></li>
                <li><a href="/industries/distribution-logistics/">Distribution &amp; Logistics</a></li>
                <li><a href="/industries/industrial-machinery/">Industrial Machinery &amp; OEM</a></li>
                <li><a href="/industries/general-industrial/">General Manufacturing</a></li>
              </ul></div>
            </div></div>
          </li>
          <li class="mega-item"><a class="mega-top" href="/capabilities/">Capabilities</a>
            <div class="mega-panel"><div class="mega-cols">
              <div class="mega-col"><p class="mega-h">Cut &amp; Form</p><ul>
                <li><a class="mega-cap" href="/capabilities/laser-cutting/"><strong>Laser &amp; Plasma Cutting</strong><span class="mega-desc">Clean, precise, repeatable parts</span></a></li>
                <li><a class="mega-cap" href="/capabilities/forming/"><strong>CNC Forming &amp; Bending</strong><span class="mega-desc">Press brake to 230 tons</span></a></li>
                <li><a class="mega-cap" href="/capabilities/cnc-machining/"><strong>CNC Machining</strong><span class="mega-desc">Turning + milling</span></a></li>
              </ul></div>
              <div class="mega-col"><p class="mega-h">Weld &amp; Finish</p><ul>
                <li><a class="mega-cap" href="/capabilities/robotic-welding/"><strong>Welding</strong><span class="mega-desc">30+ MIG stations &middot; FANUC robotic</span></a></li>
                <li><a class="mega-cap" href="/capabilities/powder-coating/"><strong>Finishing</strong><span class="mega-desc">Wet paint + powder coat</span></a></li>
                <li><a class="mega-cap" href="/capabilities/design-engineering/"><strong>Design &amp; Engineering</strong><span class="mega-desc">In-house SolidWorks</span></a></li>
              </ul></div>
              <div class="mega-col"><p class="mega-h">Quality</p><ul>
                <li><a class="mega-cap" href="/capabilities/quality-inspection/"><strong>Quality &amp; Inspection</strong><span class="mega-desc">ISO 9001 &middot; CAGE &middot; CMM</span></a></li>
                <li><a class="mega-cap" href="/capabilities/"><strong>All Capabilities &rarr;</strong><span class="mega-desc">The full one-roof shop</span></a></li>
              </ul></div>
            </div></div>
          </li>
          <li class="mega-item"><a class="mega-top" href="/managed-programs/">Managed Programs</a></li>
          <li class="mega-item"><span class="mega-top">Resources</span>
            <div class="mega-panel"><div class="mega-cols">
              <div class="mega-col"><ul>
                <li><a href="/blog/">Blog</a></li>
                <li><a href="/case-studies/">Case Studies</a></li>
                <li><a href="/how-to-spec-a-returnable-rack/">Spec a Rack: Free Guide</a></li>
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

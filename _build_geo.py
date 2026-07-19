#!/usr/bin/env python3
"""Generator for SPF geo/pillar pages.

Emits, into the website root, with chrome (head/nav/footer/analytics) byte-identical
to the live product pages:
  /returnable-packaging/index.html          master category pillar
  /returnable-packaging/<city>/index.html    10 metro pages (macon home + 9 Tier-1)
  /locations/index.html                       lightweight index hub

Run from the website/ directory:  python3 _build_geo.py
"""
import json, os

# ---------------------------------------------------------------- shared chrome
FONTS = (
'  <link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
'  <link rel="preconnect" href="https://fonts.googleapis.com">\n'
'  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
'  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;600;700&display=swap">\n'
'  <link rel="stylesheet" href="/assets/styles.css">'
)

ANALYTICS = """  <!-- ANALYTICS -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-7NE6WQG77Y"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-7NE6WQG77Y');</script>
  <script>document.addEventListener('DOMContentLoaded',function(){var s=document.getElementById('rfqSuccess');if(!s)return;new MutationObserver(function(){if(!s.hidden&&window.gtag){gtag('event','generate_lead',{event_category:'RFQ',event_label:location.pathname});}}).observe(s,{attributes:true,attributeFilter:['hidden']});});</script>
  <script type="text/javascript">(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);})(window, document, "clarity", "script", "xoinpowe8z");</script>
  <!-- /ANALYTICS -->"""

LINKEDIN = """  <!-- LinkedIn Insight Tag -->
  <script type="text/javascript">
  _linkedin_partner_id = "9403242";
  window._linkedin_data_partner_ids = window._linkedin_data_partner_ids || [];
  window._linkedin_data_partner_ids.push(_linkedin_partner_id);
  </script>
  <script type="text/javascript">
  (function(l) {
  if (!l){window.lintrk = function(a,b){window.lintrk.q.push([a,b])};
  window.lintrk.q=[]}
  var s = document.getElementsByTagName("script")[0];
  var b = document.createElement("script");
  b.type = "text/javascript";b.async = true;
  b.src = "https://snap.licdn.com/li.lms-analytics/insight.min.js";
  s.parentNode.insertBefore(b, s);})(window.lintrk);
  </script>
  <noscript>
  <img height="1" width="1" style="display:none;" alt="" src="https://px.ads.linkedin.com/collect/?pid=9403242&fmt=gif" />
  </noscript>
  <!-- /LinkedIn Insight Tag -->"""

NAV = """  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="wrap header-inner">
      <a href="/" class="brand" aria-label="Southern Perfection Fabrication — home"><img src="/assets/logo.png" alt="Southern Perfection Fabrication" class="brand-logo" width="102" height="42"></a>
      <nav class="nav" aria-label="Primary">
        <input type="checkbox" id="nav-toggle" class="nav-cb" aria-hidden="true" tabindex="-1">
        <label for="nav-toggle" class="nav-burger">Menu</label>
        <ul class="mega">
          <li class="mega-item"><a class="mega-top" href="/returnable-packaging/">Returnable Packaging</a>
            <div class="mega-panel"><div class="mega-cols">
              <div class="mega-col"><p class="mega-h">Racks &amp; Containers</p><ul>
                <li><a href="/returnable-steel-racks/">Returnable Steel Racks</a></li>
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
                <li><a href="/wip-carts/">WIP Carts</a></li>
              </ul></div>
              <div class="mega-col"><p class="mega-h">Dunnage &amp; Service</p><ul>
                <li><a href="/dunnage/">Dunnage</a></li>
                <li><a href="/custom-foam-inserts/">Custom Foam Inserts</a></li>
                <li><a href="/rack-repair-refurbishment/">Rack Repair &amp; Refurb</a></li>
              </ul></div>
            </div></div>
          </li>
          <li class="mega-item"><a class="mega-top" href="/custom-manufacturing/">Custom Manufacturing</a>
            <div class="mega-panel"><div class="mega-cols">
              <div class="mega-col"><p class="mega-h">Fabrication</p><ul>
                <li><a href="/capabilities/">Contract Manufacturing</a></li>
                <li><a href="/weldments-frames/">Weldments &amp; Frames</a></li>
                <li><a href="/sheet-metal-fabrication/">Sheet Metal Fabrication</a></li>
                <li><a href="/high-volume-manufacturing/">High-Volume Manufacturing</a></li>
              </ul></div>
              <div class="mega-col"><p class="mega-h">Structures &amp; Guards</p><ul>
                <li><a href="/industrial-structures/">Industrial Structures</a></li>
                <li><a href="/guards-platforms/">Guards &amp; Platforms</a></li>
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
          <li class="mega-item"><a class="mega-top" href="/locations/">Locations</a></li>
          <li class="mega-item"><a class="mega-top" href="/managed-programs/">Managed Programs</a></li>
          <li class="mega-item"><span class="mega-top">Resources</span>
            <div class="mega-panel"><div class="mega-cols">
              <div class="mega-col"><p class="mega-h">Learn</p><ul>
                <li><a href="/blog/">Blog</a></li>
                <li><a href="/case-studies/">Case Studies</a></li>
                <li><a href="/how-to-spec-a-returnable-rack/">Spec a Rack: Free Guide</a></li>
                <li><a href="/returnable-vs-expendable-packaging/">Returnable vs. Expendable</a></li>
                <li><a href="/returnable-packaging-roi/">ROI Calculator</a></li>
              </ul></div>
              <div class="mega-col"><p class="mega-h">Company</p><ul>
                <li><a href="/about/">About</a></li>
                <li><a href="/contact/">Contact</a></li>
              </ul></div>
            </div></div>
          </li>
        </ul>
      </nav>
      <div class="header-cta"><a href="/#rfq" class="btn btn-spark">Start an RFQ</a></div>
    </div>
  </header>"""

FOOTER = """  <footer class="site-footer">
    <div class="wrap footer-grid">
      <div><span class="brand-text">SOUTHERN PERFECTION FABRICATION</span><p class="footer-mono">Returnable steel racks &amp; material handling</p><p class="footer-mono">ISO 9001 · CAGE 2W654 · Est. 1982 · Byron, GA</p></div>
      <nav aria-label="Footer"><ul><li><a href="/returnable-packaging/">Returnable Packaging</a></li><li><a href="/returnable-steel-racks/">Returnable Racks</a></li><li><a href="/rack-repair-refurbishment/">Repair &amp; Refurb</a></li><li><a href="/dunnage/">Dunnage</a></li><li><a href="/capabilities/">Capabilities</a></li><li><a href="/locations/">Locations</a></li></ul></nav>
      <div class="footer-contact"><a href="tel:+14789564442" class="phone">478-956-4442</a><br><span class="footer-mono">Toll-free (800) 237-4726</span><br><a href="mailto:sales@southernperfection.com">sales@southernperfection.com</a><br><span class="footer-mono">232 Hwy 49 S · Byron, GA 31008</span></div>
    </div>
    <div class="wrap footer-legal"><small>© 2026 Southern Perfection Fabrication. All rights reserved.</small></div>
  </footer>"""

CTA = """<section class="cta-band"><div class="wrap center">
      <h2 class="h-light">%%CTA_H%%</h2>
      <p class="lede lede-light">%%CTA_P%%</p>
      <a href="/#rfq" class="btn btn-spark btn-lg">Start an RFQ →</a>
    </div></section>"""

def page(title, desc, canonical, schema, body, cta_h, cta_p):
    """Assemble a full HTML document identical in chrome to the live pages."""
    schema_blocks = "\n".join(
        '  <script type="application/ld+json">\n  ' + json.dumps(s, ensure_ascii=False) + "\n  </script>"
        for s in schema
    )
    og_title = title.split(" | ")[0]
    head = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{canonical}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Southern Perfection Fabrication">
  <meta property="og:title" content="{og_title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="https://southernperfection.com/assets/og-cover.jpg">
{FONTS}
{schema_blocks}
{ANALYTICS}
  <script src="/assets/rfq-attribution.js?v=fa4d94d3" defer></script>
  <!-- RB2B visitor identification -->
  <script>!function(key) {if (window.reb2b) return;window.reb2b = {loaded: true};var s = document.createElement("script");s.async = true;s.src = "https://ddwl4m2hdecbv.cloudfront.net/b/" + key + "/" + key + ".js.gz";document.getElementsByTagName("script")[0].parentNode.insertBefore(s, document.getElementsByTagName("script")[0]);}("VN080HZ1Z26J");</script>
</head>
<body>
{NAV}

  <main id="main">
{body}
{CTA.replace('%%CTA_H%%', cta_h).replace('%%CTA_P%%', cta_p)}
  </main>

{FOOTER}
{LINKEDIN}
  <script src="/assets/newsletter.js?v=e3c060fc" defer></script>
</body>
</html>
"""
    return head

# ---------------------------------------------------------------- helpers
PROD = {
 'returnable-steel-racks':('Returnable Steel Racks','Custom steel shipping racks and stack racks engineered to your part, load, and freight lanes.'),
 'automotive-racks':('Automotive Racks','Line-side and shipping racks for body, chassis, and powertrain parts, built to print.'),
 'engine-racks':('Engine &amp; Powertrain Racks','Heavy-duty racks that protect engines and large castings trip after trip.'),
 'bumper-racks':('Bumper &amp; Fascia Racks','Contoured racks that cradle painted fascias and bumpers damage-free.'),
 'tire-racks':('Tire Racks &amp; Carts','Rolling and stacking racks that move and sequence tires and wheels.'),
 'coil-racks':('Coil Racks','Cradles and racks that stage and ship steel coil and roll stock safely.'),
 'stack-racks':('Stack Racks','Stackable, nesting steel racks that save floor space and return freight.'),
 'steel-pallets':('Steel Pallets','Reusable steel pallets and skid bases built for heavy, repeat loads.'),
 'returnable-containers':('Industrial Metal Containers','Steel bins, baskets, and totes for bulk parts in a closed loop.'),
 'dunnage':('Dunnage','Steel, foam, and hybrid dunnage that indexes and protects each part.'),
 'custom-foam-inserts':('Custom Foam Inserts','CNC-cut foam that cradles delicate, machined, or finished parts.'),
 'wip-carts':('WIP Carts','Work-in-process carts and sequencing dollies that keep parts moving line-side.'),
 'industrial-carts':('Industrial Carts','Custom carts that move sub-assemblies through your plant.'),
 'kanban-flow-racks':('Kanban Flow Racks','Gravity flow racks that feed the line and pull empties back.'),
 'steel-cable-reels':('Steel Cable Reels','Returnable steel reels for wire, cable, and hose.'),
 'weldments-frames':('Weldments &amp; Frames','Precision welded frames and structures built to your drawing.'),
 'guards-platforms':('Guards &amp; Platforms','Machine guards, mezzanines, and access platforms to spec.'),
}

def prod_cards(slugs):
    out = []
    for s in slugs:
        name, d = PROD[s]
        out.append(f'          <article class="card"><h3><a href="/{s}/">{name}</a></h3><p>{d}</p></article>')
    return "\n".join(out)

def ind_cards(items):
    out = []
    for label, desc, href in items:
        h = f'<a href="{href}">{label}</a>' if href else label
        out.append(f'          <article class="card"><h3>{h}</h3><p>{desc}</p></article>')
    return "\n".join(out)

# ---------------------------------------------------------------- MASTER PILLAR
def build_pillar():
    canonical = "https://southernperfection.com/returnable-packaging/"
    title = "Returnable Packaging Manufacturer | Returnable Steel Racks &amp; Dunnage | Southern Perfection Fabrication"
    desc = ("Returnable packaging manufacturer — returnable steel racks, dunnage, metal containers & rack repair, "
            "designed and built under one roof in Byron, GA. ISO 9001, CAGE 2W654. Freight-served across the "
            "Southeast & Midwest. Send a part or a print for a concept and a number.")
    faqs = [
        ("What is returnable packaging?", "Returnable packaging is durable, reusable material handling — steel racks, metal containers, dunnage, and carts — engineered to run many trips in a closed loop instead of being thrown away like expendable cardboard or wood. It lowers cost per trip and cuts transit damage."),
        ("Are you a returnable packaging manufacturer or a broker?", "We are a manufacturer. Southern Perfection Fabrication designs, laser-cuts, forms, robotic-welds, and powder-coats every returnable packaging program in-house in Byron, GA — one vendor, one PO, one point of accountability."),
        ("What kinds of returnable packaging do you build?", "Returnable steel racks, stack racks, metal containers and totes, steel pallets, dunnage and custom foam inserts, WIP carts, and kanban flow racks — plus repair and refurbishment of existing fleets, even racks we did not build."),
        ("Where do you ship returnable packaging?", "From Byron, GA we freight returnable packaging across the Southeast and Midwest manufacturing corridor — Alabama, Tennessee, the Carolinas, Indiana, Illinois, Wisconsin, Minnesota and beyond, by LTL or full truckload."),
    ]
    schema = [
        {"@context":"https://schema.org","@graph":[
            {"@type":"BreadcrumbList","itemListElement":[
                {"@type":"ListItem","position":1,"name":"Home","item":"https://southernperfection.com/"},
                {"@type":"ListItem","position":2,"name":"Returnable Packaging","item":canonical}]},
            {"@type":"Service","name":"Returnable Packaging Design & Manufacturing","serviceType":"Returnable steel racks, dunnage, metal containers & rack repair","provider":{"@type":"Organization","name":"Southern Perfection Fabrication","telephone":"+1-478-956-4442"},"areaServed":"Southeast & Midwest United States"}
        ]},
        {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
            {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}
    ]
    prods = ['returnable-steel-racks','stack-racks','returnable-containers','steel-pallets',
             'dunnage','custom-foam-inserts','wip-carts','kanban-flow-racks']
    industries = [
        ("Automotive OEM &amp; Tier-1","Body, chassis, powertrain and sequencing racks for the line.","/industries/automotive/"),
        ("Aerospace &amp; Defense","Traceable, CAGE-backed returnable packaging and GSE.","/industries/aerospace-defense/"),
        ("EV &amp; Battery","Dunnage and racks that handle heavy, sensitive cells and trays.","/industries/ev-battery/"),
        ("Heavy Equipment","Rugged racks for large castings, weldments, and off-highway parts.","/industries/heavy-equipment/"),
        ("Food, Beverage &amp; Dairy","Washable steel containers and racks for closed-loop plants.","/industries/food-beverage-dairy/"),
        ("General Manufacturing","Custom returnable packaging for any repeatable part and lane.","/industries/general-industrial/"),
    ]
    faq_html = "\n".join(
        f'          <details><summary>{q}</summary><p>{a}</p></details>' for q,a in faqs)
    cities_links = "\n".join(
        f'              <li><a href="/returnable-packaging/{c["slug"]}/">{c["metro"]}</a></li>' for c in CITIES)
    body = f"""    <section class="hero" aria-labelledby="h">
      <div class="wrap hero-split"><div class="hero-copy">
        <p class="eyebrow"><a href="/" style="color:inherit">Home</a> · Returnable Packaging</p>
        <h1 id="h">Returnable packaging, built under one roof.</h1>
        <p class="lede">Southern Perfection Fabrication is a <strong>returnable packaging manufacturer</strong> — returnable steel racks, dunnage, metal containers, and rack repair, engineered to your part and your loop and built to come back trip after trip. Not a broker: we design, weld, and finish every program in-house in Byron, GA. Send a part or a print and we’ll turn around a concept and a number.</p>
        <div class="hero-actions"><a href="/#rfq" class="btn btn-spark btn-lg">Start an RFQ →</a><a href="/returnable-steel-racks/" class="btn btn-ghost btn-lg">See returnable steel racks</a></div>
      </div><div class="hero-media"><img src="/assets/photos/returnable-racks-fleet.jpg" alt="Rows of powder-coated returnable packaging racks staged at Southern Perfection Fabrication in Byron, GA" width="1600" loading="eager" fetchpriority="high"></div></div>
    </section>

    <section class="section"><div class="wrap article-body">
      <p class="kicker">Returnable packaging</p>
      <h2>What is returnable packaging?</h2>
      <p><strong>Returnable packaging</strong> — sometimes called returnable material handling or reusable packaging — is durable, engineered steel and foam packaging built to run many trips in a closed loop instead of being used once and thrown away. Where expendable cardboard, wood, and stretch wrap are a recurring cost that still lets parts get damaged, returnable packaging is a one-time capital investment that lowers <strong>cost per trip</strong> and protects the part every trip.</p>
      <p>As a <strong>returnable packaging manufacturer</strong> and not a broker, Southern Perfection Fabrication engineers each program in-house with SolidWorks, then laser-cuts, forms, robotic-welds, and powder-coats it <a href="/capabilities/">under one roof</a> in Byron, GA — the same way we delivered a <a href="/case-studies/engine-rack-program/">300+ engine-rack fleet in about half the quoted lead time</a>.</p>
    </div></section>

    <section class="section section-paper">
      <div class="wrap">
        <p class="kicker">What we build</p>
        <h2>The full returnable packaging line.</h2>
        <div class="cards-4">
{prod_cards(prods)}
        </div>
        <p class="lede" style="margin-top:22px">Also building <a href="/automotive-racks/">automotive racks</a>, <a href="/engine-racks/">engine racks</a>, <a href="/tire-racks/">tire racks</a>, <a href="/coil-racks/">coil racks</a> and more — and we <a href="/rack-repair-refurbishment/">repair and refurbish</a> existing fleets, even racks we didn’t build.</p>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <p class="kicker">Why SPF</p>
        <h2>The returnable packaging partner that owns the whole build.</h2>
        <div class="cards-4">
          <article class="card"><h3>One Roof</h3><p>Design, robotic welding, machining, forming &amp; finishing in-house — one vendor, one PO.</p></article>
          <article class="card"><h3>Built to Last</h3><p>Returnable packaging engineered for years of trips, not a single launch.</p></article>
          <article class="card"><h3>ISO 9001 / CAGE</h3><p>ISO 9001 quality and CAGE 2W654 — the traceability OEM and defense programs require.</p></article>
          <article class="card"><h3>Repair Too</h3><p>We don’t just build — we <a href="/rack-repair-refurbishment/">repair and refurbish</a> existing returnable fleets.</p></article>
        </div>
      </div>
    </section>

    <section class="section section-paper">
      <div class="wrap">
        <p class="kicker">Industries</p>
        <h2>Returnable packaging for the industries you build in.</h2>
        <div class="cards-4">
{ind_cards(industries)}
        </div>
      </div>
    </section>

    <section class="section"><div class="wrap article-body">
      <p class="kicker">Where we ship</p>
      <h2>Freight-served across the manufacturing corridor.</h2>
      <p>From our plant in Byron, GA we design and freight returnable packaging to manufacturers across the Southeast and Midwest — by LTL or full truckload, engineered to cube out the trailer so you pay to ship parts, not air. Explore returnable packaging by metro:</p>
      <div class="mega-cols" style="margin-top:8px"><div class="mega-col"><ul>
{cities_links}
      </ul></div></div>
      <p style="margin-top:14px"><a href="/locations/">See all locations we serve →</a></p>
    </div></section>

    <section class="section section-paper">
      <div class="wrap">
        <p class="kicker">FAQ</p>
        <h2>Returnable packaging — answered.</h2>
        <div class="faq">
{faq_html}
        </div>
      </div>
    </section>
"""
    html = page(title, desc, canonical, schema, body,
                "Ready to switch to returnable packaging?",
                "Send a photo or a print — we’ll come back with a concept and a number.")
    os.makedirs("returnable-packaging", exist_ok=True)
    with open("returnable-packaging/index.html", "w") as f:
        f.write(html)
    print("wrote returnable-packaging/index.html")

# ---------------------------------------------------------------- CITY DATA
CITIES = [
 {"slug":"macon-ga","city":"Macon","state":"GA","metro":"Macon–Warner Robins, GA","home":True,
  "freight":"right here in Middle Georgia","miles":"local","photo":"metal-fabrication-shop.jpg",
  "intro":"Byron sits in the heart of the Macon–Warner Robins market, so returnable packaging built on our floor is on your dock the same day — no freight, no lead-time surprise. We’re the local returnable packaging manufacturer for Middle Georgia’s aerospace, food and beverage, and general manufacturing plants.",
  "industries":[("Aerospace &amp; Defense","Robins-area programs that need traceable, CAGE-backed packaging and GSE.","/industries/aerospace-defense/"),
                ("Food, Beverage &amp; Dairy","Washable steel containers and racks for closed-loop food plants.","/industries/food-beverage-dairy/"),
                ("General Manufacturing","Custom returnable packaging for any repeatable Middle Georgia line.","/industries/general-industrial/"),
                ("Distribution &amp; Logistics","Reusable racks and pallets that standardize how parts move.","/industries/distribution-logistics/")],
  "prods":['returnable-steel-racks','dunnage','returnable-containers','steel-pallets']},

 {"slug":"huntsville-al","city":"Huntsville","state":"AL","metro":"Huntsville, AL","home":False,
  "freight":"about 4½ hours by truck","miles":"roughly 300 miles","photo":"returnable-steel-racks.jpg",
  "intro":"Huntsville’s aerospace, defense, and automotive plants run on precision — and on packaging that protects high-value parts and carries the traceability those programs demand. From Byron, GA we freight returnable steel racks and dunnage into the Huntsville area on a next-day lane, backed by ISO 9001 and CAGE 2W654.",
  "industries":[("Aerospace &amp; Defense","The metro’s largest cluster — traceable returnable packaging and GSE.","/industries/aerospace-defense/"),
                ("Automotive OEM &amp; Tier-1","Line-side and shipping racks for North Alabama assembly and supply.","/industries/automotive/"),
                ("Heavy Equipment","Rugged racks for large castings and off-highway components.","/industries/heavy-equipment/"),
                ("EV &amp; Battery","Dunnage and racks for heavy, sensitive cells and trays.","/industries/ev-battery/")],
  "prods":['returnable-steel-racks','weldments-frames','guards-platforms','custom-foam-inserts']},

 {"slug":"charlotte-nc","city":"Charlotte","state":"NC","metro":"Charlotte, NC","home":False,
  "freight":"about 5 hours by truck","miles":"roughly 330 miles","photo":"returnable-racks-fleet.jpg",
  "intro":"The Charlotte region’s industrial, power, and heavy-machinery plants need returnable packaging that stands up to dense, heavy parts and daily loop turns. From Byron, GA we design and freight returnable steel racks and metal containers into the Charlotte metro on a one-day lane.",
  "industries":[("Industrial / Power / Electrical","The metro’s dominant base — racks and reels for heavy electrical gear.","/industries/energy-power/"),
                ("Truck, Bus &amp; Powertrain","Sequencing and shipping racks for drivetrain and engine parts.","/industries/transportation-trailer/"),
                ("Aerospace &amp; Defense","Traceable returnable packaging for Carolina aerospace suppliers.","/industries/aerospace-defense/"),
                ("General Manufacturing","Custom returnable packaging for any repeatable Charlotte-area line.","/industries/general-industrial/")],
  "prods":['returnable-steel-racks','coil-racks','steel-cable-reels','industrial-carts']},

 {"slug":"chicago-il","city":"Chicago","state":"IL","metro":"Chicago, IL","home":False,
  "freight":"about a day and a half by truck","miles":"roughly 720 miles","photo":"food-grade-returnable-racks.jpg",
  "intro":"Chicagoland’s food, beverage, and pharmaceutical plants live and die by clean, closed-loop material handling. From Byron, GA we build washable steel containers, racks, and dunnage and freight them into the Chicago metro by LTL or full truckload.",
  "industries":[("Food, Beverage &amp; CPG","Washable steel containers and racks for high-volume food lines.","/industries/food-beverage-dairy/"),
                ("Pharma &amp; Medical Device","Clean, traceable dunnage and containers for regulated products.",None),
                ("Automotive OEM &amp; Tier-1","Line-side and shipping racks for regional assembly and supply.","/industries/automotive/"),
                ("Distribution &amp; Logistics","Reusable racks and pallets that standardize how parts move.","/industries/distribution-logistics/")],
  "prods":['returnable-containers','dunnage','steel-pallets','returnable-steel-racks']},

 {"slug":"milwaukee-wi","city":"Milwaukee","state":"WI","metro":"Milwaukee, WI","home":False,
  "freight":"about a day and a half by truck","miles":"roughly 840 miles","photo":"heavy-equipment.jpg",
  "intro":"Milwaukee’s industrial, power-equipment, and heavy-machinery makers need returnable packaging engineered for weight and abuse. From Byron, GA we build and freight returnable steel racks and industrial carts into the Milwaukee metro by LTL or full truckload.",
  "industries":[("Industrial / Power / Electrical","Racks and reels for heavy electrical and power equipment.","/industries/energy-power/"),
                ("Heavy Equipment","Rugged racks for large castings, weldments, and off-highway parts.","/industries/heavy-equipment/"),
                ("RV &amp; Powersports","Protective racks and dunnage for large, finished assemblies.",None),
                ("General Manufacturing","Custom returnable packaging for any repeatable Wisconsin line.","/industries/general-industrial/")],
  "prods":['returnable-steel-racks','weldments-frames','industrial-carts','steel-pallets']},

 {"slug":"elkhart-in","city":"Elkhart","state":"IN","metro":"Elkhart, IN","home":False,
  "freight":"about a day by truck","miles":"roughly 630 miles","photo":"returnable-steel-racks.jpg",
  "intro":"Elkhart is the RV and powersports capital of the country, and those large, finished assemblies need returnable packaging that protects paint and structure through the loop. From Byron, GA we build racks, dunnage, and foam and freight them into the Elkhart metro.",
  "industries":[("RV &amp; Powersports","The metro’s signature industry — racks and dunnage for big assemblies.",None),
                ("Marine / Boatbuilding","Cradles and racks that protect hulls, decks, and components.",None),
                ("Automotive Tier-1","Sequencing and shipping racks for regional supply.","/industries/automotive/"),
                ("General Manufacturing","Custom returnable packaging for any repeatable Northern Indiana line.","/industries/general-industrial/")],
  "prods":['returnable-steel-racks','dunnage','custom-foam-inserts','industrial-carts']},

 {"slug":"montgomery-al","city":"Montgomery","state":"AL","metro":"Montgomery, AL","home":False,
  "freight":"about 3 hours by truck","miles":"roughly 200 miles","photo":"automotive-returnable-racks.jpg",
  "intro":"Montgomery is automotive country — OEM assembly and the Tier-1 suppliers around it — plus appliance and HVAC production. From Byron, GA we’re a short freight lane away, delivering returnable automotive racks and dunnage on a same-day or next-day truck.",
  "industries":[("Automotive OEM","Line-side, sequencing, and shipping racks built to your print.","/industries/automotive/"),
                ("Automotive Tier-1","Returnable racks and dunnage that index each part for the plant.","/industries/automotive/"),
                ("Appliance &amp; HVAC","Protective racks and containers for finished units and components.",None),
                ("General Manufacturing","Custom returnable packaging for any repeatable Central Alabama line.","/industries/general-industrial/")],
  "prods":['automotive-racks','engine-racks','dunnage','returnable-steel-racks']},

 {"slug":"chattanooga-tn","city":"Chattanooga","state":"TN","metro":"Chattanooga, TN","home":False,
  "freight":"about 3½ hours by truck","miles":"roughly 230 miles","photo":"automotive-shipping-racks.jpg",
  "intro":"Chattanooga pairs automotive assembly with heavy-equipment and emerging EV/battery production — all of it hungry for returnable packaging that turns fast in the loop. From Byron, GA we’re a short freight lane away with racks, dunnage, and containers.",
  "industries":[("Heavy Equipment","Rugged racks for large castings and off-highway components.","/industries/heavy-equipment/"),
                ("Automotive OEM","Line-side and shipping racks for regional assembly.","/industries/automotive/"),
                ("EV &amp; Battery","Dunnage and racks for heavy, sensitive cells and trays.","/industries/ev-battery/"),
                ("General Manufacturing","Custom returnable packaging for any repeatable East Tennessee line.","/industries/general-industrial/")],
  "prods":['returnable-steel-racks','automotive-racks','dunnage','returnable-containers']},

 {"slug":"clarksville-tn","city":"Clarksville","state":"TN","metro":"Clarksville, TN","home":False,
  "freight":"about 5½ hours by truck","miles":"roughly 360 miles","photo":"returnable-steel-racks.jpg",
  "intro":"Clarksville’s appliance, HVAC, and fast-growing EV/battery plants need returnable packaging engineered for heavy, sensitive product. From Byron, GA we design and freight returnable steel racks and dunnage into the Clarksville metro.",
  "industries":[("Appliance &amp; HVAC","Protective racks and containers for finished units and components.",None),
                ("EV &amp; Battery","Dunnage and racks that handle heavy, sensitive cells and trays.","/industries/ev-battery/"),
                ("Tire &amp; Rubber","Rolling and stacking racks that move and sequence tires.",None),
                ("General Manufacturing","Custom returnable packaging for any repeatable Middle Tennessee line.","/industries/general-industrial/")],
  "prods":['returnable-steel-racks','dunnage','returnable-containers','industrial-carts']},

 {"slug":"minneapolis-mn","city":"Minneapolis","state":"MN","metro":"Minneapolis, MN","home":False,
  "freight":"about a day and a half by truck","miles":"roughly 1,080 miles","photo":"food-grade-returnable-racks.jpg",
  "intro":"The Twin Cities pair a deep food and beverage base with industrial, power, and medical manufacturing — all closed-loop candidates for returnable packaging. From Byron, GA we build washable containers, racks, and dunnage and freight them to the Minneapolis metro by full truckload.",
  "industries":[("Food, Beverage &amp; CPG","Washable steel containers and racks for high-volume food lines.","/industries/food-beverage-dairy/"),
                ("Industrial / Power / Electrical","Racks and reels for heavy electrical and power equipment.","/industries/energy-power/"),
                ("Pharma &amp; Medical Device","Clean, traceable dunnage and containers for regulated products.",None),
                ("General Manufacturing","Custom returnable packaging for any repeatable Minnesota line.","/industries/general-industrial/")],
  "prods":['returnable-containers','dunnage','returnable-steel-racks','steel-pallets']},

 # ---- Tier 2 ----
 {"slug":"indianapolis-in","city":"Indianapolis","state":"IN","metro":"Indianapolis, IN","home":False,
  "freight":"about a day by truck","miles":"roughly 530 miles","photo":"returnable-steel-racks.jpg",
  "intro":"Indianapolis blends powertrain and truck manufacturing with appliance, pharmaceutical, and medical-device production — a broad base of closed-loop candidates. From Byron, GA we design and freight returnable steel racks, dunnage, and containers into the Indianapolis metro.",
  "industries":[("Truck, Bus &amp; Powertrain","Sequencing and shipping racks for drivetrain and engine parts.","/industries/transportation-trailer/"),
                ("Appliance &amp; HVAC","Protective racks and containers for finished units and components.",None),
                ("Pharma &amp; Medical Device","Clean, traceable dunnage and containers for regulated products.",None),
                ("General Manufacturing","Custom returnable packaging for any repeatable Central Indiana line.","/industries/general-industrial/")],
  "prods":['returnable-steel-racks','engine-racks','dunnage','returnable-containers']},

 {"slug":"charleston-sc","city":"Charleston","state":"SC","metro":"Charleston, SC","home":False,
  "freight":"about 4 hours by truck","miles":"roughly 260 miles","photo":"automotive-returnable-racks.jpg",
  "intro":"Charleston pairs automotive and EV/battery production with aerospace and heavy equipment on the coast. From Byron, GA we’re a short freight lane away with returnable steel racks, dunnage, and battery-tray protection for the Lowcountry’s plants.",
  "industries":[("Automotive Tier-1","Sequencing and shipping racks built to your print.","/industries/automotive/"),
                ("EV &amp; Battery","Dunnage and racks that handle heavy, sensitive cells and trays.","/industries/ev-battery/"),
                ("Heavy Equipment","Rugged racks for large castings and off-highway components.","/industries/heavy-equipment/"),
                ("Aerospace &amp; Defense","Traceable returnable packaging and GSE for coastal aerospace.","/industries/aerospace-defense/")],
  "prods":['returnable-steel-racks','automotive-racks','dunnage','custom-foam-inserts']},

 {"slug":"savannah-ga","city":"Savannah","state":"GA","metro":"Savannah, GA","home":False,
  "freight":"about 2½ hours by truck","miles":"roughly 170 miles","photo":"heavy-equipment.jpg",
  "intro":"Savannah’s port-driven manufacturing base — heavy equipment, aerospace, and shipbuilding — runs on rugged returnable packaging. As a fellow Georgia manufacturer in Byron, we’re a short, often same-day freight lane from the Savannah metro.",
  "industries":[("Heavy Equipment","Rugged racks for large castings, weldments, and off-highway parts.","/industries/heavy-equipment/"),
                ("Truck, Bus &amp; Powertrain","Sequencing and shipping racks for drivetrain and engine parts.","/industries/transportation-trailer/"),
                ("Aerospace &amp; Shipbuilding","Traceable returnable packaging and GSE, CAGE 2W654.","/industries/aerospace-defense/"),
                ("General Manufacturing","Custom returnable packaging for any repeatable Coastal Georgia line.","/industries/general-industrial/")],
  "prods":['returnable-steel-racks','weldments-frames','dunnage','steel-pallets']},

 {"slug":"memphis-tn","city":"Memphis","state":"TN","metro":"Memphis, TN","home":False,
  "freight":"about 6 hours by truck","miles":"roughly 390 miles","photo":"distribution-logistics.jpg",
  "intro":"Memphis is a distribution and manufacturing crossroads — heavy equipment, appliance, and medical production feeding one of the country’s biggest logistics hubs. From Byron, GA we freight returnable steel racks, carts, and containers into the Memphis metro.",
  "industries":[("Heavy Equipment","Rugged racks for large castings and off-highway components.","/industries/heavy-equipment/"),
                ("Appliance &amp; HVAC","Protective racks and containers for finished units and components.",None),
                ("Distribution &amp; Logistics","Reusable racks and pallets that standardize how parts move.","/industries/distribution-logistics/"),
                ("Pharma &amp; Medical Device","Clean, traceable dunnage and containers for regulated products.",None)],
  "prods":['returnable-steel-racks','industrial-carts','dunnage','returnable-containers']},

 {"slug":"nashville-tn","city":"Nashville","state":"TN","metro":"Nashville, TN","home":False,
  "freight":"about 4 hours by truck","miles":"roughly 270 miles","photo":"automotive-shipping-racks.jpg",
  "intro":"Middle Tennessee around Nashville has become an automotive and consumer-products manufacturing hub. From Byron, GA we’re a short freight lane away with returnable steel racks, automotive racks, and dunnage built to your loop.",
  "industries":[("Automotive Tier-1","Line-side and shipping racks for regional assembly and supply.","/industries/automotive/"),
                ("Furniture &amp; Building Products","Protective racks and dunnage for large, finished goods.",None),
                ("Tire &amp; Rubber","Rolling and stacking racks that move and sequence tires.",None),
                ("General Manufacturing","Custom returnable packaging for any repeatable Middle Tennessee line.","/industries/general-industrial/")],
  "prods":['returnable-steel-racks','automotive-racks','tire-racks','dunnage']},

 {"slug":"greensboro-nc","city":"Greensboro","state":"NC","metro":"Greensboro, NC","home":False,
  "freight":"about 5 hours by truck","miles":"roughly 340 miles","photo":"returnable-steel-racks.jpg",
  "intro":"The Piedmont Triad around Greensboro is a growing aerospace and electronics/semiconductor corridor — production that demands clean, protective returnable packaging. From Byron, GA we design and freight racks, foam, and dunnage into the Greensboro metro.",
  "industries":[("Semiconductor &amp; Electronics","Clean, ESD-aware foam and racks for sensitive assemblies.",None),
                ("Aerospace &amp; Defense","Traceable returnable packaging and GSE, CAGE 2W654.","/industries/aerospace-defense/"),
                ("General Manufacturing","Custom returnable packaging for any repeatable Triad line.","/industries/general-industrial/"),
                ("Distribution &amp; Logistics","Reusable racks and pallets that standardize how parts move.","/industries/distribution-logistics/")],
  "prods":['returnable-steel-racks','custom-foam-inserts','dunnage','returnable-containers']},

 {"slug":"st-louis-mo","city":"St. Louis","state":"MO","metro":"St. Louis, MO","home":False,
  "freight":"about a day by truck","miles":"roughly 560 miles","photo":"food-grade-returnable-racks.jpg",
  "intro":"St. Louis spans aerospace and defense, industrial and power equipment, and a deep food and beverage base — a wide mix of closed-loop candidates. From Byron, GA we freight returnable steel racks, dunnage, and containers to the St. Louis metro.",
  "industries":[("Aerospace &amp; Defense","Traceable returnable packaging and GSE, CAGE 2W654.","/industries/aerospace-defense/"),
                ("Industrial / Power / Electrical","Racks and reels for heavy electrical and power equipment.","/industries/energy-power/"),
                ("Food, Beverage &amp; CPG","Washable steel containers and racks for high-volume food lines.","/industries/food-beverage-dairy/"),
                ("General Manufacturing","Custom returnable packaging for any repeatable Missouri line.","/industries/general-industrial/")],
  "prods":['returnable-steel-racks','weldments-frames','dunnage','returnable-containers']},

 {"slug":"wichita-ks","city":"Wichita","state":"KS","metro":"Wichita, KS","home":False,
  "freight":"about a day and a half by truck","miles":"roughly 870 miles","photo":"returnable-steel-racks.jpg",
  "intro":"Wichita is the “Air Capital of the World” — aerospace and defense manufacturing that demands traceable, protective returnable packaging. From Byron, GA we build to ISO 9001 and CAGE 2W654 and freight racks, weldments, and foam to the Wichita metro.",
  "industries":[("Aerospace &amp; Defense","The metro’s signature industry — traceable packaging and GSE.","/industries/aerospace-defense/"),
                ("Appliance &amp; HVAC","Protective racks and containers for finished units and components.",None),
                ("General Manufacturing","Custom returnable packaging for any repeatable South-Central Kansas line.","/industries/general-industrial/"),
                ("Industrial Machinery","Racks and weldments for machinery and OEM components.","/industries/industrial-machinery/")],
  "prods":['returnable-steel-racks','weldments-frames','guards-platforms','custom-foam-inserts']},

 {"slug":"cleveland-oh","city":"Cleveland","state":"OH","metro":"Cleveland, OH","home":False,
  "freight":"about a day by truck","miles":"roughly 620 miles","photo":"heavy-equipment.jpg",
  "intro":"Cleveland’s dense industrial, power-equipment, and powertrain base needs returnable packaging engineered for heavy, repeat loads. From Byron, GA we build and freight returnable steel racks, coil racks, and industrial carts into the Cleveland metro.",
  "industries":[("Industrial / Power / Electrical","The metro’s dominant base — racks and reels for heavy gear.","/industries/energy-power/"),
                ("Truck, Bus &amp; Powertrain","Sequencing and shipping racks for drivetrain and engine parts.","/industries/transportation-trailer/"),
                ("Appliance &amp; HVAC","Protective racks and containers for finished units and components.",None),
                ("General Manufacturing","Custom returnable packaging for any repeatable Northeast Ohio line.","/industries/general-industrial/")],
  "prods":['returnable-steel-racks','coil-racks','industrial-carts','weldments-frames']},

 {"slug":"detroit-mi","city":"Detroit","state":"MI","metro":"Detroit, MI","home":False,
  "freight":"about a day and a half by truck","miles":"roughly 720 miles","photo":"automotive-returnable-racks.jpg",
  "intro":"Detroit is the center of North American automotive manufacturing — OEM assembly and the Tier-1 supply base around it, all running on returnable racks and dunnage. From Byron, GA we freight automotive racks, engine racks, and dunnage into the Detroit metro.",
  "industries":[("Automotive OEM","Line-side, sequencing, and shipping racks built to your print.","/industries/automotive/"),
                ("Automotive Tier-1","Returnable racks and dunnage that index each part for the plant.","/industries/automotive/"),
                ("Truck, Bus &amp; Powertrain","Sequencing and shipping racks for drivetrain and engine parts.","/industries/transportation-trailer/"),
                ("EV &amp; Battery","Dunnage and racks for heavy, sensitive cells and trays.","/industries/ev-battery/")],
  "prods":['automotive-racks','engine-racks','bumper-racks','returnable-steel-racks']},

 # ---- Tier 3 (curated) ----
 {"slug":"kokomo-in","city":"Kokomo","state":"IN","metro":"Kokomo, IN","home":False,
  "freight":"about a day by truck","miles":"roughly 560 miles","photo":"automotive-returnable-racks.jpg",
  "intro":"Kokomo is a concentrated automotive and EV/battery town — OEM assembly, Tier-1 supply, and new battery production. From Byron, GA we design and freight returnable automotive racks, dunnage, and battery-tray protection into the Kokomo metro.",
  "industries":[("Automotive OEM &amp; Tier-1","Line-side and shipping racks built to your print.","/industries/automotive/"),
                ("EV &amp; Battery","Dunnage and racks for heavy, sensitive cells and trays.","/industries/ev-battery/"),
                ("General Manufacturing","Custom returnable packaging for any repeatable Central Indiana line.","/industries/general-industrial/"),
                ("Industrial Machinery","Racks and weldments for machinery and OEM components.","/industries/industrial-machinery/")],
  "prods":['automotive-racks','returnable-steel-racks','dunnage','custom-foam-inserts']},

 {"slug":"lafayette-in","city":"Lafayette","state":"IN","metro":"Lafayette, IN","home":False,
  "freight":"about a day by truck","miles":"roughly 580 miles","photo":"automotive-shipping-racks.jpg",
  "intro":"Lafayette blends automotive assembly with heavy-equipment and powertrain manufacturing. From Byron, GA we build and freight returnable steel racks, automotive racks, and engine racks into the Lafayette metro.",
  "industries":[("Automotive OEM","Line-side, sequencing, and shipping racks built to your print.","/industries/automotive/"),
                ("Heavy Equipment","Rugged racks for large castings and off-highway components.","/industries/heavy-equipment/"),
                ("Truck, Bus &amp; Powertrain","Sequencing and shipping racks for drivetrain and engine parts.","/industries/transportation-trailer/"),
                ("General Manufacturing","Custom returnable packaging for any repeatable Indiana line.","/industries/general-industrial/")],
  "prods":['automotive-racks','returnable-steel-racks','engine-racks','dunnage']},

 {"slug":"fort-wayne-in","city":"Fort Wayne","state":"IN","metro":"Fort Wayne, IN","home":False,
  "freight":"about a day by truck","miles":"roughly 600 miles","photo":"automotive-returnable-racks.jpg",
  "intro":"Fort Wayne pairs automotive assembly with a deep industrial and power-equipment base. From Byron, GA we design and freight returnable automotive racks, dunnage, and industrial carts into the Fort Wayne metro.",
  "industries":[("Automotive OEM","Line-side and shipping racks for truck and vehicle assembly.","/industries/automotive/"),
                ("Industrial / Power / Electrical","Racks and reels for heavy electrical and power equipment.","/industries/energy-power/"),
                ("General Manufacturing","Custom returnable packaging for any repeatable Northeast Indiana line.","/industries/general-industrial/"),
                ("Distribution &amp; Logistics","Reusable racks and pallets that standardize how parts move.","/industries/distribution-logistics/")],
  "prods":['automotive-racks','returnable-steel-racks','dunnage','industrial-carts']},

 {"slug":"bowling-green-ky","city":"Bowling Green","state":"KY","metro":"Bowling Green, KY","home":False,
  "freight":"about 5 hours by truck","miles":"roughly 320 miles","photo":"automotive-shipping-racks.jpg",
  "intro":"Bowling Green is automotive and EV/battery country — vehicle assembly plus fast-growing battery production. From Byron, GA we’re a short freight lane away with returnable automotive racks, dunnage, and battery-tray protection.",
  "industries":[("Automotive OEM","Line-side, sequencing, and shipping racks built to your print.","/industries/automotive/"),
                ("EV &amp; Battery","Dunnage and racks for heavy, sensitive cells and trays.","/industries/ev-battery/"),
                ("General Manufacturing","Custom returnable packaging for any repeatable South-Central Kentucky line.","/industries/general-industrial/"),
                ("Appliance &amp; HVAC","Protective racks and containers for finished units and components.",None)],
  "prods":['automotive-racks','returnable-steel-racks','dunnage','custom-foam-inserts']},

 {"slug":"spring-hill-tn","city":"Spring Hill","state":"TN","metro":"Spring Hill, TN","home":False,
  "freight":"about 4½ hours by truck","miles":"roughly 290 miles","photo":"automotive-returnable-racks.jpg",
  "intro":"Spring Hill is a major automotive and EV/battery hub in Middle Tennessee. From Byron, GA we’re a short freight lane away with returnable automotive racks, dunnage, and battery packaging built to your loop.",
  "industries":[("Automotive OEM","Line-side, sequencing, and shipping racks built to your print.","/industries/automotive/"),
                ("EV &amp; Battery","Dunnage and racks for heavy, sensitive cells and trays.","/industries/ev-battery/"),
                ("General Manufacturing","Custom returnable packaging for any repeatable Middle Tennessee line.","/industries/general-industrial/"),
                ("Automotive Tier-1","Returnable racks and dunnage that index each part for the plant.","/industries/automotive/")],
  "prods":['automotive-racks','returnable-steel-racks','dunnage','custom-foam-inserts']},

 {"slug":"toledo-oh","city":"Toledo","state":"OH","metro":"Toledo, OH","home":False,
  "freight":"about 10 hours by truck","miles":"roughly 650 miles","photo":"automotive-shipping-racks.jpg",
  "intro":"Toledo is a classic automotive assembly town with a strong building-products base. From Byron, GA we build and freight returnable automotive racks, stack racks, and dunnage into the Toledo metro.",
  "industries":[("Automotive OEM","Line-side and shipping racks for vehicle assembly.","/industries/automotive/"),
                ("Furniture &amp; Building Products","Protective racks and dunnage for large, finished goods.",None),
                ("General Manufacturing","Custom returnable packaging for any repeatable Northwest Ohio line.","/industries/general-industrial/"),
                ("Distribution &amp; Logistics","Reusable racks and pallets that standardize how parts move.","/industries/distribution-logistics/")],
  "prods":['automotive-racks','returnable-steel-racks','dunnage','stack-racks']},

 {"slug":"racine-wi","city":"Racine","state":"WI","metro":"Racine, WI","home":False,
  "freight":"about a day and a half by truck","miles":"roughly 810 miles","photo":"heavy-equipment.jpg",
  "intro":"Racine has a deep heavy-equipment, appliance, and consumer-products manufacturing base. From Byron, GA we build and freight returnable steel racks, weldments, and containers into the Racine metro.",
  "industries":[("Heavy Equipment","Rugged racks for large castings, weldments, and off-highway parts.","/industries/heavy-equipment/"),
                ("Appliance &amp; HVAC","Protective racks and containers for finished units and components.",None),
                ("Food, Beverage &amp; CPG","Washable steel containers and racks for high-volume lines.","/industries/food-beverage-dairy/"),
                ("General Manufacturing","Custom returnable packaging for any repeatable Southeast Wisconsin line.","/industries/general-industrial/")],
  "prods":['returnable-steel-racks','weldments-frames','industrial-carts','returnable-containers']},

 {"slug":"rocky-mount-nc","city":"Rocky Mount","state":"NC","metro":"Rocky Mount, NC","home":False,
  "freight":"about 6 hours by truck","miles":"roughly 400 miles","photo":"heavy-equipment.jpg",
  "intro":"Rocky Mount pairs heavy-equipment and engine manufacturing with pharmaceutical and medical production. From Byron, GA we design and freight returnable steel racks, engine racks, and containers into the Rocky Mount metro.",
  "industries":[("Heavy Equipment","Rugged racks for large castings, engines, and off-highway parts.","/industries/heavy-equipment/"),
                ("Pharma &amp; Medical Device","Clean, traceable dunnage and containers for regulated products.",None),
                ("Truck, Bus &amp; Powertrain","Sequencing and shipping racks for drivetrain and engine parts.","/industries/transportation-trailer/"),
                ("General Manufacturing","Custom returnable packaging for any repeatable Eastern North Carolina line.","/industries/general-industrial/")],
  "prods":['returnable-steel-racks','engine-racks','dunnage','returnable-containers']},
]

# ---------------------------------------------------------------- CITY PAGES
def build_city(c):
    slug, city, state, metro = c["slug"], c["city"], c["state"], c["metro"]
    canonical = f"https://southernperfection.com/returnable-packaging/{slug}/"
    title = f"Returnable Packaging &amp; Steel Racks in {city}, {state} | Southern Perfection Fabrication"
    desc = (f"Returnable packaging and returnable steel racks for {metro} manufacturers — dunnage, metal containers "
            f"& rack repair, built under one roof in Byron, GA and freight-served to {city}. ISO 9001, CAGE 2W654. "
            f"Send a part or a print for a concept and a number.")
    if c["home"]:
        freight_line = f"Built {c['freight']} — on your dock the same day."
        freight_para = (f"Our plant is {c['freight']}, so {city}-area manufacturers get returnable packaging with no "
                        f"freight cost and no lead-time surprise. Design, welding, and finishing all happen "
                        f"<a href=\"/capabilities/\">under one roof</a> a short drive from your plant.")
    else:
        freight_line = f"{c['miles'].capitalize()} from our plant — {c['freight']}."
        freight_para = (f"Byron, GA to {city} is {c['miles']} — {c['freight']}. We engineer every rack to cube out the "
                        f"trailer, so you ship parts, not air, whether it moves by LTL or full truckload. Design, "
                        f"welding, and finishing all happen <a href=\"/capabilities/\">under one roof</a> before it ships.")
    faqs = [
        (f"Do you serve manufacturers in {city}, {state}?",
         f"Yes. Southern Perfection Fabrication builds returnable packaging in Byron, GA and freight-serves the {metro} market — {c['freight']} away. We design, weld, and finish every program in-house, then ship it to your plant."),
        (f"How do you ship returnable racks to {city}?",
         f"By LTL or full truckload, {c['miles']} from our Byron, GA plant. Each rack is engineered to cube out the trailer so you pay to ship parts, not air, and empties nest or fold to cut return freight."),
        ("Do you build to our print?",
         "Yes, build-to-print is our standard. Send a drawing, CAD, or a photo with dimensions and we’ll return a concept and a number — usually within a couple of business days."),
        ("Can you repair racks we already run?",
         "Yes. We inspect, re-weld, re-member, and re-finish worn returnable racks — even racks we didn’t build — back to spec, usually in 1–2 weeks per batch."),
    ]
    schema = [
        {"@context":"https://schema.org","@graph":[
            {"@type":"BreadcrumbList","itemListElement":[
                {"@type":"ListItem","position":1,"name":"Home","item":"https://southernperfection.com/"},
                {"@type":"ListItem","position":2,"name":"Returnable Packaging","item":"https://southernperfection.com/returnable-packaging/"},
                {"@type":"ListItem","position":3,"name":f"{city}, {state}","item":canonical}]},
            {"@type":"Service","name":f"Returnable Packaging for {metro}","serviceType":"Returnable steel racks, dunnage, metal containers & rack repair","provider":{"@type":"Organization","name":"Southern Perfection Fabrication","telephone":"+1-478-956-4442","address":{"@type":"PostalAddress","streetAddress":"232 Hwy 49 S","addressLocality":"Byron","addressRegion":"GA","postalCode":"31008","addressCountry":"US"}},"areaServed":{"@type":"City","name":f"{city}, {state}"}}
        ]},
        {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
            {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}
    ]
    faq_html = "\n".join(f'          <details><summary>{q}</summary><p>{a}</p></details>' for q,a in faqs)
    body = f"""    <section class="hero" aria-labelledby="h">
      <div class="wrap hero-split"><div class="hero-copy">
        <p class="eyebrow"><a href="/" style="color:inherit">Home</a> · <a href="/returnable-packaging/" style="color:inherit">Returnable Packaging</a> · {city}, {state}</p>
        <h1 id="h">Returnable packaging &amp; steel racks for {metro} manufacturers.</h1>
        <p class="lede">{c['intro']}</p>
        <div class="hero-actions"><a href="/#rfq" class="btn btn-spark btn-lg">Start an RFQ →</a><a href="/returnable-steel-racks/" class="btn btn-ghost btn-lg">See returnable steel racks</a></div>
      </div><div class="hero-media"><img src="/assets/photos/{c['photo']}" alt="Returnable packaging and steel racks built by Southern Perfection Fabrication for {city}, {state} manufacturers" width="1500" loading="eager" fetchpriority="high"></div></div>
    </section>

    <section class="section"><div class="wrap article-body">
      <p class="kicker">Freight-served to {city}</p>
      <h2>{freight_line}</h2>
      <p>{freight_para}</p>
    </div></section>

    <section class="section section-paper">
      <div class="wrap">
        <p class="kicker">Industries in {city}</p>
        <h2>Returnable packaging for {city}’s plants.</h2>
        <div class="cards-4">
{ind_cards(c['industries'])}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <p class="kicker">What we build for {city}</p>
        <h2>Racks, dunnage &amp; containers — built to your loop.</h2>
        <div class="cards-4">
{prod_cards(c['prods'])}
        </div>
        <p class="lede" style="margin-top:22px">Need another format? We also build <a href="/stack-racks/">stack racks</a>, <a href="/kanban-flow-racks/">kanban flow racks</a>, and <a href="/steel-cable-reels/">steel cable reels</a> — and we <a href="/rack-repair-refurbishment/">repair and refurbish</a> existing fleets, even racks we didn’t build.</p>
      </div>
    </section>

    <section class="section section-paper"><div class="wrap article-body">
      <p class="kicker">Proof</p>
      <h2>Built to print, delivered on time.</h2>
      <p>We engineer every {city}-bound program in-house and hold ISO 9001 quality with CAGE 2W654 traceability — the same discipline behind a <a href="/case-studies/engine-rack-program/">300+ engine-rack fleet delivered in about half the quoted lead time</a>. Explore more <a href="/case-studies/">case studies</a> or see the full <a href="/returnable-packaging/">returnable packaging line</a>.</p>
    </div></section>

    <section class="section">
      <div class="wrap">
        <p class="kicker">FAQ</p>
        <h2>Returnable packaging in {city} — answered.</h2>
        <div class="faq">
{faq_html}
        </div>
      </div>
    </section>
"""
    html = page(title, desc, canonical, schema, body,
                f"Got a part in {city} that needs a rack?",
                "Send a photo or a print — we’ll come back with a concept and a number.")
    os.makedirs(f"returnable-packaging/{slug}", exist_ok=True)
    with open(f"returnable-packaging/{slug}/index.html", "w") as f:
        f.write(html)
    print(f"wrote returnable-packaging/{slug}/index.html")

# ---------------------------------------------------------------- LOCATIONS HUB
def build_locations():
    canonical = "https://southernperfection.com/locations/"
    title = "Locations We Serve | Returnable Packaging Across the Southeast &amp; Midwest | Southern Perfection Fabrication"
    desc = ("Southern Perfection Fabrication builds returnable packaging in Byron, GA and freight-serves manufacturers "
            "across the Southeast and Midwest — Huntsville, Charlotte, Chicago, Milwaukee, Elkhart, Montgomery, "
            "Chattanooga, Clarksville, Minneapolis and beyond.")
    schema = [
        {"@context":"https://schema.org","@graph":[
            {"@type":"BreadcrumbList","itemListElement":[
                {"@type":"ListItem","position":1,"name":"Home","item":"https://southernperfection.com/"},
                {"@type":"ListItem","position":2,"name":"Locations","item":canonical}]},
            {"@type":"Organization","name":"Southern Perfection Fabrication","telephone":"+1-478-956-4442","address":{"@type":"PostalAddress","streetAddress":"232 Hwy 49 S","addressLocality":"Byron","addressRegion":"GA","postalCode":"31008","addressCountry":"US"},"areaServed":"Southeast & Midwest United States"}
        ]}
    ]
    cards = "\n".join(
        f'          <article class="card"><h3><a href="/returnable-packaging/{c["slug"]}/">{c["metro"]}</a></h3>'
        f'<p>{"Our home plant — no freight, same-day delivery." if c["home"] else "Freight-served " + c["freight"] + " from Byron, GA."}</p></article>'
        for c in CITIES)
    body = f"""    <section class="hero" aria-labelledby="h">
      <div class="wrap hero-split"><div class="hero-copy">
        <p class="eyebrow"><a href="/" style="color:inherit">Home</a> · Locations</p>
        <h1 id="h">One plant in Byron, GA. Freight-served across the corridor.</h1>
        <p class="lede">Southern Perfection Fabrication designs and builds returnable packaging under one roof in Byron, GA, then freight-serves manufacturers across the Southeast and Midwest manufacturing corridor — engineered to cube out the trailer so you ship parts, not air.</p>
        <div class="hero-actions"><a href="/#rfq" class="btn btn-spark btn-lg">Start an RFQ →</a><a href="/returnable-packaging/" class="btn btn-ghost btn-lg">Returnable packaging</a></div>
      </div><div class="hero-media"><img src="/assets/photos/metal-fabrication-shop.jpg" alt="Southern Perfection Fabrication metal fabrication shop floor in Byron, GA" width="1500" loading="eager" fetchpriority="high"></div></div>
    </section>

    <section class="section section-paper">
      <div class="wrap">
        <p class="kicker">Metros we serve</p>
        <h2>Returnable packaging, delivered to your plant.</h2>
        <div class="cards-4">
{cards}
        </div>
        <p class="lede" style="margin-top:22px">Don’t see your city? We ship nationwide — <a href="/#rfq">send your part</a> and we’ll quote the lane with the build.</p>
      </div>
    </section>
"""
    html = page(title, desc, canonical, schema, body,
                "Need returnable packaging in your metro?",
                "Send a photo or a print — we’ll quote the build and the freight.")
    os.makedirs("locations", exist_ok=True)
    with open("locations/index.html", "w") as f:
        f.write(html)
    print("wrote locations/index.html")

# ---------------------------------------------------------------- run
def build_custom_manufacturing():
    canonical = "https://southernperfection.com/custom-manufacturing/"
    title = "Custom Metal Fabrication &amp; Contract Manufacturing | Southern Perfection Fabrication"
    desc = ("Custom metal fabrication and contract manufacturing under one roof in Byron, GA — weldments, "
            "industrial steel structures, sheet metal, machine guards & high-volume production. Laser, forming, "
            "robotic welding, machining & powder coat. ISO 9001, CAGE 2W654. Build to print.")
    faqs = [
        ("Do you do contract manufacturing and build to print?", "Yes — build-to-print contract manufacturing is core to what we do. Send a drawing, CAD, or a sample and we'll quote and produce it, from one-off weldments to high-volume runs, under one roof in Byron, GA."),
        ("What can you fabricate?", "Weldments and frames, industrial steel structures, sheet metal parts, machine guards and platforms, and high-volume fabricated assemblies. We laser-cut, form (press brake to 230 tons), CNC-machine, robotic-weld, and powder-coat in-house."),
        ("What certifications do you hold?", "ISO 9001 quality management and CAGE Code 2W654 for defense and government work, with in-house inspection including CMM."),
        ("Can you handle high-volume production?", "Yes. With 30+ MIG stations plus FANUC robotic welding and one of the Southeast's largest powder-coat ovens, we run repeatable high-volume production while holding tolerance and finish."),
    ]
    schema = [
        {"@context":"https://schema.org","@graph":[
            {"@type":"BreadcrumbList","itemListElement":[
                {"@type":"ListItem","position":1,"name":"Home","item":"https://southernperfection.com/"},
                {"@type":"ListItem","position":2,"name":"Custom Manufacturing","item":canonical}]},
            {"@type":"Service","name":"Custom Metal Fabrication & Contract Manufacturing","serviceType":"Weldments, structures, sheet metal, machine guards & high-volume production","provider":{"@type":"Organization","name":"Southern Perfection Fabrication","telephone":"+1-478-956-4442","address":{"@type":"PostalAddress","streetAddress":"232 Hwy 49 S","addressLocality":"Byron","addressRegion":"GA","postalCode":"31008","addressCountry":"US"}},"areaServed":"United States"}
        ]},
        {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
            {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}
    ]
    faq_html = "\n".join(f'          <details><summary>{q}</summary><p>{a}</p></details>' for q,a in faqs)
    body = f"""    <section class="hero" aria-labelledby="h">
      <div class="wrap hero-split"><div class="hero-copy">
        <p class="eyebrow"><a href="/" style="color:inherit">Home</a> · Custom Manufacturing</p>
        <h1 id="h">Custom metal fabrication &amp; contract manufacturing.</h1>
        <p class="lede">Beyond returnable packaging, Southern Perfection Fabrication is a full-service <strong>custom metal fabricator and contract manufacturer</strong> — weldments, industrial structures, sheet metal, machine guards, and high-volume production, engineered and built to your print under one roof in Byron, GA. Send a drawing or a sample and we’ll quote it.</p>
        <div class="hero-actions"><a href="/#rfq" class="btn btn-spark btn-lg">Start an RFQ →</a><a href="/capabilities/" class="btn btn-ghost btn-lg">See capabilities</a></div>
      </div><div class="hero-media"><img src="/assets/photos/metal-fabrication-shop.jpg" alt="Custom metal fabrication and contract manufacturing at Southern Perfection Fabrication in Byron, GA" width="1500" loading="eager" fetchpriority="high"></div></div>
    </section>

    <section class="section"><div class="wrap article-body">
      <p class="kicker">Custom manufacturing</p>
      <h2>One-roof contract manufacturing, built to print.</h2>
      <p>From a single prototype to a high-volume production run, we take your drawing, CAD, or sample and turn it into finished, inspected steel. Design (in-house SolidWorks), laser and plasma cutting, CNC forming to 230 tons, CNC machining, 30+ MIG stations plus FANUC robotic welding, and powder coating all happen <a href="/capabilities/">under one roof</a> — one vendor, one PO, one accountable partner since 1982.</p>
    </div></section>

    <section class="section section-paper">
      <div class="wrap">
        <p class="kicker">What we build</p>
        <h2>Custom fabrication, end to end.</h2>
        <div class="cards-4">
          <article class="card"><h3><a href="/capabilities/">Contract Manufacturing</a></h3><p>Build-to-print production of your parts and assemblies, one-off to high volume.</p></article>
          <article class="card"><h3><a href="/weldments-frames/">Weldments &amp; Frames</a></h3><p>Precision welded frames, bases, and structures to your drawing.</p></article>
          <article class="card"><h3><a href="/industrial-structures/">Industrial Structures</a></h3><p>Mezzanines, platforms, and heavy structural steel fabrication.</p></article>
          <article class="card"><h3><a href="/sheet-metal-fabrication/">Sheet Metal Fabrication</a></h3><p>Precision sheet metal parts, enclosures, and brackets.</p></article>
          <article class="card"><h3><a href="/guards-platforms/">Machine Guards &amp; Platforms</a></h3><p>Safety guarding, access platforms, and mezzanines to spec.</p></article>
          <article class="card"><h3><a href="/high-volume-manufacturing/">High-Volume Production</a></h3><p>Repeatable, robotic-welded runs that hold tolerance and finish.</p></article>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <p class="kicker">Why SPF</p>
        <h2>The one-roof fabricator OEMs standardize on.</h2>
        <div class="cards-4">
          <article class="card"><h3>One Roof</h3><p>Design, cutting, forming, machining, welding &amp; finishing in-house — one vendor, one PO.</p></article>
          <article class="card"><h3>ISO 9001 / CAGE</h3><p>ISO 9001 quality and CAGE 2W654 with in-house CMM inspection.</p></article>
          <article class="card"><h3>230-Ton + Robotic</h3><p>Press-brake forming to 230 tons; 30+ MIG stations plus FANUC robotic welding.</p></article>
          <article class="card"><h3>Powder Coat</h3><p>One of the largest powder-coat ovens in the Southeast for a finish that lasts.</p></article>
        </div>
      </div>
    </section>

    <section class="section section-paper"><div class="wrap article-body">
      <p class="kicker">Capabilities</p>
      <h2>Every process, in-house.</h2>
      <p>Explore the full shop: <a href="/capabilities/laser-cutting/">laser &amp; plasma cutting</a>, <a href="/capabilities/forming/">CNC forming &amp; bending</a>, <a href="/capabilities/cnc-machining/">CNC machining</a>, <a href="/capabilities/robotic-welding/">robotic welding</a>, <a href="/capabilities/powder-coating/">powder coating &amp; finishing</a>, <a href="/capabilities/design-engineering/">design &amp; engineering</a>, and <a href="/capabilities/quality-inspection/">quality &amp; inspection</a>. See <a href="/capabilities/">all capabilities</a>, or our returnable side at <a href="/returnable-packaging/">returnable packaging</a>.</p>
    </div></section>

    <section class="section">
      <div class="wrap">
        <p class="kicker">FAQ</p>
        <h2>Custom manufacturing — answered.</h2>
        <div class="faq">
{faq_html}
        </div>
      </div>
    </section>
"""
    html = page(title, desc, canonical, schema, body,
                "Have a print that needs a fabricator?",
                "Send a drawing or a sample — we’ll quote it and build it under one roof.")
    os.makedirs("custom-manufacturing", exist_ok=True)
    with open("custom-manufacturing/index.html", "w") as f:
        f.write(html)
    print("wrote custom-manufacturing/index.html")


def build_roi():
    canonical = "https://southernperfection.com/returnable-packaging-roi/"
    title = "Returnable Packaging ROI Calculator — Returnable vs. Disposable | Southern Perfection Fabrication"
    desc = ("Free returnable packaging ROI calculator — compare returnable steel racks vs. disposable packaging by "
            "cost per trip, payback period, and annual savings. Plug in your own numbers. Built by Southern "
            "Perfection Fabrication, Byron, GA.")
    faqs = [
        ("How do you calculate returnable packaging ROI?", "The metric that matters is cost per trip: a returnable rack's one-time cost spread across the trips it makes, plus return freight and upkeep — versus the recurring cost of disposable packaging and the transit damage it lets through. When cost per trip beats disposable, the fleet pays for itself. This calculator estimates your payback period, annual savings, and cost per trip from your numbers."),
        ("What's a typical payback period for returnable racks?", "It depends on volume and damage rates, but engineered correctly, returnable steel racks commonly pay back in well under a year on high-volume lanes — then keep saving for years, because the same racks run hundreds of trips."),
        ("Does returnable packaging really cut transit damage?", "Yes — usually the biggest hidden cost of disposable. A rack designed to index and protect each part largely eliminates the shifting and crushing that expendable packaging allows, cutting scrap, rework, and line-down."),
        ("Can you give me exact numbers for my parts?", "Yes. The calculator is a planning estimate. Send your parts, volumes, and freight lanes and we'll return exact costing with the quote — the same design-to-print process behind our rack programs."),
    ]
    schema = [
        {"@context":"https://schema.org","@graph":[
            {"@type":"BreadcrumbList","itemListElement":[
                {"@type":"ListItem","position":1,"name":"Home","item":"https://southernperfection.com/"},
                {"@type":"ListItem","position":2,"name":"Returnable Packaging","item":"https://southernperfection.com/returnable-packaging/"},
                {"@type":"ListItem","position":3,"name":"ROI Calculator","item":canonical}]},
            {"@type":"WebApplication","name":"Returnable Packaging ROI Calculator","applicationCategory":"BusinessApplication","operatingSystem":"Web","offers":{"@type":"Offer","price":"0","priceCurrency":"USD"},"provider":{"@type":"Organization","name":"Southern Perfection Fabrication","telephone":"+1-478-956-4442"}}
        ]},
        {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
            {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}
    ]
    faq_html = "\n".join(f'          <details><summary>{q}</summary><p>{a}</p></details>' for q,a in faqs)
    # NOTE: plain (non-f) string — contains JS braces.
    body = """    <section class="hero" aria-labelledby="h">
      <div class="wrap hero-split"><div class="hero-copy">
        <p class="eyebrow"><a href="/" style="color:inherit">Home</a> · <a href="/returnable-packaging/" style="color:inherit">Returnable Packaging</a> · ROI Calculator</p>
        <h1 id="h">Returnable packaging ROI calculator.</h1>
        <p class="lede">See what switching from disposable packaging to <strong>returnable steel racks</strong> is worth — cost per trip, payback period, and annual savings. Plug in your numbers below, then send us your parts for exact costing.</p>
      </div><div class="hero-media"><img src="/assets/photos/returnable-racks-fleet.jpg" alt="Returnable steel rack fleet built by Southern Perfection Fabrication in Byron, GA" width="1500" loading="eager" fetchpriority="high"></div></div>
    </section>

    <section class="section"><div class="wrap">
      <p class="kicker">Returnable vs. disposable</p>
      <h2>Run your numbers.</h2>
      <div class="roi-grid">
        <div class="roi-inputs">
          <h3>Your numbers</h3>
          <label>Annual shipments<input id="roi-n" class="roi-input" type="number" value="5000" min="0"></label>
          <label>Disposable packaging cost per shipment ($)<input id="roi-d" class="roi-input" type="number" value="18" min="0" step="0.5"></label>
          <label>Transit damage rate (%)<input id="roi-dr" class="roi-input" type="number" value="3" min="0" step="0.1"></label>
          <label>Average cost per damage incident ($)<input id="roi-dc" class="roi-input" type="number" value="250" min="0"></label>
          <label>Returnable rack cost, each ($)<input id="roi-rc" class="roi-input" type="number" value="600" min="0"></label>
          <label>Trips per rack, per year<input id="roi-tpr" class="roi-input" type="number" value="40" min="1"></label>
          <label>Return freight per trip ($)<input id="roi-rf" class="roi-input" type="number" value="3" min="0" step="0.5"></label>
        </div>
        <div class="roi-results">
          <div class="roi-hero"><span class="roi-hero-label">Payback period</span><span id="r-payback" class="roi-hero-num">—</span></div>
          <div class="roi-stats">
            <div class="roi-stat"><span id="r-save" class="roi-stat-num">—</span><span class="roi-stat-label">Annual savings</span></div>
            <div class="roi-stat"><span id="r-net3" class="roi-stat-num">—</span><span class="roi-stat-label">3-year net savings</span></div>
            <div class="roi-stat"><span id="r-cpt-ret" class="roi-stat-num">—</span><span class="roi-stat-label">Cost/trip · returnable</span></div>
            <div class="roi-stat"><span id="r-cpt-disp" class="roi-stat-num">—</span><span class="roi-stat-label">Cost/trip · disposable</span></div>
            <div class="roi-stat"><span id="r-dmg" class="roi-stat-num">—</span><span class="roi-stat-label">Transit damage avoided</span></div>
            <div class="roi-stat"><span id="r-fleet" class="roi-stat-num">—</span><span class="roi-stat-label">Fleet · <span id="r-invest">—</span> invest</span></div>
          </div>
          <a href="/#rfq" class="btn btn-spark btn-lg">Get this costed for your parts →</a>
          <p class="roi-note">Planning estimate only. Send your parts, volumes, and lanes and we’ll return exact numbers with the quote.</p>
        </div>
      </div>
    </div></section>

    <section class="section section-paper"><div class="wrap article-body">
      <p class="kicker">How the math works</p>
      <h2>It comes down to cost per trip.</h2>
      <p>Disposable packaging is a cost you pay <em>every single shipment</em> — plus the transit damage it lets through, which shows up as scrap, rework, and line-down. A <a href="/returnable-steel-racks/">returnable steel rack</a> is a one-time investment that runs hundreds of trips, so its cost per trip keeps falling while protecting the part every time. The calculator divides your rack fleet cost across its trips, adds return freight and light upkeep, then compares that to what disposable is costing you today. When you’re ready, we’ll <a href="/#rfq">cost it exactly</a> for your parts — or read the deeper <a href="/returnable-vs-expendable-packaging/">returnable vs. expendable</a> breakdown.</p>
    </div></section>

    <section class="section">
      <div class="wrap">
        <p class="kicker">FAQ</p>
        <h2>Returnable packaging ROI — answered.</h2>
        <div class="faq">
""" + faq_html + """
        </div>
      </div>
    </section>

    <script>
    (function(){
      function num(id){ var v = parseFloat(document.getElementById(id).value); return isNaN(v) ? 0 : v; }
      function money(x){ return '$' + Math.round(x).toLocaleString(); }
      function calc(){
        var n=num('roi-n'), d=num('roi-d'), dr=num('roi-dr')/100, dc=num('roi-dc'),
            rc=num('roi-rc'), tpr=num('roi-tpr'), rf=num('roi-rf');
        if(tpr<=0){ tpr=1; }
        var racks = Math.ceil(n/tpr);
        var invest = racks*rc;
        var dispAnnual = n*d + n*dr*dc;
        var retAnnual = n*rf + invest*0.03 + n*dr*0.1*dc;   /* return freight + ~3% upkeep + ~90% less damage */
        var save = dispAnnual - retAnnual;
        var payback = save>0 ? invest/save : 0;
        var net3 = 3*dispAnnual - (invest + 3*retAnnual);
        var cptRet = n>0 ? (invest + 3*retAnnual)/(3*n) : 0;
        var cptDisp = n>0 ? dispAnnual/n : 0;
        var dmgAvoid = n*dr*dc*0.9;
        function set(id,v){ var e=document.getElementById(id); if(e){ e.textContent=v; } }
        set('r-payback', payback>0 ? (payback<1 ? Math.max(1,Math.round(payback*12))+' mo' : payback.toFixed(1)+' yr') : '—');
        set('r-save', save>0 ? money(save)+'/yr' : '—');
        set('r-net3', money(net3));
        set('r-cpt-ret', money(cptRet));
        set('r-cpt-disp', money(cptDisp));
        set('r-dmg', money(dmgAvoid)+'/yr');
        set('r-fleet', racks.toLocaleString()+' racks');
        set('r-invest', money(invest));
      }
      var els = document.querySelectorAll('.roi-input');
      for(var i=0;i<els.length;i++){ els[i].addEventListener('input', calc); }
      calc();
    })();
    </script>
"""
    html = page(title, desc, canonical, schema, body,
                "Want this costed for your exact parts?",
                "Send your parts, volumes, and lanes — we’ll return real numbers with the quote.")
    os.makedirs("returnable-packaging-roi", exist_ok=True)
    with open("returnable-packaging-roi/index.html", "w") as f:
        f.write(html)
    print("wrote returnable-packaging-roi/index.html")


if __name__ == "__main__":
    build_pillar()
    build_custom_manufacturing()
    build_roi()
    for c in CITIES:
        build_city(c)
    build_locations()
    print(f"\nDONE: 2 pillars + ROI calc + {len(CITIES)} city pages + 1 locations hub = {len(CITIES)+4} pages")

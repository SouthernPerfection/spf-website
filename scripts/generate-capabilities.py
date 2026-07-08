#!/usr/bin/env python3
"""Generate the Capabilities sub-pages with REAL specs from SPF's 2026 brochure.
Run from website/ root: python3 scripts/generate-capabilities.py
Then run scripts/apply-header.py to inject the shared mega menu.
"""
import pathlib, json
ROOT = pathlib.Path(__file__).resolve().parent.parent

CAPS = [
  ("design-engineering","Design & Engineering","Design & Engineering — In-House SolidWorks | Southern Perfection",
   "In-house SolidWorks design and engineering — we turn your math data, print, or a rough idea into a buildable, production-ready part. Design-for-manufacture in Byron, GA. ISO 9001, CAGE 2W654.",
   "Design &amp; engineering, in-house.",
   "In-house <strong>SolidWorks</strong> engineering turns your math data — or a rough idea — into a buildable, production-ready part. Design-for-manufacture from day one, so it cuts, forms, welds, and finishes clean.",
   [("SolidWorks","Full 3D CAD from your math data, print, or concept."),
    ("Design-for-Manufacture","Engineered for weldability, cost, and durability up front."),
    ("Prototype to Production","Fast iteration because design and the floor share one roof."),
    ("Built to Your Standards","Validated to your part, loop, and load before we cut steel.")]),
  ("laser-cutting","Laser & Plasma Cutting","Laser & Plasma Cutting | Southern Perfection",
   "CNC laser and plasma cutting for clean, precise, repeatable parts — in carbon steel, stainless, aluminum, and magnesium. One-roof fabrication in Byron, GA. ISO 9001, CAGE 2W654.",
   "Laser &amp; plasma cutting.",
   "CNC <strong>laser and plasma cutting</strong> for clean, precise, repeatable parts — feeding straight into forming and welding without leaving the building. Carbon steel, stainless, aluminum, and magnesium.",
   [("CNC Laser","Precision laser cutting for clean, repeatable parts."),
    ("Plasma Cutting","Plasma for heavier plate and structural cuts."),
    ("Materials","Carbon steel, stainless, aluminum, and magnesium."),
    ("Repeatable","Programmed cuts for build-to-print consistency at volume.")]),
  ("forming","CNC Forming & Bending","CNC Forming, Press Brake & Bending | Southern Perfection",
   "CNC press-brake forming to 230 tons, CNC tube bending, and plate rolling — accurate, repeatable metal forming under one roof in Byron, GA. ISO 9001, CAGE 2W654.",
   "CNC forming &amp; bending.",
   "<strong>Press-brake forming to 230 tons</strong>, CNC tube bending, and plate rolling — accurate, repeatable forming that shapes the steel for your racks, frames, and assemblies.",
   [("Press Brake to 230 Tons","Heavy CNC press-brake forming for precise, repeatable bends."),
    ("CNC Tube Bending","Tube and pipe bending to your radius and spec."),
    ("Plate Rolling","Rolling for cradles, saddles, and cylindrical shapes."),
    ("To Print","Formed to your drawing and validated for fit-up.")]),
  ("cnc-machining","CNC Machining","CNC Machining — Turning & Milling | Southern Perfection",
   "Precision CNC machining — turning and milling for machined components and features — integrated with cutting, forming, welding, and finishing under one roof in Byron, GA. ISO 9001.",
   "CNC machining.",
   "Precision <strong>CNC machining</strong> — turning and milling for machined components and features — integrated with the rest of fabrication so machined parts and weldments come together under one roof.",
   [("CNC Turning","Precision turned components to your print."),
    ("CNC Milling","Milled features and components, any complexity."),
    ("Integrated","Machining feeds welding and assembly in the same building."),
    ("Any Volume","Prototype through production runs.")]),
  ("robotic-welding","Welding","Welding — MIG, TIG & FANUC Robotic | Southern Perfection",
   "MIG and TIG welding across 30+ stations, plus FANUC robotic welding — consistent, repeatable welds at production volume. One-roof fabrication in Byron, GA. ISO 9001, CAGE 2W654.",
   "Welding — 30+ stations &amp; robotic.",
   "MIG and TIG welding across <strong>30+ stations</strong>, plus <strong>FANUC robotic welding</strong> — consistent, repeatable welds at production volume, the backbone of every rack and weldment we build.",
   [("30+ MIG/TIG Stations","Deep manual welding capacity for any job size."),
    ("FANUC Robotic Welding","Automated cells for repeatable, high-volume welds."),
    ("Consistency","Programmed welds mean the 10,000th part matches the first."),
    ("Weldments &amp; Frames","Robotic-welded frames and assemblies at production volume.")]),
  ("powder-coating","Finishing","Finishing — Wet Paint & Powder Coat | Southern Perfection",
   "In-house wet paint and powder coat — one of the largest powder-coat ovens in the Southeast — for durable finishes that survive the loop. One-roof fabrication in Byron, GA. ISO 9001.",
   "Finishing — paint &amp; powder coat.",
   "In-house <strong>wet paint and powder coat</strong> — one of the <strong>largest powder-coat ovens in the Southeast</strong> — so every part ships finished, not waiting on an outside coater.",
   [("Powder Coat","One of the largest powder-coat ovens in the Southeast."),
    ("Wet Paint","Wet paint finishing where the spec calls for it."),
    ("Durable","Finishes engineered to survive the returnable loop."),
    ("In-House","No outside coater, no second shop's queue.")]),
  ("quality-inspection","Quality & Inspection","Quality, CMM Inspection & ISO 9001 | Southern Perfection",
   "An ISO 9001 quality system with CAGE 2W654 and CMM inspection — the traceability and documentation OEM and defense programs require. Byron, GA, family-owned since 1982.",
   "Quality &amp; inspection.",
   "A certified quality system built for OEM and defense work — <strong>ISO 9001</strong>, <strong>CAGE 2W654</strong>, and CMM inspection, with the documentation and traceability your programs demand.",
   [("ISO 9001","Certified quality management system."),
    ("CAGE 2W654","Defense-registered traceability for government work."),
    ("CMM Inspection","Coordinate-measuring inspection to your print."),
    ("40+ Years","Four generations, one facility, since 1982.")]),
]

TPL = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>__TITLE__</title>
  <meta name="description" content="__DESC__">
  <link rel="canonical" href="https://southernperfection.com/capabilities/__SLUG__/">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta property="og:type" content="website"><meta property="og:site_name" content="Southern Perfection Fabrication">
  <meta property="og:title" content="__NAME__ | Southern Perfection"><meta property="og:url" content="https://southernperfection.com/capabilities/__SLUG__/">
  <meta property="og:description" content="__DESC__">
  <meta property="og:image" content="https://southernperfection.com/assets/og-cover.jpg">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;600;700&display=swap">
  <link rel="stylesheet" href="/assets/styles.css">
  <script type="application/ld+json">
  __SCHEMA__
  </script>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header"><div class="wrap header-inner"><a href="/" class="brand"><span class="brand-mark"></span><span class="brand-text">SOUTHERN&nbsp;PERFECTION</span></a><div class="header-cta"><a href="tel:+14789564442" class="phone">478-956-4442</a><a href="/#rfq" class="btn btn-spark">Start an RFQ</a></div></div></header>
  <main id="main">
    <section class="hero" aria-labelledby="h"><div class="wrap">
      <p class="eyebrow"><a href="/" style="color:inherit">Home</a> · <a href="/capabilities/" style="color:inherit">Capabilities</a> · __NAME__</p>
      <h1 id="h">__H1__</h1>
      <p class="lede">__INTRO__</p>
      <div class="hero-actions"><a href="/#rfq" class="btn btn-spark btn-lg">Start an RFQ →</a><a href="/capabilities/" class="btn btn-ghost btn-lg">All capabilities</a></div>
    </div></section>
    <section class="section"><div class="wrap">
      <p class="kicker">__NAME__</p><h2>Under one roof in Byron, GA.</h2>
      <div class="cards-4">__CARDS__</div>
    </div></section>
    <section class="cta-band"><div class="wrap center">
      <h2 class="h-light">Have a part to quote?</h2><p class="lede lede-light">Send a drawing — we'll come back with a real price and lead time.</p>
      <a href="/#rfq" class="btn btn-spark btn-lg">Start an RFQ →</a>
    </div></section>
  </main>
  <footer class="site-footer"><div class="wrap footer-grid">
    <div><span class="brand-text">SOUTHERN PERFECTION FABRICATION</span><p class="footer-mono">Complete metal fabrication under one roof</p><p class="footer-mono">ISO 9001 · CAGE 2W654 · Est. 1982 · Byron, GA</p></div>
    <nav aria-label="Footer"><ul><li><a href="/capabilities/">Capabilities</a></li><li><a href="/returnable-steel-racks/">Returnable Racks</a></li><li><a href="/case-studies/">Case Studies</a></li><li><a href="/industries/">Industries</a></li><li><a href="/managed-programs/">Managed Programs</a></li><li><a href="/contact/">Contact</a></li></ul></nav>
    <div class="footer-contact"><a href="tel:+14789564442" class="phone">478-956-4442</a><br><span class="footer-mono">232 Hwy 49 S · Byron, GA 31008</span></div>
  </div><div class="wrap footer-legal"><small>© 2026 Southern Perfection Fabrication. All rights reserved.</small></div></footer>
</body>
</html>
"""

for slug,name,title,desc,h1,intro,cards in CAPS:
    schema = {"@context":"https://schema.org","@graph":[
        {"@type":"BreadcrumbList","itemListElement":[
            {"@type":"ListItem","position":1,"name":"Home","item":"https://southernperfection.com/"},
            {"@type":"ListItem","position":2,"name":"Capabilities","item":"https://southernperfection.com/capabilities/"},
            {"@type":"ListItem","position":3,"name":name.replace("&amp;","&"),"item":f"https://southernperfection.com/capabilities/{slug}/"}]},
        {"@type":"Service","name":name.replace("&amp;","&"),"provider":{"@type":"Organization","name":"Southern Perfection Fabrication","telephone":"+1-478-956-4442"}}]}
    cards_html = "".join(f'<article class="card"><h3>{c[0]}</h3><p>{c[1]}</p></article>' for c in cards)
    html = (TPL.replace("__TITLE__",title).replace("__DESC__",desc).replace("__SLUG__",slug)
               .replace("__NAME__",name).replace("__H1__",h1).replace("__INTRO__",intro)
               .replace("__CARDS__",cards_html).replace("__SCHEMA__",json.dumps(schema, ensure_ascii=False)))
    d = ROOT / "capabilities" / slug
    d.mkdir(parents=True, exist_ok=True)
    (d/"index.html").write_text(html)
    print(" -", f"capabilities/{slug}/")
print("Done.")

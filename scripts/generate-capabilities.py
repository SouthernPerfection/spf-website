#!/usr/bin/env python3
"""Generate the Capabilities sub-pages. Run from website/ root: python3 scripts/generate-capabilities.py
Header is a placeholder; run scripts/apply-header.py afterward to inject the shared mega menu.
Spec placeholders marked [from brochure] — fill from SPF's real brochure before publishing.
"""
import pathlib, json
ROOT = pathlib.Path(__file__).resolve().parent.parent

CAPS = [
  ("design-engineering","Design & Engineering","Design & Engineering — Returnable Packaging Design | Southern Perfection",
   "In-house design and engineering for returnable racks, containers, and dunnage — design-for-manufacture, CAD, validation, and prototyping under one roof in Byron, GA.",
   "Design &amp; engineering, in-house.",
   "Our engineering team turns your part and print into a validated, build-ready returnable design — design-for-manufacture from day one so it welds clean, ships dense, and runs for years.",
   [("Design-for-Manufacture","We design for weldability, cost, and durability from the first concept."),
    ("CAD &amp; Engineering","Full CAD and engineering to your standards. [Software/CAE — from brochure]"),
    ("Validation","Designs validated to your part, loop, and load before we cut steel."),
    ("Prototyping","Fast prototype-to-production because design and the floor share one roof.")]),
  ("laser-cutting","Laser Cutting","Laser Cutting &amp; Tube Laser Cutting | Southern Perfection",
   "In-house laser cutting and tube laser cutting for precision steel parts — fast, accurate, repeatable. Part of one-roof fabrication in Byron, GA. ISO 9001, CAGE 2W654.",
   "Laser cutting &amp; tube laser.",
   "Precision <strong>laser cutting</strong> and tube laser cutting in-house — accurate, repeatable parts that feed straight into welding and forming without leaving the building.",
   [("Sheet Laser","Precision flat-sheet laser cutting. [Bed size / max thickness — from brochure]"),
    ("Tube Laser","Tube and structural laser cutting for clean, weld-ready joints."),
    ("Materials","Carbon steel, stainless, and more. [Material range — from brochure]"),
    ("Repeatable","Programmed, repeatable cuts for build-to-print consistency at volume.")]),
  ("robotic-welding","Robotic Welding","Robotic Welding &amp; Fabrication | Southern Perfection",
   "Robotic welding and precision fabrication for returnable steel racks and assemblies — consistent, repeatable welds at volume. One-roof fabrication in Byron, GA. ISO 9001.",
   "Robotic welding &amp; fabrication.",
   "<strong>Robotic welding</strong> delivers consistent, repeatable welds at volume — the backbone of build-to-print quality on every rack, container, and assembly we make.",
   [("Robotic Cells","Automated welding cells for repeatable, high-volume production. [Cells/reach — from brochure]"),
    ("Weld Processes","MIG, TIG, and robotic processes to suit the part. [Processes — from brochure]"),
    ("Consistency","Programmed welds mean the 10,000th part matches the first."),
    ("Manual Too","Skilled manual welding where the part calls for it.")]),
  ("cnc-machining","CNC Machining","CNC Machining | Southern Perfection Fabrication",
   "Precision CNC machining in-house — milling and turning to close tolerances for any complexity or volume. Part of one-roof fabrication in Byron, GA. ISO 9001, CAGE 2W654.",
   "CNC machining, any complexity.",
   "Precision <strong>CNC machining</strong> — milling and turning to close tolerances — integrated with the rest of fabrication so machined features and welded structures come together under one roof.",
   [("Milling &amp; Turning","Multi-axis CNC milling and turning. [Envelope / axes — from brochure]"),
    ("Tolerances","Close-tolerance machining to your print. [Tolerance range — from brochure]"),
    ("Any Volume","From prototype to production runs."),
    ("Integrated","Machining feeds welding and assembly without leaving the building.")]),
  ("forming","Forming","Metal Forming &amp; Press Brake | Southern Perfection",
   "In-house metal forming and press-brake bending for returnable racks and steel assemblies — accurate, repeatable forms. One-roof fabrication in Byron, GA. ISO 9001.",
   "Forming &amp; press brake.",
   "In-house <strong>metal forming</strong> and press-brake bending shapes the steel that becomes your racks and containers — accurate, repeatable, and ready for welding.",
   [("Press Brake","CNC press-brake forming for precise, repeatable bends. [Max length / tonnage — from brochure]"),
    ("Rolling &amp; Shaping","Forming for cradles, saddles, and structural shapes."),
    ("To Print","Formed to your drawing and validated for fit-up."),
    ("Volume Ready","Repeatable setups for production quantities.")]),
  ("powder-coating","Powder Coating","Powder Coating &amp; Finishing | Southern Perfection",
   "In-house powder coating and finishing — durable, full-color coatings for returnable racks that survive the loop. One-roof fabrication in Byron, GA. ISO 9001, CAGE 2W654.",
   "Powder coating &amp; finishing.",
   "In-house <strong>powder coating</strong> and finishing gives every rack a durable, consistent finish that survives years of trips — no outsourcing, no handoffs.",
   [("In-House Line","Full powder-coat line under one roof. [Part size / booth — from brochure]"),
    ("Full Color","Full color and finish capability. [Colors / spec — from brochure]"),
    ("Durable","Finishes engineered to survive the returnable loop, not just look good."),
    ("Pretreatment","Proper prep and pretreatment for coating adhesion and life.")]),
  ("quality-inspection","CMM Inspection & Quality","CMM Inspection &amp; ISO 9001 Quality | Southern Perfection",
   "CMM inspection and an ISO 9001 quality system with CAGE 2W654 — the traceability and inspection OEM and defense programs require. Byron, GA.",
   "CMM inspection &amp; quality.",
   "A formal quality system built for OEM and defense work — <strong>CMM inspection</strong>, ISO 9001 processes, and CAGE 2W654 traceability, with the documentation your programs demand.",
   [("CMM Inspection","Coordinate-measuring inspection to your print. [CMM model / capacity — from brochure]"),
    ("ISO 9001","A certified ISO 9001 quality management system."),
    ("CAGE 2W654","Government-ready traceability for defense and federal work."),
    ("Reporting","Inspection reports and documentation. [PPAP/FAI as applicable — from brochure]")]),
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
      <p class="kicker">__NAME__</p><h2>Under one roof.</h2>
      <div class="cards-4">__CARDS__</div>
      <p style="margin-top:1.4rem;color:var(--steel)"><em>Bracketed specs to be filled from SPF's capability brochure.</em></p>
    </div></section>
    <section class="cta-band"><div class="wrap center">
      <h2 class="h-light">Have a part to quote?</h2><p class="lede lede-light">Send a print — we'll turn around a concept and a number.</p>
      <a href="/#rfq" class="btn btn-spark btn-lg">Start an RFQ →</a>
    </div></section>
  </main>
  <footer class="site-footer"><div class="wrap footer-grid">
    <div><span class="brand-text">SOUTHERN PERFECTION FABRICATION</span><p class="footer-mono">Returnable steel racks &amp; material handling</p><p class="footer-mono">ISO 9001 · CAGE 2W654 · Est. 1982 · Byron, GA</p></div>
    <nav aria-label="Footer"><ul><li><a href="/capabilities/">Capabilities</a></li><li><a href="/returnable-steel-racks/">Returnable Racks</a></li><li><a href="/case-studies/">Case Studies</a></li><li><a href="/industries/">Industries</a></li><li><a href="/managed-programs/">Managed Programs</a></li><li><a href="/contact/">Contact</a></li></ul></nav>
    <div class="footer-contact"><a href="tel:+14789564442" class="phone">478-956-4442</a><br><span class="footer-mono">Byron, GA</span></div>
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

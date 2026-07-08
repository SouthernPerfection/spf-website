#!/usr/bin/env python3
"""Generate the new 'What We Build' product pages. Run from website/ root.
Then run scripts/apply-header.py to inject the shared mega menu.
Card/FAQ bodies may contain inline HTML (links) — not escaped.
"""
import pathlib, json
ROOT = pathlib.Path(__file__).resolve().parent.parent

PAGES = [
  ("automotive-racks","Automotive Racks","Automotive Racks — Engine, Bumper, Coil & Tire Racks | Southern Perfection",
   "Custom returnable automotive racks — engine racks, bumper racks, coil racks, and tire racks — engineered to your parts and built to print. ISO 9001, CAGE 2W654, Byron, GA.",
   "Automotive racks, built to your parts.",
   "Custom returnable <strong>automotive racks</strong> engineered to your parts and your line — from <a href=\"/returnable-steel-racks/\">returnable steel racks</a> to part-specific engine, bumper, coil, and tire racks, built to print under one roof.",
   [("Engine Racks","Shipping and WIP racks for engines and powertrain — <a href=\"/engine-racks/\">see engine racks &rarr;</a>"),
    ("Bumper Racks","Protective racks for bumpers and fascias — <a href=\"/bumper-racks/\">see bumper racks &rarr;</a>"),
    ("Coil Racks","Cradles and racks for coils and rolls — <a href=\"/coil-racks/\">see coil racks &rarr;</a>"),
    ("Tire &amp; Wheel Racks","Racks for tires and wheels — <a href=\"/tire-racks/\">see tire racks &rarr;</a>")],
   [("Do you build part-specific automotive racks?","Yes. We design returnable racks around your specific part — engines, bumpers, coils, tires, and more — built to print."),
    ("Are the racks returnable and stackable?","Yes — engineered for the returnable loop, stackable and durable to protect parts trip after trip.")]),
  ("stack-racks","Stack Racks","Stack Racks — Stackable, Collapsible Steel Racks | Southern Perfection",
   "Custom stackable steel stack racks — stack loaded, nest or fold empty to save floor space and return freight. Built to print, ISO 9001, Byron, GA.",
   "Stackable steel stack racks.",
   "Custom <strong>stack racks</strong> — stackable, portable steel racks that stack loaded and nest or fold empty to save floor space and cut return freight. Built to your parts and your footprint.",
   [("Stackable","Stack loaded to use vertical space and cut floor footprint."),
    ("Collapsible","Fold or nest empty to slash return freight."),
    ("Built to Print","Engineered to your parts, load, and stack height."),
    ("Durable","Welded steel and durable finishes for the returnable loop.")],
   [("Do stack racks fold or nest when empty?","Yes — we build collapsible and nestable stack racks that fold or nest empty to cut return freight and storage space."),
    ("How high can they stack?","We engineer the rack and post structure to your load and desired stack height, built to print.")]),
  ("industrial-carts","Industrial Carts","Industrial Carts — Custom Material Handling Carts | Southern Perfection",
   "Custom industrial carts for line-side, WIP, and material handling — durable steel carts built to print. ISO 9001, Byron, GA.",
   "Custom industrial carts.",
   "Durable custom <strong>industrial carts</strong> for line-side delivery, WIP, and material handling — engineered to your parts and your process, built to print. See also <a href=\"/wip-carts/\">WIP carts</a> and <a href=\"/industrial-dollies/\">industrial dollies</a>.",
   [("Line-Side Delivery","Carts sized to present parts at the point of use."),
    ("WIP &amp; Kitting","Move work-in-process and kits through the plant."),
    ("Ergonomic","Built for safe, efficient manual movement."),
    ("Built to Print","Engineered to your parts, load, and aisles.")],
   [("Can you build carts to our part and aisle sizes?","Yes. We design industrial carts to your parts, load, and aisle constraints, built to print."),
    ("Do you build casters and handles to spec?","Yes — casters, handles, and shelves specified to your load and ergonomics.")]),
  ("industrial-dollies","Industrial Dollies","Industrial Dollies — Heavy-Duty Steel Dollies | Southern Perfection",
   "Custom heavy-duty industrial dollies for moving heavy parts and assemblies — durable welded steel, built to print. ISO 9001, Byron, GA.",
   "Heavy-duty industrial dollies.",
   "Custom <strong>industrial dollies</strong> engineered to move heavy parts and assemblies safely across the plant — durable welded steel, built to your load and footprint.",
   [("Heavy-Duty","Engineered for heavy parts and assemblies."),
    ("Maneuverable","Caster and swivel layouts for tight moves."),
    ("Durable Steel","Welded steel built for years of plant duty."),
    ("Built to Print","Sized to your part, load, and floor.")],
   [("What loads can your dollies handle?","We engineer dollies to your specific load — from moderate to heavy parts and assemblies, built to print."),
    ("Can you match our part's shape?","Yes — cradles, nests, and decks shaped to hold your part securely.")]),
  ("kanban-flow-racks","Kanban Flow Racks","Kanban Flow Racks — Gravity Flow Racks for Lean | Southern Perfection",
   "Custom kanban flow racks and gravity flow racks for lean and line-side replenishment — FIFO presentation, built to print. ISO 9001, Byron, GA.",
   "Kanban flow racks for lean lines.",
   "Custom <strong>kanban flow racks</strong> — gravity flow racks that present parts FIFO for lean, line-side replenishment and pull systems. Engineered to your totes, parts, and pitch, built to print.",
   [("Gravity Flow","FIFO roller and wheel lanes for first-in, first-out."),
    ("Kanban / Pull","Built for lean replenishment and pull signals."),
    ("To Your Totes","Lanes sized to your totes, bins, and parts."),
    ("Ergonomic","Presentation heights and angles for the operator.")],
   [("Do you size flow lanes to our totes?","Yes. We build gravity flow lanes to your totes, bins, and parts for smooth FIFO flow."),
    ("Can you build for kanban pull systems?","Yes — flow racks engineered for kanban and lean line-side replenishment, built to print.")]),
  ("steel-cable-reels","Steel Cable Reels","Steel Cable Reels — Custom Steel Reels for Cable & Wire | Southern Perfection",
   "Custom steel cable reels and spools for cable, wire, and hose — durable, reusable, built to print. ISO 9001, Byron, GA.",
   "Custom steel cable reels.",
   "Durable custom <strong>steel cable reels</strong> and spools for winding, storing, and shipping cable, wire, and hose — reusable and built to your dimensions and load, to print.",
   [("Any Diameter","Reels and spools built to your cable and flange size."),
    ("Reusable","Durable steel that survives repeated payout and rewind."),
    ("Heavy Loads","Engineered for the weight of your cable or hose."),
    ("Built to Print","Made to your dimensions and mounting.")],
   [("Can you build reels to our cable dimensions?","Yes. We build steel reels and spools to your cable, wire, or hose diameter, length, and weight, built to print."),
    ("Are they reusable?","Yes — durable welded steel reels engineered for repeated payout and rewind.")]),
]

TPL = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>__TITLE__</title>
  <meta name="description" content="__DESC__">
  <link rel="canonical" href="https://southernperfection.com/__SLUG__/">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta property="og:type" content="website"><meta property="og:site_name" content="Southern Perfection Fabrication">
  <meta property="og:title" content="__NAME__ | Southern Perfection"><meta property="og:url" content="https://southernperfection.com/__SLUG__/">
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
      <p class="eyebrow"><a href="/" style="color:inherit">Home</a> · What We Build · __NAME__</p>
      <h1 id="h">__H1__</h1>
      <p class="lede">__INTRO__</p>
      <div class="hero-actions"><a href="/#rfq" class="btn btn-spark btn-lg">Start an RFQ →</a><a href="/returnable-steel-racks/" class="btn btn-ghost btn-lg">See our racks</a></div>
    </div></section>
    <section class="proofbar"><div class="wrap proofbar-inner"><span>ISO&nbsp;9001</span><span>CAGE&nbsp;2W654</span><span>Build-to-Print</span><span>Byron,&nbsp;GA</span></div></section>
    <section class="section"><div class="wrap">
      <p class="kicker">__NAME__</p><h2>Built to print, under one roof.</h2>
      <div class="cards-4">__CARDS__</div>
    </div></section>
    <section class="section section-paper"><div class="wrap">
      <p class="kicker">FAQ</p><h2>__NAME__ — answered.</h2>
      <div class="faq">__FAQ__</div>
    </div></section>
    <section class="cta-band"><div class="wrap center">
      <h2 class="h-light">Have a part to quote?</h2><p class="lede lede-light">Send a part or a print — we'll come back with a concept and a number.</p>
      <a href="/#rfq" class="btn btn-spark btn-lg">Start an RFQ →</a>
    </div></section>
  </main>
  <footer class="site-footer"><div class="wrap footer-grid">
    <div><span class="brand-text">SOUTHERN PERFECTION FABRICATION</span><p class="footer-mono">Complete metal fabrication under one roof</p><p class="footer-mono">ISO 9001 · CAGE 2W654 · Est. 1982 · Byron, GA</p></div>
    <nav aria-label="Footer"><ul><li><a href="/returnable-steel-racks/">Returnable Racks</a></li><li><a href="/steel-pallets/">Steel Pallets</a></li><li><a href="/returnable-containers/">Metal Containers</a></li><li><a href="/capabilities/">Capabilities</a></li><li><a href="/industries/">Industries</a></li><li><a href="/contact/">Contact</a></li></ul></nav>
    <div class="footer-contact"><a href="tel:+14789564442" class="phone">478-956-4442</a><br><a href="mailto:sales@southernperfection.com">sales@southernperfection.com</a><br><span class="footer-mono">232 Hwy 49 S · Byron, GA 31008</span></div>
  </div><div class="wrap footer-legal"><small>© 2026 Southern Perfection Fabrication. All rights reserved.</small></div></footer>
</body>
</html>
"""

for slug,name,title,desc,h1,intro,cards,faqs in PAGES:
    schema = {"@context":"https://schema.org","@graph":[
        {"@type":"BreadcrumbList","itemListElement":[
            {"@type":"ListItem","position":1,"name":"Home","item":"https://southernperfection.com/"},
            {"@type":"ListItem","position":2,"name":name.replace("&amp;","&"),"item":f"https://southernperfection.com/{slug}/"}]},
        {"@type":"Service","name":name.replace("&amp;","&"),"provider":{"@type":"Organization","name":"Southern Perfection Fabrication","telephone":"+1-478-956-4442"}},
        {"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}]}
    cards_html = "".join(f'<article class="card"><h3>{c[0]}</h3><p>{c[1]}</p></article>' for c in cards)
    faq_html = "".join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in faqs)
    html = (TPL.replace("__TITLE__",title).replace("__DESC__",desc).replace("__SLUG__",slug)
               .replace("__NAME__",name).replace("__H1__",h1).replace("__INTRO__",intro)
               .replace("__CARDS__",cards_html).replace("__FAQ__",faq_html).replace("__SCHEMA__",json.dumps(schema, ensure_ascii=False)))
    d = ROOT / slug
    d.mkdir(parents=True, exist_ok=True)
    (d/"index.html").write_text(html)
    print(" -", f"{slug}/")
print("Done.")

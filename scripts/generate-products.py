#!/usr/bin/env python3
"""Generate the two new fabricated-product pages. Run from website/ root.
Then run scripts/apply-header.py to inject the shared mega menu.
"""
import pathlib, json
ROOT = pathlib.Path(__file__).resolve().parent.parent

PRODS = [
  ("weldments-frames","Weldments & Frames","Custom Weldments & Steel Frames | Southern Perfection Fabrication",
   "Custom weldments, steel frames, and structural assemblies — MIG/TIG and FANUC robotic welding across 30+ stations, built to print at production volume in Byron, GA. ISO 9001, CAGE 2W654.",
   "Custom weldments &amp; steel frames.",
   "Custom <strong>weldments, frames, and structural assemblies</strong> — welded across 30+ MIG/TIG stations and FANUC robotic cells, built to your print at production volume. Cut, formed, welded, and finished under one roof.",
   [("Robotic Welding","FANUC robotic cells for repeatable, high-volume welds."),
    ("30+ MIG/TIG Stations","Deep manual welding capacity for any job size."),
    ("Built to Print","Frames and assemblies fabricated to your drawing."),
    ("One Roof","Cut, form, machine, weld, and finish in one building.")],
   [("Do you build weldments at production volume?","Yes. With FANUC robotic welding and 30+ MIG/TIG stations we build weldments and frames at production volume, built to print."),
    ("Can you handle large or heavy frames?","Yes — press-brake forming to 230 tons and heavy welding let us build large, heavy structural frames and weldments."),
    ("Do you finish the weldments too?","Yes. In-house powder coat and wet paint mean your weldments ship finished, not waiting on an outside coater.")]),
  ("guards-platforms","Guards & Platforms","Machine Guarding, Safety Guards & Access Platforms | Southern Perfection",
   "Custom machine guarding, safety guards, access platforms, and mezzanines — engineered and built to print under one roof in Byron, GA. ISO 9001, CAGE 2W654.",
   "Machine guarding, platforms &amp; mezzanines.",
   "Custom <strong>machine guarding, safety guards, access platforms, and mezzanines</strong> — engineered to your equipment and floor, built to print, and finished in-house for durable service.",
   [("Machine Guarding","Safety guards and barriers engineered to your equipment."),
    ("Access Platforms","Work platforms and stairs for safe equipment access."),
    ("Mezzanines","Structural mezzanines and elevated platforms, built to print."),
    ("Durable Finish","In-house powder coat for a finish that lasts on the floor.")],
   [("Can you engineer guarding to our equipment?","Yes. We design and build machine guarding and safety guards to your equipment and floor layout, built to print."),
    ("Do you build access platforms and mezzanines?","Yes — access platforms, stairs, and structural mezzanines, engineered and fabricated under one roof."),
    ("Do you finish them?","Yes. In-house powder coat and wet paint give guarding and platforms a durable finish for the plant floor.")]),
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
      <div class="hero-actions"><a href="/#rfq" class="btn btn-spark btn-lg">Start an RFQ →</a><a href="/capabilities/" class="btn btn-ghost btn-lg">See capabilities</a></div>
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
      <h2 class="h-light">Have a drawing to quote?</h2><p class="lede lede-light">Send a print — we'll come back with a real price and lead time.</p>
      <a href="/#rfq" class="btn btn-spark btn-lg">Start an RFQ →</a>
    </div></section>
  </main>
  <footer class="site-footer"><div class="wrap footer-grid">
    <div><span class="brand-text">SOUTHERN PERFECTION FABRICATION</span><p class="footer-mono">Complete metal fabrication under one roof</p><p class="footer-mono">ISO 9001 · CAGE 2W654 · Est. 1982 · Byron, GA</p></div>
    <nav aria-label="Footer"><ul><li><a href="/returnable-steel-racks/">Returnable Racks</a></li><li><a href="/weldments-frames/">Weldments &amp; Frames</a></li><li><a href="/guards-platforms/">Guards &amp; Platforms</a></li><li><a href="/capabilities/">Capabilities</a></li><li><a href="/industries/">Industries</a></li><li><a href="/contact/">Contact</a></li></ul></nav>
    <div class="footer-contact"><a href="tel:+14789564442" class="phone">478-956-4442</a><br><span class="footer-mono">232 Hwy 49 S · Byron, GA 31008</span></div>
  </div><div class="wrap footer-legal"><small>© 2026 Southern Perfection Fabrication. All rights reserved.</small></div></footer>
</body>
</html>
"""

for slug,name,title,desc,h1,intro,cards,faqs in PRODS:
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

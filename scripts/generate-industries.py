#!/usr/bin/env python3
"""Generate the new industry pages (brochure markets). Run from website/ root.
Existing pages (automotive, ev-battery, aerospace-defense, heavy-equipment, general-industrial) are left alone.
Then run scripts/apply-header.py to inject the shared mega menu.
"""
import pathlib, json
ROOT = pathlib.Path(__file__).resolve().parent.parent

INDS = [
  ("food-beverage-dairy","Food, Beverage & Dairy","Returnable Racks & Handling for Food, Beverage & Dairy | Southern Perfection",
   "Custom returnable steel racks, containers, and material handling for food, beverage, and dairy plants — durable, washdown-friendly, built to print. ISO 9001, Byron, GA.",
   "Returnable packaging for food, beverage &amp; dairy.",
   "Returnable racks, containers, and handling engineered for food, beverage, and dairy plants — durable, easy to sanitize, and built to move product safely, trip after trip.",
   [("Returnable Racks","Steel racks and carts for ingredients, packaging, and WIP."),
    ("Stainless Options","Stainless and washdown-friendly builds where sanitation matters."),
    ("Containers &amp; Dunnage","Bins, baskets, and dunnage sized to your product."),
    ("Built to Print","Made to your line and your standards under one roof.")],
   [("Do you build stainless or washdown-friendly racks?","Yes. We work in stainless and can finish builds for washdown and sanitation environments common in food, beverage, and dairy."),
    ("Can you match our line and totes?","Yes — we design racks, carts, and containers to your product, totes, and line layout, built to print.")]),
  ("packaging-paper","Packaging & Paper","Returnable Racks for Packaging & Paper Converters | Southern Perfection",
   "Custom returnable steel racks, roll and core handling, and material handling for packaging and paper converters. Built to print under one roof in Byron, GA. ISO 9001.",
   "Returnable packaging for packaging &amp; paper.",
   "Roll racks, core handling, and returnable steel racks for packaging and paper converters — engineered to move rolls, sheets, and finished goods without damage.",
   [("Roll &amp; Core Racks","Cradles and racks for rolls, cores, and reels."),
    ("Sheet &amp; Finished Goods","Racks and carts for sheets and converted product."),
    ("Returnable Containers","Bins and containers for parts and consumables."),
    ("Built to Print","Designed to your product and freight lanes.")],
   [("Can you build roll and core racks?","Yes. We design cradles and racks that hold rolls, cores, and reels securely for transport and storage."),
    ("Do you handle finished-goods racks too?","Yes — racks and carts for sheets, converted product, and finished goods, built to your spec.")]),
  ("transportation-trailer","Transportation & Trailer","Racks, Frames & Weldments for Transportation & Trailer | Southern Perfection",
   "Returnable racks, robotic-welded frames, and weldments for transportation and trailer manufacturers. Production-volume fabrication under one roof in Byron, GA. ISO 9001, CAGE 2W654.",
   "Fabrication for transportation &amp; trailer.",
   "Returnable racks, robotic-welded frames, and weldments for transportation and trailer builders — production-volume fabrication built to print.",
   [("Weldments &amp; Frames","Robotic-welded frames and weldments at production volume."),
    ("Returnable Racks","Racks and carts for parts and sub-assemblies."),
    ("Custom Fabrication","Built to your drawing, cut to finish under one roof."),
    ("Volume Ready","Consistent, repeatable builds for production programs.")],
   [("Do you build production-volume weldments?","Yes. With 30+ MIG stations and FANUC robotic welding we build weldments and frames at production volume, built to print."),
    ("Can you handle our part racks too?","Yes — returnable racks and carts for parts and sub-assemblies, designed to your line.")]),
  ("chemical-processing","Chemical Processing","Racks, Platforms & Fabrication for Chemical Processing | Southern Perfection",
   "Durable returnable racks, platforms, and fabrication for chemical processing plants — corrosion-aware finishes, built to print. One roof in Byron, GA. ISO 9001, CAGE 2W654.",
   "Fabrication for chemical processing.",
   "Durable racks, platforms, and steel fabrication for chemical processing plants — engineered for tough environments with corrosion-aware finishes, built to print.",
   [("Racks &amp; Containers","Returnable racks and containers for drums, parts, and product."),
    ("Platforms &amp; Access","Access platforms, mezzanines, and guarding."),
    ("Corrosion-Aware Finishes","Powder coat and finishes suited to tough environments."),
    ("Built to Print","Fabricated to your spec under one roof.")],
   [("Can you finish for corrosive environments?","Yes. We powder coat and finish in-house and can specify finishes suited to chemical processing environments."),
    ("Do you build platforms and access structures?","Yes — access platforms, mezzanines, and guarding, built to your drawing.")]),
  ("mining-aggregate","Mining & Aggregate","Heavy-Duty Racks, Weldments & Guards for Mining & Aggregate | Southern Perfection",
   "Heavy-duty returnable racks, weldments, and guarding for mining and aggregate equipment. Built to print for tough duty under one roof in Byron, GA. ISO 9001.",
   "Fabrication for mining &amp; aggregate.",
   "Heavy-duty racks, weldments, and guarding for mining and aggregate operations — built tough, built to print, and built to last in demanding duty.",
   [("Heavy-Duty Racks","Racks and cradles engineered for heavy, oversized parts."),
    ("Weldments &amp; Frames","Robotic-welded heavy weldments and frames."),
    ("Guards &amp; Platforms","Machine guarding and access platforms."),
    ("Built Tough","Heavy-gauge steel and durable finishes for hard use.")],
   [("Can you handle heavy, oversized parts?","Yes. We engineer heavy-duty racks and weldments for large, heavy parts common in mining and aggregate."),
    ("Do you build machine guarding?","Yes — guarding, platforms, and access structures built to your drawing.")]),
  ("industrial-machinery","Industrial Machinery & OEM","Returnable Racks & Weldments for Industrial Machinery & OEM | Southern Perfection",
   "Returnable racks, weldments, frames, and custom fabrication for industrial machinery and OEM builders. Production volume, built to print. Byron, GA. ISO 9001, CAGE 2W654.",
   "Fabrication for industrial machinery &amp; OEM.",
   "Returnable racks, weldments, frames, and custom fabrication for industrial machinery and OEM builders — one accountable partner from cut to finish.",
   [("Weldments &amp; Frames","Robotic-welded frames and weldments at volume."),
    ("Returnable Racks","Racks and carts for parts, WIP, and sub-assemblies."),
    ("Machined Components","CNC turning and milling for machined features."),
    ("Custom Fabrication","Built to your drawing, one roof, one PO.")],
   [("Can you be a single-source fab partner?","Yes. We cut, form, machine, weld, and finish under one roof — one purchase order, one accountable team."),
    ("Do you build to our production volumes?","Yes — robotic welding and in-house scheduling let us build to your production volumes, built to print.")]),
  ("distribution-logistics","Distribution & Logistics","Returnable Racks, Containers & Pallets for Distribution & Logistics | Southern Perfection",
   "Returnable steel racks, containers, and steel pallets for distribution, warehousing, and 3PL operations. Reusable, stackable, built to print. Byron, GA. ISO 9001.",
   "Returnable packaging for distribution &amp; logistics.",
   "Returnable steel racks, containers, and pallets for distribution, warehousing, and 3PL flows — reusable, stackable, and built to move product efficiently.",
   [("Returnable Racks","Racks and stack racks for storage and transport."),
    ("Steel Containers","Wire mesh and collapsible steel containers."),
    ("Steel Pallets","Durable reusable pallets that outlast wood and plastic."),
    ("Right-Sized","Built to your product, footprint, and freight lanes.")],
   [("Do you build collapsible containers to save freight?","Yes. We build collapsible steel containers and stackable racks that fold or nest to cut return freight."),
    ("Can you match our warehouse footprint?","Yes — racks, containers, and pallets sized to your product, aisles, and racking.")]),
  ("energy-power","Energy & Power Generation","Racks, Frames & Platforms for Energy & Power Generation | Southern Perfection",
   "Returnable racks, robotic-welded frames, platforms, and fabrication for energy and power generation equipment. Built to print under one roof in Byron, GA. ISO 9001, CAGE 2W654.",
   "Fabrication for energy &amp; power generation.",
   "Returnable racks, weldments, frames, and platforms for energy and power generation equipment — heavy-duty fabrication built to print.",
   [("Racks &amp; Frames","Returnable racks and robotic-welded frames."),
    ("Platforms &amp; Access","Access platforms, mezzanines, and guarding."),
    ("Heavy Fabrication","Heavy-gauge weldments and structures."),
    ("Built to Print","Fabricated to your spec, one roof, one PO.")],
   [("Can you build heavy weldments and frames?","Yes. With FANUC robotic welding and press-brake forming to 230 tons we build heavy weldments and frames to print."),
    ("Do you build access platforms and guarding?","Yes — platforms, mezzanines, and guarding built to your drawing.")]),
]

TPL = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>__TITLE__</title>
  <meta name="description" content="__DESC__">
  <link rel="canonical" href="https://southernperfection.com/industries/__SLUG__/">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta property="og:type" content="website"><meta property="og:site_name" content="Southern Perfection Fabrication">
  <meta property="og:title" content="__NAME__ | Southern Perfection"><meta property="og:url" content="https://southernperfection.com/industries/__SLUG__/">
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
      <p class="eyebrow"><a href="/" style="color:inherit">Home</a> · <a href="/industries/" style="color:inherit">Industries</a> · __NAME__</p>
      <h1 id="h">__H1__</h1>
      <p class="lede">__INTRO__</p>
      <div class="hero-actions"><a href="/#rfq" class="btn btn-spark btn-lg">Start an RFQ →</a><a href="/returnable-steel-racks/" class="btn btn-ghost btn-lg">See our racks</a></div>
    </div></section>
    <section class="section"><div class="wrap">
      <p class="kicker">What we build for __NAME__</p><h2>Built to print, under one roof.</h2>
      <div class="cards-4">__CARDS__</div>
    </div></section>
    <section class="section section-paper"><div class="wrap">
      <p class="kicker">FAQ</p><h2>__NAME__ — answered.</h2>
      <div class="faq">__FAQ__</div>
    </div></section>
    <section class="cta-band"><div class="wrap center">
      <h2 class="h-light">Shipping parts in your industry?</h2><p class="lede lede-light">Send a part or a print — we'll turn around a concept and a number.</p>
      <a href="/#rfq" class="btn btn-spark btn-lg">Start an RFQ →</a>
    </div></section>
  </main>
  <footer class="site-footer"><div class="wrap footer-grid">
    <div><span class="brand-text">SOUTHERN PERFECTION FABRICATION</span><p class="footer-mono">Complete metal fabrication under one roof</p><p class="footer-mono">ISO 9001 · CAGE 2W654 · Est. 1982 · Byron, GA</p></div>
    <nav aria-label="Footer"><ul><li><a href="/returnable-steel-racks/">Returnable Racks</a></li><li><a href="/industries/">Industries</a></li><li><a href="/capabilities/">Capabilities</a></li><li><a href="/case-studies/">Case Studies</a></li><li><a href="/managed-programs/">Managed Programs</a></li><li><a href="/contact/">Contact</a></li></ul></nav>
    <div class="footer-contact"><a href="tel:+14789564442" class="phone">478-956-4442</a><br><span class="footer-mono">232 Hwy 49 S · Byron, GA 31008</span></div>
  </div><div class="wrap footer-legal"><small>© 2026 Southern Perfection Fabrication. All rights reserved.</small></div></footer>
</body>
</html>
"""

for slug,name,title,desc,h1,intro,cards,faqs in INDS:
    schema = {"@context":"https://schema.org","@graph":[
        {"@type":"BreadcrumbList","itemListElement":[
            {"@type":"ListItem","position":1,"name":"Home","item":"https://southernperfection.com/"},
            {"@type":"ListItem","position":2,"name":"Industries","item":"https://southernperfection.com/industries/"},
            {"@type":"ListItem","position":3,"name":name.replace("&amp;","&"),"item":f"https://southernperfection.com/industries/{slug}/"}]},
        {"@type":"Service","name":name.replace("&amp;","&")+" Fabrication","provider":{"@type":"Organization","name":"Southern Perfection Fabrication","telephone":"+1-478-956-4442"}},
        {"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}]}
    cards_html = "".join(f'<article class="card"><h3>{c[0]}</h3><p>{c[1]}</p></article>' for c in cards)
    faq_html = "".join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in faqs)
    html = (TPL.replace("__TITLE__",title).replace("__DESC__",desc).replace("__SLUG__",slug)
               .replace("__NAME__",name).replace("__H1__",h1).replace("__INTRO__",intro)
               .replace("__CARDS__",cards_html).replace("__FAQ__",faq_html).replace("__SCHEMA__",json.dumps(schema, ensure_ascii=False)))
    d = ROOT / "industries" / slug
    d.mkdir(parents=True, exist_ok=True)
    (d/"index.html").write_text(html)
    print(" -", f"industries/{slug}/")
print("Done.")

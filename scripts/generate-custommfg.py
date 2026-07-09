#!/usr/bin/env python3
"""Generate the 3 new Custom Manufacturing pages (robust model: split hero + definition +
cards + FAQ + schema). Run from website/ root, then apply-header.py + generate-sitemap.py."""
import pathlib, json

PAGES = [
 ("sheet-metal-fabrication","Sheet Metal Fabrication","Sheet Metal Fabrication | Southern Perfection Fabrication — Byron, GA",
  "Custom sheet metal fabrication — laser & plasma cutting, CNC forming to 230 tons, robotic welding, and in-house finishing under one roof. Carbon steel, stainless, aluminum. ISO 9001, CAGE 2W654, Byron, GA.",
  "Custom sheet metal fabrication.",
  "Complete <strong>sheet metal fabrication</strong> under one roof — cut, formed, welded, and finished to your print. Send a drawing and we’ll come back with a real price and lead time.",
  "laser-tube-cutting.jpg","CNC laser cutting sheet metal at Southern Perfection Fabrication, Byron GA",
  "What is sheet metal fabrication?",
  ['Sheet metal fabrication is the process of cutting, forming, and joining flat metal sheet into finished parts and assemblies — brackets, panels, enclosures, chassis, and more. It combines cutting, press-brake forming, and welding to turn a flat blank into a precise, repeatable part.',
   'Southern Perfection Fabrication does complete <strong>custom sheet metal fabrication</strong> under one roof — <a href="/capabilities/laser-cutting/">laser and plasma cutting</a>, <a href="/capabilities/forming/">CNC forming to 230 tons</a>, <a href="/capabilities/robotic-welding/">robotic welding</a>, and in-house <a href="/capabilities/powder-coating/">finishing</a> — in carbon steel, stainless, aluminum, and magnesium, built to your print.',
   'We fabricate sheet metal parts and assemblies for <a href="/industries/automotive/">automotive</a>, <a href="/industries/aerospace-defense/">aerospace and defense</a>, <a href="/industries/industrial-machinery/">industrial machinery</a>, and general manufacturing.'],
  "What we fabricate",
  [("Brackets &amp; Panels","Precision-cut and formed sheet metal parts to your print."),("Enclosures &amp; Chassis","Welded enclosures, cabinets, and chassis assemblies."),("Weldments &amp; Assemblies","Multi-part welded sheet-metal assemblies at volume."),("Prototype to Production","One-off prototypes through full production runs.")],
  [("What materials do you fabricate?","Carbon steel, stainless steel, aluminum, and magnesium, matched to your part and application."),
   ("Do you do prototype and production runs?","Yes, from one-off prototypes through repeatable production volume, all built to your print."),
   ("What is the difference between sheet metal fabrication and machining?","Fabrication cuts, forms, and welds sheet and plate into assemblies; machining removes material from solid stock to make precise components. We do both under one roof.")]),

 ("industrial-structures","Industrial Steel Structures","Industrial Steel Structures &amp; Structural Fabrication | Southern Perfection",
  "Custom industrial steel structures and structural fabrication — heavy weldments, machine bases, frames, platforms, and mezzanines built to print. Press brake to 230 tons, FANUC robotic welding. ISO 9001, Byron, GA.",
  "Industrial steel structures, built to print.",
  "Heavy <strong>industrial steel structures</strong> — machine bases, frames, platforms, and structural weldments — engineered and built under one roof to carry load and hold tolerance.",
  "heavy-equipment.jpg","Custom welded industrial steel structure fabricated by Southern Perfection Fabrication",
  "What are industrial structures?",
  ['Industrial structures are the heavy welded steel frameworks that support equipment and operations — machine bases, support frames, platforms, mezzanines, and structural weldments. They have to carry load, hold tolerance, and last.',
   'SPF engineers and builds custom industrial structures in-house — heavy <a href="/weldments-frames/">weldments and frames</a> and <a href="/guards-platforms/">platforms and mezzanines</a> — with press-brake forming to 230 tons and FANUC robotic welding, built to your print and finished on site.',
   'We build structures for <a href="/industries/heavy-equipment/">heavy equipment</a>, <a href="/industries/energy-power/">energy and power</a>, <a href="/industries/industrial-machinery/">industrial machinery</a>, and general manufacturing.'],
  "Structures we build",
  [("Machine Bases &amp; Frames","Rigid welded bases and frames engineered to your equipment."),("Platforms &amp; Mezzanines","Access platforms, stairs, and structural mezzanines."),("Heavy Weldments","Large, heavy structural weldments at production volume."),("Support Structures","Custom steel supports and frameworks, built to print.")],
  [("Can you build heavy structural weldments?","Yes. Press-brake forming to 230 tons and FANUC robotic welding let us build large, heavy structural weldments and frames."),
   ("Do you build platforms and mezzanines?","Yes — access platforms, crossover stairs, and structural mezzanines engineered to your access and load requirements."),
   ("What load ratings can you engineer to?","We engineer each structure to your specific load, with the members, gauge, and welds rated accordingly, built to print.")]),

 ("high-volume-manufacturing","High-Volume Manufacturing","High-Volume Manufacturing &amp; Production Fabrication | Southern Perfection",
  "High-volume metal fabrication — FANUC robotic welding, repeatable cutting and forming, and in-house finishing deliver consistent parts at production volume. ISO 9001, CAGE 2W654, Byron, GA.",
  "High-volume manufacturing, built to hold quality.",
  "<strong>High-volume manufacturing</strong> where the ten-thousandth part matches the first — FANUC robotic welding, programmed cutting and forming, and a quality system that holds tolerance across the run.",
  "returnable-racks-fleet.jpg","A staged fleet of identical racks from high-volume production at Southern Perfection Fabrication",
  "What is high-volume manufacturing?",
  ['High-volume manufacturing produces large quantities of identical parts to a consistent spec — where the ten-thousandth part has to match the first. It demands automation, repeatable processes, and a quality system that holds tolerance across the run.',
   'SPF scales to production volume with FANUC <a href="/capabilities/robotic-welding/">robotic welding</a>, programmed <a href="/capabilities/laser-cutting/">cutting</a> and <a href="/capabilities/forming/">forming</a>, and in-house finishing — all under an <a href="/capabilities/quality-inspection/">ISO 9001</a> quality system, so consistency holds from the first part to the last.',
   'See how we delivered <a href="/case-studies/high-volume-fleet/">1,000+ identical racks on time</a> for a launch, and <a href="/case-studies/engine-rack-program/">a 300+ engine-rack fleet in half the lead time</a>.'],
  "How we hold volume",
  [("Robotic Welding","FANUC cells for repeatable, spec-consistent welds at volume."),("Repeatable Processes","Programmed cutting and forming that repeat exactly."),("Production Capacity","Deep capacity to scale output and hold a launch window."),("Consistent Quality","ISO 9001 and CMM inspection keep tolerance across the run.")],
  [("Can you build at production volume?","Yes. Robotic welding and in-house scheduling let us scale to full production programs while holding quality."),
   ("How do you hold quality across a large run?","Programmed, repeatable processes plus an ISO 9001 quality system and CMM inspection keep the ten-thousandth part matching the first."),
   ("Do you build low volume too?","Yes — from prototypes and small runs through high-volume production, all built to your print.")]),
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
  <script type="application/ld+json">
  __FAQSCHEMA__
  </script>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header"><div class="wrap header-inner"><a href="/" class="brand"><span class="brand-mark"></span><span class="brand-text">SOUTHERN&nbsp;PERFECTION</span></a><div class="header-cta"><a href="tel:+14789564442" class="phone">478-956-4442</a><a href="/#rfq" class="btn btn-spark">Start an RFQ</a></div></div></header>
  <main id="main">
    <section class="hero" aria-labelledby="h"><div class="wrap hero-split"><div class="hero-copy">
      <p class="eyebrow"><a href="/" style="color:inherit">Home</a> · Custom Manufacturing · __NAME__</p>
      <h1 id="h">__H1__</h1>
      <p class="lede">__LEDE__</p>
      <div class="hero-actions"><a href="/#rfq" class="btn btn-spark btn-lg">Start an RFQ →</a><a href="/capabilities/" class="btn btn-ghost btn-lg">See capabilities</a></div>
    </div><div class="hero-media"><img src="/assets/photos/__IMG__" alt="__IMGALT__" width="1500" loading="eager" fetchpriority="high"></div></div></section>
    <section class="section section-paper"><div class="wrap article-body">
      <p class="kicker">__NAME__</p><h2>__DEFH2__</h2>
      __DEFPARAS__
    </div></section>
    <section class="section"><div class="wrap">
      <p class="kicker">__CARDSKICKER__</p><h2>Built to print, under one roof.</h2>
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
    <nav aria-label="Footer"><ul><li><a href="/capabilities/">Capabilities</a></li><li><a href="/sheet-metal-fabrication/">Sheet Metal</a></li><li><a href="/industrial-structures/">Industrial Structures</a></li><li><a href="/weldments-frames/">Weldments</a></li><li><a href="/industries/">Industries</a></li><li><a href="/contact/">Contact</a></li></ul></nav>
    <div class="footer-contact"><a href="tel:+14789564442" class="phone">478-956-4442</a><br><a href="mailto:sales@southernperfection.com">sales@southernperfection.com</a><br><span class="footer-mono">232 Hwy 49 S · Byron, GA 31008</span></div>
  </div><div class="wrap footer-legal"><small>© 2026 Southern Perfection Fabrication. All rights reserved.</small></div></footer>
</body>
</html>
"""

ROOT = pathlib.Path(__file__).resolve().parent.parent
for slug,name,title,desc,h1,lede,img,imgalt,defh2,defparas,cardskicker,cards,faqs in PAGES:
    schema = {"@context":"https://schema.org","@graph":[
        {"@type":"BreadcrumbList","itemListElement":[
            {"@type":"ListItem","position":1,"name":"Home","item":"https://southernperfection.com/"},
            {"@type":"ListItem","position":2,"name":name.replace("&amp;","&"),"item":f"https://southernperfection.com/{slug}/"}]},
        {"@type":"Service","name":name.replace("&amp;","&"),"provider":{"@type":"Organization","name":"Southern Perfection Fabrication","telephone":"+1-478-956-4442"}}]}
    faqschema = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}
    defp = "".join(f"<p>{p}</p>\n      " for p in defparas).rstrip()
    cards_html = "".join(f'<article class="card"><h3>{c[0]}</h3><p>{c[1]}</p></article>' for c in cards)
    faq_html = "".join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in faqs)
    html = (TPL.replace("__TITLE__",title).replace("__DESC__",desc).replace("__SLUG__",slug).replace("__NAME__",name)
               .replace("__H1__",h1).replace("__LEDE__",lede).replace("__IMG__",img).replace("__IMGALT__",imgalt)
               .replace("__DEFH2__",defh2).replace("__DEFPARAS__",defp).replace("__CARDSKICKER__",cardskicker)
               .replace("__CARDS__",cards_html).replace("__FAQ__",faq_html)
               .replace("__SCHEMA__",json.dumps(schema,ensure_ascii=False)).replace("__FAQSCHEMA__",json.dumps(faqschema,ensure_ascii=False)))
    d = ROOT/slug; d.mkdir(parents=True, exist_ok=True); (d/"index.html").write_text(html)
    print(" -", f"{slug}/")
print("Done.")

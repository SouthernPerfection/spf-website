#!/usr/bin/env python3
"""Generate the 6 case-study pages from the SPF case-study collateral.
Run from website/ root, then run scripts/apply-header.py.
Testimonial quotes are intentionally omitted until real, approved quotes are supplied.
"""
import pathlib, json
ROOT = pathlib.Path(__file__).resolve().parent.parent

# slug, category, h1, subhead, [ (stat,label) x3 ], challenge, did, result,
# why[], industries[], meta_title, meta_desc
CASES = [
  ("engine-rack-program", "Returnable Racks · Automotive Tier-1",
   "A full engine-rack fleet — weeks ahead of the line.",
   "When a Tier-1 supplier needed returnable engine racks faster than their usual source could deliver, SPF designed, welded, and finished the fleet under one roof — and hit the launch.",
   [("~6–8","Weeks to deliver (about half the quoted time)"),("300+","Returnable engine racks delivered"),("On-Time","To the program ramp / launch")],
   "A Tier-1 automotive supplier needed returnable steel racks to move finished engines between its machining and assembly operations — and needed them fast, ahead of a program ramp. Their existing rack source quoted roughly twice the lead time, a timeline that put the line start at risk.",
   "SPF engineered the engine rack in-house with SolidWorks, then cut, robotic-welded, and powder-coated the full fleet in one Byron facility — no brokered steel and no outside coater's queue. One purchase order, one accountable team, and short Southeast freight kept the whole job on a single clock.",
   "The full 300+-rack fleet was delivered in about 6–8 weeks — roughly half the lead time quoted elsewhere — in time for the program ramp. The returnable racks are built to run hundreds of trips, protecting finished engines in transit.",
   ["Fast Turnaround","One Roof","Robotic Welding","Returnable"],
   ["Automotive Tier-1","Powertrain"],
   "Case Study: Engine Rack Fleet Delivered in Half the Lead Time | Southern Perfection",
   "How SPF delivered a 300+ returnable engine-rack fleet in ~6–8 weeks — about half the quoted lead time — for a Tier-1 automotive supplier's launch. ISO 9001, Byron, GA."),
  ("custom-rack-design", "Custom Rack Design · Heavy Equipment",
   "A rack engineered for a part nothing else fit.",
   "When an off-highway OEM had an oversized, awkward weldment with no standard rack to hold it, SPF's in-house engineering turned a rough idea into a buildable, ergonomic returnable rack.",
   [("1","Design round — first-pass approval"),("1–3K lb","Rated load per rack"),("5–10","Parts staged per rack")],
   "An off-highway / heavy-equipment OEM needed to move large weldments between weld, machining, and assembly. The parts were heavy and awkward, no off-the-shelf rack fit, and manual handling raised damage and ergonomic concerns.",
   "SPF's SolidWorks team took the part data and a rough concept and engineered a returnable rack around it — load paths, fork access, and operator ergonomics designed in. A prototype was reviewed, adjusted, and moved to production, all in-house.",
   "Approved on the first design pass and rated to 1,000–3,000 lb, the rack stages 5–10 parts safely, cut manual handling, and became the standard design for the program's follow-on parts.",
   ["Build-to-Print","In-House Design","Robotic Welding","One Roof"],
   ["Heavy Equipment","Industrial Machinery"],
   "Case Study: Custom Returnable Rack Design for an Oversized Part | Southern Perfection",
   "How SPF's in-house SolidWorks engineering designed a returnable rack for an awkward off-highway weldment — first-pass approval, rated 1,000–3,000 lb. Byron, GA."),
  ("rack-repair-fleet", "Rack Repair & Refurb · Automotive",
   "An aging fleet, back to spec for a fraction of new.",
   "Rather than replace a worn fleet of returnable racks, a manufacturer had SPF inspect, repair, and re-finish them — back in service in days, at a fraction of new-build cost.",
   [("~40%","Of new-build cost"),("75–200","Racks refurbished & returned"),("1–2 wks","Turnaround per batch")],
   "After several years in a returnable loop, a manufacturer's fleet of 75–200 steel racks was bent, cracked, and worn — risking part damage and operator safety. Replacing the fleet outright was costly and slow.",
   "SPF inspected the fleet, re-welded and repaired damaged members, replaced what was beyond saving, and re-finished every rack back to original spec. Because SPF builds racks like these, the failure points were already familiar.",
   "75–200 racks returned to service at about 40% of new-build cost in 1–2 weeks per batch — extending fleet life by years and restoring safe, damage-free handling.",
   ["Repair & Refurb","Fast Turnaround","Fleet Economics","One Roof"],
   ["Automotive","General Mfg"],
   "Case Study: Returnable Rack Repair at ~40% of New-Build Cost | Southern Perfection",
   "How SPF refurbished a 75–200 rack fleet back to spec at ~40% of new-build cost, 1–2 weeks per batch. Rack repair & refurbishment, Byron, GA."),
  ("high-volume-fleet", "High-Volume Fleet · Automotive OEM",
   "1,000+ identical racks, on time for launch.",
   "An OEM ramping a new line needed a large fleet of identical returnable racks on a hard deadline — SPF's robotic welding delivered the volume and the weld consistency.",
   [("1,000+","Returnable racks delivered"),("100%","On-time to the launch date"),("Robotic","Welded for rack-to-rack consistency")],
   "An automotive OEM ramping a new line needed more than 1,000 identical returnable racks by a fixed launch date. Volume was high, the timeline tight, and weld consistency across every rack was critical.",
   "SPF ran the weldments through FANUC robotic welding for repeatable, spec-consistent joints at volume, scaling output to hold the launch window. Cutting, welding, and powder coat all stayed in-house on one PO.",
   "Over 1,000 racks delivered 100% on time for launch — every weldment robotic-welded for rack-to-rack consistency — and the account became a repeat program for follow-on parts.",
   ["Robotic Welding","Production Capacity","On-Time","One Roof"],
   ["Automotive OEM","EV / Battery"],
   "Case Study: 1,000+ Identical Returnable Racks On Time for Launch | Southern Perfection",
   "How SPF delivered 1,000+ identical returnable racks 100% on time using FANUC robotic welding for an automotive OEM launch. Byron, GA."),
  ("single-source-switch", "Single-Source Switch · Manufacturing",
   "Three vendors, one lead time — under one roof.",
   "A plant juggling separate cut, weld, and coat suppliers moved the whole job to SPF — fewer handoffs, shorter lead times, one accountable team.",
   [("~50%","Lead time cut"),("3 → 1","Suppliers consolidated"),("20–30%","Lower freight cost")],
   "A manufacturer was sourcing racks across three vendors — one cut, one welded, one coated. Handoffs stretched lead times, quality issues bounced between suppliers, and out-of-region freight added cost and delay.",
   "SPF took the entire job in-house — cut, form, weld, and finish on one floor in Byron, on a single purchase order. Short Southeast freight replaced long hauls, and one team owned the result end to end.",
   "Lead time was cut roughly in half, supplier count went from 3 to 1, and freight fell 20–30% with regional sourcing — all on one PO, with a shop the customer can visit and audit.",
   ["One Roof","One PO","SE Freight","ISO 9001"],
   ["General Mfg","Industrial Machinery"],
   "Case Study: Consolidating 3 Fab Vendors to 1, Lead Time Cut ~50% | Southern Perfection",
   "How a manufacturer cut rack lead time ~50% and freight 20–30% by consolidating cut/weld/coat to SPF's one-roof shop. Byron, GA."),
  ("tooling-gse", "Tooling Carts & GSE · Aerospace & Defense",
   "Non-flight tooling & GSE, built to a quality spec.",
   "A regulated aerospace / defense shop needed durable, traceable tooling carts and ground-support equipment — SPF built to print under ISO 9001 and CAGE 2W654.",
   [("100%","Spec conformance / acceptance"),("25–75","Carts & stands delivered"),("Ongoing","Audited, repeat supplier")],
   "An aerospace & defense manufacturer needed non-flight tooling carts, work stands, and transport GSE — precise, durable, and built to a documented quality standard with full traceability.",
   "SPF machined, robotic-welded, and finished the equipment to print under its ISO 9001 quality system and CAGE 2W654 registration — one accountable shop for fabrication, finishing, and documentation.",
   "25–75 carts and stands delivered at 100% conformance, with the documentation trail the program required — and SPF onboarded as an audited, ongoing supplier.",
   ["ISO 9001","CAGE 2W654","Build-to-Print","One Roof"],
   ["Aerospace & Defense","Industrial Machinery"],
   "Case Study: Non-Flight Tooling & GSE Built to ISO 9001 / CAGE | Southern Perfection",
   "How SPF delivered non-flight aerospace & defense tooling carts and GSE at 100% conformance under ISO 9001 and CAGE 2W654. Byron, GA."),
]

TPL = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>__TITLE__</title>
  <meta name="description" content="__DESC__">
  <link rel="canonical" href="https://southernperfection.com/case-studies/__SLUG__/">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta property="og:type" content="article"><meta property="og:site_name" content="Southern Perfection Fabrication">
  <meta property="og:title" content="__OG__"><meta property="og:url" content="https://southernperfection.com/case-studies/__SLUG__/">
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
      <p class="eyebrow"><a href="/" style="color:inherit">Home</a> · <a href="/case-studies/" style="color:inherit">Case Studies</a> · __CAT__</p>
      <h1 id="h">__H1__</h1>
      <p class="lede">__SUB__</p>
      <div class="hero-actions"><a href="/#rfq" class="btn btn-spark btn-lg">Start an RFQ →</a><a href="/assets/case-studies/__SLUG__.pdf" class="btn btn-ghost btn-lg" download>Download the one-pager (PDF)</a></div>
    </div></section>
    <section class="section"><div class="wrap">
      <div class="stat-row">__STATS__</div>
      <div class="cs-grid">
        <div><p class="kicker">The challenge</p><p>__CHALLENGE__</p></div>
        <div><p class="kicker">What SPF did</p><p>__DID__</p></div>
        <div><p class="kicker">The result</p><p>__RESULT__</p></div>
      </div>
      <div class="tags-row"><p class="kicker">Why SPF</p>__WHY__</div>
      <div class="tags-row"><p class="kicker">Industries</p>__INDS__</div>
    </div></section>
    <section class="cta-band"><div class="wrap center">
      <h2 class="h-light">Have a similar challenge?</h2><p class="lede lede-light">Send a part or a print — we'll come back with a concept and a number.</p>
      <a href="/#rfq" class="btn btn-spark btn-lg">Start an RFQ →</a>
    </div></section>
  </main>
  <footer class="site-footer"><div class="wrap footer-grid">
    <div><span class="brand-text">SOUTHERN PERFECTION FABRICATION</span><p class="footer-mono">Complete metal fabrication under one roof</p><p class="footer-mono">ISO 9001 · CAGE 2W654 · Est. 1982 · Byron, GA</p></div>
    <nav aria-label="Footer"><ul><li><a href="/case-studies/">Case Studies</a></li><li><a href="/returnable-steel-racks/">Returnable Racks</a></li><li><a href="/capabilities/">Capabilities</a></li><li><a href="/industries/">Industries</a></li><li><a href="/how-to-spec-a-returnable-rack/">Spec Guide</a></li><li><a href="/contact/">Contact</a></li></ul></nav>
    <div class="footer-contact"><a href="tel:+14789564442" class="phone">478-956-4442</a><br><a href="mailto:sales@southernperfection.com">sales@southernperfection.com</a><br><span class="footer-mono">232 Hwy 49 S · Byron, GA 31008</span></div>
  </div><div class="wrap footer-legal"><small>© 2026 Southern Perfection Fabrication. All rights reserved.</small></div></footer>
</body>
</html>
"""

for slug,cat,h1,sub,stats,challenge,did,result,why,inds,title,desc in CASES:
    og = h1.rstrip(".")
    schema = {"@context":"https://schema.org","@graph":[
        {"@type":"BreadcrumbList","itemListElement":[
            {"@type":"ListItem","position":1,"name":"Home","item":"https://southernperfection.com/"},
            {"@type":"ListItem","position":2,"name":"Case Studies","item":"https://southernperfection.com/case-studies/"},
            {"@type":"ListItem","position":3,"name":og,"item":f"https://southernperfection.com/case-studies/{slug}/"}]},
        {"@type":"Article","headline":h1,"about":cat,"description":desc,
         "publisher":{"@type":"Organization","name":"Southern Perfection Fabrication","telephone":"+1-478-956-4442"}}]}
    stats_html = "".join(f'<div class="stat"><b>{s[0]}</b><span>{s[1]}</span></div>' for s in stats)
    why_html = "".join(f'<span class="tag">{w}</span>' for w in why)
    inds_html = "".join(f'<span class="tag tag-ind">{i}</span>' for i in inds)
    html = (TPL.replace("__TITLE__",title).replace("__DESC__",desc).replace("__SLUG__",slug)
               .replace("__OG__",og).replace("__CAT__",cat).replace("__H1__",h1).replace("__SUB__",sub)
               .replace("__STATS__",stats_html).replace("__CHALLENGE__",challenge).replace("__DID__",did)
               .replace("__RESULT__",result).replace("__WHY__",why_html).replace("__INDS__",inds_html)
               .replace("__SCHEMA__",json.dumps(schema, ensure_ascii=False)))
    d = ROOT / "case-studies" / slug
    d.mkdir(parents=True, exist_ok=True)
    (d/"index.html").write_text(html)
    print(" -", f"case-studies/{slug}/")
print("Done.")

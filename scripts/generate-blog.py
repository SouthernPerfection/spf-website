#!/usr/bin/env python3
"""Generate the blog hub + articles. Run from website/ root, then apply-header.py + generate-sitemap.py."""
import pathlib, json
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATE = "2026-07-08"

# slug, metatitle, metadesc, h1, dek, body_html, [ (label,url) related ]
POSTS = [
 ("returnable-packaging-roi",
  "Returnable Packaging ROI: How to Calculate Cost per Trip | Southern Perfection",
  "Calculate returnable packaging ROI the right way — cost per trip, trips per year, and the damage and freight savings expendable packaging hides. A practical framework from Southern Perfection Fabrication.",
  "Returnable packaging ROI: how to calculate cost per trip.",
  "The single number that decides whether a returnable rack pays off — and the costs most teams forget to count.",
  """<h2>Start with cost per trip, not sticker price</h2>
<p>A returnable steel rack costs more up front than a wood crate or a cardboard box. That's the wrong comparison. The number that matters is <strong>cost per trip</strong>: the rack's cost divided by the trips it makes over its service life. A $600 rack that runs 500 trips costs about $1.20 per trip in packaging — before you count what it saves.</p>
<h2>The formula</h2>
<p>Cost per trip = (rack cost + lifetime repair cost − salvage value) ÷ total trips. A well-built <a href="/returnable-steel-racks/">returnable steel rack</a> runs hundreds of trips, and because it can be <a href="/rack-repair-refurbishment/">repaired and refurbished</a>, its service life stretches further still — lowering cost per trip every cycle.</p>
<h2>Count the costs expendable packaging hides</h2>
<p>Sticker price is only part of the story. Returnable racks win biggest on the costs expendable packaging quietly adds:</p>
<ul>
<li><strong>Transit damage.</strong> Cardboard and loose dunnage let parts shift. Scrapped parts and line-down events dwarf packaging cost.</li>
<li><strong>Repeat purchasing.</strong> You buy expendable packaging every single shipment, forever.</li>
<li><strong>Disposal &amp; labor.</strong> Someone breaks down, stores, and disposes of one-way packaging every cycle.</li>
<li><strong>Freight density.</strong> A rack engineered to cube out the trailer ships more parts per truck.</li>
</ul>
<h2>A quick worked example</h2>
<p>Say a returnable rack costs $600, runs 500 trips, and needs one $80 refurbishment. Cost per trip ≈ $1.36. If expendable packaging for the same load runs $9 per trip and lets through $2 of average damage, that's $11 per trip — roughly an 8× difference, before floor-space and labor savings.</p>
<h2>Where the math flips</h2>
<p>Returnables win when volume and trip count are high and the loop is controlled. For very low-volume or one-way lanes, expendable can still be right. The honest answer comes from your real numbers — see our deeper breakdown of <a href="/returnable-vs-expendable-packaging/">returnable vs. expendable packaging</a>, or send us your part and lanes and we'll run it.</p>""",
  [("Returnable Steel Racks","/returnable-steel-racks/"),("Returnable vs. Expendable","/returnable-vs-expendable-packaging/"),("Rack Repair & Refurb","/rack-repair-refurbishment/")]),

 ("repair-or-replace-returnable-racks",
  "Repair or Replace? When to Refurbish a Returnable Rack Fleet | Southern Perfection",
  "When to repair vs replace a returnable rack fleet — the cost, safety, and downtime signals that say refurbish instead of buy new. From Southern Perfection Fabrication.",
  "Repair or replace? When to refurbish a returnable rack fleet.",
  "A worn fleet doesn't always mean a new-build PO. Here's how to decide.",
  """<h2>The default answer is usually &ldquo;repair&rdquo;</h2>
<p>Returnable racks are built to be fixed. A rack that's bent, cracked, or worn after years in the loop can often be re-welded, re-membered, and re-finished back to original spec for <strong>a fraction of new-build cost</strong> — and back in service in days, not the weeks a new build takes. See how one fleet came <a href="/case-studies/rack-repair-fleet/">back to spec for about 40% of new</a>.</p>
<h2>Signals it's time to refurbish (not replace)</h2>
<ul>
<li>Bent uprights, cracked welds, or worn contact points — but the core structure is sound.</li>
<li>Finish failure (rust, chipped coating) that risks the part.</li>
<li>Safety concerns from damage, not from a design flaw.</li>
<li>The rack still fits the part and the loop.</li>
</ul>
<h2>Signals it's time to replace</h2>
<ul>
<li>The part changed — new geometry the old rack can't hold.</li>
<li>The design was wrong from the start (ergonomics, density, protection).</li>
<li>Damage is so widespread that repair approaches new-build cost.</li>
</ul>
<h2>Why fleet economics favor refurb</h2>
<p>Refurbishment extends fleet life by years, spreads capital over more trips (lowering <a href="/blog/returnable-packaging-roi/">cost per trip</a>), and keeps racks in rotation instead of ordering a full replacement fleet. A shop that <em>builds</em> racks already knows their failure points — which makes the repair faster and truer to spec. That's the model behind our <a href="/rack-repair-refurbishment/">rack repair &amp; refurbishment</a> service.</p>""",
  [("Rack Repair & Refurb","/rack-repair-refurbishment/"),("Case Study: Fleet Refurb","/case-studies/rack-repair-fleet/"),("Returnable Packaging ROI","/blog/returnable-packaging-roi/")]),

 ("stackable-vs-collapsible-racks",
  "Stackable vs. Collapsible Racks: Which Cuts Return Freight? | Southern Perfection",
  "Stackable vs collapsible returnable racks — how each affects loaded density and empty-return freight, and which to choose for your lanes. From Southern Perfection Fabrication.",
  "Stackable vs. collapsible racks: which cuts return freight?",
  "The empty trip costs as much as the loaded one. Here's how rack format changes the math.",
  """<h2>Loaded density vs. empty return</h2>
<p>Every returnable rack makes two trips: loaded out, empty back. Teams optimize the loaded trip and forget the return — where you're paying to ship <em>air</em>. Rack format is the biggest lever on that return cost.</p>
<h2>Stackable racks</h2>
<p><a href="/stack-racks/">Stack racks</a> stack loaded, using vertical space to cube out the truck on the way out. Rigid and simple, they're ideal when loaded density matters most and return volume is manageable.</p>
<h2>Collapsible &amp; knock-down racks</h2>
<p>Collapsible racks fold or knock down flat when empty — often 4:1 or more — so you ship far fewer trailers of empties home. When return lanes are long or frequent, that folding action can pay for the rack on return freight alone.</p>
<h2>How to choose</h2>
<ul>
<li>Long or frequent return lanes → collapsible wins on empty freight.</li>
<li>Short loops or maximum loaded density → stackable is simpler and tougher.</li>
<li>Mixed → design to the specific lanes and dunnage.</li>
</ul>
<p>The right answer is your trailer and your lanes — the reason we design <a href="/returnable-steel-racks/">returnable racks</a> and <a href="/returnable-containers/">industrial metal containers</a> to spec rather than off a shelf.</p>""",
  [("Stack Racks","/stack-racks/"),("Industrial Metal Containers","/returnable-containers/"),("Returnable Steel Racks","/returnable-steel-racks/")]),

 ("steel-vs-wood-cardboard-shipping-racks",
  "Steel vs. Wood & Cardboard Shipping Racks: A Buyer's Comparison | Southern Perfection",
  "Steel returnable shipping racks vs wood crates and cardboard — durability, cost per trip, part protection, and when each makes sense. From Southern Perfection Fabrication.",
  "Steel vs. wood &amp; cardboard shipping racks.",
  "A straight comparison across the things that actually drive total cost.",
  """<h2>Durability &amp; service life</h2>
<p>Steel returnable racks run hundreds of trips and can be repaired; wood crates splinter and cardboard is effectively single-use. Over a program's life, one steel rack replaces dozens or hundreds of expendable units.</p>
<h2>Part protection</h2>
<p>Steel racks hold parts in engineered locations with <a href="/dunnage/">dunnage</a> and <a href="/custom-foam-inserts/">foam inserts</a>, preventing the shifting that scraps parts. Wood and cardboard offer far less control, especially for heavy or finish-critical parts.</p>
<h2>Cost per trip</h2>
<p>Steel costs more up front and wins on <a href="/blog/returnable-packaging-roi/">cost per trip</a> once volume and trip count are high. Wood and cardboard have low sticker price, but you buy them again every shipment.</p>
<h2>When wood or cardboard still make sense</h2>
<p>One-way international lanes, very low volume, or uncontrolled loops can favor expendable. For repeat domestic lanes at volume, steel returnables usually win — see the full <a href="/returnable-vs-expendable-packaging/">returnable vs. expendable</a> breakdown.</p>""",
  [("Returnable vs. Expendable","/returnable-vs-expendable-packaging/"),("Dunnage","/dunnage/"),("Custom Foam Inserts","/custom-foam-inserts/")]),

 ("reduce-transit-damage-returnable-packaging",
  "How to Reduce Transit Damage with the Right Returnable Rack | Southern Perfection",
  "Cut transit damage on the line — how rack design, dunnage, and foam inserts protect parts in transport. Practical guidance from Southern Perfection Fabrication.",
  "How to reduce transit damage with the right returnable rack.",
  "Most transit damage traces back to parts that could move. Here's how to lock them down.",
  """<h2>Damage starts with movement</h2>
<p>Parts that shift, rub, or drop in transit get scrapped. The fix is a rack that holds each part in a defined, cushioned position for the whole trip.</p>
<h2>Design the rack around the part</h2>
<p>Engineered <a href="/returnable-steel-racks/">returnable racks</a> place each part in a nest or cradle with fork access and ergonomics designed in — so parts don't stack, lean, or touch steel. Getting this right up front is the cheapest engineering you'll do; our <a href="/how-to-spec-a-returnable-rack/">spec guide</a> walks through exactly what to nail down.</p>
<h2>Add the right dunnage</h2>
<p><a href="/dunnage/">Dunnage</a> and <a href="/custom-foam-inserts/">custom foam inserts</a> separate parts and absorb shock. Finish-critical surfaces get foam so steel never touches the part.</p>
<h2>Finish for the environment</h2>
<p>Powder coat and the right base material keep the rack itself from becoming a damage source through rust or wear over hundreds of trips.</p>
<p>Done together, these turn a damage problem into a solved one — see a <a href="/case-studies/custom-rack-design/">rack engineered for a part nothing else fit</a>.</p>""",
  [("Returnable Steel Racks","/returnable-steel-racks/"),("Custom Foam Inserts","/custom-foam-inserts/"),("Spec Guide","/how-to-spec-a-returnable-rack/")]),

 ("single-source-metal-fabrication",
  "Single-Source Fabrication: Why One Roof Beats Three Vendors | Southern Perfection",
  "The case for single-source metal fabrication — how one-roof cut, weld, and finish cuts lead time, freight, and quality risk vs juggling separate suppliers. Southern Perfection Fabrication.",
  "Single-source fabrication: why one roof beats three vendors.",
  "Every handoff between suppliers adds time, cost, and someone to blame.",
  """<h2>The hidden cost of handoffs</h2>
<p>Sourcing racks across a cutter, a welder, and a coater means parts truck between shops, lead times stack, and when quality slips, suppliers point at each other. Every handoff is a delay and a risk.</p>
<h2>One roof, one PO, one accountable team</h2>
<p>When cutting, forming, welding, and <a href="/capabilities/powder-coating/">finishing</a> all happen <a href="/capabilities/">under one roof</a>, the job moves on a single clock. One purchase order, one team that owns the result end to end — and a shop you can visit and audit.</p>
<h2>What it saves</h2>
<ul>
<li><strong>Lead time</strong> — no inter-shop freight or queue-stacking; often cut roughly in half.</li>
<li><strong>Freight</strong> — regional, single-facility sourcing instead of long hauls between vendors.</li>
<li><strong>Quality risk</strong> — one accountable quality system (<a href="/capabilities/quality-inspection/">ISO 9001, CMM</a>), not three.</li>
</ul>
<p>One manufacturer did exactly this — <a href="/case-studies/single-source-switch/">three vendors to one roof</a>, lead time cut ~50%, freight down 20–30%, all on one PO.</p>""",
  [("Capabilities","/capabilities/"),("Case Study: Single-Source","/case-studies/single-source-switch/"),("Quality & Inspection","/capabilities/quality-inspection/")]),
]

ART_TPL = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>__TITLE__</title>
  <meta name="description" content="__DESC__">
  <link rel="canonical" href="https://southernperfection.com/blog/__SLUG__/">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta property="og:type" content="article"><meta property="og:site_name" content="Southern Perfection Fabrication">
  <meta property="og:title" content="__OG__"><meta property="og:url" content="https://southernperfection.com/blog/__SLUG__/">
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
      <p class="eyebrow"><a href="/" style="color:inherit">Home</a> · <a href="/blog/" style="color:inherit">Blog</a></p>
      <h1 id="h">__H1__</h1>
      <p class="lede">__DEK__</p>
      <p class="article-meta">Southern Perfection Fabrication · Byron, GA</p>
    </div></section>
    <section class="section"><div class="wrap article-body">
      __BODY__
    </div></section>
    <section class="section section-paper"><div class="wrap">
      <p class="kicker">Related</p><div class="tiles">__RELATED__</div>
    </div></section>
    <section class="cta-band"><div class="wrap center">
      <h2 class="h-light">Have a part to quote?</h2><p class="lede lede-light">Send a part or a print — we'll come back with a concept and a number.</p>
      <a href="/#rfq" class="btn btn-spark btn-lg">Start an RFQ →</a>
    </div></section>
  </main>
  <footer class="site-footer"><div class="wrap footer-grid">
    <div><span class="brand-text">SOUTHERN PERFECTION FABRICATION</span><p class="footer-mono">Complete metal fabrication under one roof</p><p class="footer-mono">ISO 9001 · CAGE 2W654 · Est. 1982 · Byron, GA</p></div>
    <nav aria-label="Footer"><ul><li><a href="/blog/">Blog</a></li><li><a href="/case-studies/">Case Studies</a></li><li><a href="/returnable-steel-racks/">Returnable Racks</a></li><li><a href="/capabilities/">Capabilities</a></li><li><a href="/industries/">Industries</a></li><li><a href="/contact/">Contact</a></li></ul></nav>
    <div class="footer-contact"><a href="tel:+14789564442" class="phone">478-956-4442</a><br><a href="mailto:sales@southernperfection.com">sales@southernperfection.com</a><br><span class="footer-mono">232 Hwy 49 S · Byron, GA 31008</span></div>
  </div><div class="wrap footer-legal"><small>© 2026 Southern Perfection Fabrication. All rights reserved.</small></div></footer>
</body>
</html>
"""

for slug,title,desc,h1,dek,body,related in POSTS:
    og = h1.replace("&amp;","&").rstrip(".")
    schema = {"@context":"https://schema.org","@graph":[
        {"@type":"BreadcrumbList","itemListElement":[
            {"@type":"ListItem","position":1,"name":"Home","item":"https://southernperfection.com/"},
            {"@type":"ListItem","position":2,"name":"Blog","item":"https://southernperfection.com/blog/"},
            {"@type":"ListItem","position":3,"name":og,"item":f"https://southernperfection.com/blog/{slug}/"}]},
        {"@type":"BlogPosting","headline":og,"description":desc,"datePublished":DATE,"dateModified":DATE,
         "author":{"@type":"Organization","name":"Southern Perfection Fabrication"},
         "publisher":{"@type":"Organization","name":"Southern Perfection Fabrication","telephone":"+1-478-956-4442"},
         "mainEntityOfPage":f"https://southernperfection.com/blog/{slug}/"}]}
    rel = "".join(f'<a class="tile" href="{u}"><h3>{l}</h3><span class="tile-go">Read →</span></a>' for l,u in related)
    html = (ART_TPL.replace("__TITLE__",title).replace("__DESC__",desc).replace("__SLUG__",slug)
               .replace("__OG__",og).replace("__H1__",h1).replace("__DEK__",dek)
               .replace("__BODY__",body).replace("__RELATED__",rel)
               .replace("__SCHEMA__",json.dumps(schema, ensure_ascii=False)))
    d = ROOT/"blog"/slug; d.mkdir(parents=True, exist_ok=True)
    (d/"index.html").write_text(html)
    print(" -", f"blog/{slug}/")

# hub
cards = "".join(f'<a class="tile" href="/blog/{s}/"><h3>{h1.replace("&amp;","&").rstrip(".")}</h3><p>{dek}</p><span class="tile-go">Read →</span></a>'
                for s,t,de,h1,dek,b,r in POSTS)
hub = ART_TPL  # reuse shell minimally
hub_html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Blog — Returnable Packaging &amp; Metal Fabrication Insights | Southern Perfection</title>
<meta name="description" content="Practical guidance on returnable packaging, rack ROI, repair vs replace, transit damage, and single-source metal fabrication — from Southern Perfection Fabrication, Byron, GA.">
<link rel="canonical" href="https://southernperfection.com/blog/">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="website"><meta property="og:site_name" content="Southern Perfection Fabrication">
<meta property="og:title" content="Blog — Returnable Packaging & Metal Fabrication Insights"><meta property="og:url" content="https://southernperfection.com/blog/">
<meta property="og:description" content="Returnable packaging ROI, repair vs replace, transit damage, single-source fabrication — practical guidance.">
<meta property="og:image" content="https://southernperfection.com/assets/og-cover.jpg">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;600;700&display=swap">
<link rel="stylesheet" href="/assets/styles.css">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Blog","name":"Southern Perfection Fabrication Blog","url":"https://southernperfection.com/blog/","publisher":{{"@type":"Organization","name":"Southern Perfection Fabrication"}}}}
</script>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap header-inner"><a href="/" class="brand"><span class="brand-mark"></span><span class="brand-text">SOUTHERN&nbsp;PERFECTION</span></a><div class="header-cta"><a href="tel:+14789564442" class="phone">478-956-4442</a><a href="/#rfq" class="btn btn-spark">Start an RFQ</a></div></div></header>
<main id="main">
<section class="hero" aria-labelledby="h"><div class="wrap">
<p class="eyebrow"><a href="/" style="color:inherit">Home</a> · Blog</p>
<h1 id="h">Returnable packaging, done right.</h1>
<p class="lede">Practical guidance on speccing racks, calculating ROI, repair vs. replace, cutting transit damage, and single-source fabrication — from the shop floor in Byron, GA.</p>
</div></section>
<section class="section"><div class="wrap">
<p class="kicker">Latest</p><h2>From the shop.</h2>
<div class="tiles">{cards}</div>
</div></section>
<section class="cta-band"><div class="wrap center">
<h2 class="h-light">Have a part to quote?</h2><p class="lede lede-light">Send a part or a print — we'll come back with a concept and a number.</p>
<a href="/#rfq" class="btn btn-spark btn-lg">Start an RFQ →</a>
</div></section>
</main>
<footer class="site-footer"><div class="wrap footer-grid">
<div><span class="brand-text">SOUTHERN PERFECTION FABRICATION</span><p class="footer-mono">Complete metal fabrication under one roof</p><p class="footer-mono">ISO 9001 · CAGE 2W654 · Est. 1982 · Byron, GA</p></div>
<nav aria-label="Footer"><ul><li><a href="/blog/">Blog</a></li><li><a href="/case-studies/">Case Studies</a></li><li><a href="/returnable-steel-racks/">Returnable Racks</a></li><li><a href="/capabilities/">Capabilities</a></li><li><a href="/industries/">Industries</a></li><li><a href="/contact/">Contact</a></li></ul></nav>
<div class="footer-contact"><a href="tel:+14789564442" class="phone">478-956-4442</a><br><a href="mailto:sales@southernperfection.com">sales@southernperfection.com</a><br><span class="footer-mono">232 Hwy 49 S · Byron, GA 31008</span></div>
</div><div class="wrap footer-legal"><small>© 2026 Southern Perfection Fabrication. All rights reserved.</small></div></footer>
</body></html>
"""
(ROOT/"blog").mkdir(exist_ok=True)
(ROOT/"blog"/"index.html").write_text(hub_html)
print(" - blog/ (hub)")
print("Done.")

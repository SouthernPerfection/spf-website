#!/usr/bin/env python3
"""Wave 3 SEO robustness: expand the 13 industry pages with a definition section + deeper FAQ.
Appends FAQs where a FAQ section exists; creates one (+ schema) where it doesn't. Idempotent."""
import pathlib, re, json

DATA = {
"industries/automotive": dict(
 kicker="Automotive", h2="Returnable packaging for automotive manufacturing",
 paras=['Automotive OEMs and Tier-1 suppliers run on returnable packaging — steel racks, containers, and dunnage that move engines, bumpers, coils, tires, and sub-assemblies between plants on a tight, repeatable loop. On a launch timeline, the packaging has to be right the first time.',
        'SPF designs and builds returnable automotive packaging to your part, line, and launch date — <a href="/automotive-racks/">automotive racks</a>, <a href="/engine-racks/">engine racks</a>, <a href="/wip-carts/">WIP carts</a>, and <a href="/custom-foam-inserts/">foam dunnage</a> — engineered in-house and built to print.',
        'See how we delivered a <a href="/case-studies/engine-rack-program/">300+ engine-rack fleet in about half the quoted lead time</a> for a Tier-1 launch.'],
 faqs=[("Do you support automotive program launches?","Yes. We engineer and build returnable racks and dunnage to your launch timeline — often ahead of the schedule other sources quote."),
       ("Can you build to automotive quality standards?","Yes. We operate an ISO 9001 quality system with CMM inspection and build to print for OEM and Tier-1 programs."),
       ("What automotive parts do you build racks for?","Engines and powertrain, bumpers, coils, tires and wheels, body panels, and sub-assemblies — racks engineered to each part.")]),

"industries/aerospace-defense": dict(
 kicker="Aerospace &amp; defense", h2="Aerospace &amp; defense fabrication and crating",
 paras=['Aerospace and defense programs run on multi-year, government-funded work that rewards traceability and reliability. SPF supports both non-flight fabrication — weldments, tooling, and ground-support equipment — and custom crating and ruggedized containers for high-value assets.',
        'With CAGE 2W654, an ISO 9001 quality system, and CMM inspection, we build to your print with the documentation the programs require. We build to print; we do not certify flight-critical hardware.',
        'See how we delivered <a href="/case-studies/tooling-gse/">non-flight tooling and GSE at 100% conformance</a> for a regulated program.'],
 faqs=[("Do you have a CAGE code?","Yes — CAGE 2W654, registered to support defense and government-funded work."),
       ("Do you build to program specifications?","We build ruggedized crates, containers, tooling, and GSE to your program requirements and documentation standards. Send the spec and we will confirm."),
       ("What aerospace and defense work do you do?","Non-flight fabrication — weldments, tooling, ground-support equipment — plus custom crating and ruggedized containers.")]),

"industries/ev-battery": dict(
 kicker="EV / battery", h2="Returnable packaging for EV and battery manufacturing",
 paras=['The EV and battery corridor is scaling fast, and modules, packs, and cells need returnable steel packaging engineered for weight, protection, and the handling of sensitive components.',
        'SPF builds returnable racks, containers, and dunnage for EV and battery makers — durable, custom-engineered, and finished in-house — with the <a href="/capabilities/robotic-welding/">robotic-welding capacity</a> to scale with a new line.',
        'See how we delivered <a href="/case-studies/high-volume-fleet/">1,000+ identical racks on time</a> for a high-volume launch.'],
 faqs=[("Do you build packaging for battery modules and packs?","Yes. We engineer returnable racks, containers, and dunnage to your module, pack, or cell — protecting weight-sensitive, high-value components."),
       ("Can you scale with a new EV line?","Yes. Robotic welding and in-house scheduling let us deliver large fleets of identical racks on a launch timeline."),
       ("Do you build specialty or ESD handling?","Yes — we spec finishes, foam, and dunnage to your component’s protection and handling requirements.")]),

"industries/heavy-equipment": dict(
 kicker="Heavy equipment", h2="Returnable racks for heavy equipment and off-highway",
 paras=['Heavy equipment and off-highway builders move large, heavy, awkward parts — frames, axles, booms, and weldments — that no off-the-shelf rack fits. They need heavy-duty returnable racks engineered around the part.',
        'SPF’s in-house engineering designs heavy-duty steel racks, <a href="/weldments-frames/">weldments</a>, and <a href="/guards-platforms/">guarding</a> for off-highway parts, rated to your load and built to print.',
        'See how our engineering <a href="/case-studies/custom-rack-design/">built a rack for a part nothing else fit</a> — approved on the first design pass.'],
 faqs=[("Can you handle large, heavy, or awkward parts?","Yes. We engineer heavy-duty racks and weldments for oversized, heavy parts common in off-highway and heavy equipment."),
       ("Do you engineer custom racks for off-highway parts?","Yes. Our SolidWorks team designs a returnable rack around your specific part, load path, and handling — built to print."),
       ("What load ratings can you build to?","We engineer the rack and welds to your specific load, from moderate to heavy off-highway parts.")]),

"industries/general-industrial": dict(
 kicker="General manufacturing", h2="Returnable packaging for general manufacturing",
 paras=['Across general manufacturing — appliance, power, rail, consumer goods, and more — returnable steel racks, containers, and carts move parts efficiently and protect them in transit.',
        'SPF is a single-source fabricator for general industry: <a href="/returnable-steel-racks/">racks</a>, <a href="/returnable-containers/">metal containers</a>, <a href="/steel-pallets/">steel pallets</a>, and <a href="/industrial-carts/">carts</a>, all built to print under one roof.',
        'See how consolidating to one roof <a href="/case-studies/single-source-switch/">cut lead time roughly in half</a> for a manufacturer.'],
 faqs=[("What industries do you serve?","Automotive, aerospace and defense, EV and battery, heavy equipment, food and beverage, and general manufacturing across the Southeast and Midwest."),
       ("Can you be a single-source fabrication partner?","Yes. We cut, form, machine, weld, and finish under one roof, on one purchase order, with one accountable team."),
       ("Do you build low and high volume?","Yes — from prototypes and small runs to full production programs, built to print.")]),

"industries/food-beverage-dairy": dict(
 kicker="Food, beverage &amp; dairy", h2="Returnable packaging for food, beverage &amp; dairy",
 paras=['Food, beverage, and dairy plants need durable, sanitation-friendly returnable racks and containers that move ingredients, packaging, and product safely — often through washdown environments.',
        'SPF builds returnable racks, carts, and <a href="/returnable-containers/">containers</a> in stainless and washdown-friendly finishes for food and beverage operations, built to your line and standards.'],
 faqs=[("Do you build stainless or washdown-friendly racks?","Yes. We work in stainless and finish builds for washdown and sanitation environments common in food, beverage, and dairy."),
       ("Can you match our line and totes?","Yes — racks, carts, and containers designed to your product, totes, and line layout, built to print."),
       ("Do you build for food-grade environments?","Yes. We spec materials and finishes suited to food and beverage sanitation requirements.")]),

"industries/packaging-paper": dict(
 kicker="Packaging &amp; paper", h2="Returnable racks for packaging and paper converters",
 paras=['Packaging and paper converters move rolls, cores, sheets, and finished goods that need cradles and racks engineered to protect them from crushing and damage.',
        'SPF builds roll racks, core cradles, and returnable racks for converters, sized to your rolls and freight lanes — with <a href="/coil-racks/">coil racks</a> for wound product.'],
 faqs=[("Do you build roll and core racks?","Yes. We design cradles and racks that hold rolls, cores, and reels securely for transport and storage."),
       ("Can you handle finished-goods racks too?","Yes — racks and carts for sheets, converted product, and finished goods, built to your spec."),
       ("Are the racks returnable and stackable?","Yes. We build durable, stackable returnable racks engineered for the loop.")]),

"industries/transportation-trailer": dict(
 kicker="Transportation &amp; trailer", h2="Fabrication for transportation and trailer manufacturers",
 paras=['Truck, trailer, and transportation builders need returnable racks, robotic-welded frames, and weldments at production volume, built to print.',
        'SPF builds <a href="/weldments-frames/">weldments</a>, frames, and returnable racks for transportation and trailer manufacturers, with the <a href="/capabilities/robotic-welding/">robotic-welding capacity</a> to hold volume.'],
 faqs=[("Do you build production-volume weldments?","Yes. With 30+ MIG stations and FANUC robotic welding we build weldments and frames at production volume, built to print."),
       ("Can you build our part racks too?","Yes — returnable racks and carts for parts and sub-assemblies, designed to your line."),
       ("Do you finish in-house?","Yes. In-house powder coat and wet paint mean parts ship finished, not waiting on an outside coater.")]),

"industries/chemical-processing": dict(
 kicker="Chemical processing", h2="Fabrication for chemical processing",
 paras=['Chemical processing plants need durable racks, platforms, and fabrication built for tough, corrosive environments with corrosion-aware finishes.',
        'SPF builds returnable racks, <a href="/guards-platforms/">access platforms and guarding</a>, and steel fabrication for chemical processing — finished to survive the environment, built to print.'],
 faqs=[("Can you finish for corrosive environments?","Yes. We powder coat and finish in-house and can specify finishes suited to chemical processing environments."),
       ("Do you build platforms and access structures?","Yes — access platforms, mezzanines, and guarding, built to your drawing."),
       ("What can you fabricate for chemical plants?","Returnable racks and containers, access platforms, guarding, and custom steel fabrication, built to print.")]),

"industries/mining-aggregate": dict(
 kicker="Mining &amp; aggregate", h2="Heavy-duty fabrication for mining and aggregate",
 paras=['Mining and aggregate operations run heavy, hard-duty equipment that needs heavy-duty racks, weldments, and guarding built to survive demanding service.',
        'SPF builds heavy-duty racks, structural <a href="/weldments-frames/">weldments</a>, and <a href="/guards-platforms/">machine guarding</a> for mining and aggregate — built tough and built to print.'],
 faqs=[("Can you handle heavy, oversized parts?","Yes. We engineer heavy-duty racks and weldments for large, heavy parts common in mining and aggregate."),
       ("Do you build machine guarding?","Yes — guarding, platforms, and access structures built to your drawing."),
       ("What do you fabricate for mining?","Heavy-duty racks, structural weldments and frames, and machine guarding for hard-duty service.")]),

"industries/industrial-machinery": dict(
 kicker="Industrial machinery &amp; OEM", h2="Fabrication for industrial machinery and OEMs",
 paras=['Industrial machinery and OEM builders need returnable racks, weldments, machined parts, and custom fabrication from one accountable partner.',
        'SPF is a single-source fab partner for OEMs — <a href="/capabilities/laser-cutting/">cut</a>, <a href="/capabilities/forming/">form</a>, <a href="/capabilities/cnc-machining/">machine</a>, <a href="/capabilities/robotic-welding/">weld</a>, and <a href="/capabilities/powder-coating/">finish</a> under one roof, built to print at production volume.'],
 faqs=[("Can you be a single-source fab partner?","Yes. We cut, form, machine, weld, and finish under one roof on one purchase order, with one accountable team."),
       ("Do you build to our production volumes?","Yes. Robotic welding and in-house scheduling let us build to your production volumes, built to print."),
       ("Do you machine components too?","Yes — CNC turning and milling integrated with the rest of fabrication under one roof.")]),

"industries/distribution-logistics": dict(
 kicker="Distribution &amp; logistics", h2="Returnable packaging for distribution and logistics",
 paras=['Distribution, warehousing, and 3PL operations run on returnable steel racks, containers, and pallets — reusable, stackable, and built to move product efficiently.',
        'SPF builds returnable racks, collapsible <a href="/returnable-containers/">containers</a>, and <a href="/steel-pallets/">steel pallets</a> sized to your product, footprint, and freight lanes.'],
 faqs=[("Do you build collapsible containers to save freight?","Yes. We build collapsible steel containers and stackable racks that fold or nest to cut return freight."),
       ("Can you match our warehouse footprint?","Yes — racks, containers, and pallets sized to your product, aisles, and racking."),
       ("Do you build steel pallets?","Yes. Durable, reusable steel pallets that outlast wood and plastic for high-cycle loads.")]),

"industries/energy-power": dict(
 kicker="Energy &amp; power", h2="Fabrication for energy and power generation",
 paras=['Energy and power generation equipment needs heavy-duty racks, robotic-welded frames, platforms, and structural fabrication built to print.',
        'SPF builds returnable racks, <a href="/weldments-frames/">weldments</a>, frames, and <a href="/guards-platforms/">access platforms</a> for energy and power generation, with heavy forming and welding capacity.'],
 faqs=[("Can you build heavy weldments and frames?","Yes. FANUC robotic welding and press-brake forming to 230 tons let us build heavy weldments and frames to print."),
       ("Do you build access platforms and guarding?","Yes — platforms, mezzanines, and guarding built to your drawing."),
       ("What do you fabricate for energy?","Returnable racks, heavy weldments and frames, access platforms, and structural fabrication.")]),
}

hero_re = re.compile(r'(<section class="hero".*?</section>)', re.S)
faqdiv_re = re.compile(r'(<div class="faq">.*?)(</div>)', re.S)
schema_re = re.compile(r'("@type"\s*:\s*"FAQPage"\s*,\s*"mainEntity"\s*:\s*\[.*?)(\]\})', re.S)
cta_re = re.compile(r'(<section class="cta-band">)')

for slug, d in DATA.items():
    f = pathlib.Path(slug) / "index.html"
    html = f.read_text()
    if 'data-wave2' in html:
        print("skip:", slug); continue
    paras = "".join(f"<p>{p}</p>\n      " for p in d["paras"])
    def_sec = (f'\n\n    <section class="section" data-wave2><div class="wrap article-body">\n'
               f'      <p class="kicker">{d["kicker"]}</p>\n      <h2>{d["h2"]}</h2>\n      {paras.rstrip()}\n    </div></section>')
    html = hero_re.sub(lambda m: m.group(1) + def_sec, html, count=1)
    if '<div class="faq">' in html:  # append to existing FAQ + schema
        extra = "".join(f'\n          <details><summary>{q}</summary><p>{a}</p></details>' for q,a in d["faqs"])
        html = faqdiv_re.sub(lambda m: m.group(1) + extra + "\n        " + m.group(2), html, count=1)
        qadd = "".join(', ' + json.dumps({"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}}, ensure_ascii=False) for q,a in d["faqs"])
        html = schema_re.sub(lambda m: m.group(1) + qadd + m.group(2), html, count=1)
    else:  # create new FAQ section + schema
        items = "".join(f'\n          <details><summary>{q}</summary><p>{a}</p></details>' for q,a in d["faqs"])
        faq_sec = (f'<section class="section section-paper"><div class="wrap">\n'
                   f'      <p class="kicker">FAQ</p>\n      <h2>{d["h2"].split(" for ")[0]} — answered.</h2>\n'
                   f'      <div class="faq">{items}\n        </div>\n    </div></section>\n\n    ')
        html = cta_re.sub(lambda m: faq_sec + m.group(1), html, count=1)
        schema = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in d["faqs"]]}
        html = html.replace('</head>', '  <script type="application/ld+json">\n  ' + json.dumps(schema, ensure_ascii=False) + '\n  </script>\n</head>', 1)
    f.write_text(html)
    wc = len(re.sub(r'<[^>]+>','', re.search(r'<main.*?</main>', html, re.S).group(0)).split())
    print(f"expanded {slug} → ~{wc} words")
print("Done.")

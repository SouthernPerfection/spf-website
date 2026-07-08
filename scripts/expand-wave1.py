#!/usr/bin/env python3
"""Wave 1 SEO robustness: expand the 6 highest-volume pages with unique, keyword-mapped
content — a definition+industries section, a types/materials card section, and 3 deeper FAQs
(visible + FAQPage schema). Run once from website/ root. Idempotent (skips if already expanded)."""
import pathlib, re, json

# page -> content. cards = [(h3, body)], faqs = [(q, a_html, a_plain)]
DATA = {
"custom-foam-inserts": dict(
 kicker="Custom foam inserts", h2="What are custom foam inserts?",
 paras=[
  'Custom foam inserts are precisely-cut foam cavities that cradle a part inside a rack, tote, or crate so it cannot shift, rub, or drop in transit. Also called <strong>protective foam packaging</strong> or <strong>foam packaging inserts</strong>, they pair with a returnable rack to protect finish-critical and fragile parts trip after trip.',
  'Southern Perfection Fabrication designs <strong>custom foam packaging</strong> around your exact part geometry — routed, die-cut, or laminated from the right foam density for the load. Because we also build the <a href="/returnable-steel-racks/">rack</a> and the <a href="/dunnage/">dunnage</a>, the foam, the nest, and the steel are engineered together as one protective system — not sourced from three vendors.',
  'We supply custom foam inserts for <a href="/industries/automotive/">automotive</a> interior and finish-critical parts, <a href="/industries/ev-battery/">EV and battery</a> modules, <a href="/industries/aerospace-defense/">aerospace and defense</a> components, and general manufacturing — anywhere a part is too valuable to let touch steel.'],
 sec_h2="Foam types &amp; when to use them",
 cards=[("Polyethylene (PE)","Firm closed-cell foam that holds up over hundreds of returnable trips — ideal for heavier parts."),
        ("Polyurethane (PU)","Softer open-cell foam for delicate, lighter, or finish-critical parts."),
        ("Cross-Linked","Fine-celled premium foam for high-value or Class-A surfaces."),
        ("ESD / Anti-Static","Conductive foam for electronics, sensors, and battery components.")],
 faqs=[("What foam is best for returnable packaging?",'For returnable loops, firmer closed-cell foams like polyethylene hold up best over hundreds of trips; softer polyurethane suits delicate or finish-critical parts. We spec the density to your part and cycle.','For returnable loops, firmer closed-cell foams like polyethylene hold up best over hundreds of trips; softer polyurethane suits delicate or finish-critical parts. We spec the density to your part and cycle.'),
       ("Do foam inserts work with steel racks?",'Yes — that is the point. We design the foam nest and the <a href="/returnable-steel-racks/">steel rack</a> together so the part is cradled and protected as one system.','Yes. We design the foam nest and the steel rack together so the part is cradled and protected as one system.'),
       ("Can you match our exact part shape?",'Yes. We rout or die-cut foam to your part geometry from CAD or a physical sample, so each part seats in a defined, cushioned pocket.','Yes. We rout or die-cut foam to your part geometry from CAD or a physical sample, so each part seats in a defined, cushioned pocket.')]),

"dunnage": dict(
 kicker="Dunnage", h2="What is dunnage?",
 paras=[
  'Dunnage is the material that separates, cushions, and locates parts inside a returnable rack or container so they do not shift or contact each other in transit. <strong>Foam dunnage</strong>, fabric, and formed-steel separators all do the same job: protect the part and hold it in position, trip after trip.',
  'We build <strong>custom dunnage</strong> and <strong>reusable dunnage</strong> engineered to your part and your rack — routed foam, sewn fabric, wire dividers, or welded-steel locators. Because it is designed alongside the <a href="/returnable-steel-racks/">rack</a> and <a href="/custom-foam-inserts/">foam inserts</a>, the whole protective system works together as one.',
  'Our returnable dunnage protects parts for <a href="/industries/automotive/">automotive</a>, <a href="/industries/aerospace-defense/">aerospace and defense</a>, <a href="/industries/ev-battery/">EV and battery</a>, and general manufacturing programs across the Southeast and Midwest.'],
 sec_h2="Types of returnable dunnage",
 cards=[("Foam Dunnage","Routed or die-cut foam that cradles and separates parts."),
        ("Fabric &amp; Soft","Sewn covers and soft separators for finish-critical surfaces."),
        ("Wire &amp; Steel","Wire dividers and welded-steel locators for heavier parts."),
        ("Molded / Thermoform","Formed trays and nests for high-volume, repeatable presentation.")],
 faqs=[("What is the difference between dunnage and packaging?",'Packaging contains the shipment; dunnage is what positions and cushions each part inside it. Good returnable dunnage is the difference between parts arriving intact and arriving scrapped.','Packaging contains the shipment; dunnage is what positions and cushions each part inside it. Good returnable dunnage is the difference between parts arriving intact and arriving scrapped.'),
       ("Is returnable dunnage reusable?",'Yes. We build durable, reusable dunnage engineered to run the full life of the returnable rack it sits in — repaired or replaced as parts wear.','Yes. We build durable, reusable dunnage engineered to run the full life of the returnable rack it sits in.'),
       ("Can you design dunnage for our existing racks?",'Yes. Send the rack and the part, and we will design foam, fabric, or steel dunnage that drops into what you already run.','Yes. Send the rack and the part, and we will design foam, fabric, or steel dunnage that drops into what you already run.')]),

"stack-racks": dict(
 kicker="Stack racks", h2="What are stack racks?",
 paras=[
  'Stack racks — also called <strong>stackable steel racks</strong> or <strong>steel stack racks</strong> — are portable steel racks that stack on top of one another when loaded, using vertical space to store and ship more parts in the same footprint. Post-and-deck and knockdown designs let you build a stable column of loaded racks, then nest or fold them flat when empty.',
  'SPF builds <strong>metal stacking racks</strong> to your part, load rating, and stack height — rigid for maximum strength or collapsible to cut return freight. Every rack is engineered in-house and built to print, so it stacks square, holds its rating, and comes back for the next load.',
  'Our stack racks move parts for <a href="/industries/automotive/">automotive</a>, <a href="/industries/heavy-equipment/">heavy equipment</a>, and general manufacturing — and pair with our <a href="/returnable-steel-racks/">returnable racks</a>, <a href="/steel-pallets/">steel pallets</a>, and <a href="/returnable-containers/">metal containers</a>.'],
 sec_h2="Rigid vs. collapsible stack racks",
 cards=[("Rigid Post","Fixed post-and-deck racks for maximum strength and fast handling."),
        ("Collapsible","Knock-down racks that fold flat empty to slash return freight."),
        ("Nestable","Racks that nest together empty to save floor and trailer space."),
        ("Custom Decks","Mesh, solid, or part-specific decks matched to your load.")],
 faqs=[("How high can stack racks be stacked?",'It depends on the load rating and post design — we engineer the rack and posts to your desired stack height and weight so the loaded column stays stable and square.','It depends on the load rating and post design. We engineer the rack and posts to your desired stack height and weight so the loaded column stays stable and square.'),
       ("Do stack racks collapse when empty?",'They can. We build collapsible and knock-down stack racks that fold flat empty, often 4:1 or better, to cut the cost of shipping empties home.','We build collapsible and knock-down stack racks that fold flat empty, often 4 to 1 or better, to cut the cost of shipping empties home.'),
       ("What is the difference between stack racks and pallet racks?",'Stack racks are portable and shippable — they travel with the parts through a returnable loop. Warehouse pallet racking is fixed to the floor. We build the portable, returnable kind.','Stack racks are portable and shippable and travel with the parts through a returnable loop. Warehouse pallet racking is fixed to the floor. We build the portable, returnable kind.')]),

"tire-racks": dict(
 kicker="Tire &amp; wheel racks", h2="What are returnable tire racks?",
 paras=[
  'Returnable tire racks are steel racks and carts engineered to move and store tires and wheels through a manufacturing or distribution loop — protecting the tread and bead while shipping dense. Industrial <strong>tire storage racks</strong> hold tires securely for transport between plants, warehouses, and assembly lines, then return empty for the next load.',
  'SPF builds custom tire and wheel racks and carts to your tire size, stack count, and handling method — stackable, collapsible, or on casters for line-side delivery. Built to print and finished in-house, they protect the product and cube out the trailer.',
  'We build tire and wheel handling for <a href="/industries/automotive/">automotive</a> assembly and <a href="/industries/distribution-logistics/">distribution and logistics</a> operations, alongside our <a href="/returnable-steel-racks/">returnable racks</a> and <a href="/industrial-carts/">industrial carts</a>.'],
 sec_h2="Tire &amp; wheel racks we build",
 cards=[("Tire Shipping Racks","Stackable steel racks that ship tires dense and protect the tread."),
        ("Wheel Racks","Racks and dividers that separate and protect finished wheels."),
        ("Tire Carts","Casters for safe, ergonomic line-side tire and wheel delivery."),
        ("Stackable / Collapsible","Stack loaded, fold empty — sized to your tire and lanes.")],
 faqs=[("Do you build racks for tires and wheels?",'Yes — custom steel tire racks, wheel racks, and carts engineered to your tire or wheel size, stack count, and handling method, built to print.','Yes. Custom steel tire racks, wheel racks, and carts engineered to your tire or wheel size, stack count, and handling method, built to print.'),
       ("Are your tire racks returnable and stackable?",'Yes. We build stackable and collapsible tire racks designed for the returnable loop — stack loaded, fold or nest empty to cut return freight.','Yes. We build stackable and collapsible tire racks designed for the returnable loop.'),
       ("Can you build tire carts for line-side delivery?",'Yes. We build ergonomic tire and wheel carts on casters that present product safely at the point of use.','Yes. We build ergonomic tire and wheel carts on casters that present product safely at the point of use.')]),

"coil-racks": dict(
 kicker="Coil racks", h2="What are coil racks?",
 paras=[
  'Coil racks are heavy-duty steel racks that cradle and transport coils, rolls, and reels — steel coil, wire, tubing, or hose — keeping them from deforming, unwinding, or contacting each other in transit. <strong>Coil storage racks</strong> hold coils securely on saddles or cradles matched to the coil diameter and weight.',
  'SPF builds custom coil racks and cradles to your coil size and weight, rated for heavy loads and built to print. Cradle geometry, dividers, and finish are all engineered to your product so coils ship dense and arrive round.',
  'We build coil and roll handling for <a href="/industries/automotive/">automotive</a> and <a href="/industries/heavy-equipment/">heavy equipment</a> supply chains, <a href="/industries/packaging-paper/">packaging and paper</a> converters, and general manufacturing — plus <a href="/steel-cable-reels/">steel cable reels</a> for wire and hose.'],
 sec_h2="Coil racks we build",
 cards=[("Saddle &amp; Cradle","Contoured cradles matched to your coil diameter and weight."),
        ("Stackable Coil Racks","Racks engineered to stack loaded and save floor and freight."),
        ("Returnable Coil Racks","Durable, reusable racks built for the returnable loop."),
        ("Dividers &amp; Inserts","Separators that keep coils from contacting and marring.")],
 faqs=[("How much weight can a coil rack hold?",'We engineer coil racks to your specific coil weight — from moderate rolls to heavy steel coils — with the cradle, gauge, and welds rated to the load.','We engineer coil racks to your specific coil weight, from moderate rolls to heavy steel coils, with the cradle, gauge, and welds rated to the load.'),
       ("Do you build racks for steel coils and wire?",'Yes — coil racks and cradles for steel coil, wire, tubing, and hose, plus dedicated <a href="/steel-cable-reels/">steel cable reels</a> for wound product.','Yes. Coil racks and cradles for steel coil, wire, tubing, and hose, plus dedicated steel cable reels for wound product.'),
       ("Are coil racks stackable and returnable?",'Yes. We build stackable, returnable coil racks that ship dense and run trip after trip in a closed loop.','Yes. We build stackable, returnable coil racks that ship dense and run trip after trip in a closed loop.')]),

"guards-platforms": dict(
 kicker="Guards &amp; platforms", h2="What is machine guarding?",
 paras=[
  'Machine guarding is the custom steel barriers, fencing, and <strong>safety guards</strong> that protect operators from moving equipment, pinch points, and hazards on the plant floor. Paired with access platforms and <strong>mezzanine platforms</strong>, guarding keeps people safe while keeping the line accessible and productive.',
  'SPF designs and builds custom machine guarding, safety guards, access platforms, stairs, and mezzanines to your equipment and floor layout — engineered to your safety requirements and built to print. Cut, formed, welded, and powder-coated in-house for a durable finish that lasts on the floor.',
  'We fabricate guarding and platforms for <a href="/industries/heavy-equipment/">heavy equipment</a>, <a href="/industries/industrial-machinery/">industrial machinery and OEM</a>, <a href="/industries/energy-power/">energy</a>, and general manufacturing plants.'],
 sec_h2="Guarding, platforms &amp; access",
 cards=[("Machine Guarding","Custom fencing and barriers engineered to your equipment and hazards."),
        ("Safety Guards","Point-of-operation guards and barriers to protect operators."),
        ("Access Platforms","Work platforms and crossover stairs for safe equipment access."),
        ("Mezzanines","Structural mezzanines and elevated platforms, built to print.")],
 faqs=[("Can you engineer guarding to our equipment?",'Yes. We design machine guarding and safety guards to your specific equipment, hazards, and floor layout, then build it to print in-house.','Yes. We design machine guarding and safety guards to your specific equipment, hazards, and floor layout, then build it to print in-house.'),
       ("Do you build access platforms, stairs, and mezzanines?",'Yes — work platforms, crossover stairs, and structural mezzanines engineered to your access needs and safety requirements.','Yes. Work platforms, crossover stairs, and structural mezzanines engineered to your access needs and safety requirements.'),
       ("Do you finish guarding for the plant floor?",'Yes. Guards and platforms are powder-coated in-house for a durable, high-visibility finish that survives industrial use.','Yes. Guards and platforms are powder-coated in-house for a durable, high-visibility finish that survives industrial use.')]),
}

hero_re = re.compile(r'(<section class="hero".*?</section>)', re.S)
faq_sec_re = re.compile(r'(<section class="section[^"]*">\s*<div class="wrap">\s*<p class="kicker">FAQ)')
faqdiv_re = re.compile(r'(<div class="faq">.*?)(</div>)', re.S)
schema_re = re.compile(r'("@type"\s*:\s*"FAQPage"\s*,\s*"mainEntity"\s*:\s*\[.*?)(\]\})', re.S)

for slug, d in DATA.items():
    f = pathlib.Path(slug) / "index.html"
    html = f.read_text()
    if 'data-wave1' in html:
        print("skip (already expanded):", slug); continue

    paras = "".join(f"<p>{p}</p>\n      " for p in d["paras"])
    def_sec = (f'\n\n    <section class="section" data-wave1><div class="wrap article-body">\n'
               f'      <p class="kicker">{d["kicker"]}</p>\n      <h2>{d["h2"]}</h2>\n      {paras.rstrip()}\n    </div></section>')
    cards = "".join(f'<article class="card"><h3>{h}</h3><p>{b}</p></article>' for h,b in d["cards"])
    mat_sec = (f'\n\n    <section class="section section-paper"><div class="wrap">\n'
               f'      <p class="kicker">Built to print</p>\n      <h2>{d["sec_h2"]}</h2>\n'
               f'      <div class="cards-4">{cards}</div>\n    </div></section>\n')
    # 1. definition section after hero
    html = hero_re.sub(lambda m: m.group(1) + def_sec, html, count=1)
    # 2. materials section before FAQ section
    m = faq_sec_re.search(html)
    if m:
        html = html[:m.start()] + mat_sec + "\n    " + html[m.start():]
    else:
        print("  ! no FAQ anchor:", slug)
    # 3. extra FAQ <details>
    extra = "".join(f'\n          <details><summary>{q}</summary><p>{a}</p></details>' for q,a,_ in d["faqs"])
    html = faqdiv_re.sub(lambda m: m.group(1) + extra + "\n        " + m.group(2), html, count=1)
    # 4. schema Q&As
    qadd = "".join(', ' + json.dumps({"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":ap}}, ensure_ascii=False) for q,_,ap in d["faqs"])
    html = schema_re.sub(lambda m: m.group(1) + qadd + m.group(2), html, count=1)

    f.write_text(html)
    wc = len(re.sub(r'<[^>]+>','', re.search(r'<main.*?</main>', html, re.S).group(0)).split())
    print(f"expanded {slug} → ~{wc} words")
print("Done.")

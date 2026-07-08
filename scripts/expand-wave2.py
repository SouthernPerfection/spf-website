#!/usr/bin/env python3
"""Wave 2 SEO robustness: expand the remaining product pages with unique, keyword-mapped
content. Same structure as wave 1. Run once from website/ root. Idempotent."""
import pathlib, re, json

DATA = {
"steel-cable-reels": dict(
 kicker="Steel cable reels", h2="What are steel cable reels?",
 paras=[
  'Steel cable reels are heavy-duty flanged steel spools used to wind, store, transport, and pay out cable, wire, hose, and tubing without kinking, tangling, or damage. Also called <strong>steel reels</strong> or spools, they replace disposable wood and cardboard reels with a durable, reusable reel that runs for years.',
  'SPF builds custom <strong>steel cable reels</strong> to your cable diameter, flange size, and weight — with the drum, flanges, and arbor bore engineered to your payout equipment. Fabricated and finished in-house, they survive repeated winding and rewind cycles in a returnable loop.',
  'We build reels and spools for <a href="/industries/energy-power/">energy</a>, <a href="/industries/industrial-machinery/">industrial machinery</a>, and general manufacturing — alongside <a href="/coil-racks/">coil racks</a> for wound and rolled product.'],
 sec_h2="Steel reels we build",
 cards=[("Any Diameter","Drums and flanges sized to your cable, wire, or hose."),("Reusable","Durable steel that survives repeated payout and rewind."),("Heavy Loads","Engineered for the weight of your wound product."),("Custom Arbor","Bore and mounting matched to your payout equipment.")],
 faqs=[("Can you build reels to our cable dimensions?",'Yes. We build steel reels and spools to your cable, wire, or hose diameter, flange size, and weight, built to print.','Yes. We build steel reels and spools to your cable, wire, or hose diameter, flange size, and weight, built to print.'),
       ("Are steel cable reels reusable and returnable?",'Yes. Unlike wood or cardboard reels, our welded steel reels are engineered to run for years in a returnable loop.','Yes. Unlike wood or cardboard reels, our welded steel reels are engineered to run for years in a returnable loop.'),
       ("Why choose a steel reel over a wood reel?",'Steel reels last far longer, protect the wound product better, and lower cost per trip in a returnable loop — where wood reels splinter and are used once.','Steel reels last far longer, protect the wound product better, and lower cost per trip in a returnable loop, where wood reels splinter and are used once.')]),

"industrial-dollies": dict(
 kicker="Industrial dollies", h2="What are industrial dollies?",
 paras=[
  'Industrial dollies are low, wheeled steel platforms built to move heavy parts, assemblies, and containers across the plant floor with minimal effort. Heavy-duty <strong>steel dollies</strong> carry loads that hand trucks and light carts cannot, safely and ergonomically.',
  'SPF builds custom <strong>heavy duty dollies</strong> to your load, part shape, and casters — with cradles, nests, or decks that hold the part securely. Welded steel construction and durable finishes stand up to years of plant duty.',
  'We build dollies for <a href="/industries/automotive/">automotive</a>, <a href="/industries/heavy-equipment/">heavy equipment</a>, and general manufacturing — and pair them with our <a href="/industrial-carts/">industrial carts</a> and <a href="/wip-carts/">WIP carts</a>.'],
 sec_h2="Industrial dollies we build",
 cards=[("Heavy-Duty","Engineered for heavy parts and assemblies."),("Part-Specific","Cradles and nests that hold your part securely."),("Maneuverable","Caster and swivel layouts for tight moves."),("Built to Print","Sized to your part, load, and floor.")],
 faqs=[("What loads can your dollies handle?",'We engineer each dolly to your specific load — from moderate to heavy parts and assemblies — with the frame, casters, and welds rated to the weight.','We engineer each dolly to your specific load, from moderate to heavy parts and assemblies, with the frame, casters, and welds rated to the weight.'),
       ("Can you match our part shape?",'Yes. Cradles, nests, and decks are shaped to hold your part securely so it does not shift while moving.','Yes. Cradles, nests, and decks are shaped to hold your part securely so it does not shift while moving.'),
       ("What is the difference between a dolly and a cart?",'A dolly is a low platform on casters for moving heavy loads at floor level; a cart adds shelves and a handle for line-side delivery. We build both to your process.','A dolly is a low platform on casters for moving heavy loads at floor level; a cart adds shelves and a handle for line-side delivery. We build both.')]),

"kanban-flow-racks": dict(
 kicker="Kanban flow racks", h2="What are kanban flow racks?",
 paras=[
  'Kanban flow racks — also called <strong>gravity flow racks</strong> or <strong>carton flow racks</strong> — are shelving systems with sloped roller or wheel lanes that feed parts and totes forward by gravity, presenting them FIFO at the point of use. They are the backbone of lean, kanban, and line-side replenishment.',
  'SPF builds custom flow racks to your totes, parts, and pitch — lane width, slope, and stops all engineered so product flows smoothly and the operator reaches it ergonomically. Built to print and finished in-house.',
  'Our flow racks support lean lines in <a href="/industries/automotive/">automotive</a> and general manufacturing, and pair with our <a href="/wip-carts/">WIP carts</a> and <a href="/industrial-carts/">industrial carts</a> for full line-side flow.'],
 sec_h2="Flow racks we build",
 cards=[("Gravity Flow","FIFO roller and wheel lanes for first-in, first-out."),("Kanban / Pull","Built for lean replenishment and pull signals."),("Sized to Your Totes","Lanes matched to your totes, bins, and parts."),("Ergonomic","Presentation heights and angles for the operator.")],
 faqs=[("What is a gravity flow rack?",'A gravity flow rack uses sloped roller or wheel lanes so loaded totes roll forward to the pick face and empties return on a lower lane — no power required.','A gravity flow rack uses sloped roller or wheel lanes so loaded totes roll forward to the pick face and empties return on a lower lane, no power required.'),
       ("Do you size flow lanes to our totes?",'Yes. We build lanes to your exact tote, bin, or part size so product flows smoothly without jamming.','Yes. We build lanes to your exact tote, bin, or part size so product flows smoothly without jamming.'),
       ("Can you build for kanban pull systems?",'Yes. Our flow racks are engineered for kanban and lean line-side replenishment, built to print for your pitch and takt.','Yes. Our flow racks are engineered for kanban and lean line-side replenishment, built to print for your pitch and takt.')]),

"industrial-carts": dict(
 kicker="Industrial carts", h2="What are industrial carts?",
 paras=[
  'Industrial carts are custom wheeled steel carts that move parts, work-in-process, and kits through a plant safely and efficiently. As purpose-built <strong>material handling carts</strong>, they present parts at the point of use, reduce manual handling, and keep the line flowing.',
  'SPF builds custom industrial carts to your parts, load, and aisles — shelves, cradles, casters, and handles all specified to your process and ergonomics, built to print and finished in-house.',
  'We build carts for <a href="/industries/automotive/">automotive</a>, <a href="/industries/distribution-logistics/">distribution and logistics</a>, and general manufacturing — alongside <a href="/industrial-dollies/">dollies</a>, <a href="/wip-carts/">WIP carts</a>, and <a href="/kanban-flow-racks/">flow racks</a>.'],
 sec_h2="Industrial carts we build",
 cards=[("Line-Side Delivery","Carts sized to present parts at the point of use."),("WIP &amp; Kitting","Move work-in-process and kits through the plant."),("Ergonomic","Built for safe, efficient manual movement."),("Built to Print","Engineered to your parts, load, and aisles.")],
 faqs=[("Can you build carts to our part and aisle sizes?",'Yes. We design industrial carts to your parts, load, and aisle constraints, with shelves and casters specified to your process.','Yes. We design industrial carts to your parts, load, and aisle constraints, with shelves and casters specified to your process.'),
       ("What is the difference between a cart and a dolly?",'A cart has shelves and a handle for presenting and moving parts line-side; a <a href="/industrial-dollies/">dolly</a> is a low platform for heavy loads at floor level. We build both.','A cart has shelves and a handle for presenting and moving parts line-side; a dolly is a low platform for heavy loads at floor level. We build both.'),
       ("Do you build tilt or specialty carts?",'Yes. We build tilt carts, sequencing carts, and part-specific specialty carts engineered to your ergonomics and process.','Yes. We build tilt carts, sequencing carts, and part-specific specialty carts engineered to your ergonomics and process.')]),

"steel-pallets": dict(
 kicker="Steel pallets", h2="What are steel pallets?",
 paras=[
  'Steel pallets are durable, reusable <strong>metal pallets</strong> that replace wood and plastic for heavy, high-cycle, or hygiene-sensitive loads. Built to run as <strong>returnable pallets</strong> in a closed loop, they carry heavier weight, resist damage, and last for years.',
  'SPF builds custom steel pallets to your load, footprint, and handling method — deck type, fork pockets, and load rating all engineered to your product and your forklift or AS/RS.',
  'We build steel pallets for <a href="/industries/automotive/">automotive</a>, <a href="/industries/distribution-logistics/">distribution and logistics</a>, <a href="/industries/food-beverage-dairy/">food and beverage</a>, and general manufacturing — with <a href="/returnable-containers/">metal containers</a> and <a href="/stack-racks/">stack racks</a> to match.'],
 sec_h2="Steel pallets we build",
 cards=[("Heavy-Duty","Rated for loads that crush wood and plastic pallets."),("Reusable / Returnable","Built to run for years in a closed returnable loop."),("Custom Footprint","Sized to your load, racking, and handling."),("Any Deck","Mesh, solid, or slatted decks matched to your part.")],
 faqs=[("Why choose steel pallets over wood or plastic?",'Steel pallets carry heavier loads, survive far more trips, and resist the damage that scraps wood and plastic — lowering cost per trip in a returnable loop.','Steel pallets carry heavier loads, survive far more trips, and resist the damage that scraps wood and plastic, lowering cost per trip in a returnable loop.'),
       ("Are steel pallets returnable and reusable?",'Yes. We build durable returnable steel pallets engineered to cycle for years and be repaired if damaged.','Yes. We build durable returnable steel pallets engineered to cycle for years and be repaired if damaged.'),
       ("Can you build to our footprint and load rating?",'Yes. Deck, fork pockets, and load rating are all engineered to your exact product, racking, and handling method.','Yes. Deck, fork pockets, and load rating are all engineered to your exact product, racking, and handling method.')]),

"rack-repair-refurbishment": dict(
 kicker="Rack repair &amp; refurbishment", h2="What is rack repair and refurbishment?",
 paras=[
  'Rack repair and refurbishment restores worn, bent, or damaged returnable racks back to original spec — re-welding, re-membering, and re-finishing them so they run safely for years more, at a fraction of new-build cost. <strong>Pallet rack repair</strong> and returnable-fleet refurbishment extend fleet life instead of replacing it.',
  'SPF inspects, repairs, and re-finishes returnable racks — even racks we did not build — usually in 1 to 2 weeks per batch. Because we <a href="/returnable-steel-racks/">build racks like these</a>, we already know their failure points, which makes the repair faster and truer to spec.',
  'See how we brought an aging fleet <a href="/case-studies/rack-repair-fleet/">back to spec for about 40% of new-build cost</a>, and read <a href="/blog/repair-or-replace-returnable-racks/">when to repair vs replace</a> a returnable rack fleet.'],
 sec_h2="What refurbishment includes",
 cards=[("Inspect &amp; Assess","Evaluate every rack for damage, wear, and safety."),("Re-Weld &amp; Repair","Fix cracked welds, bent uprights, and worn contact points."),("Replace Members","Swap out members beyond saving with new steel."),("Re-Finish","Powder-coat back to original spec for a fresh service life.")],
 faqs=[("How much does rack repair cost versus new?",'Refurbishment typically runs a fraction of new-build cost — one fleet came back to spec for about 40% of new — while extending fleet life by years.','Refurbishment typically runs a fraction of new-build cost, one fleet came back to spec for about 40% of new, while extending fleet life by years.'),
       ("Can you repair racks you did not build?",'Yes. We inspect, re-weld, re-member, and re-finish returnable racks regardless of who built them, back to original spec.','Yes. We inspect, re-weld, re-member, and re-finish returnable racks regardless of who built them, back to original spec.'),
       ("How long does refurbishment take?",'Typically 1 to 2 weeks per batch, so racks are back in service in days rather than the weeks a new build takes.','Typically 1 to 2 weeks per batch, so racks are back in service in days rather than the weeks a new build takes.')]),

"weldments-frames": dict(
 kicker="Weldments &amp; frames", h2="What are custom weldments?",
 paras=[
  'A weldment is a structure or assembly built by welding multiple steel parts into one — frames, bases, brackets, and structural assemblies. <strong>Custom weldments</strong> and <strong>steel weldments</strong> are the backbone of racks, machinery, and equipment.',
  'SPF handles <strong>weldment fabrication</strong> end to end — cut, form, machine, robotic-weld, and finish under one roof. 30+ MIG/TIG stations plus <a href="/capabilities/robotic-welding/">FANUC robotic welding</a> deliver consistent, repeatable weldments at production volume.',
  'We build weldments and frames for <a href="/industries/transportation-trailer/">transportation and trailer</a>, <a href="/industries/industrial-machinery/">industrial machinery and OEM</a>, <a href="/industries/energy-power/">energy</a>, and general manufacturing programs.'],
 sec_h2="Weldments we build",
 cards=[("Frames &amp; Bases","Structural frames and equipment bases, built to print."),("Structural Assemblies","Multi-part welded assemblies at any complexity."),("Robotic-Welded","FANUC cells for repeatable welds at production volume."),("One Roof","Cut, form, machine, weld, and finish in one building.")],
 faqs=[("Do you build weldments at production volume?",'Yes. With 30+ MIG/TIG stations and FANUC robotic welding, we build weldments and frames at production volume, built to print.','Yes. With 30-plus MIG/TIG stations and FANUC robotic welding, we build weldments and frames at production volume, built to print.'),
       ("Can you handle large or heavy weldments?",'Yes. Press-brake forming to 230 tons and heavy welding let us build large, heavy structural weldments and frames.','Yes. Press-brake forming to 230 tons and heavy welding let us build large, heavy structural weldments and frames.'),
       ("Do you finish weldments in-house?",'Yes. In-house powder coat and wet paint mean your weldments ship finished, not waiting on an outside coater.','Yes. In-house powder coat and wet paint mean your weldments ship finished, not waiting on an outside coater.')]),

"returnable-containers": dict(
 kicker="Industrial metal containers", h2="What are industrial metal containers?",
 paras=[
  'Industrial metal containers — including <strong>wire mesh containers</strong>, <strong>collapsible steel containers</strong>, and <strong>custom steel containers</strong> — are reusable steel bins and boxes that store and ship parts through a returnable loop. Stronger and longer-lasting than corrugated or plastic, they protect parts and stack safely.',
  'SPF builds custom returnable containers to your part, load, and stacking — rigid or collapsible, mesh or solid — engineered to fold flat for return freight and set up fast at the line.',
  'We build metal containers for <a href="/industries/automotive/">automotive</a>, <a href="/industries/distribution-logistics/">distribution and logistics</a>, and general manufacturing — with <a href="/steel-pallets/">steel pallets</a> and <a href="/returnable-steel-racks/">returnable racks</a> to match.'],
 sec_h2="Metal containers we build",
 cards=[("Wire Mesh","Ventilated wire mesh containers for parts and consumables."),("Collapsible","Knock-down steel containers that fold flat for return freight."),("Solid Steel","Enclosed steel containers for protection and security."),("Custom &amp; Stackable","Sized to your part and engineered to stack safely.")],
 faqs=[("What is the difference between metal containers and cardboard boxes?",'Metal containers are reusable and far stronger — they protect parts better, stack safely, and run for years in a returnable loop, where cardboard is used once and offers little protection.','Metal containers are reusable and far stronger. They protect parts better, stack safely, and run for years in a returnable loop, where cardboard is used once and offers little protection.'),
       ("How do collapsible containers reduce return freight?",'Collapsible steel containers fold or knock down flat when empty — often several to one — so you ship far fewer trailers of empties back home.','Collapsible steel containers fold or knock down flat when empty, often several to one, so you ship far fewer trailers of empties back home.'),
       ("Can you build containers to fit our racks and pallets?",'Yes. We design containers to nest with your <a href="/steel-pallets/">steel pallets</a> and <a href="/returnable-steel-racks/">racks</a> so the whole returnable system works together.','Yes. We design containers to nest with your steel pallets and racks so the whole returnable system works together.')]),
}

hero_re = re.compile(r'(<section class="hero".*?</section>)', re.S)
faq_sec_re = re.compile(r'(<section class="section[^"]*">\s*<div class="wrap">\s*<p class="kicker">FAQ)')
faqdiv_re = re.compile(r'(<div class="faq">.*?)(</div>)', re.S)
schema_re = re.compile(r'("@type"\s*:\s*"FAQPage"\s*,\s*"mainEntity"\s*:\s*\[.*?)(\]\})', re.S)

for slug, d in DATA.items():
    f = pathlib.Path(slug) / "index.html"
    html = f.read_text()
    if 'data-wave1' in html or 'data-wave2' in html:
        print("skip (already expanded):", slug); continue
    paras = "".join(f"<p>{p}</p>\n      " for p in d["paras"])
    def_sec = (f'\n\n    <section class="section" data-wave2><div class="wrap article-body">\n'
               f'      <p class="kicker">{d["kicker"]}</p>\n      <h2>{d["h2"]}</h2>\n      {paras.rstrip()}\n    </div></section>')
    cards = "".join(f'<article class="card"><h3>{h}</h3><p>{b}</p></article>' for h,b in d["cards"])
    mat_sec = (f'\n\n    <section class="section section-paper"><div class="wrap">\n'
               f'      <p class="kicker">Built to print</p>\n      <h2>{d["sec_h2"]}</h2>\n'
               f'      <div class="cards-4">{cards}</div>\n    </div></section>\n')
    html = hero_re.sub(lambda m: m.group(1) + def_sec, html, count=1)
    m = faq_sec_re.search(html)
    if m: html = html[:m.start()] + mat_sec + "\n    " + html[m.start():]
    else: print("  ! no FAQ anchor:", slug)
    extra = "".join(f'\n          <details><summary>{q}</summary><p>{a}</p></details>' for q,a,_ in d["faqs"])
    html = faqdiv_re.sub(lambda m: m.group(1) + extra + "\n        " + m.group(2), html, count=1)
    qadd = "".join(', ' + json.dumps({"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":ap}}, ensure_ascii=False) for q,_,ap in d["faqs"])
    html = schema_re.sub(lambda m: m.group(1) + qadd + m.group(2), html, count=1)
    f.write_text(html)
    wc = len(re.sub(r'<[^>]+>','', re.search(r'<main.*?</main>', html, re.S).group(0)).split())
    print(f"expanded {slug} → ~{wc} words")
print("Done.")

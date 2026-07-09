#!/usr/bin/env python3
"""Wave 2b: expand the capability pages — add a definition section + a NEW FAQ section
(with FAQPage schema, since these pages have none). Run once from website/ root. Idempotent."""
import pathlib, re, json

DATA = {
"capabilities": dict(
 kicker="Contract metal fabrication", h2="What is contract metal fabrication?",
 paras=[
  'Contract metal fabrication is the outsourced design and manufacture of metal parts and assemblies — cutting, forming, machining, welding, and finishing — built to a customer’s print. A single-source fabricator does all of it under one roof instead of routing the job between separate shops.',
  'Southern Perfection Fabrication is a full-service contract metal fabricator: SolidWorks <a href="/capabilities/design-engineering/">design</a>, <a href="/capabilities/laser-cutting/">laser and plasma cutting</a>, <a href="/capabilities/forming/">CNC forming</a> to 230 tons, <a href="/capabilities/cnc-machining/">CNC machining</a>, <a href="/capabilities/robotic-welding/">30+ welding stations plus FANUC robotic</a>, and in-house <a href="/capabilities/powder-coating/">finishing</a> — all ISO 9001 and CAGE 2W654.',
  'One roof, one purchase order, one accountable team — see how that <a href="/case-studies/single-source-switch/">cut a manufacturer’s lead time roughly in half</a>.'],
 faq_h2="Contract metal fabrication — answered.",
 faqs=[("What does a contract metal fabricator do?","A contract metal fabricator builds metal parts and assemblies to your print — cutting, forming, machining, welding, and finishing — so you do not need the equipment or the separate suppliers in-house."),
       ("Do you offer single-source fabrication?","Yes. We cut, form, machine, weld, and finish under one roof on a single purchase order, with one team accountable end to end."),
       ("What are your quality certifications?","We hold an ISO 9001 quality system and CAGE 2W654 registration, with CMM inspection for the documentation and traceability OEM and defense programs require.")]),

"capabilities/cnc-machining": dict(
 kicker="CNC machining", h2="What is CNC machining?",
 paras=[
  'CNC (computer numerical control) machining is a subtractive process in which programmed machine tools — lathes and mills — remove material from a workpiece to produce precise, repeatable parts and features. It turns your CAD model or print into a finished metal component to tight tolerances.',
  'Southern Perfection Fabrication provides <strong>CNC machining</strong> — turning and milling — integrated with cutting, forming, welding, and finishing under one roof, so machined parts and weldments come together in the same building on one purchase order.',
  'We machine components in carbon steel, stainless, aluminum, and magnesium for <a href="/industries/automotive/">automotive</a>, <a href="/industries/aerospace-defense/">aerospace and defense</a>, and industrial customers as part of complete build-to-print fabrication.'],
 faq_h2="CNC machining — answered.",
 faqs=[("What is the difference between CNC turning and milling?","In turning, the part rotates against a fixed cutting tool (ideal for round parts); in milling, a rotating tool cuts a fixed part (ideal for flat and complex features). We do both."),
       ("What materials can you machine?","Carbon steel, stainless steel, aluminum, and magnesium — matched to your part and application."),
       ("Do you machine prototypes and production runs?","Yes, from one-off prototypes through repeatable production volumes, all built to your print.")]),

"capabilities/powder-coating": dict(
 kicker="Finishing", h2="What is powder coating?",
 paras=[
  'Powder coating is a dry finishing process in which electrostatically-charged powder is applied to a metal part and cured under heat into a tough, uniform, durable finish — harder and longer-lasting than liquid paint, which is why it survives the returnable loop.',
  'SPF runs one of the largest <strong>powder coating</strong> ovens in the Southeast, plus wet paint, in-house — so every part ships finished, not waiting in an outside coater’s queue.',
  'We finish racks, weldments, and fabricated parts for automotive, aerospace and defense, and industrial customers in the color and spec your program requires.'],
 faq_h2="Finishing — answered.",
 faqs=[("What is the difference between powder coat and paint?","Powder coating cures into a thicker, tougher, more durable finish than liquid paint and resists chipping and corrosion better — ideal for parts that cycle through a returnable loop."),
       ("How large a part can you powder coat?","One of the largest powder-coat ovens in the Southeast lets us finish large racks and weldments most shops have to send out."),
       ("Do you offer wet paint as well?","Yes. We run both powder coat and wet paint in-house and specify whichever your part and environment call for.")]),

"capabilities/robotic-welding": dict(
 kicker="Welding", h2="What is robotic welding?",
 paras=[
  'Robotic welding uses programmed robotic arms to make consistent, repeatable welds at high speed and volume — delivering the same quality joint on the first part and the ten-thousandth. It is how you hold weld consistency across a large production run.',
  'SPF welds across 30+ MIG and TIG stations plus FANUC <strong>robotic welding</strong> cells, so we scale from prototype to production while keeping welds spec-consistent — the backbone of every rack and <a href="/weldments-frames/">weldment</a> we build.',
  'Our welding serves <a href="/industries/automotive/">automotive</a>, <a href="/industries/transportation-trailer/">transportation and trailer</a>, and heavy industrial programs at production volume.'],
 faq_h2="Welding — answered.",
 faqs=[("What is the benefit of robotic welding?","Consistency and volume — a programmed cell repeats the exact same weld thousands of times, so quality does not drift across a production run."),
       ("Do you offer MIG and TIG welding?","Yes, across 30+ manual MIG and TIG stations plus FANUC robotic cells for high-volume work."),
       ("Can you weld at production volume?","Yes. Robotic cells and deep manual capacity let us scale from prototypes to full production programs, built to print.")]),

"capabilities/laser-cutting": dict(
 kicker="Cut", h2="What is laser and plasma cutting?",
 paras=[
  'Laser and plasma cutting are CNC processes that cut metal to precise, repeatable shapes directly from a digital file — laser for clean, tight-tolerance parts, plasma for heavier plate and structural cuts.',
  'SPF runs CNC <strong>laser and plasma cutting</strong> in-house, feeding straight into forming and welding without leaving the building, so parts stay consistent from cut to finished assembly.',
  'We cut carbon steel, stainless, aluminum, and magnesium for build-to-print racks, weldments, and components across every industry we serve.'],
 faq_h2="Laser & plasma cutting — answered.",
 faqs=[("What is the difference between laser and plasma cutting?","Laser cutting gives cleaner edges and tighter tolerances on thinner material; plasma cuts heavier plate and structural steel faster. We use both to match the part."),
       ("What materials can you cut?","Carbon steel, stainless steel, aluminum, and magnesium."),
       ("Does cutting feed into your other processes?","Yes. Cut parts move directly into forming, machining, welding, and finishing under one roof, which keeps quality and lead time tight.")]),

"capabilities/forming": dict(
 kicker="Form", h2="What is metal forming?",
 paras=[
  'Metal forming shapes flat or tubular metal into finished geometry through bending, rolling, and press-brake forming — without removing material. It is how a flat blank becomes a bracket, a channel, or a rack member.',
  'SPF forms with CNC <strong>press brakes to 230 tons</strong>, CNC tube bending, and plate rolling — accurate, repeatable forming that shapes the steel for your racks, frames, and assemblies.',
  'Formed parts feed straight into welding and finishing in the same building, built to your print.'],
 faq_h2="Forming & bending — answered.",
 faqs=[("What is press brake forming?","Press brake forming bends sheet and plate to precise angles using a punch and die — our CNC press brakes go to 230 tons for heavy, repeatable bends."),
       ("How thick or large can you form?","With press-brake capacity to 230 tons plus tube bending and plate rolling, we handle heavy-gauge and large formed parts most shops send out."),
       ("Do you offer tube bending and plate rolling?","Yes — CNC tube and pipe bending and plate rolling for cradles, saddles, and cylindrical shapes, all to your spec.")]),

"capabilities/quality-inspection": dict(
 kicker="Quality", h2="What is CMM inspection?",
 paras=[
  'A coordinate measuring machine (CMM) verifies that a finished part matches its print by precisely measuring its geometry in three dimensions. <strong>CMM inspection</strong> is the backbone of a documented, repeatable quality system.',
  'SPF runs an ISO 9001 quality system with CAGE 2W654 registration and CMM inspection — the documentation and traceability that OEM and defense programs require.',
  'That quality pedigree is why <a href="/industries/aerospace-defense/">aerospace and defense</a> and automotive-quality customers trust us with build-to-print work.'],
 faq_h2="Quality & inspection — answered.",
 faqs=[("What is CMM inspection used for?","A CMM measures a finished part in three dimensions to confirm it matches the print, producing the inspection data and traceability regulated programs require."),
       ("Are you ISO 9001 certified?","Yes. We operate a certified ISO 9001 quality management system."),
       ("Do you have a CAGE code for defense work?","Yes — CAGE 2W654, registered to support defense and government-funded programs.")]),

"capabilities/design-engineering": dict(
 kicker="Design", h2="What is design for manufacturing?",
 paras=[
  'Design for manufacturing (DFM) engineers a part so it can be built efficiently, reliably, and to cost. In-house <strong>SolidWorks design</strong> turns your math data, print, or even a rough idea into a buildable, production-ready part.',
  'SPF’s engineering team designs racks, weldments, and fabricated parts for weldability, durability, and cost from the first concept — so it cuts, forms, welds, and finishes clean instead of being redesigned two months in.',
  'Because design and the floor share one roof, we iterate fast — see how in-house engineering <a href="/case-studies/custom-rack-design/">built a rack for a part nothing else fit</a>.'],
 faq_h2="Design & engineering — answered.",
 faqs=[("Do you offer design and engineering services?","Yes. Our in-house SolidWorks team designs racks, weldments, and fabricated parts and prepares them for production."),
       ("Can you design from a rough concept?","Yes. Send math data, a print, or a rough idea and we will engineer it into a buildable, production-ready design."),
       ("What CAD software do you use?","We design in SolidWorks and can work from your CAD, prints, or physical samples.")]),
}

hero_re = re.compile(r'(<section class="hero".*?</section>)', re.S)
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
    # new FAQ section before cta-band
    faq_items = "".join(f'\n          <details><summary>{q}</summary><p>{a}</p></details>' for q,a in d["faqs"])
    faq_sec = (f'<section class="section section-paper"><div class="wrap">\n'
               f'      <p class="kicker">FAQ</p>\n      <h2>{d["faq_h2"]}</h2>\n'
               f'      <div class="faq">{faq_items}\n        </div>\n    </div></section>\n\n    ')
    html = cta_re.sub(lambda m: faq_sec + m.group(1), html, count=1)
    # FAQPage schema before </head>
    schema = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in d["faqs"]]}
    block = '  <script type="application/ld+json">\n  ' + json.dumps(schema, ensure_ascii=False) + '\n  </script>\n</head>'
    html = html.replace('</head>', block, 1)
    f.write_text(html)
    wc = len(re.sub(r'<[^>]+>','', re.search(r'<main.*?</main>', html, re.S).group(0)).split())
    print(f"expanded {slug} → ~{wc} words")
print("Done.")

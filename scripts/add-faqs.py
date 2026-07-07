#!/usr/bin/env python3
"""Add an FAQ section (+ FAQPage schema) to pages that don't have one.
Run from website/ root:  python3 scripts/add-faqs.py
Idempotent: skips any page that already contains class="faq".
"""
import re, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

FAQS = {
  "returnable-steel-racks/index.html": ("Returnable steel racks — answered.", [
    ("What is the difference between returnable and one-way racks?", "Returnable racks are built to make many trips in a closed loop — heavier-duty and reusable — versus one-way packaging that is used once. We build durable returnable steel racks engineered for years of trips."),
    ("Do you offer collapsible or stackable racks?", "Yes. Collapsible racks fold flat to cut return freight, and stackable racks nest to save floor and trailer space. We spec whichever fits your loop."),
    ("Do you build to our print?", "Yes, build-to-print is our standard. Send a drawing, CAD, or a photo with dimensions and we will return a rack concept and a number."),
    ("What is your typical lead time?", "It depends on the design and volume. Send your part and we will give you lead time along with the quote."),
  ]),
  "rack-repair-refurbishment/index.html": ("Rack repair — answered.", [
    ("What can be repaired versus replaced?", "We straighten, re-weld, and rebuild damaged racks back to spec. Units too far gone are replaced and matched to your existing fleet."),
    ("What is the turnaround on repairs?", "We are positioned in the Southeast and Midwest corridor for fast turnaround near your plant. Send photos of the damage and we will scope it."),
    ("Will repaired racks match our existing fleet?", "Yes. We repair and build replacements to your original print so the fleet stays consistent."),
    ("Do you offer scheduled fleet service?", "Yes. Our managed programs add scheduled inspection, pickup, and depot repair across the fleet."),
  ]),
  "dunnage/index.html": ("Dunnage — answered.", [
    ("What dunnage types do you offer?", "Custom foam inserts and protective foam packaging, plus fabric and returnable dunnage, engineered to your part."),
    ("Reusable versus expendable dunnage?", "We build durable, reusable and returnable dunnage designed to ride the loop, not one-way packaging."),
    ("Do you design dunnage to our part?", "Yes. We cut and shape dunnage to your part geometry so surfaces arrive clean, trip after trip."),
    ("Can you bundle dunnage with racks?", "Yes. We design the rack and the dunnage together as one system, under one roof."),
  ]),
  "capabilities/index.html": ("Capabilities — answered.", [
    ("What is your maximum part size and weight?", "We handle large, heavy fabrications. Send your part and we will confirm fit for your specific project."),
    ("What materials and thicknesses do you work with?", "Steel and specialty materials to spec, across a wide thickness range. Share your requirements and we will confirm."),
    ("What welding processes do you use?", "Robotic and manual welding for consistent, build-to-print quality at volume."),
    ("Do you hold certifications beyond ISO 9001?", "ISO 9001 and CAGE 2W654 today. Contact us to confirm any additional program certifications you require."),
  ]),
  "managed-programs/index.html": ("Managed programs — answered.", [
    ("Who owns the racks, us or you?", "In the base managed model you own the assets and we manage them. A rental model where we hold the assets is an optional step."),
    ("What do you track?", "Location, condition, counts, and utilization across your sites, with quarterly health and utilization reporting."),
    ("How does pricing work?", "A recurring fee covering management, inspection, repair, replacement, and dunnage over the program life, scoped to your fleet."),
    ("Can we start small?", "Yes. Start with one program, prove it, then scale across your plants."),
  ]),
  "industries/aerospace-defense/index.html": ("Aerospace and defense — answered.", [
    ("Do you build to program specs and MIL-SPEC?", "We build ruggedized crates and containers to your program's requirements. Send the spec and we will confirm."),
    ("Do you have a CAGE code?", "Yes — CAGE 2W654, set up to support defense and government-funded work."),
    ("Do you make ruggedized containers?", "Yes. Custom crating, military shipping crates, and ruggedized containers for high-value assets."),
    ("Are your crates reusable?", "We build both one-way crates and reusable, returnable containers depending on your program."),
  ]),
}

cta_re = re.compile(r'<section class="cta-band"')
head_re = re.compile(r'</head>')

def faq_section(heading, items):
    rows = "\n          ".join(
        f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items)
    return (
'    <section class="section section-paper">\n'
'      <div class="wrap">\n'
'        <p class="kicker">FAQ</p>\n'
f'        <h2>{heading}</h2>\n'
'        <div class="faq">\n'
f'          {rows}\n'
'        </div>\n'
'      </div>\n'
'    </section>\n\n')

def faq_schema(items):
    data = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in items]}
    return '  <script type="application/ld+json">\n  ' + json.dumps(data, ensure_ascii=False) + '\n  </script>\n'

changed = []
for rel,(heading,items) in FAQS.items():
    f = ROOT / rel
    html = f.read_text()
    if 'class="faq"' in html:
        continue
    html = html.replace('<section class="cta-band"', faq_section(heading, items) + '<section class="cta-band"', 1)
    html = html.replace('</head>', faq_schema(items) + '</head>', 1)
    f.write_text(html)
    changed.append(rel)

print(f"Added FAQ to {len(changed)} pages:")
for c in changed: print(" -", c)

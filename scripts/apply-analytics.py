#!/usr/bin/env python3
"""Inject analytics into every page — edited in ONE place, DRY across all 65 pages.

  * Google Analytics 4 (gtag)        -> traffic, sources, conversions
  * Microsoft Clarity                -> heatmaps + session recordings
  * Cloudflare Web Analytics beacon  -> privacy-first pageview baseline
  * RFQ conversion event             -> fires GA4 `generate_lead` when the
                                        homepage RFQ success panel appears
                                        (decoupled via MutationObserver — no
                                        need to touch the inline form JS).

Idempotent: re-run any time. It replaces the guarded blocks, so updating an ID
or adding a tool is just editing CONFIG below and re-running. Only the tools
whose ID is filled in get injected — empty IDs are skipped cleanly.

Run from website/ root:  python3 scripts/apply-analytics.py
"""
import re, pathlib

# ---- CONFIG: paste your IDs here, then re-run ------------------------------
GA4_ID     = "G-7NE6WQG77Y"   # Google Analytics 4 Measurement ID, e.g. "G-XXXXXXXXXX"
CLARITY_ID = ""   # Microsoft Clarity project ID,       e.g. "abcd1234ef"
CF_BEACON  = ""   # Cloudflare Web Analytics token,     e.g. "a1b2c3d4e5f6..."
# ---------------------------------------------------------------------------

ROOT = pathlib.Path(__file__).resolve().parent.parent
H_START, H_END = "<!-- ANALYTICS -->", "<!-- /ANALYTICS -->"
B_START, B_END = "<!-- CF-ANALYTICS -->", "<!-- /CF-ANALYTICS -->"


def head_block():
    """Everything that belongs in <head>, guarded by markers. '' if nothing set."""
    parts = []
    if GA4_ID:
        parts.append(
            f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>\n'
            f'  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}'
            f"gtag('js',new Date());gtag('config','{GA4_ID}');</script>"
        )
        # RFQ conversion: fire generate_lead when #rfqSuccess becomes visible.
        parts.append(
            "<script>document.addEventListener('DOMContentLoaded',function(){"
            "var s=document.getElementById('rfqSuccess');if(!s)return;"
            "new MutationObserver(function(){if(!s.hidden&&window.gtag){"
            "gtag('event','generate_lead',{event_category:'RFQ',event_label:location.pathname});"
            "}}).observe(s,{attributes:true,attributeFilter:['hidden']});});</script>"
        )
    if CLARITY_ID:
        parts.append(
            '<script type="text/javascript">(function(c,l,a,r,i,t,y){'
            "c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};"
            "t=l.createElement(r);t.async=1;t.src='https://www.clarity.ms/tag/'+i;"
            "y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);"
            f'}})(window,document,"clarity","script","{CLARITY_ID}");</script>'
        )
    if not parts:
        return ""
    return f"  {H_START}\n  " + "\n  ".join(parts) + f"\n  {H_END}\n"


def body_block():
    """Cloudflare beacon, injected before </body>. '' if not set."""
    if not CF_BEACON:
        return ""
    return (
        f"  {B_START}<script defer src=\"https://static.cloudflareinsights.com/beacon.min.js\" "
        f"data-cf-beacon='{{\"token\": \"{CF_BEACON}\"}}'></script>{B_END}\n"
    )


def upsert(html, block, start, end, before_tag):
    """Replace an existing marker block, or insert `block` right before `before_tag`."""
    existing = re.compile(re.escape(start) + r".*?" + re.escape(end) + r"\n?", re.S)
    html = existing.sub("", html)          # strip any prior injection (idempotent)
    if block:
        html = html.replace(before_tag, block + before_tag, 1)
    return html


def main():
    hb, bb = head_block(), body_block()
    changed = 0
    for path in ROOT.rglob("*.html"):
        if "node_modules" in path.parts:
            continue
        html = path.read_text(encoding="utf-8")
        new = upsert(html, hb, H_START, H_END, "</head>")
        new = upsert(new, bb, B_START, B_END, "</body>")
        if new != html:
            path.write_text(new, encoding="utf-8")
            changed += 1
    tools = [n for n, v in (("GA4", GA4_ID), ("Clarity", CLARITY_ID), ("Cloudflare", CF_BEACON)) if v]
    print(f"Analytics injected on {changed} pages. Active: {', '.join(tools) or 'none (all IDs blank)'}")


if __name__ == "__main__":
    main()

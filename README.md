# SPF Website

Marketing site for **Southern Perfection Fabrication** (Byron, GA). One job: **surface a real rack/fabrication need and open an RFQ.** Everything is engineered around that conversion event.

- **Live (staging):** https://spf-website.william-doxey.workers.dev
- **Repo:** github.com/SouthernPerfection/spf-website (this `website/` folder only)
- **Stack:** static HTML + one shared stylesheet (`/assets/styles.css`) + a small Cloudflare Worker (`worker.js`) for the RFQ endpoint. Portable to Astro later.
- **~48 pages built:** homepage, product pages (racks, containers, pallets, carts, dollies, kanban flow racks, cable reels, weldments, guards, dunnage, foam, repair), 7 capability sub-pages, 13 industry pages, managed programs, about, contact, case studies.

---

## 1. Hosting & deploy

Hosted on **Cloudflare Workers (Static Assets)**. Deploys are **automatic on git push**: Cloudflare's Workers Build runs `npx wrangler deploy`, which uploads the static files **and** the Worker.

```
git add -A && git commit -m "..." && git push origin main
# → Cloudflare rebuilds in ~30–70s. New pages can lag a few seconds across CDN edges.
```

`wrangler.jsonc` is the deploy config:
```jsonc
{
  "name": "spf-website",
  "compatibility_date": "2025-01-01",
  "main": "worker.js",              // the Worker (handles /api/rfq, serves assets)
  "assets": { "directory": "./", "binding": "ASSETS" }
}
```
`.assetsignore` keeps non-public files (`worker.js`, `scripts/`, `*.py`, `*.md`, config) out of what's served. Static pages are served directly; only unmatched routes (e.g. `/api/rfq`) hit the Worker.

> Note: `wrangler` is **not** authed locally — all deploys run on Cloudflare's side via the GitHub connection. So runtime secrets are managed in the **Cloudflare dashboard**, not via `wrangler secret` here.

---

## 2. The RFQ pipeline → HubSpot  ⭐ (the conversion event)

The homepage RFQ form (`#rfq` in `index.html`) is a **custom-designed form** that posts JSON to our own endpoint **`/api/rfq`**, handled by `worker.js`, which creates/updates a **HubSpot contact** via the CRM API.

```
Browser form  ──POST /api/rfq──►  worker.js  ──HubSpot CRM API──►  Contact created
   (index.html <script>)          (uses env.HUBSPOT_TOKEN)          (HubSpot portal 246202279, na2)
```

**Field mapping** (done in the form's inline script + `worker.js`):
- `Name` → auto-split into `firstname` + `lastname`
- `Company` → `company`, `Work email` → `email`, `Phone` → `phone`
- `Role` + `Tell us about the part` → combined into `message`
- **File upload:** the CRM API can't accept a file, so on success the form asks the prospect to email the drawing to sales@ (the email fallback also carries all fields).

**Graceful fallback:** if `/api/rfq` returns non-OK or the network fails, the form falls back to opening an email to **sales@southernperfection.com** — so it always works, even before the token is set.

### The `HUBSPOT_TOKEN` secret — where it lives & how to set it
`worker.js` reads `env.HUBSPOT_TOKEN`. It is **not in the repo** — it's an encrypted Cloudflare secret. To (re)set it:

1. **HubSpot** → Settings ⚙ → Integrations → **Private Apps** → Create a private app ("Website RFQ").
2. **Scopes:** `crm.objects.contacts.write` (+ `crm.objects.contacts.read`). Create → copy the **Access token** (`pat-na2-…`).
3. **Cloudflare** → Workers & Pages → **spf-website** → Settings → **Variables and Secrets** → Add → Type **Secret**, Name **`HUBSPOT_TOKEN`**, Value = the token → Save. Picked up at runtime immediately.

**To rotate:** delete the old token in HubSpot (Private App → deactivate/rotate), create a new one, update the `HUBSPOT_TOKEN` secret in Cloudflare. No code change needed.

**Health check:** `curl -X POST https://<host>/api/rfq -H 'Content-Type: application/json' -d '{"email":"x@example.com"}'`
- `503 {"error":"not_configured"}` → secret not set yet
- `200 {"ok":true,"action":"created"}` → working

> Aside: a HubSpot *form* (GUID `e5c7cd7b-…`) was created early on, but HubSpot's new-generation forms don't support the legacy submit API (they 404), so we use the Private-App/CRM-API route above instead. That form GUID is unused.

---

## 3. Maintenance scripts (`scripts/` — DRY templating)

Pages share one header/mega-menu and are generated from data tables. **Edit the script, then re-run it — never hand-edit 48 files.**

| Script | What it does |
|---|---|
| `apply-header.py` | Injects the canonical `<header>` (logo + mega menu) into **every** `*.html`. Edit the nav here, run once, it updates all pages. |
| `generate-capabilities.py` | Regenerates the 7 `/capabilities/*` pages from a data list (real brochure specs). |
| `generate-industries.py` | Generates the market industry pages under `/industries/*`. |
| `generate-buildpages.py` | Generates the "What We Build" product pages (automotive-racks, stack-racks, carts, dollies, kanban, cable-reels). |
| `generate-products.py` | Generates weldments-frames + guards-platforms. |
| `add-faqs.py` | Adds FAQ sections + `FAQPage` JSON-LD to selected pages. |

Typical flow: `python3 scripts/generate-*.py && python3 scripts/apply-header.py` then commit + push.

---

## 4. SEO (implemented)

- Semantic HTML5, single `<h1>`, landmarks, skip-link, zero-JS checkbox nav
- Per-page unique `<title>` / meta description / canonical, Open Graph + Twitter
- **schema.org JSON-LD:** Organization/Manufacturer/LocalBusiness + WebSite + Service + BreadcrumbList + FAQPage
- Real business facts site-wide: 232 Hwy 49 S, Byron GA 31008 · 478-956-4442 · toll-free (800) 237-4726 · sales@southernperfection.com · ISO 9001 · CAGE 2W654 · est. 1982

**Keyword clusters (one page per cluster):** returnable steel racks · automotive/stack racks · steel pallets · industrial metal containers · industrial carts/dollies · kanban flow racks · steel cable reels · weldments & frames · guards & platforms · rack repair & refurbishment · dunnage/foam · + industry modifiers (automotive, EV/battery, aerospace-defense, heavy equipment, etc.).

**Still to finish:** self-host fonts; real WebP/AVIF images with `width`/`height`; `og-cover.jpg`.

---

## 5. Pre-launch checklist

- ☐ Set `HUBSPOT_TOKEN` in Cloudflare (see §2) → RFQs create contacts directly
- ☐ **Real photos** — hero still shows `[INSERT HERO RACK PHOTO]`; add rack/shop shots + `og-cover.jpg`
- ☐ Cleared customer logos (if any)
- ☐ **Domain migration** to `southernperfection.com`: 301 redirect map + Semrush rankings baseline, then DNS cutover; submit sitemap to Google Search Console
- ☐ **Rotate the GitHub PAT** that was exposed in chat during setup

> Keep the M&A / PE / acquisition strategy **off** the public site — confidential. Managed Programs *is* public (real customer offering).

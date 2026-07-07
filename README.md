# SPF Website — Build, Hosting & SEO Guide

A revenue-first website for Southern Perfection Fabrication. **One job: surface a real rack need and open an RFQ** — mirroring the sales playbook. Everything here is engineered around that conversion event.

This folder is a **production-grade static homepage** you can open today (`index.html`) and a plan to grow it into the full site on the recommended stack.

---

## 1. Recommended stack (best SEO from hosting to everything)

| Layer | Recommendation | Why |
|---|---|---|
| **Framework** | **Astro** (static output) | Ships **zero JS by default** → top Core Web Vitals (LCP/CLS/INP), now a ranking factor. Purpose-built for content/marketing sites; per-page `<meta>` + JSON-LD is trivial. |
| **Hosting/CDN** | **Cloudflare Pages** (or Vercel) | Free-tier global CDN, automatic HTTPS, instant cache, great TTFB. Git-push to deploy. |
| **Forms / CRM** | **Embedded HubSpot form** for the RFQ | RFQ lands in HubSpot as your **system of record** (matches the playbook: HubSpot hunts, ERP quotes). Add the HubSpot tracking script for attribution. |
| **DNS** | Cloudflare DNS | Free, fast, DNSSEC, easy `southernperfection.com` + `www` → apex redirect. |
| **Analytics** | GA4 + Google Search Console + HubSpot | GSC is non-negotiable for SEO (indexing, queries, Core Web Vitals report). |

**Why not the alternatives:** WordPress → plugin bloat, security, perf tax. HubSpot CMS as host → heavier/slower Core Web Vitals and pricier, though defensible if you want marketers editing pages with no dev. For pure SEO/speed, **Astro + CDN wins**.

### Porting this homepage to Astro
The current `index.html` maps 1:1 to `src/pages/index.astro`. Move `<head>` into an `<SEO>` component, keep `styles.css` in `src/styles/`, and add:
```
npm create astro@latest
npx astro add sitemap        # auto-generates sitemap.xml at build
```

---

## 2. Deploy in ~15 minutes (static, as-is)
1. Push this `website/` folder to a GitHub repo.
2. Cloudflare Pages → **Create project** → connect repo → Framework preset: **None** (or Astro once ported) → Deploy.
3. Add custom domain `southernperfection.com`; Cloudflare auto-provisions HTTPS.
4. Add the site to **Google Search Console**, submit `sitemap.xml`.
5. Embed the HubSpot form (see §4) and paste the HubSpot tracking script before `</body>`.

---

## 3. SEO checklist (already implemented ✓ / to finish ☐)
- ✓ Semantic HTML5, single `<h1>`, logical heading order, landmarks, skip-link (a11y = SEO)
- ✓ `<title>` + meta description tuned to real search intent
- ✓ Canonical, robots meta, Open Graph + Twitter cards
- ✓ **schema.org JSON-LD**: Organization/Manufacturer/LocalBusiness + WebSite + Service (rich results, local SEO)
- ✓ `robots.txt` + `sitemap.xml`
- ✓ Mobile-first responsive, zero-JS nav (`<details>`), `prefers-reduced-motion`
- ✓ `font-display: swap`, preconnect/preload
- ☐ **Self-host fonts** (Bebas Neue + IBM Plex Sans/Mono) in `/assets/fonts/` — better CWV + privacy than the Google Fonts CDN currently linked
- ☐ **Real images** as WebP/AVIF, explicit `width`/`height` (prevents CLS), `loading="lazy"` below the fold, descriptive `alt`
- ☐ Add `og-cover.jpg` (1200×630), `favicon.svg`, `logo.png`
- ☐ Per-page unique title/description/canonical on every industry & service page
- ☐ `FAQPage` JSON-LD on Capabilities + industry pages (RFQ questions = great rich-result fodder)

### Target keywords (build a page per cluster)
- returnable steel racks / custom steel shipping racks
- material handling racks manufacturer / returnable packaging fabricator
- rack repair & refurbishment / returnable fleet repair
- returnable dunnage / WIP carts / stack racks
- \+ industry modifiers: "automotive returnable racks", "EV battery returnable packaging", "defense crating CAGE", "heavy equipment shipping racks"
- \+ geo modifiers: "Georgia / Southeast returnable racks"

---

## 4. The RFQ form (your conversion event)
Swap the native `<form>` in `index.html` for the **embedded HubSpot form** so submissions become HubSpot contacts/deals automatically. Keep the same fields (they mirror the RFQ checklist):
part photo/print upload · size & weight · parts per rack · annual volume · ship lanes · returnable? · current pain · timing · contact.
**North-star metric = RFQs started/submitted**, wired to the HubSpot dashboard alongside the sales scoreboard.

---

## 5. Full site architecture (build order)
```
/                         Homepage ...................... ✓ built (this file)
/what-we-build/           Racks · dunnage · WIP · repair
/industries/              Hub + 6 landing pages (SEO core)
  automotive-oem/ · automotive-tier-1/ · heavy-equipment/
  aerospace-defense/ · ev-battery/ · general-industrial/
/rack-repair-refurbishment/   Service page (recurring-revenue hook)
/managed-programs/        Customer-facing managed program (from existing one-pager)
/capabilities/            Specs + ISO 9001/CAGE — procurement vetting + FAQPage
/about/                   Since 1982, one roof, leadership
/contact/                 Map, hours, RFQ
/case-studies/            Engine Racks · Rack Design · Fleet Program ·
                          Rack Repair · Single-Source Switch · Tooling & GSE
```
> Keep the **M&A roll-up / PE / acquisition strategy OFF the public site** — that's confidential. Managed Programs *is* public (real customer offering).

---

## 6. Assets still needed (the §8 intake — highest-leverage before launch)
Placeholders in the code marked `[ ... ]` need real content:
- **Photos**: 6–10 rack shots (hero, industries, repair), shop-floor, logo, `og-cover.jpg`
- **Specs**: max part size/weight · materials · thickness range · welding processes · finishing options · facility size/capacity
- **Contact**: street address · sales email · RFQ portal link · LinkedIn URL
- **Confirm**: certs beyond ISO 9001/CAGE (AS9100? IATF 16949? ITAR?) · quote turnaround to advertise · customer logos cleared to show
- **Repair/refurb**: confirm scope to state publicly

A page with real rack photos + a named customer converts far better than a polished one full of placeholders. **Gathering these is the #1 pre-launch task.**

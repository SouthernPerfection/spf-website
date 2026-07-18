/**
 * SPF website Worker.
 *
 *  POST /api/rfq  ->  on an RFQ submission:
 *    1. create/update a HubSpot contact   (secret: HUBSPOT_TOKEN)
 *    2. email the full details to sales@   (secret: RESEND_API_KEY)
 *    3. email a confirmation to the prospect
 *  Each step is best-effort. We report success if the lead reached the team
 *  (HubSpot OR the internal email). If nothing lands, the site form falls
 *  back to emailing sales@ directly.
 *
 *  Everything else -> served from static assets (env.ASSETS).
 *
 *  Secrets live in the Cloudflare dashboard (Workers & Pages -> spf-website ->
 *  Settings -> Variables and Secrets), never in the repo.
 */
// 301 map: legacy Weebly .html URLs -> new clean paths (preserves SEO equity on cutover).
const REDIRECTS = {
  "/index.html": "/",
  "/services.html": "/capabilities/",
  "/capabilities.html": "/capabilities/",
  "/line-card.html": "/capabilities/",
  "/heat-treatments.html": "/capabilities/",
  "/product-overview.html": "/returnable-steel-racks/",
  "/racks.html": "/returnable-steel-racks/",
  "/category.html": "/returnable-steel-racks/",
  "/automotive-racks.html": "/automotive-racks/",
  "/automotive-racks1.html": "/automotive-racks/",
  "/wip-racks.html": "/wip-carts/",
  "/wip-racks1.html": "/wip-carts/",
  "/rack-repair.html": "/rack-repair-refurbishment/",
  "/bins--baskets.html": "/returnable-containers/",
  "/bins--baskets1.html": "/returnable-containers/",
  "/plant-safety.html": "/guards-platforms/",
  "/glass-handling-equipment.html": "/industries/general-industrial/",
  "/bakery.html": "/industries/food-beverage-dairy/",
  "/defense.html": "/industries/aerospace-defense/",
  "/about-the-company.html": "/about/",
  "/warranty.html": "/about/",
  "/careers.html": "/about/",
  "/contact.html": "/contact/",
  "/whats-new.html": "/blog/",
  "/newsletter.html": "/blog/",
  "/hand-sanitizer-stations.html": "/",
  "/surplus-equipment-sale.html": "/",
  "/store/p1/plant_safety.html": "/guards-platforms/",
  "/store/c1/featured_products.html": "/returnable-steel-racks/",
  "/store/c2/automotive.html": "/industries/automotive/",
  "/store/c3/aerospace.html": "/industries/aerospace-defense/",
  "/store/c4/defense": "/industries/aerospace-defense/",
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    // Legacy-URL 301s (active once the domain cuts over to Cloudflare).
    const dest = REDIRECTS[path.toLowerCase()];
    if (dest) return Response.redirect(url.origin + dest, 301);
    // Clean-URL: /x/index.html -> /x/  (and /index.html -> /)
    if (path.endsWith("/index.html")) {
      return Response.redirect(url.origin + path.slice(0, -10), 301);
    }
    // Legacy Weebly catch-all: any other .html or /store/ path -> home (keep /404.html reachable).
    if ((path.endsWith(".html") && path !== "/404.html") || path.startsWith("/store/")) {
      return Response.redirect(url.origin + "/", 301);
    }
    // Normalize www -> apex (canonical is the bare domain).
    if (url.hostname === "www.southernperfection.com") {
      return Response.redirect("https://southernperfection.com" + path + url.search, 301);
    }

    if (path === "/api/rfq") {
      if (request.method !== "POST") return json({ ok: false, error: "method_not_allowed" }, 405);
      return handleRfq(request, env, url.searchParams.get("debug") === "1");
    }
    if (path === "/api/rb2b") {
      if (request.method !== "POST") return json({ ok: false, error: "method_not_allowed" }, 405);
      return handleRb2b(request, env, url.searchParams.get("token"));
    }
    return env.ASSETS.fetch(request);
  },
};

const HS_BASE = "https://api.hubapi.com";
const SALES_EMAIL = "sales@southernperfection.com";
const NOTIFY_EMAIL = "mmurdock@southernperfection.com"; // internal "New RFQ" alerts route here
const FROM = "Southern Perfection Fabrication <sales@southernperfection.com>";
// Internal alerts use a distinct sender so alerting sales@ isn't a sales@->sales@
// self-send (which Resend previously auto-suppressed). Same verified domain, no
// mailbox needed — replies route to reply_to (the prospect), not here.
const ALERT_FROM = "SPF Website <notifications@southernperfection.com>";

async function handleRfq(request, env, debug) {
  let data;
  try {
    data = await request.json();
  } catch {
    return json({ ok: false, error: "bad_json" }, 400);
  }

  const email = String(data.email || "").trim();
  if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    return json({ ok: false, error: "email_required" }, 400);
  }

  const p = {
    email,
    firstname: str(data.firstname),
    lastname: str(data.lastname),
    company: str(data.company),
    phone: str(data.phone),
    message: str(data.message),
  };

  // Lead-source attribution (page the RFQ CTA was clicked from + session landing page).
  const meta = { source_page: str(data.source_page), landing_page: str(data.landing_page) };
  // Lead-magnet (gated spec-guide) submissions are lower-intent than RFQs — treat them distinctly.
  const isLM = str(data.type) === "lead_magnet";
  // Newsletter signups (footer / blog / exit-intent no-guide) — subscribe + welcome, no sales alert.
  const isNews = str(data.type) === "newsletter";
  if (isNews) {
    p.message = "Subscribed to The Returnable Report" + (meta.source_page ? " (via " + meta.source_page + ")" : "");
  } else if (data.newsletter_optin === true || str(data.newsletter_optin) === "true") {
    p.message = (p.message ? p.message + " · " : "") + "Opted into The Returnable Report newsletter";
  }

  const results = { hubspot: false, notify: false, confirm: false };
  let notifyRes = { ok: false, skipped: true };
  let confirmRes = { ok: false, skipped: true };

  // 1. HubSpot contact
  if (env.HUBSPOT_TOKEN) {
    results.hubspot = await upsertHubspot(p, env, meta).catch(() => false);
  }

  // 2 + 3. Emails via Resend
  if (env.RESEND_API_KEY) {
    // Newsletter signups skip the sales alert (keeps the inbox for real leads).
    if (!isNews) {
      // Guide downloads alert both sales@ and mmurdock@; RFQs stay on mmurdock@.
      const alertTo = isLM ? [SALES_EMAIL, NOTIFY_EMAIL] : [NOTIFY_EMAIL];
      notifyRes = await sendEmail(env, {
        to: alertTo,
        from: alertTo.includes(SALES_EMAIL) ? ALERT_FROM : FROM,
        replyTo: email,
        subject: `${isLM ? "New guide download" : "New RFQ"} — ${p.company || fullName(p) || email}`,
        html: internalHtml(p, meta, isLM),
      }).catch((e) => ({ ok: false, detail: String(e) }));
      results.notify = notifyRes.ok;
    }

    confirmRes = await sendEmail(env, {
      to: email,
      replyTo: SALES_EMAIL,
      subject: isNews
        ? "Welcome to The Returnable Report"
        : isLM
        ? "Your returnable-rack spec guide — Southern Perfection Fabrication"
        : "We received your RFQ — Southern Perfection Fabrication",
      html: isNews ? newsletterWelcomeHtml(p) : isLM ? leadMagnetHtml(p) : clientHtml(p),
    }).catch((e) => ({ ok: false, detail: String(e) }));
    results.confirm = confirmRes.ok;
  }

  const ok = results.hubspot || results.notify || (isNews && results.confirm);
  const resp = { ok, results };
  if (!ok) resp.error = "not_delivered";
  if (debug) {
    resp.debug = {
      hasHubspotToken: !!env.HUBSPOT_TOKEN,
      hasResendKey: !!env.RESEND_API_KEY,
      from: FROM,
      notify: notifyRes,
      confirm: confirmRes,
    };
  }
  return json(resp, ok ? 200 : 502);
}

// ---- HubSpot -------------------------------------------------------------
async function upsertHubspot(p, env, meta) {
  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${env.HUBSPOT_TOKEN}`,
  };
  const properties = {};
  Object.keys(p).forEach((k) => {
    if (k === "email" || p[k]) properties[k] = p[k];
  });
  // Fold lead-source into the message note (avoids needing a custom HubSpot property).
  if (meta && (meta.source_page || meta.landing_page)) {
    const note =
      "Submitted from " +
      (meta.source_page || "(unknown)") +
      (meta.landing_page && meta.landing_page !== meta.source_page
        ? " · entered site at " + meta.landing_page
        : "");
    properties.message = (properties.message ? properties.message + "\n\n" : "") + "— " + note;
  }
  const body = JSON.stringify({ properties });

  const create = await fetch(`${HS_BASE}/crm/v3/objects/contacts`, { method: "POST", headers, body });
  if (create.ok) return true;
  if (create.status === 409) {
    const update = await fetch(
      `${HS_BASE}/crm/v3/objects/contacts/${encodeURIComponent(p.email)}?idProperty=email`,
      { method: "PATCH", headers, body }
    );
    return update.ok;
  }
  return false;
}

// ---- Resend --------------------------------------------------------------
async function sendEmail(env, { to, replyTo, subject, html, from }) {
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
    },
    body: JSON.stringify({ from: from || FROM, to: Array.isArray(to) ? to : [to], reply_to: replyTo, subject, html }),
  });
  return { ok: res.ok, status: res.status, detail: res.ok ? "" : (await safeText(res)) };
}

async function safeText(res) {
  try {
    return (await res.text()).slice(0, 400);
  } catch {
    return "";
  }
}

// ---- RB2B website-visitor webhook ---------------------------------------
// RB2B POSTs an identified visitor here; we (1) email a branded alert to the team
// and (2) upsert a HubSpot contact tagged lead_source = "RB2B".
const RB2B_TO = ["tristan.wynn@southernperfection.com", "william.doxey@southernperfection.com"];

async function handleRb2b(request, env, token) {
  // Optional shared secret: if RB2B_WEBHOOK_TOKEN is set, require ?token= to match.
  if (env.RB2B_WEBHOOK_TOKEN && token !== env.RB2B_WEBHOOK_TOKEN) {
    return json({ ok: false, error: "unauthorized" }, 401);
  }
  let data;
  try {
    data = await request.json();
  } catch {
    try {
      data = Object.fromEntries(new URLSearchParams(await request.text()));
    } catch {
      data = null;
    }
  }
  if (!data || typeof data !== "object") return json({ ok: false, error: "bad_payload" }, 400);

  const v = normalizeRb2b(data);
  const who = v.name || v.company || v.email || "Website visitor";
  const subject = `Website visitor — ${who}${v.company && v.company !== who ? " · " + v.company : ""}`;

  const results = { email: false, hubspot: false };
  if (env.RESEND_API_KEY) {
    const r = await sendEmail(env, { to: RB2B_TO, replyTo: v.email || SALES_EMAIL, subject, html: rb2bHtml(v, data) }).catch(() => ({ ok: false }));
    results.email = r.ok;
  }
  if (env.HUBSPOT_TOKEN) {
    results.hubspot = await upsertRb2bContact(v, env).catch(() => false);
  }

  const ok = results.email || results.hubspot;
  const resp = { ok, results };
  if (!ok) resp.error = "not_delivered";
  return json(resp, ok ? 200 : 502);
}

function firstOf(d, keys) {
  for (const k of keys) {
    if (d[k] != null && String(d[k]).trim() !== "") return String(d[k]).trim();
  }
  return "";
}

// Map RB2B's fixed Title-Case payload (with snake_case fallbacks) to a normalized shape.
function normalizeRb2b(d) {
  const first = firstOf(d, ["First Name", "first_name", "firstName"]);
  const last = firstOf(d, ["Last Name", "last_name", "lastName"]);
  return {
    first,
    last,
    name: [first, last].filter(Boolean).join(" ") || firstOf(d, ["name", "full_name"]),
    title: firstOf(d, ["Title", "title", "job_title"]),
    company: firstOf(d, ["Company Name", "company_name", "company"]),
    email: firstOf(d, ["Business Email", "email", "work_email"]),
    website: firstOf(d, ["Website", "website", "domain"]),
    linkedin: firstOf(d, ["LinkedIn URL", "linkedin_url", "linkedin"]),
    industry: firstOf(d, ["Industry", "industry"]),
    size: firstOf(d, ["Employee Count", "company_size", "employee_count"]),
    revenue: firstOf(d, ["Estimate Revenue", "revenue"]),
    city: firstOf(d, ["City", "city"]),
    state: firstOf(d, ["State", "state", "region"]),
    zip: firstOf(d, ["Zipcode", "zip", "postal_code"]),
    page: firstOf(d, ["Captured URL", "page", "page_url", "url"]),
    referrer: firstOf(d, ["Referrer", "referrer"]),
    tags: firstOf(d, ["Tags", "tags"]),
    seenAt: firstOf(d, ["Seen At", "seen_at", "timestamp"]),
    repeat: d["is_repeat_visit"] === true || d["is_repeat_visitor"] === true,
  };
}

// Upsert a HubSpot contact from an RB2B visitor, tagged lead_source = "RB2B".
async function upsertRb2bContact(v, env) {
  const marker =
    "Identified by RB2B (website visitor)." +
    (v.page ? " Visited: " + v.page : "") +
    (v.tags ? " · Tags: " + v.tags : "") +
    (v.linkedin ? " · " + v.linkedin : "") +
    (v.seenAt ? " · Seen " + v.seenAt : "");
  const props = { lead_source: "RB2B", message: marker };
  if (v.email) props.email = v.email;
  if (v.first) props.firstname = v.first;
  if (v.last) props.lastname = v.last;
  if (v.company) props.company = v.company;
  if (v.title) props.jobtitle = v.title;
  if (v.website) props.website = v.website;
  if (v.city) props.city = v.city;
  if (v.state) props.state = v.state;
  if (v.zip) props.zip = v.zip;

  const headers = { "Content-Type": "application/json", Authorization: `Bearer ${env.HUBSPOT_TOKEN}` };
  async function attempt(p) {
    const body = JSON.stringify({ properties: p });
    const create = await fetch(`${HS_BASE}/crm/v3/objects/contacts`, { method: "POST", headers, body });
    if (create.ok) return { ok: true };
    if (create.status === 409 && p.email) {
      const upd = await fetch(`${HS_BASE}/crm/v3/objects/contacts/${encodeURIComponent(p.email)}?idProperty=email`, { method: "PATCH", headers, body });
      return { ok: upd.ok, status: upd.status };
    }
    return { ok: false, status: create.status };
  }
  let r = await attempt(props);
  // If the custom lead_source property doesn't exist in the portal, retry without it.
  if (!r.ok && r.status === 400 && "lead_source" in props) {
    const { lead_source, ...rest } = props;
    r = await attempt(rest);
  }
  return r.ok;
}

function rb2bHtml(v, raw) {
  const name = v.name || "Unknown visitor";
  const rowsData = [
    ["Title", v.title],
    ["Company", v.company],
    ["Website", v.website],
    ["Email", v.email],
    ["Industry", v.industry],
    ["Employees", v.size],
    ["Est. revenue", v.revenue],
    ["Location", [v.city, v.state, v.zip].filter(Boolean).join(", ")],
    ["Page visited", v.page],
    ["Referrer", v.referrer],
    ["Tags", v.tags],
    ["Seen at", v.seenAt],
    ["Repeat visit", v.repeat ? "Yes" : ""],
  ].filter((r) => r[1]);

  const rows = rowsData
    .map((r, i) => {
      const border = i < rowsData.length - 1 ? "border-bottom:1px solid #EDEAE3;" : "";
      const valColor = r[0] === "Email" ? "#1F3864" : "#16181C";
      return `<tr><td style="padding:9px 0;color:#6F7782;width:120px;vertical-align:top;${border}font-family:${FONT};font-size:14px;">${esc(
        r[0]
      )}</td><td style="padding:9px 0;color:${valColor};${border}font-family:${FONT};font-size:14px;line-height:1.5;word-break:break-word;">${esc(
        r[1]
      )}</td></tr>`;
    })
    .join("");

  const dump = Object.keys(raw)
    .map((k) => {
      let val = raw[k];
      if (val && typeof val === "object") val = JSON.stringify(val);
      val = String(val == null ? "" : val);
      if (!val) return "";
      return `<tr><td style="padding:5px 0;color:#9AA0A6;width:150px;vertical-align:top;font-family:${FONT};font-size:12px;">${esc(
        k
      )}</td><td style="padding:5px 0;color:#5F5E5A;font-family:${FONT};font-size:12px;line-height:1.4;word-break:break-word;">${esc(
        val.slice(0, 300)
      )}</td></tr>`;
    })
    .join("");

  const btns =
    (v.linkedin
      ? `<a href="${esc(v.linkedin)}" style="display:inline-block;margin:0 8px 8px 0;background:#0A66C2;color:#ffffff;text-decoration:none;font-size:14px;font-weight:bold;padding:11px 20px;border-radius:6px;font-family:${FONT};">View LinkedIn &rarr;</a>`
      : "") +
    (v.email
      ? `<a href="mailto:${esc(v.email)}" style="display:inline-block;margin:0 8px 8px 0;background:#DD4E14;color:#ffffff;text-decoration:none;font-size:14px;font-weight:bold;padding:11px 20px;border-radius:6px;font-family:${FONT};">Email them &rarr;</a>`
      : "");

  const header = `<tr><td style="background:#16181C;padding:20px 28px;">
          <div style="color:#DD4E14;font-size:20px;font-weight:bold;letter-spacing:1px;font-family:${FONT};">WEBSITE VISITOR</div>
          <div style="color:#ffffff;font-size:18px;font-weight:bold;margin-top:6px;font-family:${FONT};">${esc(name)}</div>
          <div style="color:#9AA0A6;font-size:12px;margin-top:4px;font-family:${FONT};">Identified by RB2B · saved to HubSpot as an RB2B lead</div>
        </td></tr>`;

  const body = `<tr><td style="padding:24px 28px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100%;">${rows}</table>
          <div style="margin-top:20px;">${btns}</div>
          ${dump ? `<div style="margin-top:22px;border-top:1px solid #EDEAE3;padding-top:14px;"><div style="color:#9AA0A6;font-size:11px;font-weight:bold;letter-spacing:1px;font-family:${FONT};margin-bottom:8px;">ALL DATA RECEIVED</div><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100%;">${dump}</table></div>` : ""}
        </td></tr>`;

  return emailShell(header, body, BRAND_FOOTER);
}

// Shared email chrome: 560px white card on a paper backdrop, table-based so it
// renders identically in Outlook / Gmail / Apple Mail. Inline styles + web-safe
// fonts only (no remote CSS/fonts, which many clients strip).
const FONT = "Arial,Helvetica,sans-serif";

function emailShell(headerHtml, bodyHtml, footerHtml) {
  return `<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#F3F1EC;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F3F1EC;">
    <tr><td align="center" style="padding:24px 12px;">
      <table role="presentation" width="560" cellpadding="0" cellspacing="0" style="width:560px;max-width:560px;background:#ffffff;border:1px solid #E3DFD6;border-radius:12px;overflow:hidden;">
        ${headerHtml}
        ${bodyHtml}
        ${footerHtml}
      </table>
    </td></tr>
  </table>
</body></html>`;
}

const BRAND_HEADER = `<tr><td style="background:#16181C;padding:22px 28px;">
          <div style="color:#ffffff;font-size:17px;font-weight:bold;letter-spacing:1px;font-family:${FONT};">SOUTHERN PERFECTION FABRICATION</div>
          <div style="margin-top:9px;height:3px;width:46px;background:#DD4E14;font-size:0;line-height:3px;">&nbsp;</div>
          <div style="color:#9AA0A6;font-size:12px;margin-top:9px;font-family:${FONT};">Complete metal fabrication under one roof</div>
        </td></tr>`;

const BRAND_FOOTER = `<tr><td style="background:#F3F1EC;padding:18px 28px;border-top:1px solid #D8D4CA;">
          <div style="color:#6F7782;font-size:12px;line-height:1.8;font-family:${FONT};">232 Hwy 49 S &middot; Byron, GA 31008<br>478-956-4442 &middot; toll-free (800) 237-4726 &middot; sales@southernperfection.com<br>ISO 9001 &middot; CAGE 2W654 &middot; Est. 1982</div>
        </td></tr>`;

function internalHtml(p, meta, isLM) {
  meta = meta || {};
  const fields = [
    ["Name", fullName(p)],
    ["Company", p.company],
    ["Email", p.email],
    ["Phone", p.phone],
    ["Details", p.message],
    ["Source", meta.source_page],
    ["Entered at", meta.landing_page && meta.landing_page !== meta.source_page ? meta.landing_page : ""],
  ].filter((r) => r[1]);
  const rows = fields
    .map((r, i) => {
      const border = i < fields.length - 1 ? "border-bottom:1px solid #EDEAE3;" : "";
      const valColor = r[0] === "Email" ? "#1F3864" : "#16181C";
      const weight = r[0] === "Name" || r[0] === "Company" ? "font-weight:bold;" : "";
      return `<tr><td style="padding:9px 0;color:#6F7782;width:96px;vertical-align:top;${border}font-family:${FONT};font-size:14px;">${esc(
        r[0]
      )}</td><td style="padding:9px 0;color:${valColor};${weight}${border}font-family:${FONT};font-size:14px;line-height:1.5;">${nl2br(esc(r[1]))}</td></tr>`;
    })
    .join("");
  const replyBtn = p.email
    ? `<a href="mailto:${encodeURIComponent(p.email)}" style="display:inline-block;margin-top:20px;background:#DD4E14;color:#ffffff;text-decoration:none;font-size:14px;font-weight:bold;padding:12px 22px;border-radius:6px;font-family:${FONT};">Reply to ${esc(p.firstname || "the prospect")} &rarr;</a>`
    : "";
  const header = `<tr><td style="background:#16181C;padding:20px 28px;">
          <div style="color:#DD4E14;font-size:20px;font-weight:bold;letter-spacing:1px;font-family:${FONT};">${isLM ? "GUIDE DOWNLOAD" : "NEW RFQ"}</div>
          <div style="color:#9AA0A6;font-size:12px;margin-top:5px;font-family:${FONT};">${isLM ? "Spec-guide lead magnet &middot; nurture lead" : "Submitted via southernperfection.com"}</div>
        </td></tr>`;
  const body = `<tr><td style="padding:24px 28px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100%;">${rows}</table>
          ${replyBtn}
        </td></tr>`;
  const footer = `<tr><td style="background:#F3F1EC;padding:14px 28px;border-top:1px solid #D8D4CA;">
          <div style="color:#6F7782;font-size:12px;font-family:${FONT};">${isLM ? "Downloaded the spec guide &mdash; a nurture lead, not an RFQ. Reply to reach them directly." : "Reply to this email to respond directly to the prospect."}</div>
        </td></tr>`;
  return emailShell(header, body, footer);
}

function clientHtml(p) {
  const first = p.firstname || "there";
  const body = `<tr><td style="padding:28px 28px 8px;">
          <div style="color:#DD4E14;font-size:12px;font-weight:bold;letter-spacing:1.5px;font-family:${FONT};">RFQ RECEIVED</div>
          <div style="color:#16181C;font-size:22px;font-weight:bold;margin:6px 0 16px;font-family:${FONT};">Thanks &mdash; we've got your RFQ.</div>
          <p style="color:#16181C;font-size:14px;line-height:1.6;margin:0 0 12px;font-family:${FONT};">Hi ${esc(first)},</p>
          <p style="color:#3c3f45;font-size:14px;line-height:1.6;margin:0 0 18px;font-family:${FONT};">Thanks for reaching out to Southern Perfection Fabrication. Your request is in front of our team now &mdash; we'll follow up within one business day with next steps.</p>
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100%;margin:0 0 20px;"><tr><td style="background:#F3F1EC;border-left:3px solid #DD4E14;padding:14px 16px;">
            <div style="color:#16181C;font-size:14px;font-weight:bold;margin-bottom:3px;font-family:${FONT};">Have a drawing or print?</div>
            <div style="color:#5F5E5A;font-size:13px;line-height:1.5;font-family:${FONT};">Just reply to this email and attach it &mdash; we'll match it to your request.</div>
          </td></tr></table>
          <a href="mailto:sales@southernperfection.com?subject=Re:%20My%20RFQ" style="display:inline-block;background:#DD4E14;color:#ffffff;text-decoration:none;font-size:14px;font-weight:bold;padding:12px 22px;border-radius:6px;font-family:${FONT};">Reply with your details &rarr;</a>
          <p style="color:#3c3f45;font-size:14px;line-height:1.6;margin:22px 0 0;font-family:${FONT};">Talk soon,<br>The team at Southern Perfection Fabrication</p>
        </td></tr>`;
  return emailShell(BRAND_HEADER, body, BRAND_FOOTER);
}

// Delivery email for the gated "How to Spec a Returnable Rack" lead magnet.
function leadMagnetHtml(p) {
  const first = p.firstname || "there";
  const body = `<tr><td style="padding:28px 28px 8px;">
          <div style="color:#DD4E14;font-size:12px;font-weight:bold;letter-spacing:1.5px;font-family:${FONT};">YOUR SPEC GUIDE</div>
          <div style="color:#16181C;font-size:22px;font-weight:bold;margin:6px 0 16px;font-family:${FONT};">How to Spec a Returnable Rack</div>
          <p style="color:#16181C;font-size:14px;line-height:1.6;margin:0 0 12px;font-family:${FONT};">Hi ${esc(first)},</p>
          <p style="color:#3c3f45;font-size:14px;line-height:1.6;margin:0 0 18px;font-family:${FONT};">Thanks for grabbing the guide &mdash; here it is. It walks through everything we need to turn a part into a rack concept and a number: part &amp; load, freight lanes, the loop, environment, and volume.</p>
          <a href="https://southernperfection.com/assets/guides/how-to-spec-a-returnable-rack.pdf" style="display:inline-block;background:#DD4E14;color:#ffffff;text-decoration:none;font-size:14px;font-weight:bold;padding:12px 22px;border-radius:6px;font-family:${FONT};">Download the guide (PDF) &rarr;</a>
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100%;margin:22px 0 0;"><tr><td style="background:#F3F1EC;border-left:3px solid #DD4E14;padding:14px 16px;">
            <div style="color:#16181C;font-size:14px;font-weight:bold;margin-bottom:3px;font-family:${FONT};">Filled in the checklist?</div>
            <div style="color:#5F5E5A;font-size:13px;line-height:1.5;font-family:${FONT};">Reply with a part photo or print and we'll turn it into a rack concept and a real quote.</div>
          </td></tr></table>
          <p style="color:#3c3f45;font-size:14px;line-height:1.6;margin:22px 0 0;font-family:${FONT};">Talk soon,<br>The team at Southern Perfection Fabrication</p>
        </td></tr>`;
  return emailShell(BRAND_HEADER, body, BRAND_FOOTER);
}

// Confirmation email for a newsletter (The Returnable Report) signup.
function newsletterWelcomeHtml(p) {
  const first = p.firstname || "there";
  const body = `<tr><td style="padding:28px 28px 8px;">
          <div style="color:#DD4E14;font-size:12px;font-weight:bold;letter-spacing:1.5px;font-family:${FONT};">THE RETURNABLE REPORT</div>
          <div style="color:#16181C;font-size:22px;font-weight:bold;margin:6px 0 16px;font-family:${FONT};">You're subscribed.</div>
          <p style="color:#16181C;font-size:14px;line-height:1.6;margin:0 0 12px;font-family:${FONT};">Hi ${esc(first)},</p>
          <p style="color:#3c3f45;font-size:14px;line-height:1.6;margin:0 0 18px;font-family:${FONT};">Thanks for subscribing to The Returnable Report &mdash; a short monthly note for people who ship parts and pay for packaging. One customer story, one shop capability, and one practical tip you can use. No spam, and you can unsubscribe anytime.</p>
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100%;margin:0 0 20px;"><tr><td style="background:#F3F1EC;border-left:3px solid #DD4E14;padding:14px 16px;">
            <div style="color:#16181C;font-size:14px;font-weight:bold;margin-bottom:3px;font-family:${FONT};">While you're here</div>
            <div style="color:#5F5E5A;font-size:13px;line-height:1.5;font-family:${FONT};">The fastest way to know if a returnable rack pays off for your parts is to run your own numbers.</div>
          </td></tr></table>
          <a href="https://southernperfection.com/returnable-packaging-roi/" style="display:inline-block;background:#DD4E14;color:#ffffff;text-decoration:none;font-size:14px;font-weight:bold;padding:12px 22px;border-radius:6px;font-family:${FONT};">See your payback &rarr; ROI calculator</a>
          <p style="color:#3c3f45;font-size:14px;line-height:1.6;margin:22px 0 0;font-family:${FONT};">Talk soon,<br>The team at Southern Perfection Fabrication<br><span style="color:#6F7782;font-size:13px;">Byron, GA &middot; building racks since 1982</span></p>
        </td></tr>`;
  return emailShell(BRAND_HEADER, body, BRAND_FOOTER);
}

// ---- helpers -------------------------------------------------------------
function str(v) {
  return typeof v === "string" ? v.trim() : "";
}
function fullName(p) {
  return [p.firstname, p.lastname].filter(Boolean).join(" ").trim();
}
function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
function nl2br(s) {
  return s.replace(/\n/g, "<br>");
}
function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json" } });
}

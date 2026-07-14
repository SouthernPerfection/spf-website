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
    return env.ASSETS.fetch(request);
  },
};

const HS_BASE = "https://api.hubapi.com";
const SALES_EMAIL = "sales@southernperfection.com";
const NOTIFY_EMAIL = "mmurdock@southernperfection.com"; // internal "New RFQ" alerts route here
const FROM = "Southern Perfection Fabrication <sales@southernperfection.com>";

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

  const results = { hubspot: false, notify: false, confirm: false };
  let notifyRes = { ok: false, skipped: true };
  let confirmRes = { ok: false, skipped: true };

  // 1. HubSpot contact
  if (env.HUBSPOT_TOKEN) {
    results.hubspot = await upsertHubspot(p, env).catch(() => false);
  }

  // 2 + 3. Emails via Resend
  if (env.RESEND_API_KEY) {
    notifyRes = await sendEmail(env, {
      to: NOTIFY_EMAIL,
      replyTo: email,
      subject: `New RFQ — ${p.company || fullName(p) || email}`,
      html: internalHtml(p),
    }).catch((e) => ({ ok: false, detail: String(e) }));
    results.notify = notifyRes.ok;

    confirmRes = await sendEmail(env, {
      to: email,
      replyTo: SALES_EMAIL,
      subject: "We received your RFQ — Southern Perfection Fabrication",
      html: clientHtml(p),
    }).catch((e) => ({ ok: false, detail: String(e) }));
    results.confirm = confirmRes.ok;
  }

  const ok = results.hubspot || results.notify;
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
async function upsertHubspot(p, env) {
  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${env.HUBSPOT_TOKEN}`,
  };
  const properties = {};
  Object.keys(p).forEach((k) => {
    if (k === "email" || p[k]) properties[k] = p[k];
  });
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
async function sendEmail(env, { to, replyTo, subject, html }) {
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
    },
    body: JSON.stringify({ from: FROM, to: [to], reply_to: replyTo, subject, html }),
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

function internalHtml(p) {
  const fields = [
    ["Name", fullName(p)],
    ["Company", p.company],
    ["Email", p.email],
    ["Phone", p.phone],
    ["Details", p.message],
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
          <div style="color:#DD4E14;font-size:20px;font-weight:bold;letter-spacing:1px;font-family:${FONT};">NEW RFQ</div>
          <div style="color:#9AA0A6;font-size:12px;margin-top:5px;font-family:${FONT};">Submitted via southernperfection.com</div>
        </td></tr>`;
  const body = `<tr><td style="padding:24px 28px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100%;">${rows}</table>
          ${replyBtn}
        </td></tr>`;
  const footer = `<tr><td style="background:#F3F1EC;padding:14px 28px;border-top:1px solid #D8D4CA;">
          <div style="color:#6F7782;font-size:12px;font-family:${FONT};">Reply to this email to respond directly to the prospect.</div>
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

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
 *  GET|POST /api/rfq/health  ->  send ONE test email via Resend to confirm the
 *    integration works (RESEND_API_KEY set + southernperfection.com verified in
 *    Resend). Does NOT touch HubSpot and does NOT email a prospect. Recipient
 *    defaults to sales@ and is restricted to @southernperfection.com so the
 *    endpoint can't be used as an open relay. Override with ?to=name@southernperfection.com.
 *
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
    // Catch-all: any other old Weebly .html or /store/ path -> home, no 404s.
    if (path.endsWith(".html") || path.startsWith("/store/")) {
      return Response.redirect(url.origin + "/", 301);
    }
    // Normalize www -> apex (canonical is the bare domain).
    if (url.hostname === "www.southernperfection.com") {
      return Response.redirect("https://southernperfection.com" + path + url.search, 301);
    }

    if (path === "/api/rfq/health") {
      if (request.method !== "GET" && request.method !== "POST") {
        return json({ ok: false, error: "method_not_allowed" }, 405);
      }
      return handleHealth(env, url.searchParams);
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
      to: SALES_EMAIL,
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

// ---- Health check --------------------------------------------------------
// Sends a single test email through Resend and reports the raw result, so you
// can confirm the integration end-to-end without submitting a fake RFQ (no
// HubSpot contact, no prospect email). Recipient is locked to our own domain.
async function handleHealth(env, params) {
  if (!env.RESEND_API_KEY) {
    return json(
      { ok: false, error: "not_configured", detail: "RESEND_API_KEY is not set in Cloudflare — no email can be sent.", from: FROM },
      503
    );
  }

  const to = String(params.get("to") || SALES_EMAIL).trim().toLowerCase();
  if (!/^[^@\s]+@southernperfection\.com$/.test(to)) {
    return json(
      { ok: false, error: "bad_recipient", detail: "Health-check email may only be sent to a @southernperfection.com address." },
      400
    );
  }

  const resend = await sendEmail(env, {
    to,
    replyTo: SALES_EMAIL,
    subject: "Resend health check — Southern Perfection Fabrication",
    html: healthHtml(to),
  }).catch((e) => ({ ok: false, detail: String(e) }));

  const resp = { ok: resend.ok, from: FROM, to, resend };
  if (!resend.ok) {
    resp.error = "send_failed";
    // Common cause: the sending domain isn't verified in Resend yet.
    resp.hint = "A 403 with a domain/verification message means southernperfection.com is not yet verified in Resend.";
  }
  return json(resp, resend.ok ? 200 : 502);
}

function healthHtml(to) {
  return `<div style="font-family:Arial,Helvetica,sans-serif;max-width:600px;color:#16181C">
    <h2 style="color:#DD4E14;margin:0 0 12px">Resend is working ✅</h2>
    <p>This is an automated health-check email confirming that the Southern Perfection Fabrication site can send mail through Resend.</p>
    <p style="color:#6F7782;font-size:13px">Sent from <strong>${esc(FROM)}</strong> to <strong>${esc(to)}</strong>. Safe to ignore.</p>
  </div>`;
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

function internalHtml(p) {
  const rows = [
    ["Name", fullName(p)],
    ["Company", p.company],
    ["Email", p.email],
    ["Phone", p.phone],
    ["Details", p.message],
  ]
    .filter((r) => r[1])
    .map(
      (r) =>
        `<tr><td style="padding:8px 12px;font-weight:600;vertical-align:top;color:#16181C;border-bottom:1px solid #D8D4CA">${esc(
          r[0]
        )}</td><td style="padding:8px 12px;color:#16181C;border-bottom:1px solid #D8D4CA">${nl2br(esc(r[1]))}</td></tr>`
    )
    .join("");
  return `<div style="font-family:Arial,Helvetica,sans-serif;max-width:600px">
    <h2 style="color:#DD4E14;margin:0 0 2px">New RFQ</h2>
    <p style="color:#6F7782;margin:0 0 16px;font-size:13px">Submitted via southernperfection.com</p>
    <table style="border-collapse:collapse;width:100%;border:1px solid #D8D4CA">${rows}</table>
    <p style="color:#6F7782;font-size:13px;margin-top:16px">Reply to this email to respond directly to the prospect.</p>
  </div>`;
}

function clientHtml(p) {
  const first = p.firstname || "there";
  return `<div style="font-family:Arial,Helvetica,sans-serif;max-width:600px;color:#16181C">
    <h2 style="color:#DD4E14;margin:0 0 12px">Thanks — we've got your RFQ.</h2>
    <p>Hi ${esc(first)},</p>
    <p>Thanks for reaching out to Southern Perfection Fabrication. We've received your request and our team is reviewing it now. We'll get back to you shortly — usually within one business day — with next steps.</p>
    <p><strong>Have a drawing or print?</strong> Just reply to this email and attach it, and we'll match it to your request.</p>
    <p style="margin-top:20px">Talk soon,<br>The team at Southern Perfection Fabrication</p>
    <hr style="border:none;border-top:1px solid #D8D4CA;margin:20px 0">
    <p style="color:#6F7782;font-size:13px">Southern Perfection Fabrication · 232 Hwy 49 S, Byron, GA 31008<br>
    478-956-4442 · toll-free (800) 237-4726 · sales@southernperfection.com</p>
  </div>`;
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

/**
 * SPF website Worker.
 * - POST /api/rfq  -> creates/updates a HubSpot contact using the private-app
 *   token stored in the encrypted secret env.HUBSPOT_TOKEN (never in the repo).
 * - Everything else -> served from static assets (env.ASSETS).
 *
 * If HUBSPOT_TOKEN is not set yet, /api/rfq returns 503 and the site's form
 * gracefully falls back to emailing sales@southernperfection.com.
 */
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/api/rfq") {
      if (request.method !== "POST") {
        return json({ ok: false, error: "method_not_allowed" }, 405);
      }
      return handleRfq(request, env);
    }
    return env.ASSETS.fetch(request);
  },
};

const HS_BASE = "https://api.hubapi.com";

async function handleRfq(request, env) {
  if (!env.HUBSPOT_TOKEN) {
    return json({ ok: false, error: "not_configured" }, 503);
  }
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

  const properties = {
    email,
    firstname: str(data.firstname),
    lastname: str(data.lastname),
    company: str(data.company),
    phone: str(data.phone),
    message: str(data.message),
  };
  // Drop empties so we never overwrite existing values with blanks.
  Object.keys(properties).forEach((k) => {
    if (k !== "email" && !properties[k]) delete properties[k];
  });

  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${env.HUBSPOT_TOKEN}`,
  };

  // Create the contact.
  const create = await fetch(`${HS_BASE}/crm/v3/objects/contacts`, {
    method: "POST",
    headers,
    body: JSON.stringify({ properties }),
  });

  if (create.ok) return json({ ok: true, action: "created" });

  // Already exists -> update by email.
  if (create.status === 409) {
    const update = await fetch(
      `${HS_BASE}/crm/v3/objects/contacts/${encodeURIComponent(email)}?idProperty=email`,
      { method: "PATCH", headers, body: JSON.stringify({ properties }) }
    );
    if (update.ok) return json({ ok: true, action: "updated" });
    return json({ ok: false, error: "update_failed", detail: await safeText(update) }, 502);
  }

  return json({ ok: false, error: "hubspot_error", status: create.status, detail: await safeText(create) }, 502);
}

function str(v) {
  return typeof v === "string" ? v.trim() : "";
}
async function safeText(res) {
  try {
    return (await res.text()).slice(0, 300);
  } catch {
    return "";
  }
}
function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

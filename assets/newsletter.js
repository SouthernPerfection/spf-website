/*
 * The Returnable Report — capture layer.
 * Injects (1) an exit-intent modal offering the spec-guide PDF for an email, and
 * (2) a footer signup band for the newsletter. Both POST to /api/rfq:
 *   modal  -> type:lead_magnet  (delivers the guide + alerts sales)
 *   footer -> type:newsletter   (welcome email, no sales alert)
 * Self-contained, progressive-enhancement, no dependencies.
 */
(function () {
  if (window.__spfNewsletter) return;
  window.__spfNewsletter = true;

  var ENDPOINT = "/api/rfq";
  var GUIDE_PDF = "/assets/guides/how-to-spec-a-returnable-rack.pdf";
  var EI_SUPPRESS_DAYS = 30;
  // Pages where the exit-intent modal shouldn't fire (a form is already the point).
  var EI_SKIP = ["/how-to-spec-a-returnable-rack/", "/contact/"];

  function lsGet(k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { window.localStorage.setItem(k, v); } catch (e) {} }
  function ssGet(k) { try { return window.sessionStorage.getItem(k); } catch (e) { return null; } }
  function now() { return new Date().getTime(); }
  function validEmail(v) { return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v); }

  function post(payload) {
    return fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).then(function (r) { return r.ok; }).catch(function () { return false; });
  }

  function fireLead(category, label) {
    if (window.gtag) window.gtag("event", "generate_lead", { event_category: category, event_label: label });
  }

  function attribution(source) {
    return {
      source_page: source,
      landing_page: ssGet("spf_landing") || location.pathname,
    };
  }

  /* ---------- styles ---------- */
  var css =
    ".spf-nl-band{background:#16181C;color:#F3F1EC;padding:34px 20px;font-family:'IBM Plex Sans',system-ui,sans-serif}" +
    ".spf-nl-band .in{max-width:1080px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;gap:18px 28px;justify-content:space-between}" +
    ".spf-nl-band .cta h3{font-family:'Bebas Neue',sans-serif;font-weight:400;letter-spacing:1px;font-size:28px;margin:0 0 4px;color:#fff}" +
    ".spf-nl-band .cta p{margin:0;font-size:14px;color:#B9BDC4;max-width:520px}" +
    ".spf-nl-form{display:flex;gap:8px;flex-wrap:wrap}" +
    ".spf-nl-form input{border:1px solid #3a3d44;background:#0f1114;color:#fff;border-radius:6px;padding:12px 14px;font-size:14px;font-family:inherit;min-width:230px}" +
    ".spf-nl-form input::placeholder{color:#8a8f98}" +
    ".spf-nl-form button{background:#DD4E14;color:#fff;border:0;border-radius:6px;padding:12px 20px;font-size:14px;font-weight:700;font-family:inherit;cursor:pointer}" +
    ".spf-nl-form button:hover{background:#c4440f}" +
    ".spf-nl-msg{font-size:13px;margin-top:8px;color:#9fe0c8}" +
    ".spf-nl-msg.err{color:#f2a58c}" +
    /* modal */
    ".spf-ei-ov{position:fixed;inset:0;background:rgba(10,12,15,.62);z-index:99998;display:flex;align-items:center;justify-content:center;padding:18px;opacity:0;transition:opacity .18s}" +
    ".spf-ei-ov.show{opacity:1}" +
    ".spf-ei{width:380px;max-width:100%;background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,.35);font-family:'IBM Plex Sans',system-ui,sans-serif;transform:translateY(8px);transition:transform .18s}" +
    ".spf-ei-ov.show .spf-ei{transform:none}" +
    ".spf-ei .top{position:relative;background:radial-gradient(120% 120% at 100% 0%,#1F3864 0%,#16181C 60%);color:#fff;padding:20px 22px}" +
    ".spf-ei .top .k{font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#DD4E14;font-weight:700}" +
    ".spf-ei .top h4{font-family:'Bebas Neue',sans-serif;font-weight:400;font-size:27px;letter-spacing:.5px;margin:6px 0 0;line-height:1}" +
    ".spf-ei .x{position:absolute;top:12px;right:14px;color:#cfd3d9;background:none;border:0;font-size:22px;line-height:1;cursor:pointer}" +
    ".spf-ei .in2{padding:18px 22px 22px}" +
    ".spf-ei .in2 p.d{margin:0 0 12px;color:#3c3f45;font-size:13.5px;line-height:1.5}" +
    ".spf-ei input{width:100%;border:1px solid #D8D4CA;border-radius:7px;padding:11px 13px;font-size:14px;font-family:inherit;margin:0 0 9px}" +
    ".spf-ei button.go{width:100%;background:#DD4E14;color:#fff;border:0;border-radius:7px;padding:12px;font-size:14px;font-weight:700;font-family:inherit;cursor:pointer}" +
    ".spf-ei button.go:hover{background:#c4440f}" +
    ".spf-ei .fine{font-size:11px;color:#6F7782;text-align:center;margin:10px 0 0}" +
    ".spf-ei .msg{font-size:13px;margin-top:9px;color:#0f7b6c;text-align:center}" +
    ".spf-ei .msg.err{color:#c4440f}" +
    ".spf-ei a.dl{display:inline-block;margin-top:6px;color:#1F3864;font-weight:700;font-size:14px}";
  var st = document.createElement("style");
  st.textContent = css;
  document.head.appendChild(st);

  /* ---------- footer signup band ---------- */
  function buildBand() {
    var band = document.createElement("section");
    band.className = "spf-nl-band";
    band.setAttribute("aria-label", "Newsletter signup");
    band.innerHTML =
      '<div class="in">' +
        '<div class="cta"><h3>Get The Returnable Report</h3>' +
        '<p>One useful email a month for people who ship parts and pay for packaging — a customer story, a shop capability, and a practical tip. No spam.</p></div>' +
        '<div><form class="spf-nl-form" novalidate>' +
          '<input type="email" name="email" placeholder="Work email" autocomplete="email" required>' +
          '<button type="submit">Subscribe</button>' +
          '<div class="spf-nl-msg" hidden></div>' +
        '</form></div>' +
      '</div>';
    var form = band.querySelector("form");
    var msg = band.querySelector(".spf-nl-msg");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var email = form.email.value.trim();
      if (!validEmail(email)) { msg.hidden = false; msg.className = "spf-nl-msg err"; msg.textContent = "Please enter a valid email."; return; }
      var btn = form.querySelector("button"); btn.disabled = true; btn.textContent = "…";
      var a = attribution("footer");
      post({ email: email, type: "newsletter", source_page: a.source_page, landing_page: a.landing_page }).then(function (ok) {
        if (ok) {
          lsSet("spf_subscribed", "1");
          fireLead("Newsletter", "footer");
          form.innerHTML = '<div class="spf-nl-msg" style="color:#9fe0c8">✓ You\'re in — check your inbox to confirm. Talk soon.</div>';
        } else {
          btn.disabled = false; btn.textContent = "Subscribe";
          msg.hidden = false; msg.className = "spf-nl-msg err"; msg.textContent = "Something went wrong — email sales@southernperfection.com and we'll add you.";
        }
      });
    });
    var footer = document.querySelector(".site-footer");
    if (footer && footer.parentNode) footer.parentNode.insertBefore(band, footer);
    else document.body.appendChild(band);
  }

  /* ---------- exit-intent modal ---------- */
  function buildModal() {
    var ov = document.createElement("div");
    ov.className = "spf-ei-ov";
    ov.innerHTML =
      '<div class="spf-ei" role="dialog" aria-modal="true" aria-label="Free guide">' +
        '<div class="top"><button class="x" aria-label="Close">×</button>' +
          '<div class="k">Free guide · PDF</div>' +
          '<h4>How to Spec a Returnable Rack</h4></div>' +
        '<div class="in2">' +
          '<p class="d">The 6-point checklist our engineers use to turn a part into a rack — and a real quote. Get it free.</p>' +
          '<form novalidate>' +
            '<input type="email" name="email" placeholder="Work email" autocomplete="email" required>' +
            '<input type="text" name="firstname" placeholder="First name (optional)" autocomplete="given-name">' +
            '<button type="submit" class="go">Send me the guide →</button>' +
            '<div class="msg" hidden></div>' +
          '</form>' +
          '<div class="fine">No spam. One useful email a month. Unsubscribe anytime.</div>' +
        '</div>' +
      '</div>';
    document.body.appendChild(ov);

    function close() { ov.classList.remove("show"); setTimeout(function () { ov.style.display = "none"; }, 200); }
    ov.querySelector(".x").addEventListener("click", close);
    ov.addEventListener("click", function (e) { if (e.target === ov) close(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });

    var form = ov.querySelector("form");
    var msg = ov.querySelector(".msg");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var email = form.email.value.trim();
      if (!validEmail(email)) { msg.hidden = false; msg.className = "msg err"; msg.textContent = "Please enter a valid email."; return; }
      var btn = form.querySelector(".go"); btn.disabled = true; btn.textContent = "Sending…";
      var a = attribution("exit-intent-modal");
      post({ email: email, firstname: form.firstname.value.trim(), type: "lead_magnet", source_page: a.source_page, landing_page: a.landing_page, message: "Downloaded lead magnet via exit-intent modal" }).then(function (ok) {
        if (ok) {
          lsSet("spf_subscribed", "1");
          fireLead("Lead Magnet", "exit-intent");
          form.parentNode.querySelector(".fine").style.display = "none";
          form.outerHTML = '<div class="msg" style="color:#0f7b6c">✓ Check your inbox — your guide is on the way.</div>' +
            '<a class="dl" href="' + GUIDE_PDF + '" target="_blank" rel="noopener">Or download it now →</a>';
        } else {
          btn.disabled = false; btn.textContent = "Send me the guide →";
          msg.hidden = false; msg.className = "msg err"; msg.textContent = "Something went wrong — please try again.";
        }
      });
    });

    return { show: function () { ov.style.display = "flex"; requestAnimationFrame(function () { ov.classList.add("show"); }); } };
  }

  /* ---------- triggers ---------- */
  function armExitIntent(modal) {
    if (EI_SKIP.indexOf(location.pathname) !== -1) return;
    if (lsGet("spf_subscribed")) return;
    var last = parseInt(lsGet("spf_ei_shown") || "0", 10);
    if (last && now() - last < EI_SUPPRESS_DAYS * 864e5) return;

    var fired = false;
    function trigger() {
      if (fired) return;
      fired = true;
      lsSet("spf_ei_shown", String(now()));
      modal.show();
    }
    // Desktop: mouse leaves the top of the viewport.
    document.addEventListener("mouseout", function (e) {
      if (e.clientY <= 0 && !e.relatedTarget && !e.toElement) trigger();
    });
    // Touch / no-hover fallback: after 45s of engagement.
    if (window.matchMedia && window.matchMedia("(hover: none)").matches) {
      setTimeout(trigger, 45000);
    }
  }

  function init() {
    buildBand();
    var modal = buildModal();
    armExitIntent(modal);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();

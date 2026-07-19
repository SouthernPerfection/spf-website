/*
 * The Returnable Report — capture layer.
 * Two polished modals from one builder:
 *   - Guide modal (exit-intent)  -> type:lead_magnet  (delivers the PDF + alerts sales)
 *   - Newsletter modal (button)  -> type:newsletter   (welcome email, no sales alert)
 * Plus a footer "Subscribe" band whose button opens the newsletter modal, and any
 * element with [data-nl-open] opens it too. Self-contained, no dependencies.
 */
(function () {
  if (window.__spfNewsletter) return;
  window.__spfNewsletter = true;

  var ENDPOINT = "/api/rfq";
  var GUIDE_PDF = "/assets/guides/how-to-spec-a-returnable-rack.pdf";
  var ROI_URL = "/returnable-packaging-roi/";
  var EI_SUPPRESS_DAYS = 30;
  var EI_SKIP = ["/how-to-spec-a-returnable-rack/", "/contact/"];

  function lsGet(k){ try { return localStorage.getItem(k); } catch(e){ return null; } }
  function lsSet(k,v){ try { localStorage.setItem(k,v); } catch(e){} }
  function ssGet(k){ try { return sessionStorage.getItem(k); } catch(e){ return null; } }
  function nowMs(){ return new Date().getTime(); }
  function validEmail(v){ return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v); }
  function esc(s){ return String(s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];}); }

  function post(payload){
    return fetch(ENDPOINT,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)})
      .then(function(r){return r.ok;}).catch(function(){return false;});
  }
  function fireLead(cat,label){ if(window.gtag) window.gtag("event","generate_lead",{event_category:cat,event_label:label}); }
  function attribution(source){ return { source_page: source, landing_page: ssGet("spf_landing") || location.pathname }; }

  /* ---------- styles ---------- */
  var css =
    /* footer newsletter section — light cream band, distinct from the dark footer, inline form */
    ".spf-nl-band{background:#F3F1EC;color:#16181C;padding:48px 20px;border-top:3px solid #DD4E14;font-family:'IBM Plex Sans',system-ui,sans-serif}" +
    ".spf-nl-band .in{max-width:1080px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;gap:20px 44px;justify-content:space-between}" +
    ".spf-nl-band .txt{flex:1 1 380px}" +
    ".spf-nl-band .k{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#DD4E14;font-weight:600;margin-bottom:7px}" +
    ".spf-nl-band h3{font-family:'Bebas Neue',sans-serif;font-weight:400;letter-spacing:1px;font-size:32px;margin:0 0 6px;color:#16181C;line-height:1}" +
    ".spf-nl-band p{margin:0;font-size:14px;color:#6F7782;max-width:560px;line-height:1.5}" +
    ".spf-nl-form{display:flex;gap:8px;flex-wrap:wrap;align-items:flex-start}" +
    ".spf-nl-form input{border:1px solid #D8D4CA;background:#fff;color:#16181C;border-radius:7px;padding:13px 15px;font-size:14px;font-family:inherit;min-width:240px}" +
    ".spf-nl-form input:focus{outline:2px solid #DD4E14;outline-offset:1px;border-color:#DD4E14}" +
    ".spf-nl-form button{background:#DD4E14;color:#fff;border:0;border-radius:7px;padding:13px 24px;font-size:15px;font-weight:700;font-family:inherit;cursor:pointer;white-space:nowrap}" +
    ".spf-nl-form button:hover{background:#c4440f}" +
    ".spf-nl-form button:disabled{opacity:.7;cursor:default}" +
    ".spf-nl-msg{flex-basis:100%;font-size:13px;margin-top:3px;color:#c4440f}" +
    ".spf-nl-done{border-left:3px solid #DD4E14;padding-left:15px;min-width:260px}" +
    ".spf-nl-done .big{font-family:'Bebas Neue',sans-serif;font-size:28px;color:#16181C;letter-spacing:.5px;line-height:1}" +
    ".spf-nl-done p{margin:5px 0 0;color:#3c3f45;font-size:14px}" +
    /* blog end-of-post CTA — clean dark card */
    ".spf-nl-inpost{max-width:768px;margin:22px auto 44px;background:#16181C;border-radius:14px;padding:30px 34px;color:#F3F1EC;font-family:'IBM Plex Sans',system-ui,sans-serif}" +
    ".spf-nl-inpost .row{display:flex;flex-wrap:wrap;align-items:center;gap:20px 32px;justify-content:space-between}" +
    ".spf-nl-inpost .txt{flex:1 1 350px}" +
    ".spf-nl-inpost .k{font-family:'IBM Plex Mono',monospace;font-size:10.5px;letter-spacing:2.5px;text-transform:uppercase;color:#DD4E14;font-weight:600;margin-bottom:9px}" +
    ".spf-nl-inpost h3{font-family:'Bebas Neue',sans-serif;font-weight:400;letter-spacing:.8px;font-size:30px;margin:0 0 8px;color:#ffffff;line-height:1.0}" +
    ".spf-nl-inpost p{margin:0;font-size:13.5px;color:#B9BDC4;line-height:1.55;max-width:460px}" +
    ".spf-nl-inpost button{background:#DD4E14;color:#fff;border:0;border-radius:8px;padding:13px 26px;font-size:15px;font-weight:700;font-family:inherit;cursor:pointer;white-space:nowrap}" +
    ".spf-nl-inpost button:hover{background:#c4440f}" +
    /* overlay + card */
    ".spf-m-ov{position:fixed;inset:0;background:rgba(9,11,14,.6);backdrop-filter:blur(3px);z-index:99998;display:none;align-items:center;justify-content:center;padding:18px;opacity:0;transition:opacity .18s}" +
    ".spf-m-ov.show{opacity:1}" +
    ".spf-m{width:400px;max-width:100%;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 24px 70px rgba(0,0,0,.4);font-family:'IBM Plex Sans',system-ui,sans-serif;transform:translateY(10px) scale(.99);transition:transform .2s}" +
    ".spf-m-ov.show .spf-m{transform:none}" +
    ".spf-m .top{position:relative;background:radial-gradient(120% 130% at 100% 0%,#1F3864 0%,#16181C 62%);color:#fff;padding:22px 24px 20px}" +
    ".spf-m .top .k{font-family:'IBM Plex Mono',monospace;font-size:10.5px;letter-spacing:2px;text-transform:uppercase;color:#DD4E14;font-weight:600}" +
    ".spf-m .top h4{font-family:'Bebas Neue',sans-serif;font-weight:400;font-size:30px;letter-spacing:.5px;margin:7px 0 0;line-height:.98}" +
    ".spf-m .top .tl{font-size:12.5px;color:#C7CBD1;margin-top:5px}" +
    ".spf-m .x{position:absolute;top:14px;right:15px;color:#cfd3d9;background:none;border:0;font-size:24px;line-height:1;cursor:pointer;padding:2px 6px}" +
    ".spf-m .x:hover{color:#fff}" +
    ".spf-m .in2{padding:20px 24px 24px}" +
    ".spf-m .in2 p.d{margin:0 0 14px;color:#3c3f45;font-size:13.5px;line-height:1.55}" +
    ".spf-m input{width:100%;border:1px solid #D8D4CA;border-radius:8px;padding:12px 14px;font-size:14px;font-family:inherit;margin:0 0 10px;color:#16181C}" +
    ".spf-m input:focus{outline:2px solid #DD4E14;outline-offset:1px;border-color:#DD4E14}" +
    ".spf-m textarea{width:100%;border:1px solid #D8D4CA;border-radius:8px;padding:12px 14px;font-size:14px;font-family:inherit;margin:0 0 10px;color:#16181C;min-height:84px;resize:vertical}" +
    ".spf-m textarea:focus{outline:2px solid #DD4E14;outline-offset:1px;border-color:#DD4E14}" +
    ".spf-m button.go{width:100%;background:#DD4E14;color:#fff;border:0;border-radius:8px;padding:13px;font-size:15px;font-weight:700;font-family:inherit;cursor:pointer}" +
    ".spf-m button.go:hover{background:#c4440f}" +
    ".spf-m button.go:disabled{opacity:.7;cursor:default}" +
    ".spf-m .fine{font-size:11.5px;color:#6F7782;text-align:center;margin:11px 0 0;line-height:1.5}" +
    ".spf-m .msg{font-size:13.5px;margin-top:10px;text-align:center;color:#c4440f}" +
    ".spf-m .msg.err{color:#c4440f}" +
    ".spf-m .done{padding:2px 0 2px 15px;border-left:3px solid #DD4E14}" +
    ".spf-m .done .big{font-family:'Bebas Neue',sans-serif;font-size:28px;color:#16181C;letter-spacing:.5px;line-height:1}" +
    ".spf-m .done p{color:#3c3f45;font-size:13.5px;margin:6px 0 0}" +
    ".spf-m .done a.dl{display:inline-block;margin-top:12px;color:#fff;background:#1F3864;text-decoration:none;font-weight:700;font-size:13.5px;padding:10px 18px;border-radius:7px}";
  var st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);

  /* ---------- shared modal builder ---------- */
  function makeModal(cfg){
    var ov = document.createElement("div");
    ov.className = "spf-m-ov";
    var nameField = cfg.showName ? '<input type="text" name="firstname" placeholder="First name (optional)" autocomplete="given-name">' : '';
    ov.innerHTML =
      '<div class="spf-m" role="dialog" aria-modal="true" aria-label="'+esc(cfg.title)+'">' +
        '<div class="top"><button class="x" aria-label="Close">&times;</button>' +
          '<div class="k">'+cfg.eyebrow+'</div>' +
          '<h4>'+cfg.title+'</h4>' +
          (cfg.tagline?'<div class="tl">'+cfg.tagline+'</div>':'') +
        '</div>' +
        '<div class="in2">' +
          '<p class="d">'+cfg.desc+'</p>' +
          '<form novalidate>' +
            '<input type="email" name="email" placeholder="Work email" autocomplete="email" required>' +
            nameField +
            '<button type="submit" class="go">'+cfg.button+'</button>' +
            '<div class="msg" hidden></div>' +
          '</form>' +
          '<div class="fine">'+cfg.fine+'</div>' +
        '</div>' +
      '</div>';
    document.body.appendChild(ov);

    function close(){ ov.classList.remove("show"); setTimeout(function(){ ov.style.display="none"; }, 200); }
    function open(){ ov.style.display="flex"; requestAnimationFrame(function(){ ov.classList.add("show"); }); var i=ov.querySelector('input[name=email]'); if(i) setTimeout(function(){i.focus();},60); }
    ov.querySelector(".x").addEventListener("click", close);
    ov.addEventListener("click", function(e){ if(e.target===ov) close(); });
    document.addEventListener("keydown", function(e){ if(e.key==="Escape" && ov.classList.contains("show")) close(); });

    var form = ov.querySelector("form");
    var msg = ov.querySelector(".msg");
    var in2 = ov.querySelector(".in2");
    form.addEventListener("submit", function(e){
      e.preventDefault();
      var email = form.email.value.trim();
      if(!validEmail(email)){ msg.hidden=false; msg.className="msg err"; msg.textContent="Please enter a valid email."; return; }
      var btn = form.querySelector(".go"); btn.disabled=true; btn.textContent="Sending…";
      var a = attribution(cfg.source);
      var payload = { email: email, type: cfg.type, source_page: a.source_page, landing_page: a.landing_page };
      if(cfg.showName) payload.firstname = form.firstname.value.trim();
      if(cfg.message) payload.message = cfg.message;
      post(payload).then(function(ok){
        if(ok){
          lsSet("spf_subscribed","1");
          fireLead(cfg.category, cfg.label);
          in2.innerHTML = '<div class="done"><div class="big">'+cfg.doneTitle+'</div><p>'+cfg.doneMsg+'</p>'+(cfg.doneLink||'')+'</div>';
        } else {
          btn.disabled=false; btn.textContent=cfg.button;
          msg.hidden=false; msg.className="msg err"; msg.textContent="Something went wrong — please try again.";
        }
      });
    });
    return { open: open, close: close };
  }

  /* ---------- the two modals ---------- */
  var guideModal = makeModal({
    eyebrow: "Free guide &middot; PDF",
    title: "How to Spec a Returnable Rack",
    tagline: "",
    desc: "The 6-point checklist our engineers use to turn a part into a rack &mdash; and a real quote. Get it free.",
    showName: true,
    button: "Send me the guide &rarr;",
    fine: "No spam. One useful email a month. Unsubscribe anytime.",
    type: "lead_magnet",
    source: "exit-intent-modal",
    message: "Downloaded lead magnet via exit-intent modal",
    category: "Lead Magnet", label: "exit-intent",
    doneTitle: "Check your inbox",
    doneMsg: "Your guide is on the way.",
    doneLink: '<a class="dl" href="'+GUIDE_PDF+'" target="_blank" rel="noopener">Or download it now &rarr;</a>'
  });

  var newsletterModal = makeModal({
    eyebrow: "Newsletter &middot; monthly",
    title: "The Returnable Report",
    tagline: "For people who ship parts and pay for packaging.",
    desc: "One useful email a month &mdash; a customer story, a shop capability, and a practical tip you can use. No spam, unsubscribe anytime.",
    showName: false,
    button: "Subscribe &rarr;",
    fine: "Join packaging &amp; ops pros at OEMs and Tier-1s. We never share your email.",
    type: "newsletter",
    source: "subscribe-modal",
    category: "Newsletter", label: "modal",
    doneTitle: "You're in.",
    doneMsg: "Check your inbox to confirm — talk soon.",
    doneLink: '<a class="dl" href="'+ROI_URL+'">See the ROI calculator &rarr;</a>'
  });

  /* ---------- footer newsletter section (own cream band, inline form) ---------- */
  function buildBand(){
    var band = document.createElement("section");
    band.className = "spf-nl-band";
    band.setAttribute("aria-label","Subscribe to The Returnable Report");
    band.innerHTML =
      '<div class="in">' +
        '<div class="txt"><div class="k">Newsletter &middot; monthly</div>' +
          '<h3>Get The Returnable Report</h3>' +
          '<p>One useful email a month for people who ship parts and pay for packaging &mdash; a customer story, a shop capability, and a practical tip. No spam.</p></div>' +
        '<form class="spf-nl-form" novalidate>' +
          '<input type="email" name="email" placeholder="Work email" autocomplete="email" required>' +
          '<button type="submit">Subscribe &rarr;</button>' +
          '<div class="spf-nl-msg" hidden></div>' +
        '</form>' +
      '</div>';
    var form = band.querySelector("form");
    var msg = band.querySelector(".spf-nl-msg");
    form.addEventListener("submit", function(e){
      e.preventDefault();
      var email = form.email.value.trim();
      if(!validEmail(email)){ msg.hidden=false; msg.textContent="Please enter a valid email."; return; }
      var btn = form.querySelector("button"); btn.disabled=true; btn.textContent="…";
      var a = attribution("footer");
      post({ email: email, type:"newsletter", source_page:a.source_page, landing_page:a.landing_page }).then(function(ok){
        if(ok){
          lsSet("spf_subscribed","1");
          fireLead("Newsletter","footer");
          form.outerHTML = '<div class="spf-nl-done"><div class="big">You\'re in.</div><p>Check your inbox to confirm &mdash; talk soon.</p></div>';
        } else {
          btn.disabled=false; btn.innerHTML="Subscribe &rarr;";
          msg.hidden=false; msg.textContent="Something went wrong — email sales@southernperfection.com and we'll add you.";
        }
      });
    });
    var footer = document.querySelector(".site-footer");
    if(footer && footer.parentNode) footer.parentNode.insertBefore(band, footer);
    else document.body.appendChild(band);
  }

  /* ---------- site-wide RFQ / "send a print" modal ---------- */
  function buildRfqModal(){
    var ov = document.createElement("div");
    ov.className = "spf-m-ov";
    ov.innerHTML =
      '<div class="spf-m" role="dialog" aria-modal="true" aria-label="Get a quote">' +
        '<div class="top"><button class="x" aria-label="Close">&times;</button>' +
          '<div class="k">Get a quote</div>' +
          '<h4>Send us your part</h4>' +
          '<div class="tl">A rack concept and a real number &mdash; usually within a business day.</div>' +
        '</div>' +
        '<div class="in2">' +
          '<p class="d">Tell us about the part and we\'ll come back with a concept and a quote. Have a print or photo? Reply to the confirmation email and attach it &mdash; we\'ll match it to your request.</p>' +
          '<form novalidate>' +
            '<input type="text" name="firstname" placeholder="First name" autocomplete="given-name">' +
            '<input type="text" name="company" placeholder="Company" autocomplete="organization">' +
            '<input type="email" name="email" placeholder="Work email" autocomplete="email" required>' +
            '<textarea name="message" placeholder="The part &amp; need &mdash; size, weight, volume, lanes, timing"></textarea>' +
            '<button type="submit" class="go">Send it &rarr;</button>' +
            '<div class="msg" hidden></div>' +
          '</form>' +
          '<div class="fine">478-956-4442 &middot; sales@southernperfection.com &middot; We reply within one business day.</div>' +
        '</div>' +
      '</div>';
    document.body.appendChild(ov);
    function close(){ ov.classList.remove("show"); setTimeout(function(){ ov.style.display="none"; }, 200); }
    function open(){ ov.style.display="flex"; requestAnimationFrame(function(){ ov.classList.add("show"); }); var i=ov.querySelector('input[name=email]'); if(i) setTimeout(function(){i.focus();},60); }
    ov.querySelector(".x").addEventListener("click", close);
    ov.addEventListener("click", function(e){ if(e.target===ov) close(); });
    document.addEventListener("keydown", function(e){ if(e.key==="Escape" && ov.classList.contains("show")) close(); });
    var form = ov.querySelector("form"); var msg = ov.querySelector(".msg"); var in2 = ov.querySelector(".in2");
    form.addEventListener("submit", function(e){
      e.preventDefault();
      var email = form.email.value.trim();
      if(!validEmail(email)){ msg.hidden=false; msg.className="msg err"; msg.textContent="Please enter a valid email."; return; }
      var btn = form.querySelector(".go"); btn.disabled=true; btn.textContent="Sending…";
      var payload = {
        firstname: form.firstname.value.trim(),
        company: form.company.value.trim(),
        email: email,
        message: form.message.value.trim(),
        source_page: location.pathname,
        landing_page: ssGet("spf_landing") || location.pathname,
        gclid: ssGet("spf_gclid") || ""
      };
      post(payload).then(function(ok){
        if(ok){
          fireLead("RFQ", location.pathname);
          in2.innerHTML = '<div class="done"><div class="big">We\'ve got it.</div><p>Check your inbox for a confirmation &mdash; reply and attach a print or photo of the part and we\'ll match it to your request. We reply within one business day.</p></div>';
        } else {
          btn.disabled=false; btn.innerHTML="Send it &rarr;";
          msg.hidden=false; msg.className="msg err"; msg.textContent="Something went wrong — email sales@southernperfection.com and we'll jump on it.";
        }
      });
    });
    return { open: open, close: close };
  }

  /* ---------- blog end-of-post subscribe CTA ---------- */
  function buildBlogCta(){
    if(!/^\/blog\/.+/.test(location.pathname)) return; // blog posts only, not the /blog/ index
    var art = document.querySelector(".article-body");
    if(!art) return;
    var sec = art.closest("section") || art;
    var cta = document.createElement("div");
    cta.className = "spf-nl-inpost";
    cta.innerHTML =
      '<div class="row">' +
        '<div class="txt">' +
          '<div class="k">The Returnable Report</div>' +
          '<h3>Get one useful email a month</h3>' +
          '<p>A customer story, a shop capability, and a practical tip &mdash; for the people who ship parts and pay for packaging. No spam, unsubscribe anytime.</p>' +
        '</div>' +
        '<button type="button" data-nl-open>Subscribe &rarr;</button>' +
      '</div>';
    if(sec.parentNode) sec.parentNode.insertBefore(cta, sec.nextSibling);
  }

  /* ---------- exit-intent (guide) ---------- */
  function armExitIntent(){
    if(EI_SKIP.indexOf(location.pathname) !== -1) return;
    if(lsGet("spf_subscribed")) return;
    var last = parseInt(lsGet("spf_ei_shown")||"0",10);
    if(last && nowMs()-last < EI_SUPPRESS_DAYS*864e5) return;
    var fired=false;
    function trigger(){ if(fired) return; fired=true; lsSet("spf_ei_shown",String(nowMs())); guideModal.open(); }
    document.addEventListener("mouseout", function(e){ if(e.clientY<=0 && !e.relatedTarget && !e.toElement) trigger(); });
    if(window.matchMedia && window.matchMedia("(hover: none)").matches) setTimeout(trigger, 45000);
  }

  function init(){
    buildBand();
    buildBlogCta();
    var rfqModal = buildRfqModal();
    document.addEventListener("click", function(e){
      if(!e.target.closest) return;
      var nl = e.target.closest("[data-nl-open]");
      if(nl){ e.preventDefault(); newsletterModal.open(); return; }
      var rq = e.target.closest('a[href*="#rfq"], [data-rfq-open]');
      if(rq){
        // Homepage RFQ form is on-page — keep the native scroll there; upgrade every
        // other page's "Start an RFQ" CTA to open the in-context modal.
        if(location.pathname === "/" && !rq.hasAttribute("data-rfq-open")) return;
        e.preventDefault(); rfqModal.open();
      }
    });
    // Deep-link: /?subscribe or #subscribe opens the newsletter modal (e.g. the LinkedIn button).
    if(/[?&]subscribe(=|&|$)/.test(location.search) || location.hash === "#subscribe"){
      newsletterModal.open();
    }
    armExitIntent();
  }
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();

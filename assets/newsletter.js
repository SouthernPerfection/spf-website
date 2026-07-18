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
    /* footer band */
    ".spf-nl-band{background:radial-gradient(120% 160% at 100% 0%,#1F3864 0%,#16181C 58%);color:#F3F1EC;padding:40px 20px;font-family:'IBM Plex Sans',system-ui,sans-serif}" +
    ".spf-nl-band .in{max-width:1080px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;gap:16px 40px;justify-content:space-between}" +
    ".spf-nl-band .k{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#DD4E14;font-weight:600;margin-bottom:6px}" +
    ".spf-nl-band h3{font-family:'Bebas Neue',sans-serif;font-weight:400;letter-spacing:1px;font-size:30px;margin:0 0 4px;color:#fff;line-height:1}" +
    ".spf-nl-band p{margin:0;font-size:14px;color:#B9BDC4;max-width:560px}" +
    ".spf-nl-band .sub{background:#DD4E14;color:#fff;border:0;border-radius:7px;padding:14px 26px;font-size:15px;font-weight:700;font-family:inherit;cursor:pointer;white-space:nowrap}" +
    ".spf-nl-band .sub:hover{background:#c4440f}" +
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
    ".spf-m button.go{width:100%;background:#DD4E14;color:#fff;border:0;border-radius:8px;padding:13px;font-size:15px;font-weight:700;font-family:inherit;cursor:pointer}" +
    ".spf-m button.go:hover{background:#c4440f}" +
    ".spf-m button.go:disabled{opacity:.7;cursor:default}" +
    ".spf-m .fine{font-size:11.5px;color:#6F7782;text-align:center;margin:11px 0 0;line-height:1.5}" +
    ".spf-m .msg{font-size:13.5px;margin-top:10px;text-align:center;color:#0f7b6c}" +
    ".spf-m .msg.err{color:#c4440f}" +
    ".spf-m .done{text-align:center;padding:6px 0 2px}" +
    ".spf-m .done .big{font-family:'Bebas Neue',sans-serif;font-size:26px;color:#16181C;letter-spacing:.5px}" +
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

  /* ---------- footer band (button opens the newsletter modal) ---------- */
  function buildBand(){
    var band = document.createElement("section");
    band.className = "spf-nl-band";
    band.setAttribute("aria-label","Subscribe to The Returnable Report");
    band.innerHTML =
      '<div class="in">' +
        '<div><div class="k">Newsletter</div>' +
          '<h3>Get The Returnable Report</h3>' +
          '<p>One useful email a month for people who ship parts and pay for packaging &mdash; a customer story, a shop capability, and a practical tip. No spam.</p></div>' +
        '<button type="button" class="sub" data-nl-open>Subscribe &rarr;</button>' +
      '</div>';
    var footer = document.querySelector(".site-footer");
    if(footer && footer.parentNode) footer.parentNode.insertBefore(band, footer);
    else document.body.appendChild(band);
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
    document.addEventListener("click", function(e){
      var t = e.target.closest && e.target.closest("[data-nl-open]");
      if(t){ e.preventDefault(); newsletterModal.open(); }
    });
    armExitIntent();
  }
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();

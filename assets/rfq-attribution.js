/* RFQ attribution: remember where the visitor started and where they clicked the
   RFQ CTA, so a lead submitted on the homepage form can be traced to its source
   page. Pure sessionStorage — no cookies, no network, fails silently. */
(function () {
  "use strict";
  try {
    var ss = window.sessionStorage;
    if (!ss) return;
    // Landing page = first page of this session (best "what brought them in" signal).
    if (!ss.getItem("spf_landing")) {
      ss.setItem("spf_landing", location.pathname);
    }
    // Google Ads click id (gclid / gbraid / wbraid) — captured once per session so an
    // RFQ can be tied back to the ad click for offline conversion import (click -> RFQ
    // -> won revenue back into Google Ads). Additive, best-effort.
    try {
      var qs = new URLSearchParams(location.search);
      var gid = qs.get("gclid") || qs.get("gbraid") || qs.get("wbraid");
      if (gid && !ss.getItem("spf_gclid")) ss.setItem("spf_gclid", gid);
    } catch (err) {}
    // Source page = the page the visitor was on when they clicked an RFQ CTA
    // (links to #rfq / /#rfq). Captured on the way to the homepage form.
    document.addEventListener(
      "click",
      function (e) {
        var t = e.target;
        var a = t && t.closest ? t.closest('a[href*="#rfq"]') : null;
        if (a) {
          try { ss.setItem("spf_source", location.pathname); } catch (err) {}
        }
      },
      true
    );
  } catch (err) {
    /* attribution is best-effort; never block the page */
  }
})();

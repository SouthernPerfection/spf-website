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

/* Careers apply form -> /api/apply (Resend emails applicant + team). */
(function () {
  var form = document.getElementById("applyForm");
  if (!form) return;
  var msg = document.getElementById("applyMsg");
  var f = form.elements;
  function val(n) { return f[n] && f[n].value ? String(f[n].value).trim() : ""; }
  function show(t, err) {
    if (!msg) return;
    msg.textContent = t;
    msg.style.display = "block";
    msg.style.color = err ? "#b3261e" : "#0f7b6c";
  }
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var data = {
      name: val("name"), email: val("email"), phone: val("phone"),
      role: val("role") || document.title, experience: val("experience"), message: val("message"),
    };
    if (!data.name || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(data.email)) {
      show("Please enter your name and a valid email address.", true);
      return;
    }
    var btn = form.querySelector('button[type="submit"]');
    var orig = btn ? btn.textContent : "";
    if (btn) { btn.disabled = true; btn.textContent = "Sending…"; }
    fetch("/api/apply", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        if (res && res.ok) {
          form.style.display = "none";
          show("Thanks, " + data.name.split(" ")[0] + "! We got your application and emailed a confirmation to " + data.email + ". We'll be in touch soon.", false);
          if (window.gtag) gtag("event", "generate_lead", { event_category: "Careers", event_label: data.role });
        } else {
          show("Something went wrong sending that. Please email receptionist@southernperfection.com and we'll take it from there.", true);
          if (btn) { btn.disabled = false; btn.textContent = orig; }
        }
      })
      .catch(function () {
        show("Something went wrong sending that. Please email receptionist@southernperfection.com and we'll take it from there.", true);
        if (btn) { btn.disabled = false; btn.textContent = orig; }
      });
  });
})();

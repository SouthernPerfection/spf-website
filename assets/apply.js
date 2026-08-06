/* Careers screening form -> /api/apply.
   Fast fit-screen: contact + eligibility + shift availability + tape-measure
   competency check + optional work history + consents. On submit we build a
   branded PDF of the application client-side (pdf-lib, lazy-loaded) and hand it
   to the Worker, which emails it (with a PASS/FAIL tape score) to the applicant
   and to the SPF team via Resend. PDF is best-effort — if it can't be built the
   application still goes through and the team gets a branded HTML record. */
(function () {
  var form = document.getElementById("applyForm");
  if (!form) return;
  var msg = document.getElementById("applyMsg");
  var f = form.elements;

  function val(n) { return f[n] && typeof f[n].value === "string" ? f[n].value.trim() : ""; }
  function radio(n) {
    var els = form.querySelectorAll('input[name="' + n + '"]');
    for (var i = 0; i < els.length; i++) if (els[i].checked) return els[i].value;
    return "";
  }
  function checks(n) {
    var out = [], els = form.querySelectorAll('input[name="' + n + '"]:checked');
    for (var i = 0; i < els.length; i++) out.push(els[i].value);
    return out;
  }
  function checked(n) { return !!(f[n] && f[n].checked); }
  function show(t, err) {
    if (!msg) return;
    msg.textContent = t;
    msg.style.display = "block";
    msg.style.color = err ? "#b3261e" : "#0f7b6c";
    if (err) msg.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  /* felony -> reveal describe box */
  var felonyBox = form.querySelector(".af-felony");
  form.querySelectorAll('input[name="felony"]').forEach(function (r) {
    r.addEventListener("change", function () {
      if (felonyBox) felonyBox.hidden = radio("felony") !== "Yes";
    });
  });

  /* score the tape-measure check against each fieldset's data-answer */
  function scoreTape() {
    var out = { total: 0, score: 0, answers: [] };
    form.querySelectorAll(".af-tape").forEach(function (fs, i) {
      var input = fs.querySelector("input[type=radio]");
      if (!input) return;
      var name = input.name, correct = fs.getAttribute("data-answer") || "";
      var given = radio(name);
      var ok = given && given === correct;
      out.total++; if (ok) out.score++;
      out.answers.push({ q: i + 1, given: given, correct: correct, ok: !!ok });
    });
    return out;
  }

  function collect() {
    return {
      role: val("role") || document.title,
      name: val("name"), email: val("email"), phone: val("phone"),
      experience: val("experience"),
      age18: radio("age18"), workAuth: radio("workAuth"), transport: radio("transport"),
      overtime: radio("overtime"), drugScreen: radio("drugScreen"),
      shifts: checks("shifts"),
      felony: radio("felony"), felonyDesc: val("felonyDesc"),
      tape: scoreTape(),
      history: [
        { co: val("job1co"), title: val("job1title"), dates: val("job1dates"), reason: val("job1reason") },
        { co: val("job2co"), title: val("job2title"), dates: val("job2dates"), reason: val("job2reason") }
      ].filter(function (j) { return j.co || j.title; }),
      message: val("message"),
      consents: { certify: checked("consentTrue"), atWill: checked("consentAtWill"), drug: checked("consentDrug") },
      submittedAt: new Date().toISOString()
    };
  }

  function validate(d) {
    if (!d.name) return "Please enter your name.";
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(d.email)) return "Please enter a valid email address.";
    if (!d.phone) return "Please enter a phone number.";
    var yn = { age18: "if you're 18 or older", workAuth: "your U.S. work authorization", transport: "your transportation", overtime: "overtime availability", drugScreen: "the drug-screen question" };
    for (var k in yn) if (!d[k]) return "Please answer " + yn[k] + ".";
    if (!d.shifts.length) return "Please pick at least one shift you can work.";
    if (!d.felony) return "Please answer the felony question (yes or no).";
    for (var i = 0; i < d.tape.answers.length; i++) if (!d.tape.answers[i].given) return "Please answer all three tape-measure questions — a wrong answer is fine, we train for it.";
    if (!d.consents.certify || !d.consents.atWill || !d.consents.drug) return "Please check the three acknowledgment boxes to submit.";
    return "";
  }

  /* Build a branded 1-page PDF of the application. Returns {pdf,pdfName} or null. */
  function lastName(n) { var p = String(n || "").trim().split(/\s+/); return (p[p.length - 1] || "applicant").replace(/[^A-Za-z0-9]/g, ""); }
  async function buildPdf(d) {
    var lib;
    try { lib = await import("https://esm.sh/pdf-lib@1.17.1"); } catch (e) { return null; }
    try {
      var SPARK = lib.rgb(0.867, 0.306, 0.078), INK = lib.rgb(0.086, 0.094, 0.11), STEEL = lib.rgb(0.435, 0.467, 0.51);
      var doc = await lib.PDFDocument.create();
      var font = await doc.embedFont(lib.StandardFonts.Helvetica);
      var bold = await doc.embedFont(lib.StandardFonts.HelveticaBold);
      var page = doc.addPage([612, 792]);
      var W = 612, M = 48, y = 792 - 44;

      try {
        var buf = await (await fetch("/assets/logo.png")).arrayBuffer();
        var png = await doc.embedPng(buf), s = 34 / png.height;
        page.drawImage(png, { x: M, y: y - 24, width: png.width * s, height: 34 });
      } catch (e) {}
      page.drawText("APPLICATION FOR EMPLOYMENT", { x: W - M - bold.widthOfTextAtSize("APPLICATION FOR EMPLOYMENT", 11), y: y - 6, size: 11, font: bold, color: INK });
      page.drawText("Southern Perfection Fabrication Holdings, Inc.", { x: W - M - font.widthOfTextAtSize("Southern Perfection Fabrication Holdings, Inc.", 8), y: y - 18, size: 8, font: font, color: STEEL });
      y -= 40;
      page.drawRectangle({ x: M, y: y, width: W - 2 * M, height: 2.5, color: SPARK }); y -= 22;

      function sectionTitle(t) { page.drawText(t.toUpperCase(), { x: M, y: y, size: 9, font: bold, color: SPARK }); y -= 15; }
      function wrap(t, fnt, sz, max) {
        var words = String(t).split(/\s+/), lines = [], cur = "";
        for (var i = 0; i < words.length; i++) {
          var test = cur ? cur + " " + words[i] : words[i];
          if (fnt.widthOfTextAtSize(test, sz) > max && cur) { lines.push(cur); cur = words[i]; } else cur = test;
        }
        if (cur) lines.push(cur); return lines.length ? lines : [""];
      }
      function row(k, v) {
        if (v === "" || v == null) return;
        page.drawText(k, { x: M, y: y, size: 9, font: bold, color: STEEL });
        var lines = wrap(v, font, 10, W - 2 * M - 150);
        for (var i = 0; i < lines.length; i++) { page.drawText(lines[i], { x: M + 150, y: y, size: 10, font: font, color: INK }); if (i < lines.length - 1) y -= 13; }
        y -= 16;
      }

      sectionTitle("Applicant");
      row("Position applied for", d.role);
      row("Name", d.name);
      row("Email", d.email);
      row("Phone", d.phone);
      row("Relevant experience", d.experience);
      y -= 4; sectionTitle("Availability & eligibility");
      row("18 or older", d.age18);
      row("U.S. work authorized", d.workAuth);
      row("Reliable transportation", d.transport);
      row("Open to overtime", d.overtime);
      row("Consents to drug screen", d.drugScreen);
      row("Shifts available", d.shifts.join(", "));
      row("Felony conviction", d.felony + (d.felonyDesc ? " - " + d.felonyDesc : ""));

      y -= 4; sectionTitle("Tape-measure check");
      page.drawText(d.tape.score + " / " + d.tape.total + " correct", { x: M, y: y, size: 13, font: bold, color: d.tape.score === d.tape.total ? lib.rgb(0.06, 0.48, 0.42) : SPARK }); y -= 18;
      d.tape.answers.forEach(function (a) {
        row("Q" + a.q + " (answer " + a.correct + ")", (a.given || "-") + "  " + (a.ok ? "[correct]" : "[missed]"));
      });

      if (d.history.length) {
        y -= 4; sectionTitle("Work history");
        d.history.forEach(function (j) { row(j.co || "Employer", [j.title, j.dates, j.reason ? "left: " + j.reason : ""].filter(Boolean).join(" | ")); });
      }
      if (d.message) { y -= 4; sectionTitle("Notes"); wrap(d.message, font, 10, W - 2 * M).forEach(function (l) { page.drawText(l, { x: M, y: y, size: 10, font: font, color: INK }); y -= 13; }); }

      y -= 8; sectionTitle("Acknowledgments");
      ["Certified information is true & complete", "Understands employment is at-will", "Consents to pre-employment drug screen"].forEach(function (t) {
        page.drawText("[x] " + t, { x: M, y: y, size: 9, font: font, color: INK }); y -= 13;
      });

      var when = new Date(d.submittedAt).toLocaleString("en-US");
      page.drawText("Submitted online " + when + "  |  232 Hwy 49 S, Byron, GA 31008  |  478-956-4442  |  Est. 1982", { x: M, y: 34, size: 7.5, font: font, color: STEEL });

      return { pdf: await doc.saveAsBase64(), pdfName: "SPF-Application-" + lastName(d.name) + ".pdf" };
    } catch (e) { return null; }
  }

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    var d = collect();
    var err = validate(d);
    if (err) { show(err, true); return; }
    var btn = form.querySelector('button[type="submit"]');
    var orig = btn ? btn.textContent : "";
    if (btn) { btn.disabled = true; btn.textContent = "Sending…"; }
    show("Building your application…", false);

    var pdf = await buildPdf(d);
    if (pdf) { d.pdf = pdf.pdf; d.pdfName = pdf.pdfName; }

    try {
      var r = await fetch("/api/apply", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(d) });
      var res = await r.json();
      if (res && res.ok) {
        form.style.display = "none";
        show("Thanks, " + d.name.split(" ")[0] + "! Your application is in — we emailed a copy to " + d.email + ". We’ll be in touch soon. (Don’t worry about the tape-measure questions — we train.)", false);
        if (window.gtag) gtag("event", "generate_lead", { event_category: "Careers", event_label: d.role });
      } else {
        show("Something went wrong sending that. Please email receptionist@southernperfection.com and we’ll take it from there.", true);
        if (btn) { btn.disabled = false; btn.textContent = orig; }
      }
    } catch (e2) {
      show("Something went wrong sending that. Please email receptionist@southernperfection.com and we’ll take it from there.", true);
      if (btn) { btn.disabled = false; btn.textContent = orig; }
    }
  });
})();

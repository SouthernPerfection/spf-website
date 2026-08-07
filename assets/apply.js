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
      var rgb = lib.rgb;
      var INK = rgb(0.086, 0.094, 0.11), SPARK = rgb(0.867, 0.306, 0.078), PAPER = rgb(0.957, 0.949, 0.925),
          STEEL = rgb(0.435, 0.467, 0.51), WHITE = rgb(1, 1, 1), GREEN = rgb(0.05, 0.45, 0.38), RED = rgb(0.72, 0.16, 0.12), LT = rgb(0.78, 0.8, 0.83);
      var doc = await lib.PDFDocument.create();
      var font = await doc.embedFont(lib.StandardFonts.Helvetica);
      var bold = await doc.embedFont(lib.StandardFonts.HelveticaBold);
      var W = 612, H = 792, M = 44, page = doc.addPage([W, H]);
      var rt = function (t, x, y, s, ff, c) { page.drawText(t, { x: x - ff.widthOfTextAtSize(t, s), y: y, size: s, font: ff, color: c }); };

      // header band
      page.drawRectangle({ x: 0, y: H - 96, width: W, height: 96, color: INK });
      page.drawRectangle({ x: 0, y: H - 100, width: W, height: 4, color: SPARK });
      try { var buf = await (await fetch("/assets/logo.png")).arrayBuffer(); var png = await doc.embedPng(buf), sc0 = 34 / png.height; page.drawImage(png, { x: M, y: H - 64, width: png.width * sc0, height: 34 }); } catch (e) {}
      rt("APPLICATION FOR EMPLOYMENT", W - M, H - 46, 14, bold, WHITE);
      rt("Southern Perfection Fabrication Holdings, Inc.", W - M, H - 60, 8.5, font, LT);
      rt("Received " + new Date(d.submittedAt).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" }), W - M, H - 74, 8.5, font, SPARK);

      // tape-measure score band
      var sc = d.tape.score, tot = d.tape.total, SCORECOL = sc === tot ? GREEN : (sc >= 2 ? SPARK : RED);
      var by = H - 124, bh = 60;
      page.drawRectangle({ x: M, y: by - bh, width: W - 2 * M, height: bh, color: PAPER });
      page.drawRectangle({ x: M, y: by - bh, width: 6, height: bh, color: SCORECOL });
      page.drawText(sc + "/" + tot, { x: 64, y: by - 42, size: 30, font: bold, color: SCORECOL });
      page.drawText("TAPE-MEASURE CHECK", { x: 150, y: by - 24, size: 11, font: bold, color: INK });
      page.drawText("We train — this score is a guide, not a gate.", { x: 150, y: by - 42, size: 9.5, font: font, color: STEEL });
      var mark = function (x, y, ok) {
        if (ok) { page.drawLine({ start: { x: x, y: y + 2 }, end: { x: x + 3, y: y - 1 }, thickness: 1.6, color: WHITE }); page.drawLine({ start: { x: x + 3, y: y - 1 }, end: { x: x + 8, y: y + 6 }, thickness: 1.6, color: WHITE }); }
        else { page.drawLine({ start: { x: x, y: y + 6 }, end: { x: x + 7, y: y - 1 }, thickness: 1.6, color: WHITE }); page.drawLine({ start: { x: x, y: y - 1 }, end: { x: x + 7, y: y + 6 }, thickness: 1.6, color: WHITE }); }
      };
      var pw = 52, gap = 8, px0 = W - M - (3 * pw + 2 * gap);
      d.tape.answers.forEach(function (a, i) { var x = px0 + i * (pw + gap); page.drawRectangle({ x: x, y: by - 42, width: pw, height: 22, color: a.ok ? GREEN : RED }); page.drawText("Q" + (i + 1), { x: x + 9, y: by - 35, size: 10, font: bold, color: WHITE }); mark(x + 32, by - 32, a.ok); });

      var y = by - bh - 30, rowi = 0;
      var wrap = function (t, fn, sz, mx) { var ws = String(t).split(/\s+/), ls = [], c = ""; for (var i = 0; i < ws.length; i++) { var tt = c ? c + " " + ws[i] : ws[i]; if (fn.widthOfTextAtSize(tt, sz) > mx && c) { ls.push(c); c = ws[i]; } else c = tt; } if (c) ls.push(c); return ls.length ? ls : [""]; };
      var section = function (t) { y -= 8; page.drawText(t.toUpperCase(), { x: M, y: y, size: 10, font: bold, color: SPARK }); page.drawRectangle({ x: M, y: y - 6, width: 34, height: 2.5, color: SPARK }); y -= 20; rowi = 0; };
      var row = function (k, v) { if (v === "" || v == null) return; var lines = wrap(v, font, 10.5, W - 2 * M - 8 - 176); var rh = Math.max(21, lines.length * 14 + 7); if (rowi % 2 === 0) page.drawRectangle({ x: M, y: y - rh + 14, width: W - 2 * M, height: rh, color: PAPER }); page.drawText(k, { x: M + 10, y: y, size: 9, font: bold, color: STEEL }); lines.forEach(function (ln, i) { page.drawText(ln, { x: M + 176, y: y - i * 14, size: 10.5, font: font, color: INK }); }); y -= rh; rowi++; };

      section("Applicant");
      row("Position applied for", d.role); row("Name", d.name); row("Email", d.email); row("Phone", d.phone); row("Relevant experience", d.experience);
      section("Availability & eligibility");
      row("18 or older", d.age18); row("U.S. work authorized", d.workAuth); row("Reliable transportation", d.transport); row("Open to overtime", d.overtime); row("Consents to drug screen", d.drugScreen); row("Shifts available", d.shifts.join(", ")); row("Felony conviction", d.felony + (d.felonyDesc ? " — " + d.felonyDesc : ""));
      if (d.history.length) { section("Work history"); d.history.forEach(function (j) { row(j.co || "Employer", [j.title, j.dates, j.reason ? "left: " + j.reason : ""].filter(Boolean).join("  ·  ")); }); }
      if (d.message) { section("Notes"); var ls = wrap(d.message, font, 10.5, W - 2 * M - 20); if (rowi % 2 === 0) page.drawRectangle({ x: M, y: y - ls.length * 14 + 7, width: W - 2 * M, height: ls.length * 14 + 7, color: PAPER }); ls.forEach(function (l, i) { page.drawText(l, { x: M + 10, y: y - i * 14, size: 10.5, font: font, color: INK }); }); y -= ls.length * 14 + 10; }
      section("Acknowledgments");
      ["Certified information is true & complete", "Understands employment is at-will", "Consents to pre-employment drug screen"].forEach(function (t) { page.drawLine({ start: { x: M + 2, y: y + 1 }, end: { x: M + 5, y: y - 2 }, thickness: 1.6, color: GREEN }); page.drawLine({ start: { x: M + 5, y: y - 2 }, end: { x: M + 11, y: y + 6 }, thickness: 1.6, color: GREEN }); page.drawText(t, { x: M + 20, y: y, size: 10, font: font, color: INK }); y -= 17; });

      // footer band
      page.drawRectangle({ x: 0, y: 0, width: W, height: 30, color: INK });
      var foot = "232 Hwy 49 S, Byron, GA 31008   ·   478-956-4442   ·   southernperfection.com   ·   Est. 1982";
      page.drawText(foot, { x: (W - font.widthOfTextAtSize(foot, 8)) / 2, y: 11, size: 8, font: font, color: LT });

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

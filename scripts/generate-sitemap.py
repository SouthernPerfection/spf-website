#!/usr/bin/env python3
"""Regenerate sitemap.xml from every index.html on disk. Run from website/ root.

Each URL gets an accurate <lastmod> from that file's last git commit date — the
one optional tag Google actually uses (to decide when to recrawl). It stays
correct automatically: edit one page, only that page's lastmod moves. <priority>
is kept as a minor hint for non-Google crawlers (Google ignores it).
"""
import pathlib, subprocess, datetime
ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://southernperfection.com"
TODAY = datetime.date.today().isoformat()


def last_mod(path: pathlib.Path) -> str:
    """Last git commit date (YYYY-MM-DD) for this file; fall back to file mtime, then today."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(path)],
            cwd=ROOT, capture_output=True, text=True, timeout=10,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except Exception:
        pass
    try:
        return datetime.date.fromtimestamp(path.stat().st_mtime).isoformat()
    except Exception:
        return TODAY


urls = []
for f in ROOT.rglob("index.html"):
    if any(part in ("node_modules", "scripts", "docs") for part in f.parts):
        continue
    rel = f.parent.relative_to(ROOT).as_posix()
    path = "/" if rel == "." else f"/{rel}/"
    if path == "/":
        prio = "1.0"
    elif path.count("/") == 2:  # /foo/  top-level
        prio = "0.8"
    else:
        prio = "0.7"
    urls.append((path, prio, last_mod(f)))

urls.sort(key=lambda u: (u[0] != "/", u[0]))
lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for path, prio, lastmod in urls:
    lines.append(
        f'  <url><loc>{BASE}{path}</loc>'
        f'<lastmod>{lastmod}</lastmod>'
        f'<priority>{prio}</priority></url>'
    )
lines.append('</urlset>')
(ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n")
print(f"sitemap.xml: {len(urls)} URLs (lastmod from git)")

#!/usr/bin/env python3
"""Regenerate sitemap.xml from every index.html on disk. Run from website/ root."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://southernperfection.com"

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
    urls.append((path, prio))

urls.sort(key=lambda u: (u[0] != "/", u[0]))
lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for path, prio in urls:
    lines.append(f'  <url><loc>{BASE}{path}</loc><priority>{prio}</priority></url>')
lines.append('</urlset>')
(ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n")
print(f"sitemap.xml: {len(urls)} URLs")

"""Apply the search settings for the public GitHub Pages build."""

import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree


origin = "https://gorshkovablog.github.io"
site = Path(sys.argv[1])
pages = [site / path for path in ("index.html", "about/index.html", "recipes/index.html")]
pages.extend(sorted(site.glob("recipes/*/index.html")))
about = site / "about/index.html"
about_title = "Анастасия Горшкова (Листова) — биография и семья"

sitemap = ElementTree.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
for page in pages:
    head, closing_tag, body = page.read_text(encoding="utf-8").partition("</head>")
    url = origin + "/" + page.relative_to(site).as_posix().removesuffix("index.html")
    if not closing_tag or f'<link rel="canonical" href="{url}">' not in head:
        raise ValueError(f"Missing head or unexpected canonical: {page}")

    head = head.replace('<meta name="robots" content="noindex,nofollow">', "")
    if page == about:
        head = re.sub(r"<title>[^<]+</title>", f"<title>{about_title}</title>", head)
        head = re.sub(r'<meta property="og:title" content="[^"]+">',
                      f'<meta property="og:title" content="{about_title}">', head)
        profile = re.search(r'<script type="application/ld\+json">(.*?)</script>', head, re.S)
        data = json.loads(profile.group(1))
        data["mainEntity"]["alternateName"] = "Анастасия Горшкова"
        head = head[:profile.start(1)] + json.dumps(data, ensure_ascii=False) + head[profile.end(1):]
    page.write_text(head + closing_tag + body, encoding="utf-8")
    ElementTree.SubElement(ElementTree.SubElement(sitemap, "url"), "loc").text = url

ElementTree.indent(sitemap)
ElementTree.ElementTree(sitemap).write(site / "sitemap.xml", encoding="utf-8", xml_declaration=True)
(site / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {origin}/sitemap.xml\n", encoding="utf-8")

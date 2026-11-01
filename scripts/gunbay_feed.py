# Gun Bay Global Advisory blog reader for fetch_feeds.py (site has no RSS; blog.html is static cards).
def gunbay(u, get, clean, iso, D, re, max_items=12):
    """Parse blog.html cards (newest first): link, category, month, title, excerpt. arg ending #health returns only cards tagged wealth-health; otherwise the finance, real-asset, jurisdiction and macro cards. Exact day comes from
    the article's own byline ('Month D, YYYY'); falls back to the 1st of the card's month."""
    health = u.endswith("#health"); u = u.split("#")[0]
    base = u.rstrip("/") + "/"
    h = get(base + "blog.html")
    out = []
    for m in re.finditer(r'<a href="(blog/[^"]+\.html)"[^>]*>\s*<article[^>]*data-cat="([^"]*)"(.*?)</article>', h, re.S):
        href, cat, body = m.groups()
        t = re.search(r'<h[23][^>]*>(.*?)</h[23]>', body, re.S)
        p_ = re.search(r'<p>(.*?)</p>', body, re.S)
        d = re.search(r'class="post-(?:card-)?date">([^<]+)<', body)
        lab = re.search(r'class="post-(?:card-)?cat">([^<]+)<|class="post-category">([^<]+)<', body)
        label = html_text(lab.group(1) or lab.group(2)) if lab else ""
        if not t: continue
        out.append({"href": href, "cat": cat, "label": label, "title": clean(re.sub(r"<br\s*/?>", " ", re.sub(r"(?<![:?.!,;])<br\s*/?>(?=\s*<em)", ": ", t.group(1))), 160),
                    "summary": clean(p_.group(1) if p_ else ""), "month": (d.group(1).strip() if d else "")})
    keep = [o for o in out if ("wealth-health" in o["cat"].split()) == health]
    items = []
    for o in keep[:max_items]:
        dt = None
        try:
            a = get(base + o["href"])
            h1 = re.search(r"<h1[^>]*>(.*?)</h1>", a, re.S)
            if h1 and clean(h1.group(1), 300): o["title"] = clean(h1.group(1), 160)
            dm = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2}), (\d{4})", a[:200000][a.find("<main") if "<main" in a else 0:])
            if dm: dt = D.datetime.strptime(" ".join(dm.groups()), "%B %d %Y").replace(tzinfo=D.timezone.utc)
        except Exception: pass
        if not dt:
            try: dt = D.datetime.strptime(o["month"], "%b %Y").replace(tzinfo=D.timezone.utc)
            except Exception: continue
        items.append({"title": o["title"], "url": base + o["href"], "date": iso(dt), "summary": o["summary"]})
    if not items: raise Exception("gunbay cards not found")
    return items
def html_text(s):
    import html, re
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()

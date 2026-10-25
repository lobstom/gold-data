# Operation Wisedome journal reader for fetch_feeds.py (site has no RSS; posts are a JS array in its bundle).
def wisedome(u, get, clean, iso, D, re):
    """wisedome.org has no feed: its journal posts are a JS array in the site bundle
    ({slug,title,author,date,body,excerpt}). Read the bundle URL from index.html, then
    take title, date and the site's own excerpt for each post. Preview = that excerpt."""
    h = get(u); m = re.search(r'src="(/assets/index-[^"]+\.js)"', h)
    if not m: raise Exception("wisedome bundle not found")
    b = get(u.rstrip("/") + m.group(1)); out = []
    for p_ in re.finditer(r'\{slug:"([^"]+)",title:"((?:[^"\\]|\\.)*)",author:"[^"]*",date:"(\d{4}-\d\d-\d\d)",body:`.*?`,excerpt:"((?:[^"\\]|\\.)*)"', b, re.S):
        slug, t, d, ex = p_.groups()
        try: dt = D.datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=D.timezone.utc)
        except Exception: continue
        out.append({"title": clean(t.replace('\\"','"'), 160), "url": u.rstrip("/") + "/journal/" + slug, "date": iso(dt), "summary": clean(ex.replace('\\"','"'))})
    if not out: raise Exception("wisedome journal array not found")
    return out

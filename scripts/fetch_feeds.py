#!/usr/bin/env python3
"""Hourly feed aggregator. Writes feeds.json (stdlib only)."""
import json, re, html, sys, urllib.request, urllib.parse, datetime as D, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
HDRS = {"User-Agent":UA, "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language":"en-US,en;q=0.9"}
PER_SOURCE = 15
SOURCES = [
 {"id":"debriefing","name":"The Debriefing","topic":"Politics & Strategy","type":"tg","arg":"Castlerock2021"},
 {"id":"rattletrap","name":"RattleTrap 1776","topic":"Politics & Strategy","type":"tg","arg":"rattletrap1776"},
 {"id":"bioclandestine","name":"BioClandestine","topic":"Politics & Strategy","type":"tg","arg":"bioclandestine"},
 {"id":"yurta","name":"Yurta Capital","topic":"Markets","type":"tg","arg":"yurta06"},
 {"id":"crude","name":"The Crude Chronicles","topic":"Energy","type":"rss","arg":"https://thecrudechronicles.substack.com/feed"},
 {"id":"gr","name":"Goehring & Rozencwajg","topic":"Energy","type":"rss","arg":"https://blog.gorozen.com/blog/rss.xml"},
 {"id":"bison","name":"Josh Young - Bison Insights","topic":"Energy","type":"rss","arg":"https://bisoninterests.substack.com/feed"},
 {"id":"igwt","name":"In Gold We Trust","topic":"Gold","type":"rss","arg":"https://www.incrementum.li/feed/"},
 {"id":"gata","name":"GATA","topic":"Gold","type":"rss","arg":"https://www.gata.org/rss.xml"},
 {"id":"acqmult","name":"Acquirer's Multiple","topic":"Markets","type":"rss","arg":"https://acquirersmultiple.com/feed/"},
 {"id":"pig","name":"Priced in Gold","topic":"Gold","type":"rss","arg":"https://pricedingold.com/feed"},
 {"id":"monetarymetals","name":"Monetary Metals","topic":"Gold","type":"wpj","arg":"https://www.monetary-metals.com/wp-json/wp/v2/article?per_page=15"},
 {"id":"tfm","name":"TF Metals Report","topic":"Gold","type":"feedly","arg":"http://www.tfmetalsreport.com/blog/feed"},
 {"id":"aier","name":"AIER","topic":"Markets","type":"rss","arg":"https://www.aier.org/feed/"},
 {"id":"gcaptain","name":"gCaptain","topic":"Energy","type":"rss","arg":"https://gcaptain.com/feed/"},
 {"id":"stonge","name":"Peter St Onge","topic":"Markets","type":"rss","arg":"https://www.profstonge.com/feed"},
 {"id":"pafere","name":"Krzysztof Szczawinski - PAFERE","topic":"Markets","type":"rss","arg":"https://www.pafere.org/author/krzysztof-szczawinski/feed/"},
 {"id":"bowtiedmara","name":"BowTiedMara","topic":"Politics & Strategy","type":"rss","arg":"https://www.bowtiedmara.io/feed"},
 {"id":"aasecon","name":"AAS Economics","topic":"Markets","type":"rss","arg":"https://aaseconomics.substack.com/feed"},
 {"id":"oldeconomy","name":"TheOldEconomy","topic":"Markets","type":"rss","arg":"https://theoldeconomy.substack.com/feed"},
 {"id":"eugyppius","name":"eugyppius","topic":"Politics & Strategy","type":"rss","arg":"https://eugyppius.substack.com/feed"},
 {"id":"lacalle","name":"Daniel Lacalle","topic":"Markets","type":"rss","arg":"https://dlacalle.com/en/feed/"},
 {"id":"shirk","name":"Cody Shirk","topic":"Markets","type":"rss","arg":"https://www.codyshirk.com/feed"},
 {"id":"lorenz","name":"Swen Lorenz - Undervalued Shares","topic":"Markets","type":"rss","arg":"https://www.undervalued-shares.com/feed/"},
 {"id":"attila","name":"Attila Rebak","topic":"Markets","type":"rss","arg":"https://attilarebak.substack.com/feed"},
 {"id":"frontierviking","name":"FrontierViking","topic":"Markets","type":"rss","arg":"https://frontierviking.substack.com/feed"},
 {"id":"timprice","name":"Tim Price","topic":"Markets","type":"rss","arg":"https://timprice.substack.com/feed"},
 {"id":"riskhedge","name":"RiskHedge","topic":"Markets","type":"rss","arg":"https://riskhedgeresearch.substack.com/feed"},
 {"id":"superspiked","name":"Super-Spiked","topic":"Energy","type":"rss","arg":"https://arjunmurti.substack.com/feed"},
 {"id":"felder","name":"The Felder Report","topic":"Markets","type":"felder","arg":"https://thefelderreport.com/feed/"},
 {"id":"armstrong","name":"Armstrong Economics","topic":"Markets","type":"rss","arg":"https://www.armstrongeconomics.com/feed/"},
 {"id":"dmitriev","name":"Kirill Dmitriev","topic":"Politics & Strategy","type":"tg","arg":"kadmitriev"},
 {"id":"rpsmith","name":"Ronald P. Smith - EMOGCP","topic":"Energy","type":"rss","arg":"https://ronaldpsmith.substack.com/feed"},
 {"id":"sonar21","name":"Larry Johnson - Sonar21","topic":"Politics & Strategy","type":"rss","arg":"https://sonar21.com/feed/"},
 {"id":"ritter","name":"Scott Ritter","topic":"Politics & Strategy","type":"rss","arg":"https://scottritter.substack.com/feed"},
 {"id":"americancompass","name":"American Compass","topic":"Politics & Strategy","type":"feedly","arg":"https://americancompass.org/feed/"},
 {"id":"simplicius","name":"Simplicius","topic":"Politics & Strategy","type":"rss","arg":"https://simplicius76.substack.com/feed"},
 {"id":"alhajji","name":"Anas Alhajji","topic":"Energy","type":"rss","arg":"https://anasalhajjieoa.substack.com/feed"},
 {"id":"jcpa","name":"JCPA","topic":"Politics & Strategy","type":"rss","arg":"https://jcpa.org/feed/"},
 {"id":"brandao","name":"Shannon Brandao - China Boss News","topic":"Politics & Strategy","type":"rss","arg":"https://shannonbrandao.substack.com/feed"},
 {"id":"jinf","name":"JINF","topic":"Politics & Strategy","type":"rss","arg":"https://en.jinf.jp/feed"},
 {"id":"taipeitimes","name":"Taipei Times","topic":"Politics & Strategy","type":"rdf","arg":"https://www.taipeitimes.com/xml/index.rss"},
 {"id":"afc","name":"Asia Frontier Capital","topic":"Markets","type":"afc","arg":"https://www.asiafrontiercapital.com"},
]
import os
FIX={"TheDebriefing17":"/tmp/x.html","SecScottBessent":"/tmp/b.html"}
def get(u):
    if os.environ.get("PROTO"):
        for k,v in FIX.items():
            if u.endswith(k): return open(v).read()
    import time
    for attempt in range(2):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=HDRS), timeout=25).read().decode("utf-8","replace")
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt == 0:
                time.sleep(25); continue
            if e.code == 403 and ("substack.com" in u or "marksdailyapple.com" in u):
                return get_substack_proxied(u)
            raise

def get_substack_proxied(u):
    """Substack Cloudflare-blocks runner IPs. Free routes, in order:
    allorigins on the RSS feed, r.jina.ai on the archive API, allorigins on the archive API."""
    import time
    archive = u.replace("/feed", "/api/v1/archive?sort=new&offset=0&limit=15")
    def fetch(target, tries=2, timeout=30):
        last = None
        for _ in range(tries):
            try:
                return urllib.request.urlopen(urllib.request.Request(target, headers=HDRS), timeout=timeout).read().decode("utf-8","replace")
            except Exception as ex:
                last = ex; time.sleep(5)
        raise last
    def synth(body):
        from email.utils import format_datetime
        posts, _ = json.JSONDecoder().raw_decode(body[body.index("["):])
        items = []
        for p_ in posts:
            try:
                dt = D.datetime.fromisoformat(p_["post_date"].replace("Z","+00:00"))
                pub = format_datetime(dt)
            except Exception:
                continue
            items.append("<item><title>%s</title><link>%s</link><pubDate>%s</pubDate><description>%s</description></item>" % (
                html.escape(p_.get("title","") or ""), html.escape(p_.get("canonical_url","") or ""),
                pub, html.escape(p_.get("description","") or p_.get("subtitle","") or "")))
        return '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>%s</channel></rss>' % "".join(items)
    try:
        return fetch("https://api.allorigins.win/raw?url=" + urllib.parse.quote(u, safe=""))
    except Exception:
        pass
    try:
        return synth(fetch("https://r.jina.ai/" + archive, timeout=45))
    except Exception:
        pass
    return synth(fetch("https://api.allorigins.win/raw?url=" + urllib.parse.quote(archive, safe="")))

def feedly(u):
    """Feedly reader cache (streams API, no auth, low rate) for sites whose
    Cloudflare blocks datacenter IPs. u = the feed URL Feedly indexes (http)."""
    fid = "feed/" + u
    q = "https://cloud.feedly.com/v3/streams/contents?streamId=" + urllib.parse.quote(fid, safe="") + "&count=15"
    d = json.loads(get(q))
    out=[]
    for it in d.get("items", []):
        try: dt = D.datetime.fromtimestamp((it.get("published") or it.get("crawled"))/1000, D.timezone.utc)
        except Exception: continue
        url = ""
        for a in it.get("alternate") or []:
            if a.get("href"): url = re.sub(r"[?&]utm_[^&]*","",a["href"]).rstrip("?&"); break
        body = ((it.get("summary") or {}).get("content") or (it.get("content") or {}).get("content") or "")
        body = re.sub(r"^\s*<p[^>]*>By\s.*?(?:Comments?|Likes?).*?</p>", "", body, count=1, flags=re.S)
        out.append({"title":clean(it.get("title",""),160),"url":url,"date":iso(dt),"summary":clean(body)})
    if not out: raise RuntimeError("feedly stream empty")
    return out
def felder(u):
    """Felder's RSS descriptions are boilerplate excerpts; pull the first real
    paragraph from each article page instead (weekly pub, so ~10 fetches/run)."""
    items = rss(u)
    for g in items:
        if "most interesting things" not in (g["summary"] or "").lower(): continue
        try:
            h = get(g["url"])
            i = h.find('class="post-content"')
            seg = h[i:i+80000] if i >= 0 else h
            for m in re.finditer(r"<p[^>]*>(.*?)</p>", seg, re.S):
                txt = clean(m.group(1), 400)
                if not txt or txt in ("LINK","STAT","QUOTE","CHART","TWEET"): continue
                if txt.lower().startswith("below are some of the most interesting things"): continue
                g["summary"] = clean(txt)
                break
        except Exception:
            pass
    return items
def wpj(u):
    """WordPress REST posts as feed items. Site WAF blocks some IPs: direct first, r.jina.ai fallback."""
    try:
        body = get(u)
    except urllib.error.HTTPError as e:
        if e.code != 403: raise
        body = get("https://r.jina.ai/" + u)
    posts, _ = json.JSONDecoder().raw_decode(body[body.index("["):])
    out=[]
    for p_ in posts:
        try: dt = D.datetime.fromisoformat(p_["date_gmt"]+"+00:00")
        except Exception: continue
        bh = (p_.get("content") or {}).get("rendered") or (p_.get("excerpt") or {}).get("rendered") or ""
        out.append({"title":clean(p_["title"]["rendered"],160),"url":p_["link"],"date":iso(dt),"summary":clean(bh)})
    return out
def clean(s, n=220):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or "")); s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[:n].rsplit(" ",1)[0] + "…"
def iso(d): return d.astimezone(D.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def rss(u, s_social=False):
    x = get(u)
    x = re.sub(r"&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)([A-Za-z][A-Za-z0-9]*);", lambda m: html.unescape(m.group(0)) if html.unescape(m.group(0))!=m.group(0) else "", x)
    r = ET.fromstring(x); out=[]
    atom = r.tag.endswith("feed")
    ns = "{http://www.w3.org/2005/Atom}"
    entries = r.findall(ns + "entry") if atom else r.iter("item")
    for it in entries:
        if atom:
            d = it.findtext(ns + "published") or it.findtext(ns + "updated")
            try: dt = D.datetime.fromisoformat(d.replace("Z", "+00:00"))
            except Exception: continue
            t = clean(it.findtext(ns + "title"), 300 if s_social else 160)
            body = it.findtext(ns + "content") or it.findtext(ns + "summary") or ""
            url = next((link.get("href") for link in it.findall(ns + "link") if link.get("rel", "alternate") == "alternate"), None)
        else:
            d = it.findtext("pubDate")
            try: dt = parsedate_to_datetime(d)
            except Exception:
                try: dt = D.datetime.fromisoformat(d.replace("Z","+00:00"))
                except Exception: continue
            t = clean(it.findtext("title"), 300 if s_social else 160)
            body = it.findtext("{http://purl.org/rss/1.0/modules/content/}encoded") or it.findtext("description") or ""
            url = it.findtext("link")
        if t.startswith("Quote post") or not t: t = clean(body, 300) or t
        out.append({"title":t,"url":url,"date":iso(dt),"summary":"" if s_social else clean(body)})
    return out
def oembed_text(u):
    try:
        d = json.loads(get("https://publish.twitter.com/oembed?url=" + u))
        p = re.search(r"<p[^>]*>(.*?)</p>", d.get("html",""), re.S)
        if not p: return ""
        t = re.sub(r"<[^>]+>", " ", p.group(1))
        t = re.sub(r"https?://t\.co/\w+|pic\.twitter\.com/\w+", " ", t)
        return clean(t, 400)
    except Exception:
        return ""
def translate(t, sl="ru", tl="en"):
    """Free Google MT: Chrome-extension endpoint first, gtx fallback.
    Returns the original text if both fail."""
    if not t: return t
    q = urllib.parse.quote(t[:1500])
    for u in ("https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl=%s&tl=%s&q=%s" % (sl, tl, q),
              "https://translate.googleapis.com/translate_a/single?client=gtx&sl=%s&tl=%s&dt=t&q=%s" % (sl, tl, q)):
        try:
            d = json.loads(get(u))
            if isinstance(d, list) and d:
                if isinstance(d[0], str) and d[0].strip(): return d[0]
                if isinstance(d[0], list):
                    out = "".join(seg[0] for seg in d[0] if seg and seg[0])
                    if out.strip(): return out
        except Exception:
            pass
    return t
def tg(ch):
    h = get(f"https://t.me/s/{ch}"); out=[]
    for blk in h.split('tgme_widget_message_wrap')[1:]:
        m = re.search(r'href="(https://t\.me/[^"]+/\d+)[^"]*"[^>]*>\s*<time[^>]*datetime="([^"]+)"', blk)
        tx = re.search(r'tgme_widget_message_text[^>]*>(.*?)</div>', blk, re.S)
        if not m: continue
        raw = tx.group(1) if tx else ""
        text = clean(raw or "(media post)", 400)
        url = m.group(1)
        xl = re.search(r'href="(https?://(?:x|twitter)\.com/[^"]+/status/\d+)[^"]*"', raw)
        if xl:
            url = xl.group(1)
            pv = re.search(r'link_preview_description[^>]*>(.*?)</div>', blk, re.S)
            if pv:
                text = clean(pv.group(1), 400)
            elif text.startswith(("https://x.com","https://twitter.com")):
                text = oembed_text(url) or "New post on X"
        out.append({"title":clean(text,300),"url":url,"date":iso(D.datetime.fromisoformat(m.group(2))),"summary":""})
    return out
def xsyn(user):
    h = get(f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{user}")
    d = json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', h, re.S).group(1))
    out=[]
    for e in d["props"]["pageProps"]["timeline"]["entries"]:
        t = e.get("content",{}).get("tweet")
        if not t: continue
        dt = D.datetime.strptime(t["created_at"], "%a %b %d %H:%M:%S +0000 %Y").replace(tzinfo=D.timezone.utc)
        txt = clean(re.sub(r"https://t\.co/\w+","",t["full_text"]), 400)
        out.append({"title":clean(txt,300),"url":"https://x.com/%s/status/%s"%(user,t["id_str"]),"date":iso(dt),"summary":""})
    return out
def treasury():
    h = get("https://home.treasury.gov/news/press-releases"); out=[]
    for m in re.finditer(r'<time datetime=([\dTZ:-]+)[^>]*>.*?<a href=(/news/press-releases/[^ >]+)[^>]*>(.*?)</a>', h, re.S):
        out.append({"title":clean(m.group(3),160),"url":"https://home.treasury.gov"+m.group(2),"date":m.group(1),"summary":""})
    return out
SOURCES_VF = [
 {"id":"mda","name":"Mark's Daily Apple","topic":"Primal","type":"rss","arg":"https://www.marksdailyapple.com/feed"},
 {"id":"ferriss","name":"Tim Ferriss","topic":"Performance","type":"rss","arg":"https://tim.blog/feed/"},
 {"id":"paleo","name":"The Paleo Diet","topic":"Paleo","type":"rss","arg":"https://www.thepaleodiet.com/feed/"},
 {"id":"dietdoctor","name":"Diet Doctor","topic":"Low carb","type":"rss","arg":"https://www.dietdoctor.com/feed"},
 {"id":"attia","name":"Peter Attia","topic":"Longevity","type":"rss","arg":"https://peterattiamd.com/feed/"},
 {"id":"blueprint","name":"Blueprint (Bryan Johnson)","topic":"Longevity","type":"rss","arg":"https://blueprint.bryanjohnson.com/blogs/news.atom"},
]
if os.environ.get("VF")=="1" or (len(sys.argv)>2 and sys.argv[2]=="vf"): SOURCES = SOURCES_VF

def rdf(u):
    """RSS 1.0 (RDF) feeds: namespaced items with dc:date. Titles only."""
    x = get(u)
    r = ET.fromstring(x); out = []
    R = "{http://purl.org/rss/1.0/}"; DC = "{http://purl.org/dc/elements/1.1/}"
    for it in r.iter(R + "item"):
        d = it.findtext(DC + "date")
        try: dt = D.datetime.fromisoformat(d.replace("Z", "+00:00"))
        except Exception: continue
        t = clean(it.findtext(R + "title"), 160)
        url = it.findtext(R + "link") or it.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about")
        if not t: continue
        out.append({"title": t, "url": url, "date": iso(dt), "summary": ""})
    return out
def afc(u):
    """Asia Frontier Capital monthly newsletters: scrape the year index pages
    (/YYYY.html) for issue links; issues are HTML pages, no PDFs exist."""
    out = []
    now = D.datetime.now(D.timezone.utc)
    years = [now.year] + ([now.year - 1] if now.month == 1 else [])
    for y in years:
        try: h = get("%s/%d.html" % (u, y))
        except Exception: continue
        for m in re.finditer(r'<a[^>]+href="(/newsletter-\d{4}/[^"]+\.html)"[^>]*>\s*(Newsletter Issue[^<]+?)\s*</a>', h, re.I):
            url, t = m.group(1), clean(m.group(2), 120)
            mm = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})', t)
            if not mm: continue
            dt = D.datetime.strptime("%s %s" % (mm.group(1), mm.group(2)), "%B %Y").replace(tzinfo=D.timezone.utc)
            out.append({"title": t, "url": u + url, "date": iso(dt), "summary": ""})
    return out
FN = {"rss":rss,"felder":felder,"feedly":feedly,"rsssocial":lambda u:rss(u,True),"tg":tg,"xsyn":xsyn,"wpj":wpj,"rdf":rdf,"afc":afc}
try: prev=json.load(open(sys.argv[1] if len(sys.argv)>1 else "feeds.json"))
except Exception: prev={"items":[]}
res=[]; items=[]; now=D.datetime.now(D.timezone.utc)
def noisy(t):
    t = (t or "").strip()
    if len(t) < 20: return True
    if t.startswith(("RT http","RT: http","Quote post","(media post)")): return True
    if re.match(r"^(Video|Image) post from", t): return True
    if re.fullmatch(r"https?://\S+", t): return True
    return False
FILTER = {"rattletrap","medvedev","dmitriev"}
# Tom 2026-10-17: /feeds shows proper text only - strip raw links and emoji
# from visible titles/previews for every source (no source should go empty).
LINK_RE = re.compile(r"https?://\S+|t\.me/\S+", re.I)
EMOJI_RE = re.compile("[\U0001F300-\U0001F64F\U0001F680-\U0001F6FF\U0001F900-\U0001FAFF\u2600-\u26FF\u2700-\u27BF\u203C\u2049\uFE0F\u200D\u20E3]")
def strip_noise(s):
    s = LINK_RE.sub(" ", s or "")
    s = EMOJI_RE.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()
# RattleTrap includes Telegram service notices alongside its actual posts.
# Keep this narrowly scoped to livestream lifecycle/announcement titles.
RATTLETRAP_NOTICE = re.compile(
    r"^(?:"
    r"(?:(?:the|a|my|our)\s+)?(?:live[\s-]?stream|livestream|stream|broadcast|voice chat)\s+(?:(?:has|is|was)\s+(?:been\s+)?)?(?:started|finished|ended|stopped|starting|over|scheduled|will start|starts|going live|live|cancelled|canceled)\b"
    r"|(?:[\w .'-]{1,60}\s+)?(?:has\s+)?(?:started|finished|ended|stopped)\s+(?:a\s+)?(?:live[\s-]?stream|livestream|stream|broadcast)\b"
    r"|(?:we are|we're|i am|i'm)\s+(?:going live|live now|live)\b"
    r"|(?:going live|live now|now live|streaming now|starting (?:a )?(?:live )?stream)\b"
    r"|(?:join|watch|tune in to)\s+(?:the\s+)?(?:live[\s-]?stream|livestream|stream|broadcast)\b"
    r"|derek johnson\s+(?:is going live|went live|is live now)\b"
    r")(?:\b|$).*$",
    re.I,
)
TRANSLATE_RU = {"medvedev","dmitriev"}
TRANSLATE_PL = {"pafere"}
DESCS = {'debriefing': 'Telegram commentary on markets and geopolitics; filtered to economics and finance.', 'rattletrap': "Derek Johnson's Telegram channel, arguing from military and constitutional documents that Trump remains commander-in-chief.", 'bioclandestine': 'Anonymous Telegram commentator on US politics, Ukraine, and bioweapon programs; pro-Trump, anti-establishment lean.', 'americancompass': 'Conservative think tank for post-free-market economics: industrial policy, labor, and finance reform.', 'dmitriev': "Head of the Russian Direct Investment Fund and Putin's deal negotiator; Telegram posts machine-translated to English.", 'pafere': 'Polish free-market think tank; Krzysztof Szczawinski\'s essays on economics and communism, machine-translated to English.', 'bowtiedmara': 'Anonymous Substack on Argentina and Latin America: macro, politics, and Buenos Aires real estate; libertarian, pro-Milei lean.', 'aasecon': 'Austrian-style adjusted money supply and global macro analysis.', 'oldeconomy': 'Deep value and old-economy sectors: shipping cycles, commodities, and energy.', 'eugyppius': 'Anonymous German academic; long-form analysis of German and EU politics and the Ukraine war.', 'lacalle': 'Spanish Austrian-school economist and fund manager on central banks, sovereign debt, and energy.', 'simplicius': 'Anonymous long-form Substack on the Russia-Ukraine war and geopolitics; pro-Russian perspective.', 'jcpa': 'Jerusalem Center for Public Affairs; Israeli security and diplomacy analysis from a hawkish perspective.', 'brandao': 'China geopolitics and political economy, hawkish on the CCP. Paywalled posts show free teasers.', 'jinf': 'Japan Institute for National Fundamentals; conservative Japanese think tank on security, history, and the constitution.', 'taipeitimes': "Taiwan's main English-language daily, pro-independence editorial lean; filtered to NTFB topics.", 'rpsmith': 'Monitors Russian and global oil & gas: production, exports, sanctions, and shadow fleets.', 'sonar21': 'Former CIA analyst; daily commentary on the Russia-Ukraine war and US foreign policy, sharply critical of Western policy.', 'ritter': 'Former UN weapons inspector and Marine intelligence officer on the war and US-Russia relations; critical of NATO. Paywalled posts dropped.', 'afc': 'Fund manager focused on Asian frontier markets; free monthly newsletters.', 'yurta': 'Telegram channel on markets and investing.', 'acqmult': "Tobias Carlisle's deep value investing site: funds, podcast, and books.", 'aier': 'American Institute for Economic Research; free-market and Austrian-school economics commentary.', 'stonge': 'Economist writing daily on markets, inflation, and the Fed from an Austrian perspective.', 'shirk': 'Newsletter on private deals, resource stocks, and frontier markets.', 'lorenz': 'Deep value and special situations newsletter; long-form and contrarian.', 'attila': 'Markets and energy Substack; filtered to NTFB topics, personal essays dropped.', 'frontierviking': 'Substack on frontier and emerging market investing.', 'timprice': 'UK value fund manager at Price Value Partners; weekly market and macro commentaries.', 'riskhedge': 'Investment research newsletter on growth, technology, and disruption themes.', 'felder': "Jesse Felder's contrarian macro and market analysis; valuation-focused with a bearish lean.", 'armstrong': "Martin Armstrong's public posts on markets, cycles, and geopolitics; private blog posts excluded.", 'alhajji': 'Energy economist covering oil markets, OPEC, and energy geopolitics.', 'crude': 'Historic perspectives on the oil industry and markets.', 'gr': 'Natural resource investment firm; deeply researched quarterly commodity letters, bullish on real assets.', 'bison': 'Oil & gas equity investor; public posts on E&P stocks and energy macro.', 'gcaptain': 'Maritime news site; filtered to oil, freight, and shipping.', 'superspiked': 'Arjun Murti, former Goldman Sachs oil analyst; weekly energy macro commentary.', 'igwt': "Ronald-Peter Stoeferle's annual In Gold We Trust report with Mark Valek.", 'gata': 'Gold Anti-Trust Action Committee; documented record of precious-metals market manipulation.', 'pig': "Charles Vollum's market prices measured in gold.", 'monetarymetals': "Keith Weiner's firm and research on yield paid in gold.", 'tfm': "Turd Ferguson's metals and macro commentary."}
PROMO = {"dietdoctor": re.compile(r"\bmember benefit\b|sign up for diet doctor plus|\bfree trial\b", re.I)}
KEYWORDS = {"debriefing": re.compile(r"econom|financ|\brails?\b|railroad|\btrad(?:e|es|ing|er|ers)\b|\bdebts?\b|\bbank|\bfund(?:s|ed|ing)?\b|\bfed\b|federal reserve|treasury|dollar|tariff|sanction|sovereign wealth|\boil\b|energy|\bgold\b|inflation|\brates?\b|credit|currenc|\bmarkets?\b|shipping|\bports?\b|supply chain|\biran|china|chinese|bessent", re.I), "attila": re.compile(r"\besg\b|fossil|energy|\bgold\b|\boil\b|bubble|\bdebt|crisis|\bcredit|value invest|economic|profit|valuing|inflation|monetary|\bprices?\b|financ|depression|commodit|uranium|\bmining|interest rate|\bfed\b|central bank|dollar|currenc|\btrade\b|stock market|\bmarkets?\b", re.I), "gcaptain": re.compile(r"oil|crude|tanker|lng|lpg|fuel|bunker|sanction|freight|hormuz|trade|tariff|shipping rate|charter|opec|energy|gas\b|pipeline|refiner|red sea|suez|panama canal|shadow fleet", re.I), "taipeitimes": re.compile(r"trade|tariff|econom|energy|nuclear|\boil\b|\bgas\b|\bgold\b|chip|tsmc|semiconductor|export|import|fiscal|\bfed\b|monetary|central bank|interest rate|inflation|defen[cs]e|military|\barms\b|sanction|supply chain|china|beijing|rare earth|dollar|yuan|currenc|shipping|strait|export control|\bai\b", re.I),}
for s in SOURCES:
    try:
        if s["type"]=="combo":
            got = treasury()
        elif s["type"]=="treasury":
            got = treasury()
        else:
            got = FN[s["type"]](s["arg"])
        if s["id"] in FILTER: got = [g for g in got if not noisy(g["title"])]
        if s["id"] == "rattletrap": got = [g for g in got if not RATTLETRAP_NOTICE.search(g["title"])]
        seen=set(); ded=[]
        for g in sorted(got, key=lambda x:x["date"], reverse=True):
            k = g["url"] or g["title"][:80]
            if k in seen: continue
            seen.add(k); ded.append(g)
        if s["id"]=="ferriss": ded = [g for g in ded if "transcript" not in g["title"].lower()]
        if s["id"]=="bowtiedmara":
            for g in ded: g["summary"]=re.sub(r"^Welcome(?: back)? [^!]{1,40}!\s*", "", g["summary"] or "")
        if s["id"]=="armstrong": ded = [g for g in ded if not g["title"].startswith("PRIVATE BLOG")]
        if s["id"]=="debriefing": ded = [g for g in ded if len((g["title"] or "").strip())>=60]
        if s["id"]=="attila": ded = [g for g in ded if not re.search(r"personal essay|balzac|self-help|\bmiser\b|roman emperor|\bluck\b", g["title"]+" "+g["summary"], re.I)]
        if s["id"]=="ritter":
            for g in ded: g["summary"]=re.sub(r"\s*Donat\w*\s*Real Scott Ritter is a reader-supported.*$", "", g["summary"], flags=re.S)
            ded = [g for g in ded if (g["summary"] or "").strip()]
        if s["id"]=="kremlin": ded = [g for g in ded if not re.search(r"birthday greetings|^greetings\b|^congratulations\b|^condolences\b|awarded honorary|welcome address", g["title"], re.I)]
        if s["id"]=="medvedev": ded = [g for g in ded if len((g["title"] or "").strip())>=80]
        if s["id"] in KEYWORDS: ded = [g for g in ded if KEYWORDS[s["id"]].search(g["title"]+" "+re.sub(r"Subscribe free and.*$","",g["summary"],flags=re.S))]
        if s["id"] in PROMO: ded = [g for g in ded if not PROMO[s["id"]].search(g["title"]+" "+g["summary"])]
        got = ded[:PER_SOURCE]
        tr_lang = "ru" if s["id"] in TRANSLATE_RU else ("pl" if s["id"] in TRANSLATE_PL else None)
        if tr_lang:
            pmap = {i["url"]: i for i in prev["items"] if i.get("source")==s["id"]}
            for g in got:
                old = pmap.get(g["url"])
                if old and old.get("ru")==g["title"]:
                    g["title"] = old["title"]
                else:
                    g["ru"] = g["title"]
                    g["title"] = clean(translate(g["title"], tr_lang), 300)
                if g.get("summary"):
                    if old and old.get("ru_sum")==g["summary"]:
                        g["summary"] = old.get("summary", g["summary"])
                    else:
                        g["ru_sum"] = g["summary"]
                        g["summary"] = clean(translate(g["summary"], tr_lang), 400)
        for g in got:
            g["title"] = strip_noise(g["title"])
            g["summary"] = strip_noise(g["summary"])
        got = [g for g in got if g["title"]]
        for g in got: g.update(source=s["id"])
        items += got
        res.append({**{k:s[k] for k in("id","name","topic")},"desc":DESCS.get(s["id"],""),"ok":True,"count":len(got),"latest":got[0]["date"] if got else None})
    except Exception as ex:
        print("FAIL",s["id"],ex,file=sys.stderr)
        old=[i for i in prev["items"] if i["source"]==s["id"]]
        for g in old:
            g["title"] = strip_noise(g.get("title",""))
            g["summary"] = strip_noise(g.get("summary",""))
        old = [g for g in old if g["title"]]
        if s["id"] in PROMO: old = [i for i in old if not PROMO[s["id"]].search(i.get("title","")+" "+i.get("summary",""))]
        items+=old
        res.append({**{k:s[k] for k in("id","name","topic")},"desc":DESCS.get(s["id"],""),"ok":False,"count":len(old),"latest":old[0]["date"] if old else None,"error":str(ex)[:120]})
items.sort(key=lambda x:x["date"], reverse=True)
json.dump({"generated":iso(now),"sources":res,"items":items}, open(sys.argv[1] if len(sys.argv)>1 else "feeds.json","w"), ensure_ascii=False, separators=(",",":"))
print(len(items),"items;", sum(r["ok"] for r in res),"/",len(res),"sources ok")

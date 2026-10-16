#!/usr/bin/env python3
"""Hourly feed aggregator. Writes feeds.json (stdlib only)."""
import json, re, html, sys, urllib.request, urllib.parse, datetime as D, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
HDRS = {"User-Agent":UA, "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language":"en-US,en;q=0.9"}
PER_SOURCE = 15
SOURCES = [
 {"id":"debriefing","name":"The Debriefing (Telegram)","topic":"Politics","type":"tg","arg":"Castlerock2021"},
 {"id":"bessent-x","name":"Scott Bessent (X)","topic":"Treasury","type":"xsyn","arg":"SecScottBessent"},
 {"id":"treasury","name":"US Treasury press releases","topic":"Treasury","type":"treasury"},
 {"id":"rattletrap","name":"RattleTrap 1776 (Telegram)","topic":"Politics","type":"tg","arg":"rattletrap1776"},
 {"id":"bioclandestine","name":"BioClandestine (Telegram)","topic":"Politics","type":"tg","arg":"bioclandestine"},
 {"id":"yurta","name":"Yurta Capital (Telegram)","topic":"Markets","type":"tg","arg":"yurta06"},
 {"id":"trump","name":"Trump (Truth Social mirror)","topic":"Politics","type":"rsssocial","arg":"https://trumpstruth.org/feed"},
 {"id":"crude","name":"The Crude Chronicles","topic":"Energy","type":"rss","arg":"https://thecrudechronicles.substack.com/feed"},
 {"id":"gr","name":"Goehring & Rozencwajg","topic":"Energy","type":"rss","arg":"https://blog.gorozen.com/blog/rss.xml"},
 {"id":"bison","name":"Josh Young - Bison Insights","topic":"Energy","type":"rss","arg":"https://bisoninterests.substack.com/feed"},
 {"id":"emedia","name":"eMedia Press","topic":"Newsletters","type":"rss","arg":"https://emediapress.com/feed"},
 {"id":"igwt","name":"In Gold We Trust","topic":"Gold","type":"rss","arg":"https://www.incrementum.li/feed/"},
 {"id":"gata","name":"GATA","topic":"Gold","type":"rss","arg":"https://www.gata.org/rss.xml"},
 {"id":"acqmult","name":"Acquirer's Multiple","topic":"Markets","type":"rss","arg":"https://acquirersmultiple.com/feed/"},
 {"id":"pig","name":"Priced in Gold","topic":"Gold","type":"rss","arg":"https://pricedingold.com/feed"},
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
            if e.code == 403 and "substack.com" in u:
                p = "https://api.allorigins.win/raw?url=" + urllib.parse.quote(u, safe="")
                return urllib.request.urlopen(urllib.request.Request(p, headers=HDRS), timeout=30).read().decode("utf-8","replace")
            raise
def clean(s, n=220):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or "")); s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[:n].rsplit(" ",1)[0] + "…"
def iso(d): return d.astimezone(D.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def rss(u, s_social=False):
    r = ET.fromstring(get(u)); out=[]
    for it in r.iter("item"):
        d = it.findtext("pubDate")
        try: dt = parsedate_to_datetime(d)
        except Exception: continue
        t = clean(it.findtext("title"), 300 if s_social else 160)
        body = it.findtext("{http://purl.org/rss/1.0/modules/content/}encoded") or it.findtext("description") or ""
        if t.startswith("Quote post") or not t: t = clean(body, 300) or t
        out.append({"title":t,"url":it.findtext("link"),"date":iso(dt),"summary":"" if s_social else clean(body)})
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
FN = {"rss":rss,"rsssocial":lambda u:rss(u,True),"tg":tg,"xsyn":xsyn}
try: prev=json.load(open(sys.argv[1] if len(sys.argv)>1 else "feeds.json"))
except Exception: prev={"items":[]}
res=[]; items=[]; now=D.datetime.now(D.timezone.utc)
for s in SOURCES:
    try:
        got = treasury() if s["type"]=="treasury" else FN[s["type"]](s["arg"])
        got = sorted(got, key=lambda x:x["date"], reverse=True)[:PER_SOURCE]
        for g in got: g.update(source=s["id"])
        items += got
        res.append({**{k:s[k] for k in("id","name","topic")},"ok":True,"count":len(got),"latest":got[0]["date"] if got else None})
    except Exception as ex:
        print("FAIL",s["id"],ex,file=sys.stderr)
        old=[i for i in prev["items"] if i["source"]==s["id"]]; items+=old
        res.append({**{k:s[k] for k in("id","name","topic")},"ok":False,"count":len(old),"latest":old[0]["date"] if old else None,"error":str(ex)[:120]})
items.sort(key=lambda x:x["date"], reverse=True)
json.dump({"generated":iso(now),"sources":res,"items":items}, open(sys.argv[1] if len(sys.argv)>1 else "feeds.json","w"), ensure_ascii=False, separators=(",",":"))
print(len(items),"items;", sum(r["ok"] for r in res),"/",len(res),"sources ok")

#!/usr/bin/env python3
"""Post new NTFB items to the Telegram channel @notimeforbull00.

Sources:
1. Ghost RSS (https://notimeforbull.com/rss/) - new blog posts, auto.
2. telegram_queue.json - manually queued items (e.g. final X-post texts).

State (telegram_state.json) tracks posted RSS guids and drained queue ids.
Secrets via env: TG_BOT_TOKEN. Channel: TG_CHANNEL (default @notimeforbull00).
"""
import json, os, re, html, urllib.request, urllib.parse, xml.etree.ElementTree as ET

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_PATH = os.path.join(REPO_DIR, "telegram_state.json")
QUEUE_PATH = os.path.join(REPO_DIR, "telegram_queue.json")
RSS_URL = "https://notimeforbull.com/rss/"
TOKEN = os.environ["TG_BOT_TOKEN"]
CHANNEL = os.environ.get("TG_CHANNEL", "@notimeforbull00")

def load_json(path, default):
    try:
        with open(path) as f: return json.load(f)
    except Exception: return default

def tg_send(text):
    data = urllib.parse.urlencode({
        "chat_id": CHANNEL, "text": text,
        "parse_mode": "HTML", "disable_web_page_preview": "false",
    }).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data=data)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def clean_preview(raw, limit=200):
    t = re.sub(r"<[^>]+>", " ", raw or "")
    t = html.unescape(re.sub(r"\s+", " ", t)).strip()
    return (t[:limit].rsplit(" ", 1)[0] + "...") if len(t) > limit else t

def format_post(title, preview, link):
    parts = [f"<b>{html.escape(title)}</b>"]
    if preview: parts.append(html.escape(preview))
    if link: parts.append(link)
    return "\n\n".join(parts)

state = load_json(STATE_PATH, {"posted_guids": [], "drained_ids": []})
queue = load_json(QUEUE_PATH, [])
changed = False

# 1) RSS items
try:
    with urllib.request.urlopen(urllib.request.Request(RSS_URL, headers={"User-Agent": "ntfb-tg-bot"}), timeout=30) as r:
        root = ET.fromstring(r.read())
    items = root.findall(".//item")
    for it in reversed(items):  # oldest first
        guid = (it.findtext("guid") or it.findtext("link") or "").strip()
        if not guid or guid in state["posted_guids"]: continue
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        preview = clean_preview(it.findtext("description"))
        tg_send(format_post(title, preview, link))
        state["posted_guids"].append(guid)
        changed = True
except Exception as e:
    print(f"RSS fetch/post failed (fail-soft): {e}")

# 2) Manual queue (X posts etc.) - entries: {"id": str, "text": str}
remaining = []
for q in queue:
    qid = str(q.get("id", ""))
    if qid in state["drained_ids"]: continue
    try:
        tg_send(q["text"] if q.get("raw") else format_post(q.get("title", ""), q.get("preview", ""), q.get("link", "")))
        state["drained_ids"].append(qid)
        changed = True
    except Exception as e:
        print(f"Queue item {qid} failed: {e}")
        remaining.append(q)

state["posted_guids"] = state["posted_guids"][-500:]
state["drained_ids"] = state["drained_ids"][-500:]
if changed:
    with open(STATE_PATH, "w") as f: json.dump(state, f, indent=1)
    with open(QUEUE_PATH, "w") as f: json.dump(remaining, f, indent=1)
print("done, changed:", changed)

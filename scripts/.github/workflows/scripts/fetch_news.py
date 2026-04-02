#!/usr/bin/env python3
import os, re, sys
from datetime import datetime, timezone, timedelta
from html import unescape
import feedparser, requests

JST = timezone(timedelta(hours=9))
NOW = datetime.now(JST)
SINCE = NOW - timedelta(hours=24)
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

FEEDS = {
    "🇺🇸 US": [
        ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
        ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
        ("The Verge AI", "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"),
    ],
    "🇨🇳 中国": [
        ("量子位", "https://www.qbitai.com/feed"),
        ("机器之心", "https://www.jiqizhixin.com/rss"),
        ("新智元", "https://www.zhidx.com/feed"),
    ],
    "🇯🇵 日本": [
        ("ITmedia AI+", "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml"),
        ("Gigazine", "https://gigazine.net/news/rss_2.0/"),
        ("ASCII.jp AI", "https://ascii.jp/rss.xml"),
    ],
}

AI_KEYWORDS = ["AI","人工知能","人工智能","ChatGPT","GPT","LLM","生成AI","生成式",
               "机器学习","深度学习","機械学習","neural","machine learning","generative",
               "Gemini","Claude","OpenAI","Anthropic","DeepMind","Llama","Grok"]
AI_SPECIFIC = {"VentureBeat AI","TechCrunch AI","The Verge AI","量子位","机器之心","新智元","ITmedia AI+"}

def clean_html(t):
    return unescape(re.sub(r"<[^>]+>", "", t or "")).strip()

def is_recent(e):
    p = e.get("published_parsed") or e.get("updated_parsed")
    if not p: return True
    return datetime(*p[:6], tzinfo=timezone.utc) >= SINCE.astimezone(timezone.utc)

def is_ai(e, src):
    if src in AI_SPECIFIC: return True
    return any(k.lower() in (e.get("title","")+" "+e.get("summary","")).lower() for k in AI_KEYWORDS)

def fetch_region(region, feeds):
    items = []
    for src, url in feeds:
        if len(items) >= 6: break
        try:
            for e in feedparser.parse(url, request_headers={"User-Agent":"Mozilla/5.0"}).entries[:15]:
                if is_recent(e) and is_ai(e, src):
                    t, l = clean_html(e.get("title","")), e.get("link","")
                    if t and l:
                        items.append(f"• [{t}]({l})  `{src}`")
                        break
        except Exception as ex:
            print(f"[WARN] {src}: {ex}", file=sys.stderr)
    return items

def main():
    if not DISCORD_WEBHOOK_URL:
        print("ERROR: DISCORD_WEBHOOK_URL not set", file=sys.stderr); sys.exit(1)
    results = {r: fetch_region(r, f) for r, f in FEEDS.items()}
    today = NOW.strftime("%Y年%m月%d日")
    embeds = [{"title": r, "description": "\n".join(i) or "_新着なし_",
               "color": {"🇺🇸 US":0x3498DB,"🇨🇳 中国":0xE74C3C,"🇯🇵 日本":0x2ECC71}.get(r,0x95A5A6)}
              for r, i in results.items()]
    resp = requests.post(DISCORD_WEBHOOK_URL,
                         json={"content":f"## 🤖 AI ニュースダイジェスト — {today}",
                               "embeds":embeds,"username":"AI News Bot"}, timeout=15)
    resp.raise_for_status()
    print(f"Posted (HTTP {resp.status_code})")

if __name__ == "__main__":
    main()

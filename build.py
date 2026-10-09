"""Portfolio site for noppruts (นพรุจ). python build.py -> dist/ ; deploy with products/shop-tools/fee-reader/deploy.py.

Portfolio (English) is built from facts read in the author's own project READMEs/docstrings. No invented metrics, clients,
credentials or reviews. Product pages (Thai) target Thai sellers' search queries.
Optional config.json: {"base": "...", "contact": [{"label": "Facebook", "url": "https://..."}], "sameAs": ["https://..."]}
"""
import base64
import html
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

H = Path(__file__).resolve().parent
ROOT = H.parents[1]
cfg = {"base": "https://nopprut.pages.dev", "contact": [], "sameAs": [], "email": ""}
if (H / "config.json").exists():
    cfg.update(json.loads((H / "config.json").read_text(encoding="utf-8")))
BASE = cfg["base"].rstrip("/")
TODAY = date.today().isoformat()
HANDLE, THAI = "noppruts", "นพรุจ"
FREE_TOOL = "https://fee-reader-free.pages.dev/"
SRC = "https://flowaccount.com/blog/commission-fees-ecommerce-shopee-lazada-tiktok/"
OUT = H / "dist"
(OUT / "assets").mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------ data (all from the author's own folders)
FEATURED = [
    dict(cat="geo", title="SAR Crop-Damage Verification", sub="Parcel-level flood & crop damage from free satellite radar",
         body="Turns open Sentinel-1 SAR imagery into per-plot flood and crop-damage estimates for Thai rice insurers and lenders. "
              "A rice-transplanting mask avoids flagging normal wet paddy as damage, and every result carries scene IDs, software versions, "
              "parameters and a confidence score so it can be defended in a claims dispute. Flood/damage module implemented; crop and carbon modules are interfaces for later.",
         tags=["Python", "Sentinel-1 SAR", "PostGIS", "Zarr", "Docker"]),
    dict(cat="auto", title="AI Content Factory (n8n + Python)", sub="Idea → finished 9:16 video, with a human gate before publishing",
         body="n8n decides what to make and when (scheduling, topic selection, approval routing, analytics); a Python video factory turns a topic into a subtitled "
              "vertical video (script, video generation, TTS, FFmpeg) behind a local HTTP API with a restart-safe state machine. Nothing publishes without explicit approval.",
         tags=["n8n", "Python", "FFmpeg", "TTS", "Facebook Graph API"]),
    dict(cat="agents", title="LINE AI Assistant for a Repair Shop", sub="Diagnosis help for staff, service reminders for customers",
         body="One LINE Official Account serving two audiences: staff send fault codes or symptoms for an AI diagnosis and log completed jobs; customers link their LINE to their phone "
              "number and receive a reminder when the ~6-month service is due. A daily scheduler inside the same process pushes the reminders.",
         tags=["Python", "LINE Messaging API", "APScheduler", "Flex Messages", "LLM"]),
    dict(cat="agents", title="Agent Invest", sub="Multi-agent investment monitoring (private)",
         body="Full-stack system: FastAPI backend and Next.js dashboard where several AI agents analyse symbols, store predictions and compare them with later prices to track accuracy per "
              "timeframe. Builds daily reports and talks to users through a Telegram bot by command or natural language.",
         tags=["FastAPI", "Next.js", "Telegram Bot", "Docker", "LLM agents"]),
]
MORE = [
    dict(cat="agents", title="Test-Eng Assist", body="Autonomous local CLI agent for test engineers: an agent loop that calls tools, plus ingestion, RAG, scheduler and a dashboard; packaged as an executable.", tags=["Python", "Typer", "RAG"]),
    dict(cat="agents", title="Autonomous Agent Loop", body="Plan → split into sub-tasks → call tools → verify → repeat until done, with a multi-agent orchestrator and a sandboxed workspace.", tags=["Python", "Multi-agent"]),
    dict(cat="agents", title="Windows Computer-Control Agent", body="ReAct loop: capture the screen, ask a vision-language model for the next action, run it through GUI/shell tools, observe, repeat until the goal is met.", tags=["Python", "VLM", "Automation"]),
    dict(cat="auto", title="News Pipeline with Telegram Approval", body="Runs three times a day on Bangkok time and routes each item through a Telegram bot for human approval before it goes out.", tags=["Python", "Telegram", "Scheduler"]),
    dict(cat="auto", title="LINE Slip-OCR Assistant", body="Photo of a trade slip → Thai+English OCR → Flex confirmation card → tax calculation → logged to an Excel workbook that doubles as the database.", tags=["Python", "EasyOCR", "LINE", "Excel"]),
    dict(cat="auto", title="Shop Automation Pack (n8n)", body="Two importable n8n workflows for small online shops: a daily sales summary and a new-order alert with validation. Run end-to-end on a local n8n instance with test data.", tags=["n8n", "Telegram", "Google Sheets"]),
    dict(cat="quant", title="Thai Stock Monitor", body="Watches SET/mai stocks, generates signals from price and indicator thresholds, simulates trades in a paper portfolio, alerts via Telegram/LINE, Next.js dashboard. Live execution deliberately not implemented.", tags=["Python", "Next.js", "yfinance"]),
    dict(cat="quant", title="Quant Signal Engine", body="Market data and news sentiment (FinBERT/VADER) combined with EMA, RSI, ATR and Kelly sizing to output signals with dynamic stop-loss and take-profit levels.", tags=["Python", "NLP", "Quant math"]),
    dict(cat="quant", title="Algorithmic Trading Research (private)", body="Research workflow built around a written edge standard: net-of-cost expectancy, out-of-sample tests, sample-size minimums and regime analysis. Findings are not published.", tags=["Python", "Backtesting", "HMM regimes"]),
    dict(cat="create", title="Character IP Studio", body="An orange-cat character and supporting cast turned into LINE sticker, emoji and theme packs, short animated films and wallpapers. Films come from a deterministic frame-accurate HTML engine rendered with Playwright and FFmpeg, with synthesised audio normalised to -14 LUFS.", tags=["Playwright", "FFmpeg", "NumPy", "LINE Creators"]),
    dict(cat="create", title="1-Minute Product Clip Generator", body="A product JSON and photo become a vertical clip with Thai voice-over in about a minute, without rendering a browser page per frame.", tags=["Python", "Pillow", "edge-tts", "FFmpeg"]),
    dict(cat="tools", title="Shop Fee Reader (live)", body="Mobile web tool that shows where each baht of a Shopee, TikTok Shop or Lazada sale goes, break-even price and break-even ROAS. All data stays in the browser. Free and paid editions are deployed on Cloudflare Pages.", tags=["JavaScript", "Cloudflare Pages"], link=(FREE_TOOL, "Try it")),
    dict(cat="tools", title="Stock & Sales Spreadsheet", body="Excel workbook for small shops with SUMIFS/INDEX-MATCH dashboards, low-stock alerts and charts. Every dashboard value was checked against an independent Python calculation.", tags=["Excel", "openpyxl"]),
    dict(cat="security", title="AppSec Testing & Remediation (OWASP Juice Shop)",
         body="Found and documented 3 real vulnerabilities (SQL injection auth bypass, IDOR, SQL injection + info disclosure) in a locally-run copy of OWASP's own intentionally-vulnerable training app, then patched the vulnerable code and re-verified against the original requests that the fixes held while legitimate use kept working. Full requests/responses and the code diff are in the reports.",
         tags=["AppSec", "SQL Injection", "Access Control", "Node.js/TypeScript"],
         links=[("/security/report-1-juice-shop.pdf", "Findings (PDF)"), ("/security/report-2-remediation.pdf", "Remediation (PDF)")]),
]
FILTERS = [("all", "All"), ("agents", "AI agents"), ("auto", "Automation"), ("geo", "Geospatial"), ("quant", "Quant"), ("create", "Creative"), ("tools", "Tools"), ("security", "Security")]
STACK = ["Python", "FastAPI", "Next.js", "n8n", "Docker", "PostGIS", "LINE Messaging API", "Telegram Bot API", "Playwright", "FFmpeg", "EasyOCR", "APScheduler", "Cloudflare Pages", "Excel / openpyxl"]

CSS = """
:root{--bg:#0c0e13;--bg2:#12151c;--card:#151a23;--ink:#eef1f6;--mut:#9aa5b8;--line:#232a37;--acc:#ff8a3d;--acc2:#ffc15e;--glow:rgba(255,138,61,.18)}
@media (prefers-color-scheme:light){:root{--bg:#fffaf3;--bg2:#fff3e3;--card:#fff;--ink:#241810;--mut:#6d5a4a;--line:#f0dcc6;--acc:#d9531e;--acc2:#e08a1e;--glow:rgba(217,83,30,.12)}}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.65 Inter,"Segoe UI","Sarabun","Noto Sans Thai",system-ui,sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--acc)}.wrap{max-width:1040px;margin:0 auto;padding:0 20px}
header.top{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 86%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;height:58px}
.brand{font-weight:800;letter-spacing:.2px;color:var(--ink);text-decoration:none;display:flex;align-items:center;gap:10px}
.brand img{width:30px;height:30px;border-radius:50%;background:var(--glow);object-fit:cover}
nav a{color:var(--mut);text-decoration:none;margin-left:20px;font-weight:600;font-size:.95rem}nav a:hover{color:var(--ink)}
.hero{padding:64px 0 36px;background:radial-gradient(900px 380px at 78% -10%,var(--glow),transparent 70%)}
.hero .wrap{display:grid;grid-template-columns:1.5fr 1fr;gap:28px;align-items:center}
.eyebrow{color:var(--acc);font-weight:700;letter-spacing:.14em;text-transform:uppercase;font-size:.78rem}
h1{font-size:clamp(2rem,5vw,3.2rem);line-height:1.12;margin:.35em 0 .4em;letter-spacing:-.02em}
h1 em{font-style:normal;background:linear-gradient(90deg,var(--acc),var(--acc2));-webkit-background-clip:text;background-clip:text;color:transparent}
.lead{color:var(--mut);font-size:1.1rem;max-width:34em}
.cta{display:flex;gap:12px;flex-wrap:wrap;margin-top:22px}
.btn{display:inline-block;padding:11px 20px;border-radius:12px;font-weight:700;text-decoration:none;border:1px solid var(--line);color:var(--ink);background:var(--card)}
.btn.p{background:linear-gradient(90deg,var(--acc),var(--acc2));color:#1a0f06;border:0}
.avatar{justify-self:center;width:min(300px,70vw);aspect-ratio:1;border-radius:50%;background:radial-gradient(circle at 50% 40%,var(--glow),transparent 70%);display:grid;place-items:center}
.avatar img{width:86%;filter:drop-shadow(0 16px 30px rgba(0,0,0,.3))}
section{padding:34px 0}h2{font-size:1.6rem;margin:0 0 6px;letter-spacing:-.01em}.sub{color:var(--mut);margin:0 0 20px}
.grid{display:grid;gap:16px}.g2{grid-template-columns:repeat(2,1fr)}.g3{grid-template-columns:repeat(3,1fr)}
.card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:20px;transition:transform .18s,border-color .18s}
.card:hover{transform:translateY(-3px);border-color:color-mix(in srgb,var(--acc) 55%,var(--line))}
.card h3{margin:0 0 2px;font-size:1.15rem}.card .s{color:var(--acc);font-weight:600;font-size:.9rem;margin-bottom:8px}.card p{color:var(--mut);margin:.4em 0 12px;font-size:.97rem}
.card.big{padding:24px}.card.big h3{font-size:1.3rem}
.tags{display:flex;flex-wrap:wrap;gap:6px}.tag{font-size:.76rem;padding:3px 10px;border-radius:99px;border:1px solid var(--line);color:var(--mut);background:var(--bg2)}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 18px}.chip{cursor:pointer;border:1px solid var(--line);background:var(--card);color:var(--mut);padding:6px 14px;border-radius:99px;font:inherit;font-size:.9rem}
.chip.on{background:var(--acc);border-color:var(--acc);color:#1a0f06;font-weight:700}
.principles{grid-template-columns:repeat(3,1fr)}.principles .card h3{font-size:1.02rem}
.stack{display:flex;flex-wrap:wrap;gap:8px}.stack .tag{font-size:.88rem;padding:6px 14px}
footer{border-top:1px solid var(--line);margin-top:30px;padding:26px 0;color:var(--mut);font-size:.9rem}
.hide{display:none}
/* article pages */
.page{max-width:760px;margin:0 auto;padding:30px 20px}.page h1{font-size:1.9rem}.page h2{margin-top:1.8em}
table{width:100%;border-collapse:collapse;font-size:.95rem}th,td{border-bottom:1px solid var(--line);padding:8px 6px;text-align:left}.tl{overflow-x:auto}
details{border-bottom:1px solid var(--line);padding:9px 0}summary{cursor:pointer;font-weight:700}.note{color:var(--mut);font-size:.9rem}
@media(max-width:760px){.hero .wrap{grid-template-columns:1fr}.avatar{order:-1;width:170px}.g2,.g3,.principles{grid-template-columns:1fr}nav a{margin-left:12px;font-size:.88rem}}
"""

NAV = [("/#work", "Work"), ("/#tools", "Tools"), ("/guide/shopee-lazada-tiktok-fees-2569/", "Fee guide (TH)")]
if cfg["contact"]:
    NAV.append(("/#contact", "Contact"))


def shell(path, title, desc, body, schema, lang="en", article=False, og="/og.png"):
    url = f"{BASE}{path}"
    ld = "".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schema)
    nav = "".join(f'<a href="{h}">{html.escape(t)}</a>' for h, t in NAV)
    doc = f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{url}">
<meta name="theme-color" content="#0c0e13"><link rel="icon" href="/assets/cat.png">
<meta property="og:type" content="website"><meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}{og}"><meta name="twitter:card" content="summary_large_image">
<style>{CSS}</style>{ld}</head><body>
<header class="top"><div class="wrap"><a class="brand" href="/"><img src="/assets/cat.png" alt="" width="30" height="30">{HANDLE}</a><nav>{nav}</nav></div></header>
{body}
<footer><div class="wrap">© {date.today().year} {HANDLE} ({THAI}) · Updated {TODAY}</div></footer></body></html>"""
    f = OUT / path.strip("/") / "index.html" if path != "/" else OUT / "index.html"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(doc, encoding="utf-8")


def tags(ts):
    return '<div class="tags">' + "".join(f'<span class="tag">{html.escape(t)}</span>' for t in ts) + "</div>"


def card(p, big=False):
    link_list = p.get("links") or ([p["link"]] if p.get("link") else [])
    link = ("<p>" + " &nbsp; ".join(f'<a href="{u}">{html.escape(t)} →</a>' for u, t in link_list) + "</p>") if link_list else ""
    sub = f'<div class="s">{html.escape(p["sub"])}</div>' if p.get("sub") else ""
    return (f'<article class="card{" big" if big else ""}" data-cat="{p["cat"]}"><h3>{html.escape(p["title"])}</h3>{sub}'
            f'<p>{html.escape(p["body"])}</p>{link}{tags(p["tags"])}</article>')


person = {"@context": "https://schema.org", "@type": "Person", "@id": f"{BASE}/#person", "name": HANDLE, "alternateName": THAI, "url": f"{BASE}/",
          "jobTitle": "Builder of AI agents, automation and data tools", "image": f"{BASE}/assets/cat.png",
          "knowsAbout": ["AI agents", "workflow automation", "n8n", "LINE bots", "SAR remote sensing", "quantitative research", "Python"]}
if cfg["sameAs"]:
    person["sameAs"] = cfg["sameAs"]
if cfg.get("email"):
    person["email"] = cfg["email"]
site_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": HANDLE, "url": f"{BASE}/", "publisher": {"@id": f"{BASE}/#person"}}

# ------------------------------------------------------------------ home (English portfolio)
chips = "".join(f'<button class="chip{" on" if k == "all" else ""}" data-f="{k}">{html.escape(v)}</button>' for k, v in FILTERS)
contact = ""
if cfg["contact"]:
    btns = "".join(f'<a class="btn{" p" if i == 0 else ""}" href="{html.escape(c["url"])}">{html.escape(c["label"])}</a>' for i, c in enumerate(cfg["contact"]))
    services = [("AI video creation", "Short vertical videos (Reels, TikTok, Shorts) with Thai voice-over and subtitles."),
                ("LINE OA bots & chatbots", "LINE Official Account bots with automation: replies, reminders, staff tools."),
                ("n8n workflow automation", "Connect Sheets, LINE, Telegram and APIs so repetitive work runs itself."),
                ("AI object detection (YOLO)", "Counting and quality-control from images, e.g. product counting.")]
    svc = "".join(f'<div class="card"><h3>{html.escape(a)}</h3><p>{html.escape(b)}</p></div>' for a, b in services)
    contact = (f'<section id="contact"><div class="wrap"><h2>Work with me</h2><p class="sub">Services listed on my Fastwork profile. Tell me what is slow, manual or unreliable in your process.</p>'
               f'<div class="grid g2">{svc}</div><div class="cta">{btns}</div></div></section>')
principles = [("Verify before claiming", "Numbers get checked against an independent calculation before they ship. Every fee table here cites its source and date."),
              ("Humans stay in the loop", "Publishing, payments and anything irreversible wait for an explicit approval step. Automation drafts; people decide."),
              ("Ship small, measure", "Start with the smallest version a real user can try, put it online, and let usage decide what gets built next.")]
home = f"""
<section class="hero"><div class="wrap"><div>
<div class="eyebrow">AI agents · automation · data tools</div>
<h1>I build software that <em>takes work off your plate</em>.</h1>
<p class="lead">Hi, I'm {HANDLE} ({THAI}) from Thailand. I build AI agents, workflow automation and data tools: LINE and Telegram bots, n8n pipelines, satellite-radar analytics and quantitative research tooling.</p>
<div class="cta"><a class="btn p" href="#work">See my work</a><a class="btn" href="#tools">Try a live tool</a></div></div>
<div class="avatar"><img src="/assets/cat.png" alt="Orange cat mascot" width="260" height="320"></div></div></section>
<section id="work"><div class="wrap"><h2>Selected work</h2><p class="sub">Four projects that show the range. Details come from the projects' own documentation.</p>
<div class="grid g2">{"".join(card(p, True) for p in FEATURED)}</div></div></section>
<section><div class="wrap"><h2>More projects</h2><p class="sub">Filter by area.</p><div class="chips" id="chips">{chips}</div>
<div class="grid g3" id="more">{"".join(card(p) for p in MORE)}</div></div></section>
<section id="tools"><div class="wrap"><h2>Live tools</h2><p class="sub">Things you can open right now (Thai interface, built for online sellers).</p>
<div class="grid g2">
<article class="card big"><h3>Shop Fee Reader</h3><div class="s">Free · Shopee, TikTok Shop, Lazada</div><p>See where each baht of a sale goes, the break-even price and break-even ROAS. Data stays in your browser.</p><p><a class="btn p" href="{FREE_TOOL}">Open the free tool</a> &nbsp; <a href="/tools/fee-reader/">Details (TH)</a></p></article>
<article class="card big"><h3>Marketplace Fee Guide 2569</h3><div class="s">Thai article · sourced rates</div><p>Fee table for the three platforms with a worked example and an FAQ on checking unexpected deductions.</p><p><a class="btn" href="/guide/shopee-lazada-tiktok-fees-2569/">Read the guide (TH)</a></p></article></div></div></section>
<section><div class="wrap"><h2>How I work</h2><p class="sub">Three habits that show up across the projects above.</p>
<div class="grid principles">{"".join(f'<div class="card"><h3>{html.escape(a)}</h3><p>{html.escape(b)}</p></div>' for a, b in principles)}</div></div></section>
<section><div class="wrap"><h2>Tools I use</h2><p class="sub">Taken from the projects above, not a wish list.</p><div class="stack">{"".join(f'<span class="tag">{html.escape(s)}</span>' for s in STACK)}</div></div></section>
{contact}
<script>document.getElementById('chips').addEventListener('click',function(e){{var f=e.target.dataset.f;if(!f)return;this.querySelectorAll('.chip').forEach(function(c){{c.classList.toggle('on',c===e.target)}});document.querySelectorAll('#more .card').forEach(function(c){{c.classList.toggle('hide',f!=='all'&&c.dataset.cat!==f)}})}})</script>"""
shell("/", f"{HANDLE} — AI agents, automation & data tools",
      f"{HANDLE} ({THAI}) builds AI agents, workflow automation and data tools: LINE/Telegram bots, n8n pipelines, SAR analytics and quant research. Portfolio and live tools.",
      home, [person, site_ld])

# ------------------------------------------------------------------ Thai product pages (target Thai search queries)
faq = [
 ("ค่าธรรมเนียม Shopee รวมกี่ %?", "ไม่มีตัวเลขเดียวสำหรับทุกร้าน ขึ้นกับประเภทร้าน หมวดสินค้า และโปรแกรมที่เข้าร่วม ตามตารางของ FlowAccount ปี 2569 Shopee มีค่าคอมมิชชั่น 7.49–19.26% ค่าธุรกรรม 3.21–7.49% ค่าบริการโปรแกรม 5.35–8.56% (เฉพาะร้านที่เข้าร่วม) และค่าแพลตฟอร์ม 1.07 บาทต่อออเดอร์ กรณีต่ำสุดที่ไม่เข้าโปรแกรมเท่ากับประมาณ 10.70% บวก 1.07 บาท ให้ตรวจอัตราจริงของร้านใน Seller Center"),
 ("ทำไมถูกหักเงินที่ไม่รู้ที่มา ตรวจอย่างไร?", "เปิดหน้ารายได้ของออเดอร์ใน Seller Center จดยอดที่ถูกหักแต่ละบรรทัด หารด้วยราคาขายเพื่อดูเป็น % แล้วเทียบกับอัตราของร้านคุณ ถ้ามีรายการที่ไม่ตรงหรือไม่รู้ที่มา ให้ถ่ายภาพหน้าจอแล้วสอบถามแพลตฟอร์มผ่านศูนย์ช่วยเหลือ ผู้ขายบางคนรายงานว่าเจอการหักที่ไม่คาดคิด เช่น ค่า Affiliate เครื่องมือเปรียบเทียบเป็นเพียงตัวช่วยตรวจ ไม่ได้ยืนยันว่าแพลตฟอร์มผิดพลาด"),
 ("ราคาเสมอตัว (break-even) คิดอย่างไร?", "ราคาที่กำไรเท่ากับศูนย์ คือ (ต้นทุน + ค่าส่งที่ร้านออก + ค่าแพ็ก + ค่าแพลตฟอร์มคงที่) ÷ (1 − อัตราค่าธรรมเนียมรวมเป็นสัดส่วน − สัดส่วนค่าโฆษณา) ถ้ามีเพดานค่าธรรมเนียมต่อชิ้น เช่น ค่า Commerce Growth ของ TikTok Shop ที่มีเพดาน 199 บาท ต้องคิดแยกเมื่อราคาสูง เครื่องมือฟรีคำนวณให้อัตโนมัติ"),
 ("ROAS เสมอตัวคืออะไร?", "ค่า ROAS ต่ำสุดที่ยิงโฆษณาแล้วไม่ขาดทุน คำนวณจากราคาขายหารกำไรก่อนหักค่าโฆษณา เช่น ตัวอย่างด้านล่างได้ประมาณ 2.4 ถ้า ROAS จริงต่ำกว่านี้ ออเดอร์จากแอดทำให้ขาดทุน"),
 ("เครื่องมือฟรีหรือเปล่า ข้อมูลไปไหน?", "ฉบับพื้นฐาน (คำนวณกำไร ตั้งอัตรา) ใช้ฟรี ไม่ต้องสมัคร ข้อมูลที่กรอกเก็บในเบราว์เซอร์ของคุณเท่านั้น ไม่ส่งขึ้นเซิร์ฟเวอร์ ฉบับเต็มราคา 99 บาท เพิ่มตรวจยอดที่ถูกหักเทียบอัตรา บันทึกหลายสินค้า และส่งออก CSV"),
]
faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
article_ld = {"@context": "https://schema.org", "@type": "Article", "headline": "ค่าธรรมเนียม Shopee, Lazada, TikTok Shop ปี 2569 คิดยังไง (พร้อมตัวอย่างคำนวณ)", "inLanguage": "th",
              "datePublished": TODAY, "dateModified": TODAY, "author": {"@id": f"{BASE}/#person"}, "mainEntityOfPage": f"{BASE}/guide/shopee-lazada-tiktok-fees-2569/", "citation": SRC}
faq_html = "".join(f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>" for q, a in faq)
guide = f"""<div class="page"><h1>ค่าธรรมเนียม Shopee, Lazada, TikTok Shop ปี 2569 คิดยังไง</h1>
<p class="note">ตัวเลขอ้างอิงจากบทความของ <a href="{SRC}" rel="nofollow noopener">FlowAccount</a> ตรวจเมื่อ {TODAY} (รวม VAT) แพลตฟอร์มปรับอัตราบ่อยและแต่ละร้านต่างกัน ให้ยืนยันกับ Seller Center ของร้านคุณก่อนตัดสินใจ</p>
<p><b>คำตอบสั้น:</b> ไม่มีตัวเลข % เดียวที่ใช้ได้ทุกร้าน ค่าธรรมเนียมแยกเป็นหลายก้อน (คอมมิชชั่น ค่าธุรกรรม ค่าโปรแกรม ค่าคงที่ต่อออเดอร์) ที่รวมกันเป็นสิบกว่า % ของราคาขาย ใช้ตารางด้านล่างประมาณการ แล้วคำนวณของร้านคุณด้วยเครื่องมือฟรี</p>
<h2>ตารางอัตราค่าธรรมเนียม (ปี 2569)</h2><div class="tl"><table>
<tr><th>แพลตฟอร์ม</th><th>ค่าธรรมเนียม</th><th>อัตรา</th><th>เงื่อนไข</th></tr>
<tr><td rowspan="4">Shopee</td><td>คอมมิชชั่น</td><td>7.49–19.26%</td><td>ตามประเภทร้านและหมวด</td></tr>
<tr><td>ค่าบริการโปรแกรม</td><td>5.35–8.56%</td><td>เฉพาะร้านที่เข้าร่วมโปรแกรม</td></tr>
<tr><td>ค่าธุรกรรมการชำระเงิน</td><td>3.21–7.49%</td><td>ต่างกันตามวิธีชำระ</td></tr>
<tr><td>ค่าแพลตฟอร์ม</td><td>1.07 บาท</td><td>ทุกออเดอร์</td></tr>
<tr><td rowspan="4">TikTok Shop</td><td>คอมมิชชั่นการตลาด</td><td>5.35–7.49%</td><td>ตามหมวดสินค้า</td></tr>
<tr><td>ค่าธุรกรรม</td><td>3.21%</td><td>ทุกคำสั่งซื้อ</td></tr>
<tr><td>ค่า Commerce Growth</td><td>5.35–6.42%</td><td>เพดาน 199 บาทต่อชิ้น</td></tr>
<tr><td>ค่าแพลตฟอร์ม</td><td>1.07 บาท</td><td>เฉพาะร้านขาย &gt;100 ชิ้นใน 30 วัน</td></tr>
<tr><td rowspan="2">Lazada</td><td>ค่าธรรมเนียมการขาย</td><td>6.96–18.73%</td><td>ตามประเภทร้านและหมวด</td></tr>
<tr><td>ค่าชำระเงิน</td><td>3.21%</td><td>ทุกช่องทาง</td></tr></table></div>
<h2>ตัวอย่างคำนวณ: ขายสินค้า 199 บาทบน Shopee</h2>
<p>สมมติ (เป็นตัวอย่างเท่านั้น): ร้านไม่เข้าโปรแกรมบริการ ใช้อัตราต่ำสุดในตาราง ต้นทุนสินค้า 90 บาท ค่าแพ็ก 5 บาท ไม่ซื้อโฆษณา</p>
<div class="tl"><table><tr><th>รายการ</th><th>บาท</th><th>% ของราคา</th></tr>
<tr><td>ราคาขาย</td><td>199.00</td><td>100.0%</td></tr><tr><td>− คอมมิชชั่น 7.49%</td><td>14.91</td><td>7.5%</td></tr>
<tr><td>− ค่าธุรกรรม 3.21%</td><td>6.39</td><td>3.2%</td></tr><tr><td>− ค่าแพลตฟอร์ม</td><td>1.07</td><td>0.5%</td></tr>
<tr><td>− ต้นทุนสินค้า</td><td>90.00</td><td>45.2%</td></tr><tr><td>− ค่าแพ็ก</td><td>5.00</td><td>2.5%</td></tr>
<tr><td><b>= กำไร</b></td><td><b>81.64</b></td><td><b>41.0%</b></td></tr></table></div>
<p>ค่าธรรมเนียมรวม 22.36 บาท (11.2%) ราคาเสมอตัวประมาณ 107.59 บาท และ ROAS เสมอตัวประมาณ 2.4 ถ้าร้านเข้าโปรแกรมบริการหรือหมวดมีคอมมิชชั่นสูงกว่านี้ ตัวเลขจะต่างมาก จึงควรใส่อัตราจริงของร้าน</p>
<p><a class="btn p" href="{FREE_TOOL}">คำนวณของร้านคุณฟรี</a></p>
<h2>คำถามที่พบบ่อย</h2>{faq_html}
<h2>ข้อจำกัดที่ควรรู้</h2><ul><li>อัตราในตารางเป็นค่าสาธารณะ ไม่ใช่ข้อเสนอเฉพาะของร้านคุณ</li><li>ไม่ครอบคลุมภาษี (เช่น VAT หรือภาษีเงินได้) กรุณาปรึกษาผู้ทำบัญชี</li><li>ไม่ได้ดึงข้อมูลจากแพลตฟอร์มอัตโนมัติ ต้องกรอกตัวเลขเอง</li></ul>
<p class="note">เขียนโดย <a href="/">{HANDLE} ({THAI})</a> · ปรับปรุงล่าสุด {TODAY}</p></div>"""
shell("/guide/shopee-lazada-tiktok-fees-2569/", "ค่าธรรมเนียม Shopee, Lazada, TikTok Shop 2569 คิดยังไง",
      "สรุปอัตราค่าธรรมเนียม Shopee, Lazada, TikTok Shop ปี 2569 พร้อมวิธีตรวจยอดที่ถูกหัก ตัวอย่างคำนวณกำไรต่อออเดอร์ ราคาเสมอตัว และ ROAS เสมอตัว",
      guide, [article_ld, faq_ld, person], lang="th")

app_ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "ตัวอ่านค่าธรรมเนียมร้านออนไลน์", "url": f"{BASE}/tools/fee-reader/",
          "applicationCategory": "BusinessApplication", "operatingSystem": "Any (web browser)", "inLanguage": "th",
          "description": "คำนวณกำไรหลังหักค่าธรรมเนียม Shopee, TikTok Shop, Lazada ราคาเสมอตัว และ ROAS เสมอตัว", "author": {"@id": f"{BASE}/#person"},
          "offers": [{"@type": "Offer", "name": "ฉบับฟรี", "price": "0", "priceCurrency": "THB"}, {"@type": "Offer", "name": "ฉบับเต็ม", "price": "99", "priceCurrency": "THB"}]}
tool = f"""<div class="page"><h1>ตัวอ่านค่าธรรมเนียมร้านออนไลน์</h1>
<p>เครื่องมือเว็บสำหรับผู้ขาย Shopee, TikTok Shop และ Lazada ใช้บนมือถือหรือคอมได้ทันที ไม่ต้องสมัคร ไม่ต้องติดตั้ง</p>
<p><a class="btn p" href="{FREE_TOOL}">เปิดฉบับฟรี</a></p>
<h2>ทำอะไรได้</h2><ul><li>แยกให้เห็นว่าราคาขายถูกหักเป็นคอมมิชชั่น ค่าธุรกรรม ค่าแพลตฟอร์มเท่าไร เหลือกำไรกี่บาทและกี่ %</li>
<li>บอกราคาเสมอตัวและราคาที่ได้กำไรตามเป้า (รวมเพดานค่า Commerce Growth ของ TikTok Shop)</li><li>บอก ROAS เสมอตัว ก่อนซื้อโฆษณา</li><li>แก้อัตราเองเมื่อแพลตฟอร์มปรับค่าธรรมเนียม</li></ul>
<h2>ฉบับฟรี และฉบับเต็ม 99 บาท</h2><div class="tl"><table><tr><th></th><th>ฟรี</th><th>เต็ม 99 บาท</th></tr>
<tr><td>คำนวณกำไร ราคาเสมอตัว ROAS</td><td>✓</td><td>✓</td></tr><tr><td>ตั้งอัตราเอง</td><td>✓</td><td>✓</td></tr>
<tr><td>ตรวจยอดที่ถูกหักเทียบอัตรา (แจ้งเตือนเมื่อหักเกิน)</td><td>–</td><td>✓</td></tr><tr><td>บันทึกหลายสินค้า และส่งออก CSV</td><td>–</td><td>✓</td></tr></table></div>
<h2>ข้อจำกัด</h2><ul><li>อัตราตั้งต้นเป็นข้อมูลสาธารณะ (ดู<a href="/guide/shopee-lazada-tiktok-fees-2569/">คู่มือค่าธรรมเนียม</a>) ต้องแก้ให้ตรงกับร้านคุณ</li><li>ไม่ดึงข้อมูลจากแพลตฟอร์มอัตโนมัติ</li><li>ไม่ใช่คำแนะนำภาษีหรือบัญชี</li><li>ข้อมูลเก็บในเบราว์เซอร์เครื่องนี้ ควรส่งออก CSV เก็บไว้</li></ul></div>"""
shell("/tools/fee-reader/", "ตัวอ่านค่าธรรมเนียมร้านออนไลน์ — คำนวณกำไรฟรี",
      "เครื่องมือฟรีบนมือถือ ดูว่าแต่ละบาทที่ขายถูกหักเป็นอะไร เหลือกำไรเท่าไร ราคาเสมอตัว ROAS เสมอตัว แก้อัตราเองได้ ข้อมูลอยู่ในเครื่องคุณ", tool, [app_ld, person], lang="th")

# ------------------------------------------------------------------ security reports (PDFs, sourced from the author's own auto-facebook/career/portfolio)
SECURITY_SRC = ROOT.parent / "auto-facebook" / "career" / "portfolio"
(OUT / "security").mkdir(parents=True, exist_ok=True)
_sec_files = [
    (SECURITY_SRC / "report-01-juice-shop" / "Portfolio-Report-1-Juice-Shop-Security-Assessment.pdf", "report-1-juice-shop.pdf"),
    (SECURITY_SRC / "report-02-remediation" / "Portfolio-Report-2-From-Finding-to-Fix.pdf", "report-2-remediation.pdf"),
]
for src, name in _sec_files:
    if src.exists():
        shutil.copyfile(src, OUT / "security" / name)

# ------------------------------------------------------------------ assets, og, robots, sitemap
from PIL import Image  # noqa: E402
cat = Image.open(ROOT / "films/ep02-hot-desk/assets/cat_12.png").convert("RGBA")
cat.thumbnail((520, 640))
cat.save(OUT / "assets" / "cat.png", optimize=True)

sys.path.insert(0, str(ROOT / "tools"))
from thai_text import find_chrome  # noqa: E402
cat64 = base64.b64encode((OUT / "assets" / "cat.png").read_bytes()).decode()
og = f"""<!doctype html><meta charset=utf-8><style>body{{margin:0;width:1200px;height:630px;background:radial-gradient(900px 500px at 85% 0%,#4a2a14,#0c0e13 70%);font-family:Segoe UI,Arial,sans-serif;color:#eef1f6;display:flex;align-items:center}}
.t{{padding:0 70px;width:760px}}.e{{color:#ff8a3d;font-weight:700;letter-spacing:.16em;font-size:26px}}h1{{font-size:96px;margin:10px 0;letter-spacing:-2px}}p{{font-size:34px;margin:0;color:#9aa5b8;line-height:1.35}}img{{height:500px}}</style>
<div class=t><div class=e>PORTFOLIO</div><h1>noppruts</h1><p>AI agents · automation<br>· data tools</p></div><img src="data:image/png;base64,{cat64}">"""
tmp = H / "og.html"
tmp.write_text(og, encoding="utf-8")
subprocess.run([find_chrome(), "--headless", "--disable-gpu", "--hide-scrollbars", "--window-size=1200,630", "--force-device-scale-factor=1",
                "--virtual-time-budget=2000", f"--screenshot={(OUT / 'og.png').resolve()}", tmp.resolve().as_uri()], check=True, capture_output=True, timeout=90)
tmp.unlink()

urls = ["/", "/guide/shopee-lazada-tiktok-fees-2569/", "/tools/fee-reader/", "/security/report-1-juice-shop.pdf", "/security/report-2-remediation.pdf"]
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
(OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                 + "".join(f"<url><loc>{BASE}{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls) + "</urlset>", encoding="utf-8")
(OUT / "llms.txt").write_text(f"# {HANDLE} ({THAI})\n> Builds AI agents, workflow automation and data tools. Portfolio and live tools.\n\n- [Portfolio]({BASE}/)\n- [Thai fee guide 2569]({BASE}/guide/shopee-lazada-tiktok-fees-2569/)\n- [Shop fee reader tool]({BASE}/tools/fee-reader/)\n- [Security findings report]({BASE}/security/report-1-juice-shop.pdf)\n- [Security remediation report]({BASE}/security/report-2-remediation.pdf)\n", encoding="utf-8")
print("built", sorted(str(p.relative_to(OUT)) for p in OUT.rglob("*") if p.is_file()))

# Web Scraping — Everything You Need to Know (Week 2)

Goal for the week: gather messy real-world data about ~30+ Indian startups from 4 sources (YC, Wikipedia, Inc42/YourStory, DPIIT data.gov.in) and feed it into a RAG corpus. Time-box: **~1.5 hrs per source**. If hostile, skip.

This note is the full mental model — concepts, tools, patterns, ethics, traps — so you can scrape with judgment, not by copy-paste.

---

## 1. The Mental Model

Web scraping = **3 layers**, in this order:

1. **Acquire** — fetch raw bytes from a URL (HTTP request, or browser automation if JS-rendered).
2. **Parse** — turn HTML/JSON into structured Python objects (BeautifulSoup, lxml, json).
3. **Extract & Clean** — pull the fields you want, normalize them (strip whitespace, fix encoding, drop boilerplate).

A scraper is **not** a one-shot script — it's a pipeline that must handle: retries, rate limits, partial failures, schema drift, and re-runs. Design it as such.

**Cardinal rule:** prefer an **official API** > **structured data feed (RSS, sitemap, CSV)** > **HTML scraping** > **headless browser**. Each step up costs you 5–10× more time and fragility.

---

## 2. How the Web Actually Works (the parts that bite you)

- **HTTP requests** carry: method (GET/POST), URL, headers (User-Agent, Cookie, Accept, Referer), body (for POST).
- **Status codes you'll see often:**
  - `200` OK — got content
  - `301/302` — redirect (follow it)
  - `403` — forbidden (often anti-bot)
  - `404` — gone
  - `429` — rate limited (back off!)
  - `503` — server busy or bot wall (Cloudflare etc.)
- **Cookies & sessions** — many sites set a cookie on first visit, require it on subsequent. Use a `Session` object.
- **JS rendering** — modern sites ship an empty `<div id="app">` and fill it with JS. `requests` sees the empty shell. You either (a) find the underlying JSON API the JS calls (best), or (b) use Playwright.
- **AJAX / XHR** — open DevTools → Network → XHR tab. The data you want is usually already there as JSON. Steal that endpoint.

---

## 3. Polite & Legal Scraping (do not skip)

- **robots.txt** — read `https://site.com/robots.txt`. It tells you which paths are off-limits. Not legally binding everywhere, but ignoring it gets you banned and looks bad in interviews.
- **Terms of Service** — some sites (LinkedIn, X) explicitly forbid scraping. Don't.
- **Rate limiting** — never hammer. Default: **1 request per 1–2 seconds**, with jitter. Use `asyncio.sleep(random.uniform(1, 2))`.
- **User-Agent** — set a real, identifiable UA. Example: `"IndianStartupRAG/0.1 (prayag@metquay.com)"`. Honesty > spoofing Chrome.
- **Caching** — cache every response to disk on first fetch. Re-runs hit cache, not the server. Saves you and them.
- **Identify yourself** — for academic/research scraping, including an email in UA is the convention.
- **Public vs private data** — public webpages = generally OK. Anything behind login = legal grey/red zone, skip.
- **Personal data (GDPR/DPDP)** — startup names, founder names that are *publicly published* on company websites are fine. Don't aggregate personal contact info.

---

## 4. The Toolbox

### Core libraries

| Tool | Use when |
|------|----------|
| `httpx` (async) | Default HTTP client. Async + same API as `requests`. |
| `requests` | Simple sync scripts. |
| `BeautifulSoup` (bs4) | Parse HTML, navigate by tag/class. Forgiving. |
| `lxml` | Fast HTML/XML parsing. Use as bs4's backend: `BeautifulSoup(html, "lxml")`. |
| `selectolax` | 5–10× faster than bs4 for simple selectors. Worth knowing. |
| `Playwright` | JS-heavy sites. Headless Chromium. Heavy — last resort. |
| `wikipedia-api` | Wikipedia. Clean API, no HTML parsing needed. |
| `feedparser` | RSS/Atom feeds. |
| `pandas` | CSV/Excel sources like data.gov.in. |
| `tenacity` | Retries with exponential backoff. |
| `tqdm` | Progress bars over long scrapes. |

### What each does, in one line

- **httpx**: `async with httpx.AsyncClient() as c: r = await c.get(url)` — concurrent requests, HTTP/2, timeouts built-in.
- **BeautifulSoup**: `soup.find("div", class_="company").get_text(strip=True)` — DOM navigation.
- **Playwright**: spins up a real browser, runs the JS, gives you the rendered DOM. Slow (~1–3 s/page) but bulletproof for SPAs.

---

## 5. Parsing HTML — the patterns you'll use 95% of the time

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "lxml")

# By tag + class
title = soup.find("h1", class_="company-name").get_text(strip=True)

# By CSS selector (often cleaner)
desc = soup.select_one("div.company-desc p").get_text(strip=True)

# All matches
founders = [a.get_text(strip=True) for a in soup.select("ul.founders li a")]

# Attribute
url = soup.find("a", string="Website")["href"]
```

**Selector strategy:**
1. Open DevTools → Elements, right-click target → **Copy → Copy selector**.
2. Simplify the auto-generated selector — strip unstable `nth-child` indexes.
3. Prefer **stable attributes** (`data-*`, semantic classes) over visual classes (`.css-1q2w3e` — auto-generated, will change).

---

## 6. Async Scraping with httpx (the production pattern)

```python
import httpx, asyncio, random
from tenacity import retry, stop_after_attempt, wait_exponential

HEADERS = {"User-Agent": "IndianStartupRAG/0.1 (prayag@metquay.com)"}
SEM = asyncio.Semaphore(5)  # max 5 concurrent requests

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=20))
async def fetch(client: httpx.AsyncClient, url: str) -> str:
    async with SEM:
        await asyncio.sleep(random.uniform(0.5, 1.5))  # jitter
        r = await client.get(url, headers=HEADERS, timeout=20.0)
        r.raise_for_status()
        return r.text

async def scrape_all(urls):
    async with httpx.AsyncClient(http2=True, follow_redirects=True) as client:
        return await asyncio.gather(*(fetch(client, u) for u in urls), return_exceptions=True)
```

**Why this shape:**
- `Semaphore` = concurrency cap, your real rate limiter.
- `tenacity` = retries with backoff on transient 5xx / network blips.
- `return_exceptions=True` = one failed page doesn't kill the batch.

---

## 7. Caching — non-negotiable

Every successful response → write to `cache/{hash(url)}.html`. On re-run, read from disk first. Tools:

- `hishel` — drop-in async HTTP cache for httpx, respects HTTP cache headers.
- Or roll your own with `pathlib` + `hashlib.sha1(url.encode()).hexdigest()`.

You will re-run your scraper 20+ times while debugging. Without cache, you'll get rate-limited, banned, or just waste hours.

---

## 8. When the site fights back (and what to do)

| Defense | Symptom | Counter |
|---------|---------|---------|
| User-Agent block | 403 with default UA | Set realistic UA |
| Rate limit | 429 / connection reset | Lower concurrency, add jitter, longer delays |
| Cloudflare/JS challenge | 503 + HTML challenge page | Playwright, or skip site |
| Geo block | 403 from non-IN IP | Skip unless critical |
| Login wall | redirect to /login | Skip — ToS likely forbids |
| CAPTCHA | image challenge | **Stop.** Site doesn't want you. |
| Honeypot links | invisible `<a>` that bans you | Respect `display:none` and `rel="nofollow"` |

**The 1.5-hour rule:** if you've spent 90 minutes on one source, drop it. You have 3 others.

---

## 9. APIs hidden inside websites (the pro move)

Most modern sites are SPAs that call an internal JSON API. Find it:

1. DevTools → **Network** tab → filter **Fetch/XHR**.
2. Interact with the page (search, scroll, click).
3. Watch for JSON responses with the data you want.
4. Right-click the request → **Copy as cURL** → convert to httpx with [curlconverter.com](https://curlconverter.com).

**YC company directory** does this — the page calls **Algolia's search API**. Hit Algolia directly, get clean JSON, skip HTML entirely. This is your fastest path for YC.

---

## 10. Wikipedia — the easy mode

```python
import wikipediaapi
wiki = wikipediaapi.Wikipedia(user_agent="IndianStartupRAG/0.1", language="en")
page = wiki.page("Flipkart")
text = page.text          # full article, plain text
summary = page.summary    # lead section
links = page.links        # dict of linked pages
```

No scraping, no HTML, no rate problems. Use this for any company with a Wikipedia article.

---

## 11. Government data — data.gov.in (DPIIT)

These are usually downloadable CSV/XLSX. No scraping required.

```python
import pandas as pd
df = pd.read_csv("https://data.gov.in/.../dpiit_startups.csv")
```

If the file is behind a click-to-download wall, just download it manually once and commit the raw file to `data/raw/`. Pragmatism > automation when N=1.

---

## 12. Playwright — only when forced

```python
from playwright.async_api import async_playwright

async def render(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        html = await page.content()
        await browser.close()
        return html
```

Cost: ~1–3 s/page + ~300 MB RAM per browser. Only use when:
- Page is empty without JS.
- No internal API you can hit instead.

---

## 13. Cleaning scraped text (don't skip — RAG quality depends on it)

After fetching, every doc passes through:

1. **Strip nav/footer/sidebar** — use bs4 to remove `<nav>`, `<footer>`, `<aside>`, `<script>`, `<style>`.
2. **Normalize whitespace** — `re.sub(r"\s+", " ", text).strip()`.
3. **Decode HTML entities** — `html.unescape(text)`.
4. **Fix Unicode** — `ftfy.fix_text(text)` (the `ftfy` library) catches mojibake.
5. **Boilerplate removal** — `trafilatura.extract(html)` is excellent — it gives you just the main article text, no nav/ads. Strong default.
6. **Language filter** — drop docs that aren't English (use `langdetect` or `fasttext`).
7. **Dedup** — hash normalized text; drop exact duplicates. Near-dup is harder (MinHash/SimHash) but skip for now.

**Recommendation:** start with `trafilatura` for article-style sources (Inc42, YourStory). It handles 80% of cleaning for free.

---

## 14. Storing what you scrape

Schema (matches the Week 2 plan):

```sql
documents(
  id, source, url, title, raw_html, clean_text,
  scraped_at, metadata jsonb
)
```

- Store **both** raw HTML and clean text. You'll want to re-clean later when your cleaner improves; re-scraping is expensive.
- `metadata` jsonb: author, published_date, company name, sector — anything you parsed out.
- One row per URL. URL is the natural key.

---

## 15. Project structure (week 2 build)

```
indian-startup-rag/
├── scrapers/
│   ├── __init__.py
│   ├── base.py          # shared: session, cache, retry, rate limit
│   ├── yc.py            # Algolia API
│   ├── wikipedia.py     # wikipedia-api
│   ├── inc42.py         # httpx + bs4
│   └── dpiit.py         # pandas read_csv
├── cleaning/
│   └── pipeline.py      # trafilatura + normalize
├── storage/
│   └── documents.py     # insert into Postgres
├── cache/               # raw HTML on disk
├── data/raw/            # CSVs, downloads
└── Makefile             # make scrape-yc, make scrape-all
```

Each scraper exposes the same interface: `async def scrape() -> list[Document]`. The orchestrator just calls them all.

---

## 16. Observability while scraping

- Log every URL fetched + status code + duration.
- Print a running counter: `[12/50] Fetched X (200, 1.2s)`.
- At the end, print a summary: total fetched, errors by type, total bytes.
- Write a `scrape_report.json` per run for the README later.

Hard to overstate how much faster debugging is with good logs.

---

## 17. Common pitfalls (echo of the plan + more)

- **Scraping rabbit hole.** 1.5 hr cap per source. Move on.
- **No cache.** Don't re-hit the server every dev iteration.
- **Hardcoded selectors.** Sites change. Comment what each selector targets, group them.
- **Synchronous loop over 500 URLs.** Use async + semaphore. ~10× faster, polite.
- **No retries.** Transient 5xx will kill 5–10% of pages otherwise.
- **Forgetting to set User-Agent.** Default `python-httpx/x.y` triggers 403 on many sites.
- **Storing only clean text.** Re-cleaning needs raw HTML.
- **Scraping JS pages without checking for an API first.** Always check Network tab first.
- **Hammering during dev.** Add `LIMIT=5` env var so dev runs hit 5 URLs, not 500.

---

## 18. Interview-ready talking points

If asked about scraping in an interview:

- "I prioritized official APIs first (YC's Algolia backend, Wikipedia's API), HTML scraping second, and skipped sites with hostile anti-bot."
- "Async with `httpx` + a semaphore for concurrency control, `tenacity` for retries with exponential backoff."
- "Cached raw HTML on disk so re-runs were free; stored raw + clean text in Postgres so I could re-clean without re-scraping."
- "Used `trafilatura` for article extraction — much better signal than rolling my own."
- "Respected robots.txt and set an identifiable User-Agent."
- "Time-boxed each source to 1.5 hours — corpus diversity matters more than completing every source."

---

## 19. Quick reference — the 10 commands you'll actually run

```bash
# install
pip install httpx beautifulsoup4 lxml trafilatura wikipedia-api tenacity playwright ftfy pandas tqdm
playwright install chromium

# inspect robots
curl https://www.ycombinator.com/robots.txt

# peek a page
curl -A "IndianStartupRAG/0.1" https://example.com | head -50

# pretty-print JSON from an API
curl -s '<algolia-url>' | jq .

# run scraper with limit during dev
LIMIT=5 python -m scrapers.yc
```

---

## 20. Decision tree when you sit down at a new source

```
Is there an official API?  ── yes ──> use it. done.
            │ no
            ▼
Is the data in a downloadable file (CSV/JSON)?  ── yes ──> download once. done.
            │ no
            ▼
Open DevTools → Network. Does the page call an internal JSON API?
            │ yes ──> hit that endpoint directly with httpx.
            │ no
            ▼
View page source (Ctrl+U). Is the data in the initial HTML?
            │ yes ──> httpx + BeautifulSoup.
            │ no  (data appears only after JS runs)
            ▼
Is it critical to the corpus?
            │ no  ──> skip this source.
            │ yes
            ▼
Playwright. Headless. Cache aggressively.
```

That's the whole game. Build the pipeline once, plug in 4 scrapers, move on to chunking by Wednesday.

---
name: web-fetcher
description: >
  Fetch any URL or local PDF and return structured markdown content with semantic
  chunks. Use this skill whenever the user asks to read, summarise, research, or
  extract information from a webpage, article, documentation site, blog post, or
  PDF file. Automatically detects JavaScript-heavy pages (Next.js, Vue, Angular,
  Nuxt) and falls back to Playwright/Crawl4AI rendering. Local PDFs are extracted
  with pypdf. Returns a FetchResult with full markdown, links, images, and
  pre-chunked sections ready for downstream agents.
license: MIT
metadata:
  author: Bernhard Zechmann
  version: "1.0"
---

# Web Fetch Skill

Fetches URLs and returns structured, token-optimised markdown content for agent
consumption. Uses a two-path architecture: lightweight HTTP (static) or full
browser rendering (dynamic/JS).

---

## When to use this skill

- User provides a URL and asks to read, summarise, or extract information
- Research tasks requiring current web content
- Documentation lookups
- Competitive or content analysis from external sites
- Any task where `web_fetch` is needed as a sub-step

---

## Tool

**`web_fetch(url, render_js, max_tokens)`** — registered directly on the agent via `tools/web_fetch.py`.
Call it as a tool, not as a skill. No skill invocation needed.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `url` | `str` | required | Full URL (http/https) or local PDF path (file:// or plain path) |
| `render_js` | `bool` | `False` | Force browser rendering |
| `max_tokens` | `int` | `4000` | Token budget for returned chunks |

---

## Render path selection

| Condition | Path used |
|---|---|
| Local PDF file | PDF extraction (pypdf) |
| Default call | Static (httpx + trafilatura) |
| JS triggers detected in HTML | Automatic fallback to browser |
| `render_js=True` | Browser (Crawl4AI + Playwright) |
| Static fetch throws exception | Browser fallback |

**JS triggers that force browser rendering:**
`__NEXT_DATA__`, `__nuxt`, `ng-version`, `ember-application`, `react-app`,
`webpack`, `hydration`, `data-reactroot`, `vue-app`, `application/json`

---

## Output schema

```python
FetchResult:
  url:          str           # canonical URL fetched
  title:        str | None    # page <title> or og:title
  markdown:     str           # full extracted markdown
  summary:      str | None    # optional — agent fills this from chunks
  links:        list[str]     # deduplicated absolute hrefs
  images:       list[str]     # deduplicated absolute image srcs
  metadata:     dict          # HTTP status, og tags, etc.
  chunks:       list[Chunk]   # semantic sections within token budget
  render_path:  str           # "static" | "browser" | "pdf"

Chunk:
  heading:         str | None  # section heading (H1/H2/H3)
  content:         str         # section text
  tokens_estimate: int         # rough token count (chars / 4)
```

---

## Agent instructions

1. Call `web_fetch(url=<url>)` — static path is the default and fastest.
2. If the page returns mostly empty markdown or JS placeholders, retry with
   `render_js=True`.
3. Use `chunks` to navigate large pages — work section by section rather than
   passing the full `markdown` to the model at once.
4. Fill `summary` yourself after reading the chunks.
5. Cite sources using `links` where relevant.

---

## Usage examples

### Basic fetch
```python
result = await web_fetch(url="https://docs.agno.com/introduction")
```

### Force browser rendering (SPA / Next.js)
```python
result = await web_fetch(url="https://nextjsapp.example.com", render_js=True)
```

### Narrow token budget (large pages)
```python
result = await web_fetch(url="https://longpage.example.com", max_tokens=2000)
```

---

## Dependencies

Install with:
```bash
pip install -r skills/core/web-fetcher/requirements.txt
playwright install chromium
```

---

## Render paths — internal module map

```
tools/web_fetch.py          ← @tool entry point / router
tools/web_fetch_lib/
  ├── extraction.py         ← httpx.AsyncClient + trafilatura (static path)
  ├── crawl4ai_engine.py    ← Crawl4AI AsyncWebCrawler (browser path)
  ├── chunking.py           ← semantic section splitter with token budget
  └── schemas.py            ← FetchResult + Chunk Pydantic models
```

---

## Phase roadmap

| Phase | Status | Scope |
|---|---|---|
| 1 — MVP | **done** | Static fetch, Crawl4AI fallback, chunking, Agno tool |
| 2 — Dynamic Web | planned | Playwright direct engine, screenshot support |
| 3 — Production | planned | Redis cache, browser pool, retry/backoff, URL normalization |
| 4 — Advanced | planned | Recursive crawl, relevance filtering, PDF/table extraction |

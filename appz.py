#!/usr/bin/env python3
import asyncio, hashlib, re, sys, urllib.parse as up
from pathlib import Path
from typing import Set, List

import httpx, trafilatura
from tqdm import tqdm

# ---------- CONFIG ----------
MAX_DEPTH = 4          # avoids infinite spider traps
CRAWL_DELAY = 1.0       # polite scanning
HEADERS = {"User-Agent": "Mozilla/5.0 ..."}
# ----------------------------

def slugify_url(url: str) -> str:
    slug = re.sub(r'[^0-9A-Za-z\-]+', '-', up.urlparse(url).path or 'index')[:120]
    h = hashlib.sha256(url.encode()).hexdigest()[:6]
    fname = f"{slug}-{h}.md".lower()
    if len(fname.encode('utf-8')) > 240:
        cut = 240 - 9
        fname = f"{slug[:cut]}-{h}.md"
    return fname

async def scan(start: str) -> List[str]:
    seen, frontier = set([start]), [start]
    pbar = tqdm(desc="Scanning", total=1, unit="url")
    async with httpx.AsyncClient(headers=HEADERS, timeout=10) as client:
        while frontier:
            url = frontier.pop(0)
            pbar.set_postfix(url=url[-40:])
            try:
                r = await client.get(url)
                r.raise_for_status()
                for href in re.findall(r'href=[\'"]?([^\'" >]+)', r.text):
                    nxt = up.urljoin(url, href)
                    if up.urlparse(nxt).netloc == up.urlparse(start).netloc and nxt not in seen:
                        seen.add(nxt); frontier.append(nxt)
                        pbar.total += 1; pbar.refresh()
            except Exception:
                pass
            pbar.update()
            await asyncio.sleep(CRAWL_DELAY)
    pbar.close()
    return list(seen)

async def scrape(urls: List[str], out_dir: Path):
    pbar = tqdm(desc="Scraping", total=len(urls), unit="page")
    success = 0
    async with httpx.AsyncClient(headers=HEADERS, timeout=15) as client:
        for url in urls:
            try:
                r = await client.get(url)
                if (res := trafilatura.extract(r.text, url=url,
                                               output_format="markdown",
                                               include_comments=False)):
                    Path(out_dir, slugify_url(url)).write_text(res, encoding="utf-8")
                    success += 1
            except Exception:
                pass
            pbar.set_postfix(success=success, fail=pbar.n - success)
            pbar.update()
    pbar.close()

def main():
    start = input("Start URL: ").strip()
    if not start.startswith(("http://", "https://")):
        start = "http://" + start
    domain = up.urlparse(start).netloc.replace(':', '_')
    out_dir = Path(domain); out_dir.mkdir(exist_ok=True)

    print("➜ Phase 1: scanning...")
    urls = asyncio.run(scan(start))
    count = len(urls)
    print(f"Discovered {count} unique in-scope pages.")

    limit = input(f"Enter pages to scrape [default={count}]: ").strip()
    limit = int(limit) if limit.isdigit() and int(limit) > 0 else count
    urls = urls[:limit]

    print("➜ Phase 2: scraping...")
    asyncio.run(scrape(urls, out_dir))
    print(f"Done. Markdown saved to ./{domain}")

if __name__ == "__main__":
    main()

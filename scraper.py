"""
Run once to scrape Jaro Education website:
    python3 scraper.py
Saves chunks to jaro_chunks.json
"""
import json
import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.jaroeducation.com/"
MAX_PAGES = 60
CHUNK_SIZE = 400  # words per chunk


def clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_text(text: str, source: str) -> list[dict]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), CHUNK_SIZE):
        chunk = " ".join(words[i : i + CHUNK_SIZE])
        if len(chunk) > 100:
            chunks.append({"text": chunk, "source": source})
    return chunks


def scrape() -> list[dict]:
    visited, queue, all_chunks = set(), [BASE_URL], []
    domain = urlparse(BASE_URL).netloc

    while queue and len(visited) < MAX_PAGES:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if "text/html" not in resp.headers.get("Content-Type", ""):
                continue
        except Exception as e:
            print(f"skip {url}: {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = clean(soup.get_text(separator=" "))
        all_chunks.extend(chunk_text(text, url))
        print(f"scraped {url} — {len(all_chunks)} chunks so far")

        for a in soup.find_all("a", href=True):
            href = urljoin(url, a["href"])
            p = urlparse(href)
            if p.netloc == domain and href not in visited and p.scheme in ("http", "https"):
                queue.append(href)

        time.sleep(0.5)

    return all_chunks


if __name__ == "__main__":
    chunks = scrape()
    with open("jaro_chunks.json", "w") as f:
        json.dump(chunks, f)
    print(f"saved {len(chunks)} chunks to jaro_chunks.json")

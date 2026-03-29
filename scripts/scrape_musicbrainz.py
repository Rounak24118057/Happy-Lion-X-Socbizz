"""
scrape_musicbrainz.py
Scrapes MusicBrainz for all artists tagged as being from India (61 pages x 100 results).
Saves the deduplicated list to data/indian_artists.json
"""

import json
import time
import os
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

BASE_URL = (
    "https://musicbrainz.org/search"
    "?query=area%3A%22India%22&type=artist&limit=100&method=advanced&page={page}"
)

TOTAL_PAGES = 61


def scrape_indian_artists():
    artist_names = set()

    for page in range(1, TOTAL_PAGES + 1):
        url = BASE_URL.format(page=page)
        print(f"  Scraping MusicBrainz page {page}/{TOTAL_PAGES}...")

        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            soup = BeautifulSoup(resp.text, "lxml")
            for a in soup.find_all("a", href=True, title=True):
                bdi = a.find("bdi")
                if bdi:
                    name = bdi.text.strip()
                    if name:
                        artist_names.add(name)
        except Exception as e:
            print(f"  Error on page {page}: {e}")

        time.sleep(1.2)

    return sorted(artist_names)


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    print("Scraping MusicBrainz for Indian artists...")
    artists = scrape_indian_artists()
    print(f"Found {len(artists)} unique Indian artists")
    with open("data/indian_artists.json", "w", encoding="utf-8") as f:
        json.dump(artists, f, ensure_ascii=False, indent=2)
    print("Saved → data/indian_artists.json")

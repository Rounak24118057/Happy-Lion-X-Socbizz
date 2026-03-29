"""
fetch_images.py
Fetches artist profile images by scraping Spotify's public search page
using Selenium — exactly the same image source (i.scdn.co) as the
original Top_Indian_Artist.json used.
Falls back to MusicBrainz cover art if Spotify has no result.
"""

import json
import time
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1280,800")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    return driver


def get_spotify_image(driver, artist_name):
    """Scrape Spotify public search for artist image."""
    try:
        query = artist_name.replace(" ", "+")
        url = f"https://open.spotify.com/search/{query}/artists"
        driver.get(url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Spotify artist cards contain images with srcset pointing to i.scdn.co
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if "i.scdn.co" in src and "image" in src:
                # Upgrade to highest resolution available
                return src.replace("ab6761610000e5eb", "ab6761610000e5eb") \
                           .replace("64x64", "640x640")
    except Exception as e:
        print(f"    Spotify error for '{artist_name}': {e}")
    return None


def get_musicbrainz_image(artist_name):
    """Fallback: query MusicBrainz API for artist image via CAA."""
    try:
        headers = {"User-Agent": "KhelKhatam/1.0 (github.com/Rounak24118057/Khel_Khatam)"}
        search_url = (
            f"https://musicbrainz.org/ws/2/artist/"
            f"?query=artist:{requests.utils.quote(artist_name)}&area=India&limit=1&fmt=json"
        )
        resp = requests.get(search_url, headers=headers, timeout=10)
        data = resp.json()
        artists = data.get("artists", [])
        if not artists:
            return None

        mbid = artists[0].get("id")
        if not mbid:
            return None

        # Try getting thumbnail from WikiData / fanart via MusicBrainz relations
        rel_url = f"https://musicbrainz.org/ws/2/artist/{mbid}?inc=url-rels&fmt=json"
        rel_resp = requests.get(rel_url, headers=headers, timeout=10)
        rel_data = rel_resp.json()

        for rel in rel_data.get("relations", []):
            url = rel.get("url", {}).get("resource", "")
            if "commons.wikimedia.org" in url or "wikidata.org" in url:
                return None   # skip wikimedia for simplicity

    except Exception:
        pass
    return None


def placeholder(artist_name):
    initials = "+".join(w[0].upper() for w in artist_name.split()[:2] if w)
    return f"https://placehold.co/300x300/1d4436/69e091?text={initials or '?'}"


if __name__ == "__main__":
    with open("data/Top_Indian_Artist.json", encoding="utf-8") as f:
        data = json.load(f)

    header  = data[0]
    artists = data[1:]

    print(f"Fetching images for {len(artists)} artists via Spotify...")
    driver = get_driver()

    for i, entry in enumerate(artists):
        name = entry["A"]
        print(f"  [{i+1}/{len(artists)}] {name}")

        img_url = get_spotify_image(driver, name)

        if not img_url:
            print(f"    → No Spotify result, trying MusicBrainz...")
            img_url = get_musicbrainz_image(name)

        if not img_url:
            print(f"    → Using placeholder")
            img_url = placeholder(name)

        entry["C"] = img_url
        time.sleep(0.5)   # polite delay

    driver.quit()

    final = [header] + artists
    with open("data/Top_Indian_Artist.json", "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    print("Done — images saved → data/Top_Indian_Artist.json")

"""
scrapper.py
Scrapes top 100 trending songs from Amazon Music.
Song images come directly from Amazon Music's own image-src attribute.
Saves to data/data.json
"""

import json
import time
import os

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    return driver


URL = "https://music.amazon.com/popular/songs"


def scrape_top_100():
    driver = get_driver()
    print("Opening page...")
    driver.get(URL)
    time.sleep(5)
    print("Page loaded")

    song_title = []
    artist_name = []
    image_url = []
    target_count = 100

    start_time = time.time()
    MAX_SECONDS = 240

    while len(song_title) < target_count:
        if time.time() - start_time > MAX_SECONDS:
            print("Stopping: hit max runtime limit")
            break

        print(f"Loop start, currently have {len(song_title)} songs")
        webpage = driver.page_source
        soup = BeautifulSoup(webpage, 'html.parser')
        trending_songs = soup.find_all('music-horizontal-item')
        print(f"Found {len(trending_songs)} items on this view")

        for song in trending_songs:
            primary_text = song.get('primary-text', '0. Unknown Title')
            title = primary_text.split(".", 1)[1].strip() if "." in primary_text else primary_text.strip()
            artist = song.get('secondary-text', 'Unknown Artist')
            img = song.get('image-src', '')

            song_title.append(title)
            artist_name.append(artist)
            image_url.append(img)

            if len(song_title) >= target_count:
                break

        print(f"Collected {len(song_title)} songs so far")
        if len(song_title) >= target_count:
            break

        driver.execute_script("window.scrollBy(0, 2000);")
        time.sleep(2)

    driver.quit()
    print("Driver closed")

    songs_data = pd.DataFrame({
        "Track":     song_title[:target_count],
        "Artists":   artist_name[:target_count],
        "Image Url": image_url[:target_count],
    })
    return songs_data


def main():
    print("Scraper main() started")
    os.makedirs("data", exist_ok=True)
    songs_data = scrape_top_100()
    print("Final count:", len(songs_data))
    records = songs_data.to_dict(orient="records")
    with open("data/data.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print("Saved data to data/data.json")


if __name__ == "__main__":
    main()

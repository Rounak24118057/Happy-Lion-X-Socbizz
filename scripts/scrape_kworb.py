"""
scrape_kworb.py
1. Scrapes all ~2000 artists + Today scores from kworb.net
2. Uses a BROADER built-in Indian artist seed list (covers Punjabi, Tamil, Telugu, Hindi etc.)
   combined with whatever MusicBrainz returned
3. Fuzzy-matches and ranks by Today score — keeps top 100
"""

import json
import os
import requests
from bs4 import BeautifulSoup
from rapidfuzz import process, fuzz

KWORB_URL = "https://kworb.net/ww/artisttotals.html"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

MATCH_THRESHOLD = 75   # lowered from 82 so more names match
TOP_N = 100

# Broad seed list of well-known Indian artists across all genres/languages
# This catches artists MusicBrainz misses (Punjabi pop, new-gen artists etc.)
SEED_ARTISTS = [
    "Arijit Singh", "A. R. Rahman", "AR Rahman", "Shreya Ghoshal", "Sonu Nigam",
    "KK", "Udit Narayan", "Lata Mangeshkar", "Asha Bhosle", "Kumar Sanu",
    "Alka Yagnik", "Kishore Kumar", "Mohammed Rafi", "Mukesh", "Manna Dey",
    "Pritam", "Vishal-Shekhar", "Shankar Ehsaan Loy", "Amit Trivedi",
    "Sachin-Jigar", "Ajay-Atul", "Yuvan Shankar Raja", "Anirudh Ravichander",
    "Ilaiyaraaja", "Harris Jayaraj", "Thaman S", "Devi Sri Prasad",
    "Sid Sriram", "Armaan Malik", "Jubin Nautiyal", "Darshan Raval",
    "Guru Randhawa", "Badshah", "Yo Yo Honey Singh", "Diljit Dosanjh",
    "AP Dhillon", "Shubh", "Karan Aujla", "Sidhu Moose Wala",
    "Imran Khan", "Gurdas Maan", "Jazzy B", "Sukhbir",
    "Hardy Sandhu", "Harrdy Sandhu", "B Praak", "Jaani",
    "Neha Kakkar", "Tony Kakkar", "Tulsi Kumar", "Dhvani Bhanushali",
    "Asees Kaur", "Nikk", "Rajveer", "Jassie Gill",
    "Pav Dharia", "Kulwinder Billa", "Mankirt Aulakh", "Jordan Sandhu",
    "Satinder Sartaaj", "Ammy Virk", "Ranjit Bawa", "Sippy Gill",
    "Sunidhi Chauhan", "Shilpa Rao", "Neeti Mohan", "Jonita Gandhi",
    "Palak Muchhal", "Monali Thakur", "Rekha Bhardwaj", "Kavita Krishnamurthy",
    "Shankar Mahadevan", "Hariharan", "Kailash Kher", "Mohit Chauhan",
    "Javed Ali", "Shaan", "Kunal Ganjawala", "Abhijeet",
    "Siddharth Slathia", "Salim-Sulaiman", "Meet Bros", "Mithoon",
    "Vishal Mishra", "Tanishk Bagchi", "Sachet-Parampara", "Sachet Tandon",
    "Parampara Tandon", "Rochak Kohli", "Amaal Mallik", "Armaan Malik",
    "Ankit Tiwari", "Jeet Gannguli", "Himesh Reshammiya", "Anu Malik",
    "Benny Dayal", "Nakash Aziz", "Shashwat Sachdev", "Gourov Dasgupta",
    "Dhanush", "Vijay Sethupathi", "Sivakarthikeyan", "Suriya",
    "Prabhu Deva", "Vijay", "Allu Arjun", "Ram Charan",
    "S. P. Balasubrahmanyam", "S. P. Balasubramanyam", "S.P.B",
    "Chitra", "S. Janaki", "P. Susheela", "Vani Jairam",
    "Blaaze", "Haricharan", "Naresh Iyer", "Tanvi Shah",
    "Vishal Dadlani", "Shekhar Ravjiani", "Sunitha Upadrashta",
    "Rahul Sipligunj", "Anurag Kulkarni", "Yazin Nizar",
    "Karthik", "Vijay Prakash", "Divakar", "Usha Uthup",
    "Papon", "Zubeen Garg", "Shalmali Kholgade", "Akriti Kakkar",
    "Prakriti Kakkar", "Antara Mitra", "Sanam Puri", "Sanam",
    "Lucky Ali", "Euphoria", "Indian Ocean", "Strings",
    "Nucleya", "Ritviz", "Prateek Kuhad", "Aakash Mehta",
    "King", "Raftaar", "Divine", "Naezy", "Brodha V",
    "Seedhe Maut", "MC Stan", "Ikka", "Emiway Bantai",
    "Tesher", "Ricky Kej", "Shankar Tucker",
    "Geet Sagar", "Clinton Cerejo", "Ehsaan Noorani", "Loy Mendonsa",
]


def scrape_kworb():
    print("Scraping kworb.net...")
    resp = requests.get(KWORB_URL, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(resp.text, "lxml")
    table = soup.find("table")
    rows = table.find_all("tr")[1:]
    kworb = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 3:
            continue
        name = cols[0].text.strip()
        today_raw = cols[2].text.strip().replace(",", "")
        try:
            today = int(today_raw)
        except ValueError:
            today = 0
        kworb.append({"name": name, "today": today})
    print(f"Found {len(kworb)} artists on kworb")
    return kworb


def match_artists(indian_artists, kworb_list):
    kworb_names  = [a["name"] for a in kworb_list]
    kworb_lookup = {a["name"]: a["today"] for a in kworb_list}

    # Combine MusicBrainz list + seed list, deduplicate
    all_indian = list(set(indian_artists + SEED_ARTISTS))
    print(f"Total Indian artist names to match: {len(all_indian)}")

    seen_kworb = set()
    matched = []

    for indian_name in all_indian:
        result = process.extractOne(
            indian_name, kworb_names, scorer=fuzz.token_sort_ratio
        )
        if result and result[1] >= MATCH_THRESHOLD:
            kworb_name = result[0]
            if kworb_name in seen_kworb:
                continue   # don't add same kworb artist twice
            seen_kworb.add(kworb_name)
            matched.append({
                "indian_name": indian_name,
                "kworb_name":  kworb_name,
                "today":       kworb_lookup[kworb_name],
            })

    matched.sort(key=lambda x: x["today"], reverse=True)
    print(f"Matched {len(matched)} Indian artists — keeping top {TOP_N}")
    return matched[:TOP_N]


def build_output(matched):
    output = [{"A": "Artist_Name", "B": "Today_Score", "C": "Image_Url"}]
    for entry in matched:
        output.append({
            "A": entry["indian_name"],
            "B": str(entry["today"]),
            "C": ""
        })
    return output


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    with open("data/indian_artists.json", encoding="utf-8") as f:
        indian_artists = json.load(f)
    print(f"Loaded {len(indian_artists)} artists from MusicBrainz")

    kworb_list = scrape_kworb()
    matched    = match_artists(indian_artists, kworb_list)
    output     = build_output(matched)

    with open("data/Top_Indian_Artist.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(output)-1} ranked artists → data/Top_Indian_Artist.json")
    print("\nTop 10 preview:")
    for e in output[1:11]:
        print(f"  {e['A']:30s}  Today: {e['B']}")

# 🎵 Music Tracker — SocBizIITR

Live rankings of trending songs and top Indian artists, auto-updated daily.

## 🌐 Live Site
`https://<your-username>.github.io/<repo-name>/`

## 📁 Structure
```
├── index.html              # Top 100 trending songs
├── Artist_Ranking.html     # Top Indian artists 
├── data/
│   ├── data.json           # Auto-updated songs data
│   ├── Top_Indian_Artist.json  # Auto-updated artist rankings
│   └── indian_artists.json # Indian artists list from MusicBrainz
├── scripts/
│   ├── scrapper.py         
│   ├── scrape_musicbrainz.py  
│   ├── scrape_kworb.py     
│   └── fetch_images.py     
└── .github/workflows/
    └── update.yml          # GitHub Actions: runs daily at midnight IST
```

## ⚙️ How It Works
1. **GitHub Actions** triggers every day at midnight IST (18:30 UTC)
2. Scrapes **Amazon Music** for top 100 trending songs → `data/data.json`
3. Scrapes **MusicBrainz** for ~6000 Indian artist names → `data/indian_artists.json`
4. Scrapes **kworb.net** for all 2000 artists + their iTunes Today scores
5. **Fuzzy-matches** Indian artists against kworb list, ranks by Today score → `data/Top_Indian_Artist.json`
6. Fetches **artist images** from iTunes Search API (free, no key needed)
7. Auto-commits and pushes updated data → GitHub Pages serves fresh site

## 🚀 Setup (one-time)
1. Fork / clone this repo
2. Go to **Settings → Pages → Branch: main → /(root) → Save**
3. That's it — Actions will run automatically every night

## 🔧 Manual Trigger
Go to **Actions → Update Music Data → Run workflow**

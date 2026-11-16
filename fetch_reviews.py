"""
Fetch recent Google Play reviews for Peak's Toy Blast and Toon Blast.

Usage:
    pip install google-play-scraper pandas
    python fetch_reviews.py

Output: data/peak_reviews.csv
"""
import os
import time
import pandas as pd
from google_play_scraper import reviews, Sort

GAMES = {
    "Toy Blast": "net.peakgames.amy",
    "Toon Blast": "net.peakgames.toonblast",
}
REVIEWS_PER_GAME = 5000   # newest English reviews from the US store
BATCH = 200

all_rows = []
for game, app_id in GAMES.items():
    print(f"Fetching {game} ({app_id})...")
    rows, token = [], None
    while len(rows) < REVIEWS_PER_GAME:
        try:
            batch, token = reviews(app_id, lang="en", country="us",
                                   sort=Sort.NEWEST, count=BATCH,
                                   continuation_token=token)
        except Exception as e:
            print(f"  Stopped early: {e}")
            break
        if not batch:
            break
        rows.extend(batch)
        print(f"  {len(rows)} reviews")
        if token is None:
            break
        time.sleep(1)  # be polite to the server
    if not rows:
        print(f"  WARNING: no reviews found for {game}. Check the app id.")
    for r in rows[:REVIEWS_PER_GAME]:
        all_rows.append({
            "game": game,
            "review_id": r["reviewId"],
            "date": r["at"],
            "score": r["score"],
            "thumbs_up": r["thumbsUpCount"],
            "app_version": r.get("reviewCreatedVersion"),
            "text": r["content"],
        })

df = pd.DataFrame(all_rows)
os.makedirs("data", exist_ok=True)
df.to_csv("data/peak_reviews.csv", index=False)
print(f"\nDone: {len(df)} reviews saved to data/peak_reviews.csv")
print(df.groupby("game")["score"].agg(["count", "mean"]).round(2))

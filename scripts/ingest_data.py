"""
RecoMart Data Ingestion Script
--------------------------------
Ingests two sources:
  1. Local ratings data (u.data)   -> simulates clickstream/interaction logs
  2. OMDb API                      -> simulates external metadata/sentiment source

Includes: logging, retries, error handling, partitioned raw storage.
"""

import os
import time
import logging
import requests
import pandas as pd
from datetime import datetime

# ---------- CONFIG ----------
OMDB_API_KEY = "49bd96c5"   # <-- replace with your free OMDb API key
RAW_DIR = "data/raw"
LOG_DIR = "logs"
TODAY = datetime.now().strftime("%Y-%m-%d")
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=f"{LOG_DIR}/ingestion_{TODAY}.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


def ingest_ratings():
    """Source 1: Ingest local ratings data (acts as clickstream/interaction source)."""
    try:
        path = os.path.join(RAW_DIR, "ml-100k", "u.data")
        cols = ["user_id", "item_id", "rating", "timestamp"]
        df = pd.read_csv(path, sep="\t", names=cols)

        out_dir = os.path.join(RAW_DIR, "interactions", TODAY)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "ratings.csv")
        df.to_csv(out_path, index=False)

        logger.info(f"SUCCESS | Ingested {len(df)} rating records -> {out_path}")
        print(f"[OK] Ingested {len(df)} ratings -> {out_path}")
        return df
    except Exception as e:
        logger.error(f"FAILED | Ratings ingestion error: {e}")
        print(f"[FAIL] Ratings ingestion failed: {e}")
        return None


def ingest_movie_metadata(sample_size=50):
    """Source 2: Ingest movie metadata from OMDb API (external source) with retries."""
    try:
        item_path = os.path.join(RAW_DIR, "ml-100k", "u.item")
        movies = pd.read_csv(
            item_path, sep="|", encoding="latin-1", header=None, usecols=[0, 1]
        )
        movies.columns = ["item_id", "title"]

        # Clean year out of title, e.g. "Toy Story (1995)" -> "Toy Story"
        movies["clean_title"] = movies["title"].str.replace(r"\s*\(\d{4}\)", "", regex=True)

        sample = movies.head(sample_size)
        records = []

        for _, row in sample.iterrows():
            title = row["clean_title"]
            success = False
            attempt = 0

            while not success and attempt < MAX_RETRIES:
                attempt += 1
                try:
                    resp = requests.get(
                        "http://www.omdbapi.com/",
                        params={"t": title, "apikey": OMDB_API_KEY},
                        timeout=5
                    )
                    data = resp.json()

                    if data.get("Response") == "True":
                        records.append({
                            "item_id": row["item_id"],
                            "title": title,
                            "imdb_rating": data.get("imdbRating"),
                            "genre": data.get("Genre"),
                            "metascore": data.get("Metascore")
                        })
                        logger.info(f"SUCCESS | Fetched metadata for '{title}'")
                        success = True
                    else:
                        logger.warning(f"NOT FOUND | '{title}' -> {data.get('Error')}")
                        success = True  # don't retry on "not found", only on network errors

                except requests.exceptions.RequestException as e:
                    logger.warning(f"RETRY {attempt}/{MAX_RETRIES} | '{title}' error: {e}")
                    time.sleep(RETRY_DELAY)

            if not success:
                logger.error(f"FAILED | Could not fetch metadata for '{title}' after {MAX_RETRIES} attempts")

        df = pd.DataFrame(records)
        out_dir = os.path.join(RAW_DIR, "metadata", TODAY)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "movie_metadata.csv")
        df.to_csv(out_path, index=False)

        logger.info(f"SUCCESS | Ingested metadata for {len(df)} movies -> {out_path}")
        print(f"[OK] Ingested metadata for {len(df)} movies -> {out_path}")
        return df

    except Exception as e:
        logger.error(f"FAILED | Metadata ingestion error: {e}")
        print(f"[FAIL] Metadata ingestion failed: {e}")
        return None


if __name__ == "__main__":
    print("Starting RecoMart data ingestion...")
    logger.info("=== Ingestion run started ===")

    ratings_df = ingest_ratings()
    metadata_df = ingest_movie_metadata(sample_size=50)

    logger.info("=== Ingestion run finished ===")
    print("Ingestion complete. Check logs/ folder for details.")

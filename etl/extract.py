import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

fake = Faker()
np.random.seed(42)
random.seed(42)

GENRE_ARTISTS = {
    "pop":        ["Taylor Swift", "Ed Sheeran", "Dua Lipa", "Harry Styles", "Olivia Rodrigo", "Ariana Grande", "Billie Eilish"],
    "hip-hop":    ["Drake", "Kendrick Lamar", "Travis Scott", "J. Cole", "Post Malone", "Nicki Minaj", "Cardi B"],
    "rock":       ["Arctic Monkeys", "Imagine Dragons", "Coldplay", "Radiohead", "Linkin Park", "Foo Fighters", "The Killers"],
    "electronic": ["Calvin Harris", "Martin Garrix", "Disclosure", "Aphex Twin", "Four Tet", "Bicep", "Bonobo"],
    "r-n-b":      ["SZA", "Frank Ocean", "Beyonce", "The Weeknd", "H.E.R.", "Jhene Aiko", "Ella Mai"]
}

GENRE_POPULARITY = {
    "pop":        (55, 95),
    "hip-hop":    (50, 90),
    "rock":       (40, 85),
    "electronic": (30, 80),
    "r-n-b":      (45, 88)
}

# Messy genre label variants — simulates inconsistent data entry
GENRE_MESSY_LABELS = {
    "pop":        ["pop", "Pop", "POP", "pop music", ""],
    "hip-hop":    ["hip-hop", "Hip-Hop", "HIP-HOP", "hip hop", "hiphop"],
    "rock":       ["rock", "Rock", "ROCK", "Rock Music", ""],
    "electronic": ["electronic", "Electronic", "ELECTRONIC", "electro", "EDM"],
    "r-n-b":      ["r-n-b", "R&B", "rnb", "RNB", "r&b"]
}

def messy_release_date():
    """Generate dates in inconsistent formats — like real scraped data."""
    start = datetime(2015, 1, 1)
    end   = datetime(2024, 12, 31)
    date  = start + timedelta(days=random.randint(0, (end - start).days))

    # Randomly pick a date format
    fmt = random.choice([
        "%Y-%m-%d",    # 2024-01-15  (correct format)
        "%d/%m/%Y",    # 15/01/2024
        "%m-%d-%Y",    # 01-15-2024
        "%b %Y",       # Jan 2024    (missing day)
        "%Y",          # 2024        (missing month and day)
        None           # missing date entirely
    ])

    if fmt is None:
        return np.nan
    return date.strftime(fmt)

def messy_explicit(value):
    """Simulate inconsistent explicit flags."""
    if value is True:
        return random.choice([True, "yes", "1", 1, "True", "explicit"])
    else:
        return random.choice([False, "no", "0", 0, "False", "clean", ""])

def generate_tracks(n_per_genre=3000):
    """
    Generate realistic + messy Spotify-style track data.
    15,000 records with real-world data quality issues.
    """
    print("Generating realistic messy Spotify-style data...")

    tracks = []

    for genre, artists in GENRE_ARTISTS.items():
        low, high = GENRE_POPULARITY[genre]

        for i in range(n_per_genre):

            # --- Intentional missing values ---
            artist_name  = random.choice(artists) if random.random() > 0.05 else np.nan   # 5% missing
            album_name   = f"{fake.word().capitalize()} {fake.word().capitalize()}" if random.random() > 0.08 else ""  # 8% empty string
            track_name   = f"{fake.word().capitalize()} {fake.word().capitalize()}" if random.random() > 0.03 else np.nan  # 3% missing

            # --- Messy popularity scores ---
            popularity = int(np.clip(np.random.normal((low + high) / 2, (high - low) / 6), 0, 100))
            if random.random() < 0.04:
                popularity = random.choice([np.nan, -1, 101, 999, ""])   # 4% corrupted

            # --- Messy duration ---
            duration_ms = random.randint(150000, 270000)
            if random.random() < 0.03:
                duration_ms = random.choice([-1000, 0, 999999999, np.nan])  # 3% corrupted

            # --- Duplicate records (3% chance) ---
            repeat = 2 if random.random() < 0.03 else 1

            for _ in range(repeat):
                tracks.append({
                    "track_id":     f"{genre[:3].upper()}{i:05d}",
                    "track_name":   track_name,
                    "artist_name":  artist_name,
                    "album_name":   album_name,
                    "popularity":   popularity,
                    "duration_ms":  duration_ms,
                    "explicit":     messy_explicit(random.random() < 0.3),
                    "release_date": messy_release_date(),
                    "genre":        random.choice(GENRE_MESSY_LABELS[genre])
                })

    df = pd.DataFrame(tracks)

    # Shuffle so duplicates and nulls are spread randomly
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    print(f"Total records generated : {len(df)}")
    print(f"Missing artist_name     : {df['artist_name'].isna().sum()}")
    print(f"Missing track_name      : {df['track_name'].isna().sum()}")
    print(f"Empty album_name        : {(df['album_name'] == '').sum()}")
    print(f"Missing release_date    : {df['release_date'].isna().sum()}")
    print(f"Duplicate track_ids     : {df.duplicated(subset='track_id').sum()}")
    return df


if __name__ == "__main__":
    df = generate_tracks(n_per_genre=3000)

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/raw_tracks.csv", index=False)

    print("\nSample data:")
    print(df.head(10))
    print("\nSaved to data/raw_tracks.csv")  
import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

fake = Faker('en_GB')
np.random.seed(456)
random.seed(456)

# Constants 

# Funnel stages in order — user must go through them sequentially
FUNNEL_STAGES = [
    "app_open",
    "search_browse",
    "track_preview",
    "full_play",
    "artist_follow",
    "premium_conversion"
]

# Drop-off probabilities at each stage
# These are NOT pre-baked insights — they just ensure
# realistic funnel shape. SQL will calculate actual rates.
STAGE_CONTINUATION = {
    "app_open":           0.80,   # 80% continue after opening app
    "search_browse":      0.75,   # 75% of those preview a track
    "track_preview":      0.70,   # 70% of those play full track
    "full_play":          0.55,   # 55% of those follow artist
    "artist_follow":      0.35,   # 35% of those convert to premium
}

DEVICES   = ["mobile", "desktop", "tablet", "smart_tv"]
LOCATIONS = ["London", "Manchester", "Birmingham", "Leeds",
             "New York", "Los Angeles", "Mumbai", "Berlin",
             "Paris", "Sydney", "Toronto", "São Paulo"]

# Helper Functions 

def random_timestamp(start_year=2023, end_year=2024):
    """Generate a random timestamp."""
    start = datetime(start_year, 1, 1)
    end   = datetime(end_year, 12, 31)
    delta = end - start
    return start + timedelta(
        days=random.randint(0, delta.days),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )

def messy_timestamp(ts):
    """
    Inconsistent timestamp formats —
    simulates data coming from different app versions.
    """
    if random.random() < 0.04:
        return np.nan
    fmt = random.choice([
        "%Y-%m-%d %H:%M:%S",   # 2024-01-15 08:23:45  standard
        "%d/%m/%Y %H:%M",      # 15/01/2024 08:23     European
        "%Y-%m-%dT%H:%M:%SZ",  # 2024-01-15T08:23:45Z ISO format
        "%m/%d/%Y %I:%M %p",   # 01/15/2024 08:23 AM  US format
    ])
    return ts.strftime(fmt)

def introduce_nulls(value, null_rate=0.04):
    """Randomly replace value with null-like entry."""
    if random.random() < null_rate:
        return random.choice([np.nan, None, "", "unknown"])
    return value

def corrupt_number(value, corrupt_rate=0.03):
    """Randomly corrupt numeric values."""
    if random.random() < corrupt_rate:
        return random.choice([-1, 99999, np.nan])
    return value

# Session Generator 

def generate_session(user_id, track_ids, session_id, base_timestamp):
    """
    Generate one user session — a sequence of funnel events.
    User starts at app_open and drops off at some point.
    Each session is tied to one primary track.
    """
    events     = []
    track_id   = random.choice(track_ids)
    device     = random.choice(DEVICES)
    location   = random.choice(LOCATIONS)
    current_ts = base_timestamp

    for stage in FUNNEL_STAGES:
        # Always generate app_open — every session starts here
        events.append({
            "session_id":       session_id,
            "user_id":          user_id,
            "track_id":         introduce_nulls(track_id,  null_rate=0.02),
            "event_type":       stage,
            "timestamp":        messy_timestamp(current_ts),
            "device":           introduce_nulls(device,    null_rate=0.03),
            "location":         introduce_nulls(location,  null_rate=0.05),
            "session_duration_secs": corrupt_number(
                                    random.randint(10, 3600),
                                    corrupt_rate=0.03
                                ),
        })

        # Advance timestamp slightly for next event
        current_ts += timedelta(seconds=random.randint(30, 300))

        # After each stage decide if user continues or drops off
        if stage in STAGE_CONTINUATION:
            if random.random() > STAGE_CONTINUATION[stage]:
                break   # user dropped off — stop generating events

    return events

# Main Events Generator 

def generate_events(users_df, tracks_df, sessions_per_user=25):
    """
    Generate raw messy event data linking users to tracks.
    Each user has multiple sessions — each session is a funnel journey.
    """
    print("Generating event data...")

    # Get clean user_ids and track_ids to reference
    user_ids  = users_df["user_id"].dropna().unique().tolist()
    track_ids = tracks_df["track_id"].dropna().unique().tolist()

    all_events = []
    session_counter = 1

    for user_id in user_ids:
        # Each user has a random number of sessions
        n_sessions = random.randint(1, sessions_per_user)

        for _ in range(n_sessions):
            session_id  = f"S{session_counter:07d}"
            base_ts     = random_timestamp(2023, 2024)

            session_events = generate_session(
                user_id, track_ids, session_id, base_ts
            )
            all_events.extend(session_events)
            session_counter += 1

    df = pd.DataFrame(all_events)

    # Add event_id column
    df.insert(0, "event_id", [f"E{i+1:07d}" for i in range(len(df))])

    # Add ~2% duplicate rows
    dupes = df.sample(frac=0.02, random_state=42)
    df    = pd.concat([df, dupes], ignore_index=True)
    df    = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Summary 
    print(f"Total events generated      : {len(df)}")
    print(f"Unique users                : {df['user_id'].nunique()}")
    print(f"Unique sessions             : {df['session_id'].nunique()}")
    print(f"Unique tracks referenced    : {df['track_id'].nunique()}")
    print(f"Missing timestamps          : {df['timestamp'].isna().sum()}")
    print(f"Duplicate rows              : {df.duplicated().sum()}")
    print(f"\nEvent type breakdown:")
    print(df["event_type"].value_counts())

    return df

# Main 

if __name__ == "__main__":
    # Load existing data so we can reference real user_ids and track_ids
    users_df  = pd.read_csv("data/users_data.csv")
    tracks_df = pd.read_csv("data/product_data.csv")

    df = generate_events(users_df, tracks_df, sessions_per_user=25)

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/events_data.csv", index=False)

    print("\nSample data:")
    print(df.head(10))
    print("\nSaved to data/events_data.csv")
import pandas as pd
import numpy as np
from dateutil import parser as dateparser
import os

# Load Raw Data 

def load_raw():
    tracks = pd.read_csv("data/product_data.csv")
    users  = pd.read_csv("data/users_data.csv")
    events = pd.read_csv("data/events_data.csv")
    print(f"Loaded — Tracks: {len(tracks):,} | Users: {len(users):,} | Events: {len(events):,}")
    return tracks, users, events

# Shared Helpers 

def parse_date(value):
    """
    Parse any date format into YYYY-MM-DD.
    Returns NaN if unparseable.
    """
    if pd.isna(value) or str(value).strip() in ["", "N/A", "unknown"]:
        return np.nan
    try:
        return dateparser.parse(str(value)).strftime("%Y-%m-%d")
    except:
        return np.nan

def parse_timestamp(value):
    """
    Parse any timestamp format into YYYY-MM-DD HH:MM:SS.
    Returns NaN if unparseable.
    """
    if pd.isna(value) or str(value).strip() in ["", "N/A", "unknown"]:
        return np.nan
    try:
        return dateparser.parse(str(value)).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return np.nan

def standardise_bool(value, true_values, false_values):
    """
    Convert messy boolean variants to 1/0.
    Returns NaN if unrecognised.
    """
    if pd.isna(value) or str(value).strip() in ["", "N/A", "unknown"]:
        return np.nan
    if str(value).strip().lower() in [str(v).lower() for v in true_values]:
        return 1
    if str(value).strip().lower() in [str(v).lower() for v in false_values]:
        return 0
    return np.nan

def replace_unknown(df, columns):
    """Replace 'unknown', 'N/A', empty strings with NaN."""
    for col in columns:
        df[col] = df[col].replace(
            ["unknown", "N/A", "", "Unknown", "UNKNOWN"], np.nan
        )
    return df

# Transform Tracks 

def transform_tracks(df):
    print("\nTransforming tracks...")
    original_len = len(df)

    # Standardise genre labels → 5 clean genres
    genre_map = {
        "pop": "pop", "Pop": "pop", "POP": "pop", "pop music": "pop",
        "hip-hop": "hip-hop", "Hip-Hop": "hip-hop", "HIP-HOP": "hip-hop",
        "hip hop": "hip-hop", "hiphop": "hip-hop",
        "rock": "rock", "Rock": "rock", "ROCK": "rock", "Rock Music": "rock",
        "electronic": "electronic", "Electronic": "electronic",
        "ELECTRONIC": "electronic", "electro": "electronic", "EDM": "electronic",
        "r-n-b": "r-n-b", "R&B": "r-n-b", "rnb": "r-n-b",
        "RNB": "r-n-b", "r&b": "r-n-b"
    }
    df["genre"] = df["genre"].map(genre_map)

    # Standardise explicit → 1/0
    df["explicit"] = df["explicit"].apply(
        lambda x: standardise_bool(
            x,
            true_values=  [True, "true", "1", 1, "yes", "explicit"],
            false_values= [False, "false", "0", 0, "no", "clean"]
        )
    )

    # Parse release_date → YYYY-MM-DD
    df["release_date"] = df["release_date"].apply(parse_date)

    # Fix corrupted popularity — must be 0-100
    df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce")
    df.loc[df["popularity"] < 0,   "popularity"] = np.nan
    df.loc[df["popularity"] > 100, "popularity"] = np.nan

    # Fix corrupted duration — must be between 30s and 10 mins in ms
    df["duration_ms"] = pd.to_numeric(df["duration_ms"], errors="coerce")
    df.loc[df["duration_ms"] < 30000,    "duration_ms"] = np.nan
    df.loc[df["duration_ms"] > 600000,   "duration_ms"] = np.nan

    # Fill missing text fields
    df["artist_name"] = df["artist_name"].fillna("Unknown Artist")
    df["album_name"]  = df["album_name"].fillna("Unknown Album")
    df["track_name"]  = df["track_name"].fillna("Unknown Track")

    # Summary
    print(f"  Rows before : {original_len:,}")
    print(f"  Rows after  : {len(df):,}")
    print(f"  Nulls in genre   : {df['genre'].isna().sum()}")
    print(f"  Nulls in explicit: {df['explicit'].isna().sum()}")
    print(f"  Genre distribution:\n{df['genre'].value_counts()}")

    return df

#  Transform Users 

def transform_users(df):
    print("\nTransforming users...")
    original_len = len(df)

    # Remove duplicates
    df = df.drop_duplicates()
    print(f"  Removed {original_len - len(df)} duplicate rows")

    # Replace unknown-like values with NaN
    df = replace_unknown(df, [
        "age_group", "gender", "country", "device_type",
        "signup_source", "subscription_plan", "payment_method"
    ])

    # Standardise boolean columns → 1/0
    df["is_premium"] = df["is_premium"].apply(
        lambda x: standardise_bool(
            x,
            true_values=  ["premium", "yes", "1", 1, "true", True],
            false_values= ["free", "no", "0", 0, "false", False]
        )
    )
    df["free_trial_used"] = df["free_trial_used"].apply(
        lambda x: standardise_bool(
            x,
            true_values=  ["yes", "1", 1, "true", True],
            false_values= ["no", "0", 0, "false", False]
        )
    )
    df["cancelled_subscription"] = df["cancelled_subscription"].apply(
        lambda x: standardise_bool(
            x,
            true_values=  ["yes", "1", 1, "true", True, "churned"],
            false_values= ["no", "0", 0, "false", False, "active"]
        )
    )

    # Parse all date columns → YYYY-MM-DD
    date_cols = [
        "signup_date", "trial_end_date",
        "subscription_date", "cancellation_date", "last_active_date"
    ]
    for col in date_cols:
        df[col] = df[col].apply(parse_date)

    # Convert monthly_cost to float
    df["monthly_cost"] = pd.to_numeric(df["monthly_cost"], errors="coerce")

    # Fix corrupted engagement values
    df["daily_listening_mins"] = pd.to_numeric(df["daily_listening_mins"], errors="coerce")
    df.loc[df["daily_listening_mins"] < 0,    "daily_listening_mins"] = np.nan
    df.loc[df["daily_listening_mins"] > 1440, "daily_listening_mins"] = np.nan  # max 24hrs

    df["skip_rate"] = pd.to_numeric(df["skip_rate"], errors="coerce")
    df.loc[df["skip_rate"] < 0, "skip_rate"] = np.nan
    df.loc[df["skip_rate"] > 1, "skip_rate"] = np.nan  # must be 0.0-1.0

    df["repeat_play_count"] = pd.to_numeric(df["repeat_play_count"], errors="coerce")
    df.loc[df["repeat_play_count"] < 0,    "repeat_play_count"] = np.nan
    df.loc[df["repeat_play_count"] > 1000, "repeat_play_count"] = np.nan
    
    df["playlist_count"] = pd.to_numeric(df["playlist_count"], errors="coerce")
    df.loc[df["playlist_count"] < 0,   "playlist_count"] = np.nan
    df.loc[df["playlist_count"] > 500, "playlist_count"] = np.nan

    print(f"  Rows after cleaning : {len(df):,}")
    print(f"  Premium users       : {df['is_premium'].sum()}")
    print(f"  Cancelled users     : {df['cancelled_subscription'].sum()}")

    return df

# Transform Events 

def transform_events(df):
    print("\nTransforming events...")
    original_len = len(df)

    # Remove duplicates
    df = df.drop_duplicates()
    print(f"  Removed {original_len - len(df)} duplicate rows")

    # Parse timestamps → YYYY-MM-DD HH:MM:SS
    df["timestamp"] = df["timestamp"].apply(parse_timestamp)

    # Replace unknown-like values
    df = replace_unknown(df, ["device", "location"])

    # Fix corrupted session duration — must be between 1s and 24hrs
    df["session_duration_secs"] = pd.to_numeric(df["session_duration_secs"], errors="coerce")
    df.loc[df["session_duration_secs"] < 1,     "session_duration_secs"] = np.nan
    df.loc[df["session_duration_secs"] > 86400,  "session_duration_secs"] = np.nan

    print(f"  Rows after cleaning     : {len(df):,}")
    print(f"  Missing timestamps      : {df['timestamp'].isna().sum()}")
    print(f"  Event type breakdown:\n{df['event_type'].value_counts()}")

    return df

# Main 

if __name__ == "__main__":
    # Install dateutil if not present
    try:
        from dateutil import parser
    except ImportError:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dateutil"])

    tracks, users, events = load_raw()

    tracks_clean = transform_tracks(tracks)
    users_clean  = transform_users(users)
    events_clean = transform_events(events)

    os.makedirs("data", exist_ok=True)
    tracks_clean.to_csv("data/clean_tracks.csv", index=False)
    users_clean.to_csv("data/clean_users.csv",   index=False)
    events_clean.to_csv("data/clean_events.csv", index=False)

    print("\n All three clean files saved to data/")
    print(f"   clean_tracks.csv — {len(tracks_clean):,} rows")
    print(f"   clean_users.csv  — {len(users_clean):,} rows")
    print(f"   clean_events.csv — {len(events_clean):,} rows")
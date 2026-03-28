import pandas as pd
import numpy as np

# ── Load all three files ───────────────────────────────────────────────────────

tracks = pd.read_csv("data/product_data.csv")
users  = pd.read_csv("data/users_data.csv")
events = pd.read_csv("data/events_data.csv")

# ── Helper ─────────────────────────────────────────────────────────────────────

def inspect(df, name):
    print(f"\n{'='*60}")
    print(f"  {name.upper()}")
    print(f"{'='*60}")
    
    print(f"\n── Shape ──────────────────────────────────────────────────")
    print(f"Rows: {df.shape[0]:,}   Columns: {df.shape[1]}")
    
    print(f"\n── Column Types ───────────────────────────────────────────")
    print(df.dtypes)
    
    print(f"\n── Missing Values ─────────────────────────────────────────")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        "missing_count": missing,
        "missing_%": missing_pct
    })
    print(missing_df[missing_df["missing_count"] > 0])
    
    print(f"\n── Duplicate Rows ─────────────────────────────────────────")
    print(f"Duplicates: {df.duplicated().sum():,}")
    
    print(f"\n── Sample Data (5 rows) ───────────────────────────────────")
    print(df.head(5).to_string())
    
    print(f"\n── Unique Values per Column ───────────────────────────────")
    for col in df.columns:
        n_unique = df[col].nunique()
        if n_unique < 20:
            print(f"{col}: {df[col].unique()}")
        else:
            print(f"{col}: {n_unique} unique values")

# ── Run inspection ─────────────────────────────────────────────────────────────

inspect(tracks, "raw_tracks")
inspect(users,  "raw_users")
inspect(events, "raw_events")
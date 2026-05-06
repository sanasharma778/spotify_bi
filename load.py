import pandas as pd
import sqlite3
import os

# ── Load Clean CSVs ────────────────────────────────────────────────────────────

def load_clean_data():
    tracks = pd.read_csv("data/clean_tracks.csv")
    users  = pd.read_csv("data/clean_users.csv")
    events = pd.read_csv("data/clean_events.csv")
    print(f"Loaded — Tracks: {len(tracks):,} | Users: {len(users):,} | Events: {len(events):,}")
    return tracks, users, events

# ── Load into SQLite ───────────────────────────────────────────────────────────

def load_to_warehouse(tracks, users, events, db_path="data/warehouse.db"):
    """
    Load all three clean dataframes into SQLite database.
    Each dataframe becomes a table in the warehouse.
    """
    print(f"\nConnecting to warehouse: {db_path}")
    conn = sqlite3.connect(db_path)

    # Load tracks → dim_tracks table
    tracks.to_sql(
        "dim_tracks",       # table name
        conn,               # database connection
        if_exists="replace", # replace table if it already exists
        index=False         # don't write dataframe index as a column
    )
    print(f"  dim_tracks loaded    : {len(tracks):,} rows")

    # Load users → dim_users table
    users.to_sql(
        "dim_users",
        conn,
        if_exists="replace",
        index=False
    )
    print(f"  dim_users loaded     : {len(users):,} rows")

    # Load events → fact_events table
    events.to_sql(
        "fact_events",
        conn,
        if_exists="replace",
        index=False
    )
    print(f"  fact_events loaded   : {len(events):,} rows")

    return conn

# ── Verify Load ────────────────────────────────────────────────────────────────

def verify_warehouse(conn):
    """
    Run quick checks to confirm data loaded correctly.
    """
    print("\nVerifying warehouse...")

    tables = ["dim_tracks", "dim_users", "fact_events"]

    for table in tables:
        count = pd.read_sql(f"SELECT COUNT(*) as count FROM {table}", conn)
        print(f"  {table}: {count['count'][0]:,} rows")

    # Test a join across all three tables
    test_query = """
        SELECT 
            u.country,
            COUNT(DISTINCT e.user_id) as unique_users,
            COUNT(*)                  as total_events
        FROM fact_events e
        JOIN dim_users  u ON e.user_id  = u.user_id
        JOIN dim_tracks t ON e.track_id = t.track_id
        GROUP BY u.country
        ORDER BY total_events DESC
        LIMIT 5
    """
    print("\nTest join — top 5 countries by events:")
    result = pd.read_sql(test_query, conn)
    print(result.to_string(index=False))

# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    tracks, users, events = load_clean_data()
    conn = load_to_warehouse(tracks, users, events)
    verify_warehouse(conn)

    conn.close()
    print("\nWarehouse ready at data/warehouse.db")
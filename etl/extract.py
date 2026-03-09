import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from dotenv import load_dotenv
import os

# load secret keys from .env file
load_dotenv()

# connect to spotify API using the credentials
client_id=os.getenv("SPOTIFY_CLIENT_ID")
client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")

auth_manager = SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
    )
sp = spotipy.Spotify(auth_manager=auth_manager)

def get_tracks_by_genre(genre, limit=100):
     """
    Search Spotify for tracks in a given genre.
    Returns a clean dataframe of track info.
    """
     print(f"Fetching tracks for genre: {genre}...")

     tracks = []

     # Spotify returns max 50 per request, so we make 2 requests to get 100
     for offset in range(0, limit, 20):
        results = sp.search(
            q=f"genre:{genre}",
            type="track",
            limit=20,
            offset=offset
        )
        
        # Loop through each track returned
        for item in results["tracks"]["items"]:
            tracks.append({
                "track_id":     item["id"],
                "track_name":   item["name"],
                "artist_name":  item["artists"][0]["name"],
                "album_name":   item["album"]["name"],
                "popularity":   item["popularity"],    # Spotify score 0-100
                "duration_ms":  item["duration_ms"],   # length in milliseconds
                "explicit":     item["explicit"],      # True/False
                "release_date": item["album"]["release_date"],
                "genre":        genre
            })
            
        return pd.DataFrame(tracks)


def extract_all_genres():
    """
    Pull tracks across multiple genres and combine into one dataframe.
    """
    genres = ["pop", "hip-hop", "rock", "electronic", "r-n-b"]
    
    all_tracks = []
    
    for genre in genres:
        df = get_tracks_by_genre(genre)
        all_tracks.append(df)
    
    # Stack all genres into one big dataframe
    combined = pd.concat(all_tracks, ignore_index=True)
    
    # Remove duplicate tracks (same song can appear in multiple genre searches)
    combined = combined.drop_duplicates(subset="track_id")
    
    print(f"\nTotal tracks extracted: {len(combined)}")
    return combined


if __name__ == "__main__":
    df = extract_all_genres()
    print(df.head())
    
    # Save raw data so we don't need to call API every time
    df.to_csv("data/raw_tracks.csv", index=False)
    print("Saved to data/raw_tracks.csv")


import pandas as pd

# Change this to whichever file you want to look at
df = pd.read_csv("data/clean_tracks.csv")

print("\n Tracks")
print("── Shape ──────────────────────────────")
print(df.shape)

print("\n── First 5 rows ────────────────────────")
print(df.head())

print("\n── Column info ─────────────────────────")
print(df.info())

print("\n── Basic stats ─────────────────────────")
print(df.describe())

df = pd.read_csv("data/clean_events.csv")

print("\n Events")
print("── Shape ──────────────────────────────")
print(df.shape)

print("\n── First 5 rows ────────────────────────")
print(df.head())

print("\n── Column info ─────────────────────────")
print(df.info())

print("\n── Basic stats ─────────────────────────")
print(df.describe())

df = pd.read_csv("data/clean_users.csv")

print("\n Users")
print("── Shape ──────────────────────────────")
print(df.shape)

print("\n── First 5 rows ────────────────────────")
print(df.head())

print("\n── Column info ─────────────────────────")
print(df.info())

print("\n── Basic stats ─────────────────────────")
print(df.describe())
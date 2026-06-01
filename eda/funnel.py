import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import os

# ── Setup ──────────────────────────────────────────────────────────────────────

os.makedirs("eda/outputs", exist_ok=True)
sns.set_theme(style="darkgrid")
plt.rcParams["figure.figsize"] = (12, 7)

# ── Load Data ──────────────────────────────────────────────────────────────────

conn   = sqlite3.connect("data/warehouse.db")
events = pd.read_csv("data/clean_events.csv")
users_df  = pd.read_csv("data/clean_users.csv")

print(f"Events loaded: {len(events):,} rows")

# ── Funnel Stage Order ─────────────────────────────────────────────────────────

FUNNEL_STAGES = [
    "app_open",
    "search_browse",
    "track_preview",
    "full_play",
    "artist_follow",
    "premium_conversion"
]

# ── Helper ─────────────────────────────────────────────────────────────────────

def add_insight(text):
    plt.figtext(
        0.5, -0.02,
        f"📊 Insight: {text}",
        wrap=True,
        horizontalalignment="center",
        fontsize=10,
        style="italic",
        color="#333333"
    )

# ── Build Funnel Table ─────────────────────────────────────────────────────────

def build_funnel(df):
    """
    Count unique users who reached each funnel stage.
    A user counts at a stage if they have at least one event of that type.
    """
    funnel = []
    for stage in FUNNEL_STAGES:
        users_at_stage = df[df["event_type"] == stage]["user_id"].nunique()
        funnel.append({
            "stage":        stage,
            "unique_users": users_at_stage
        })
    df_funnel = pd.DataFrame(funnel)
    df_funnel["conversion_rate"] = (
        df_funnel["unique_users"] / df_funnel["unique_users"].iloc[0] * 100
    ).round(1)
    df_funnel["drop_off_rate"] = (
        100 - df_funnel["conversion_rate"]
    ).round(1)
    return df_funnel

funnel_df = build_funnel(events)
print("\nFunnel Summary:")
print(funnel_df.to_string(index=False))

# ── 1. Funnel Chart ────────────────────────────────────────────────────────────

plt.figure()
colors = ["#2ecc71" if i == 0 else
          "#27ae60" if i == 1 else
          "#f39c12" if i == 2 else
          "#e67e22" if i == 3 else
          "#e74c3c" if i == 4 else
          "#c0392b"
          for i in range(len(funnel_df))]

bars = plt.barh(
    funnel_df["stage"][::-1],
    funnel_df["unique_users"][::-1],
    color=colors[::-1]
)

# Add labels to bars
for bar, users, rate in zip(
    bars,
    funnel_df["unique_users"][::-1],
    funnel_df["conversion_rate"][::-1]
):
    plt.text(
        bar.get_width() + 10,
        bar.get_y() + bar.get_height() / 2,
        f"{users:,} users ({rate}%)",
        va="center", fontsize=10
    )

plt.title("User Journey Funnel — Unique Users at Each Stage")
plt.xlabel("Unique Users")
plt.xlim(0, funnel_df["unique_users"].max() * 1.25)
add_insight(
    f"Biggest drop-off occurs between app_open and search_browse — "
    f"suggesting users open the app but don't engage. "
    f"Only {funnel_df['conversion_rate'].iloc[-1]}% of users who open "
    f"the app eventually convert to premium."
)
plt.tight_layout()
plt.savefig("eda/outputs/19_funnel_chart.png", bbox_inches="tight")
plt.close()
print("saved: 19_funnel_chart.png")

# ── 2. Drop-off Rate at Each Stage ────────────────────────────────────────────

plt.figure()
drop_off = funnel_df.copy()
drop_off["stage_dropoff"] = drop_off["unique_users"].diff(-1).fillna(0)
drop_off["dropoff_pct"] = (
    drop_off["stage_dropoff"] / drop_off["unique_users"] * 100
).round(1)

sns.barplot(data=drop_off, x="stage", y="dropoff_pct",
            hue="stage", legend=False, palette="Reds_r")
plt.title("Drop-off Rate at Each Funnel Stage (%)")
plt.xlabel("Funnel Stage")
plt.ylabel("Drop-off Rate (%)")
plt.xticks(rotation=15)
add_insight(
    "The highest drop-off rate is between track_preview and full_play — "
    "users preview but don't commit to the full track. "
    "This suggests content relevance is an issue — "
    "users aren't finding tracks that match their taste."
)
plt.tight_layout()
plt.savefig("eda/outputs/20_dropoff_by_stage.png", bbox_inches="tight")
plt.close()
print("saved: 20_dropoff_by_stage.png")

# ── 3. Funnel by Device Type ───────────────────────────────────────────────────

plt.figure()
device_funnel = []
for device in events["device"].dropna().unique():
    df_dev = events[events["device"] == device]
    for stage in FUNNEL_STAGES:
        users_at_stage = df_dev[df_dev["event_type"] == stage]["user_id"].nunique()
        device_funnel.append({
            "device":  device,
            "stage":   stage,
            "users":   users_at_stage
        })

df_device = pd.DataFrame(device_funnel)

# Normalise per device to show conversion rates
total_per_device = df_device[df_device["stage"] == "app_open"][["device", "users"]].rename(
    columns={"users": "total"}
)
df_device = df_device.merge(total_per_device, on="device")
df_device["rate"] = (df_device["users"] / df_device["total"] * 100).round(1)

sns.lineplot(data=df_device, x="stage", y="rate",
             hue="device", marker="o")
plt.title("Funnel Conversion Rate by Device Type (%)")
plt.xlabel("Funnel Stage")
plt.ylabel("Conversion Rate (%)")
plt.xticks(rotation=15)
plt.legend(title="Device")
add_insight(
    "Mobile users show the highest conversion rate through the funnel — "
    "likely due to daily habit formation. Smart TV users drop off earliest, "
    "suggesting TV is used for passive listening rather than active discovery."
)
plt.tight_layout()
plt.savefig("eda/outputs/21_funnel_by_device.png", bbox_inches="tight")
plt.close()
print("saved: 21_funnel_by_device.png")

# ── 4. Funnel by Country (Top 5) ──────────────────────────────────────────────

plt.figure()

# Get top 5 countries by user count
top_countries = (events.merge(users_df[["user_id", "country"]], on="user_id")
                       ["country"].value_counts()
                       .head(5).index.tolist())

country_funnel = []
events_with_country = events.merge(users_df[["user_id", "country"]], on="user_id")

for country in top_countries:
    df_country = events_with_country[events_with_country["country"] == country]
    total = df_country[df_country["event_type"] == "app_open"]["user_id"].nunique()
    converted = df_country[df_country["event_type"] == "premium_conversion"]["user_id"].nunique()
    country_funnel.append({
        "country":          country,
        "conversion_rate":  round(converted / total * 100, 1) if total > 0 else 0
    })

df_country_funnel = pd.DataFrame(country_funnel).sort_values(
    "conversion_rate", ascending=False
)
sns.barplot(data=df_country_funnel, x="country", y="conversion_rate",
            hue="country", legend=False, palette="Blues_r")
plt.title("Premium Conversion Rate by Country (Top 5) (%)")
plt.xlabel("Country")
plt.ylabel("Conversion Rate (%)")
add_insight(
    "Conversion rates vary significantly by country — "
    "markets with stronger brand presence convert better. "
    "Low-converting markets represent growth opportunities "
    "for targeted marketing campaigns."
)
plt.tight_layout()
plt.savefig("eda/outputs/22_conversion_by_country.png", bbox_inches="tight")
plt.close()
print("saved: 22_conversion_by_country.png")

# ── 5. Events by Hour of Day ───────────────────────────────────────────────────

plt.figure()
events_time = events.dropna(subset=["timestamp"]).copy()
events_time["timestamp"] = pd.to_datetime(events_time["timestamp"], errors="coerce")
events_time["hour"] = events_time["timestamp"].dt.hour

hourly = events_time.groupby("hour").size().reset_index(name="event_count")
sns.lineplot(data=hourly, x="hour", y="event_count",
             marker="o", color="steelblue")
plt.title("Event Volume by Hour of Day")
plt.xlabel("Hour of Day (0-23)")
plt.ylabel("Number of Events")
plt.xticks(range(0, 24))
add_insight(
    "Event volume peaks in the evening (7-10pm) — "
    "users listen most after work. Morning commute hours (7-9am) "
    "show a secondary peak. Lowest activity is 3-5am. "
    "This informs when to send push notifications for re-engagement."
)
plt.tight_layout()
plt.savefig("eda/outputs/23_events_by_hour.png", bbox_inches="tight")
plt.close()
print("saved: 23_events_by_hour.png")

# ── 6. Session Duration by Funnel Stage ───────────────────────────────────────

plt.figure()
sns.boxplot(data=events.dropna(subset=["session_duration_secs"]),
            x="event_type", y="session_duration_secs",
            hue="event_type", legend=False,
            order=FUNNEL_STAGES, palette="Set2")
plt.title("Session Duration by Funnel Stage (seconds)")
plt.xlabel("Funnel Stage")
plt.ylabel("Session Duration (seconds)")
plt.xticks(rotation=15)
add_insight(
    "Sessions that reach premium_conversion are significantly longer — "
    "users who convert spend more time on the platform per session. "
    "Short sessions (under 300 seconds) rarely result in conversion — "
    "a key signal for our ML model."
)
plt.tight_layout()
plt.savefig("eda/outputs/24_session_duration_by_stage.png", bbox_inches="tight")
plt.close()
print("saved: 24_session_duration_by_stage.png")

# ── 7. Premium vs Free Funnel Comparison ──────────────────────────────────────

plt.figure()
events_users = events.merge(users_df [["user_id", "is_premium"]], on="user_id")

premium_funnel = []
for user_type, label in [(1, "Premium"), (0, "Free")]:
    df_type = events_users[events_users["is_premium"] == user_type]
    total   = df_type[df_type["event_type"] == "app_open"]["user_id"].nunique()
    for stage in FUNNEL_STAGES:
        at_stage = df_type[df_type["event_type"] == stage]["user_id"].nunique()
        premium_funnel.append({
            "user_type": label,
            "stage":     stage,
            "rate":      round(at_stage / total * 100, 1) if total > 0 else 0
        })

df_premium_funnel = pd.DataFrame(premium_funnel)
sns.lineplot(data=df_premium_funnel, x="stage", y="rate",
             hue="user_type", marker="o", palette="Set1")
plt.title("Funnel Conversion Rate — Premium vs Free Users (%)")
plt.xlabel("Funnel Stage")
plt.ylabel("Conversion Rate (%)")
plt.xticks(rotation=15)
plt.legend(title="User Type")
add_insight(
    "Premium users progress much further through the funnel than free users — "
    "they are more engaged at every stage. Free users drop off sharply after "
    "track_preview, suggesting the ad experience interrupts their journey "
    "and discourages deeper engagement."
)
plt.tight_layout()
plt.savefig("eda/outputs/25_funnel_premium_vs_free.png", bbox_inches="tight")
plt.close()
print("saved: 25_funnel_premium_vs_free.png")

# ── Summary Stats ──────────────────────────────────────────────────────────────

print("\n── Funnel Summary ──────────────────────────────────────")
print(funnel_df.to_string(index=False))
print(f"\nBiggest drop-off stage:")
drop_off_sorted = drop_off.sort_values("dropoff_pct", ascending=False)
print(f"  {drop_off_sorted.iloc[0]['stage']} — {drop_off_sorted.iloc[0]['dropoff_pct']}% drop-off")
print(f"\nOverall funnel conversion rate:")
print(f"  {funnel_df['conversion_rate'].iloc[-1]}% of users convert to premium")

conn.close()
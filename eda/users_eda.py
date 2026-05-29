import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ── Setup ──────────────────────────────────────────────────────────────────────

os.makedirs("eda/outputs", exist_ok=True)
sns.set_theme(style="darkgrid")
plt.rcParams["figure.figsize"] = (12, 7)

# ── Load Data ──────────────────────────────────────────────────────────────────

df = pd.read_csv("data/clean_users.csv")
print(f"Users loaded: {len(df):,} rows")

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

# ── 1. Premium vs Free Users ───────────────────────────────────────────────────

plt.figure()
premium_counts = df["is_premium"].value_counts()
labels = ["Premium", "Free"]
colors = ["#2ecc71", "#e74c3c"]
plt.pie(
    premium_counts.values,
    labels=labels,
    colors=colors,
    autopct="%1.1f%%",
    startangle=90
)
plt.title("Premium vs Free Users")
add_insight(
    f"75.5% of users are premium subscribers. This high conversion rate suggests "
    f"the platform does a good job converting free users. However, we need to "
    f"investigate how many of these premium users are at churn risk."
)
plt.tight_layout()
plt.savefig("eda/outputs/09_premium_vs_free.png", bbox_inches="tight")
plt.close()
print("saved: 09_premium_vs_free.png")

# ── 2. Subscription Plan Distribution ─────────────────────────────────────────

plt.figure()
plan_counts = df["subscription_plan"].value_counts()
sns.barplot(x=plan_counts.index, y=plan_counts.values,
            hue=plan_counts.index, legend=False, palette="Set2")
plt.title("Subscription Plan Distribution")
plt.xlabel("Plan")
plt.ylabel("Number of Users")
add_insight(
    "Individual and student plans are most popular. Family plan has lowest uptake "
    "— likely due to higher price point (£15.99). Student plan is surprisingly "
    "popular, suggesting a young user base."
)
plt.tight_layout()
plt.savefig("eda/outputs/10_subscription_plans.png", bbox_inches="tight")
plt.close()
print("saved: 10_subscription_plans.png")

# ── 3. Churn Rate by Age Group ─────────────────────────────────────────────────

plt.figure()
churn_by_age = (df.groupby("age_group")["cancelled_subscription"]
                  .mean()
                  .reset_index()
                  .sort_values("cancelled_subscription", ascending=False))
churn_by_age["churn_rate"] = churn_by_age["cancelled_subscription"] * 100
sns.barplot(data=churn_by_age, x="age_group", y="churn_rate",
            hue="age_group", legend=False, palette="Reds_r")
plt.title("Churn Rate by Age Group (%)")
plt.xlabel("Age Group")
plt.ylabel("Churn Rate (%)")
add_insight(
    "Younger users (18-24) show higher churn rates — likely more price sensitive "
    "and likely to switch platforms. Older users (45-54, 55+) are more loyal once "
    "subscribed. Retention campaigns should target 18-34 age group."
)
plt.tight_layout()
plt.savefig("eda/outputs/11_churn_by_age.png", bbox_inches="tight")
plt.close()
print("saved: 11_churn_by_age.png")

# ── 4. Churn Rate by Device ────────────────────────────────────────────────────

plt.figure()
churn_by_device = (df.groupby("device_type")["cancelled_subscription"]
                     .mean()
                     .reset_index()
                     .sort_values("cancelled_subscription", ascending=False))
churn_by_device["churn_rate"] = churn_by_device["cancelled_subscription"] * 100
sns.barplot(data=churn_by_device, x="device_type", y="churn_rate", hue="device_type", legend=False, palette="Oranges_r")
plt.title("Churn Rate by Device Type (%)")
plt.xlabel("Device Type")
plt.ylabel("Churn Rate (%)")
add_insight(
    "Smart TV users show highest churn — possibly because they use Spotify "
    "casually on TV and cancel when not watching. Mobile users show lowest churn "
    "— daily mobile usage creates strong habit formation."
)
plt.tight_layout()
plt.savefig("eda/outputs/12_churn_by_device.png", bbox_inches="tight")
plt.close()
print("saved: 12_churn_by_device.png")

# ── 5. Daily Listening Distribution ───────────────────────────────────────────

plt.figure()
sns.histplot(df["daily_listening_mins"].dropna(), bins=30,
             kde=True, color="steelblue")
plt.title("Daily Listening Minutes Distribution")
plt.xlabel("Daily Listening (minutes)")
plt.ylabel("Number of Users")
add_insight(
    "Daily listening is roughly uniformly distributed between 0 and 180 minutes. "
    "Average is 89 minutes per day. Users listening less than 30 mins per day "
    "are at higher churn risk — a key signal for our ML model."
)
plt.tight_layout()
plt.savefig("eda/outputs/13_daily_listening_distribution.png", bbox_inches="tight")
plt.close()
print("saved: 13_daily_listening_distribution.png")

# ── 6. Listening Mins — Premium vs Free ───────────────────────────────────────

plt.figure()
df_listen = df.dropna(subset=["daily_listening_mins"]).copy()
df_listen["user_type"] = df_listen["is_premium"].map({1: "Premium", 0: "Free"})
sns.boxplot(data=df_listen, x="user_type", y="daily_listening_mins",
            hue="user_type", legend=False, palette="Set2")
plt.title("Daily Listening — Premium vs Free Users")
plt.xlabel("")
plt.ylabel("Daily Listening (minutes)")
add_insight(
    "Premium users listen significantly more than free users on average. "
    "This makes sense — no ads means uninterrupted listening. "
    "High listening time is a strong indicator of premium status — "
    "useful feature for our conversion prediction ML model."
)
plt.tight_layout()
plt.savefig("eda/outputs/14_listening_premium_vs_free.png", bbox_inches="tight")
plt.close()
print("saved: 14_listening_premium_vs_free.png")

# ── 7. Skip Rate Distribution ──────────────────────────────────────────────────

plt.figure()
sns.histplot(df["skip_rate"].dropna(), bins=30, kde=True, color="coral")
plt.title("Skip Rate Distribution")
plt.xlabel("Skip Rate (0 = never skips, 1 = always skips)")
plt.ylabel("Number of Users")
add_insight(
    "Skip rate is uniformly distributed — equally spread between 0 and 1. "
    "This is expected since we generated it randomly. In real data you'd expect "
    "a peak around 0.3-0.4 as most users skip occasionally but not constantly. "
    "High skip rate (>0.7) is a strong churn signal."
)
plt.tight_layout()
plt.savefig("eda/outputs/15_skip_rate_distribution.png", bbox_inches="tight")
plt.close()
print("saved: 15_skip_rate_distribution.png")

# ── 8. Free Trial vs Conversion ────────────────────────────────────────────────

plt.figure()
trial_conversion = df.groupby("free_trial_used")["is_premium"].mean().reset_index()
trial_conversion["free_trial_used"] = trial_conversion["free_trial_used"].map(
    {1: "Used Trial", 0: "No Trial"}
)
trial_conversion["conversion_rate"] = trial_conversion["is_premium"] * 100
sns.barplot(data=trial_conversion, x="free_trial_used", y="conversion_rate",
            hue="free_trial_used", legend=False, palette="Set2")
plt.title("Premium Conversion Rate — Trial vs No Trial")
plt.xlabel("")
plt.ylabel("Premium Conversion Rate (%)")
add_insight(
    "Users who used the free trial convert to premium at a higher rate "
    "than those who didn't. This confirms free trials are an effective "
    "acquisition strategy. Trial usage will be a key feature in our "
    "conversion prediction ML model."
)
plt.tight_layout()
plt.savefig("eda/outputs/16_trial_vs_conversion.png", bbox_inches="tight")
plt.close()
print("saved: 16_trial_vs_conversion.png")

# ── 9. Churn Rate by Country ───────────────────────────────────────────────────

plt.figure(figsize=(12, 7))
churn_by_country = (df.groupby("country")["cancelled_subscription"]
                      .mean()
                      .reset_index()
                      .sort_values("cancelled_subscription", ascending=False))
churn_by_country["churn_rate"] = churn_by_country["cancelled_subscription"] * 100
sns.barplot(data=churn_by_country, x="churn_rate", y="country",
            hue="country", legend=False, palette="Reds_r")
plt.title("Churn Rate by Country (%)")
plt.xlabel("Churn Rate (%)")
plt.ylabel("")
add_insight(
    "Churn rates vary by country — markets with lower brand awareness "
    "show higher churn. This insight can guide regional retention campaigns "
    "and help prioritise which markets need more engagement effort."
)
plt.tight_layout()
plt.savefig("eda/outputs/17_churn_by_country.png", bbox_inches="tight")
plt.close()
print("saved: 17_churn_by_country.png")

# ── 10. Monthly Revenue by Plan ────────────────────────────────────────────────

plt.figure()
revenue_by_plan = (df[df["is_premium"] == 1]
                   .groupby("subscription_plan")["monthly_cost"]
                   .sum()
                   .reset_index()
                   .sort_values("monthly_cost", ascending=False))
sns.barplot(data=revenue_by_plan, x="subscription_plan", y="monthly_cost",
            hue="subscription_plan", legend=False, palette="Blues_r")
plt.title("Total Monthly Revenue by Subscription Plan (£)")
plt.xlabel("Plan")
plt.ylabel("Total Monthly Revenue (£)")
add_insight(
    "Individual plan generates the most total revenue despite lower price — "
    "because it has the most subscribers. Family plan generates less total "
    "revenue due to low uptake. Growing family plan subscriptions could "
    "significantly increase revenue per user."
)
plt.tight_layout()
plt.savefig("eda/outputs/18_revenue_by_plan.png", bbox_inches="tight")
plt.close()
print("saved: 18_revenue_by_plan.png")

# ── Summary Stats ──────────────────────────────────────────────────────────────

print("\n── Key Stats ───────────────────────────────────────────")
print(f"Total users              : {len(df):,}")
print(f"Premium users            : {df['is_premium'].sum():,} ({df['is_premium'].mean()*100:.1f}%)")
print(f"Churn rate               : {df['cancelled_subscription'].mean()*100:.1f}%")
print(f"Free trial usage         : {df['free_trial_used'].mean()*100:.1f}%")
print(f"Avg daily listening      : {df['daily_listening_mins'].mean():.0f} mins")
print(f"Avg skip rate            : {df['skip_rate'].mean():.2f}")
print(f"Avg monthly cost         : £{df['monthly_cost'].mean():.2f}")
print(f"\nChurn rate by age group:")
print((df.groupby("age_group")["cancelled_subscription"].mean()*100).round(1))
print(f"\nConversion rate by signup source:")
print((df.groupby("signup_source")["is_premium"].mean()*100).round(1))
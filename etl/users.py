import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

fake = Faker('en_GB')
np.random.seed(123)
random.seed(123)

# Constants

N_USERS = 2000

# Weighted — reflects real world known facts, not insights
COUNTRIES = {
    "UK": 0.45, "US": 0.20, "India": 0.10,
    "Germany": 0.07, "France": 0.06, "Brazil": 0.05,
    "Australia": 0.04, "Canada": 0.03
}

DEVICES = {
    "mobile": 0.55, "desktop": 0.25,
    "tablet": 0.12, "smart_tv": 0.08
}

# Unweighted — purely random so SQL discovers real patterns
AGE_GROUPS     = ["18-24", "25-34", "35-44", "45-54", "55+"]
GENDERS        = ["M", "F", "Other", "Prefer not to say"]
SIGNUP_SOURCES = ["organic", "social_media", "referral", "ad", "unknown"]
PLANS          = ["individual", "student", "family", "free"]
PAYMENT_METHODS = ["card", "paypal", "google_pay", "apple_pay"]

PLAN_COSTS = {
    "individual": 9.99,
    "student":    4.99,
    "family":     15.99,
    "free":       0.00
}

# Helper Functions

def weighted_choice(options_dict):
    """Pick randomly based on probability weights."""
    keys   = list(options_dict.keys())
    values = list(options_dict.values())
    return random.choices(keys, weights=values, k=1)[0]

def random_date(start_year=2021, end_year=2024):
    """Generate a random date between two years."""
    start = datetime(start_year, 1, 1)
    end   = datetime(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

def messy_date(date):
    """
    Return date in inconsistent formats.
    Simulates data coming from multiple systems.
    """
    if date is None:
        return np.nan
    fmt = random.choice([
        "%Y-%m-%d",   # 2024-01-15   standard
        "%d/%m/%Y",   # 15/01/2024   European
        "%m-%d-%Y",   # 01-15-2024   US style
        "%b %Y",      # Jan 2024     missing day
        "%Y",         # 2024         missing month and day
    ])
    return date.strftime(fmt)

def messy_bool(value, true_variants, false_variants):
    """
    Simulate inconsistent boolean values.
    Different systems store True/False differently.
    """
    if value:
        return random.choice(true_variants)
    return random.choice(false_variants)

def introduce_nulls(value, null_rate=0.05):
    """Randomly replace value with a null-like entry."""
    if random.random() < null_rate:
        return random.choice([np.nan, None, "", "N/A", "unknown"])
    return value

def corrupt_number(value, corrupt_rate=0.03):
    """Randomly corrupt numeric values to simulate bad data."""
    if random.random() < corrupt_rate:
        return random.choice([-1, -999, 99999, np.nan])
    return value

# User Profile Generator 

def generate_users(n=N_USERS):
    """
    Generate raw messy user profile data.
    No derived metrics or pre-baked insights —
    all insights will be discovered via SQL and Python.
    """
    print(f"Generating {n} user profiles...")
    users = []

    for i in range(n):

        # Core identity 
        user_id     = f"U{i+1:05d}"
        age_group   = random.choice(AGE_GROUPS)       # unweighted
        gender      = random.choice(GENDERS)           # unweighted
        country     = weighted_choice(COUNTRIES)       # weighted — known fact
        device      = weighted_choice(DEVICES)         # weighted — known fact
        signup_src  = random.choice(SIGNUP_SOURCES)    # unweighted
        signup_date = random_date(2021, 2023)

        # Free trial 
        # Raw fact only — SQL will tell us if trial users convert more
        free_trial_used = random.choice([True, False])
        trial_end_date  = (
            signup_date + timedelta(days=30)
            if free_trial_used else None
        )

        # Subscription 
        # Purely random — SQL will discover which plan is most popular
        plan       = random.choice(PLANS)
        is_premium = plan != "free"

        if is_premium:
            subscription_date = signup_date + timedelta(
                days=random.randint(0, 180)
            )
            monthly_cost   = PLAN_COSTS[plan]
            payment_method = random.choice(PAYMENT_METHODS)  # unweighted

            # Raw fact — SQL will calculate churn rate
            cancelled = random.choice([True, False])
            cancellation_date = (
                subscription_date + timedelta(days=random.randint(30, 730))
                if cancelled else None
            )
        else:
            subscription_date = None
            monthly_cost      = 0.00
            payment_method    = None
            cancelled         = False
            cancellation_date = None

        # Raw engagement facts 
        # Purely random ranges — SQL will find the patterns
        daily_listening_mins = random.randint(0, 180)
        skip_rate            = round(random.uniform(0.0, 1.0), 2)
        repeat_play_count    = random.randint(0, 100)
        playlist_count       = random.randint(0, 50)
        last_active_date     = random_date(2023, 2024)

        # Build row with messiness 
        users.append({
            "user_id":      user_id,

            # Demographics
            "age_group":        introduce_nulls(age_group,  null_rate=0.04),
            "gender":           introduce_nulls(gender,     null_rate=0.06),
            "country":          introduce_nulls(country,    null_rate=0.03),
            "device_type":      introduce_nulls(device,     null_rate=0.04),
            "signup_source":    introduce_nulls(signup_src, null_rate=0.07),

            # Dates — inconsistent formats
            "signup_date":          messy_date(signup_date) if random.random() > 0.03 else np.nan,
            "trial_end_date":       messy_date(trial_end_date) if trial_end_date else np.nan,
            "subscription_date":    messy_date(subscription_date) if subscription_date else np.nan,
            "cancellation_date":    messy_date(cancellation_date) if cancellation_date else np.nan,
            "last_active_date":     messy_date(last_active_date) if random.random() > 0.05 else np.nan,

            # Booleans — inconsistent representations
            "is_premium":   messy_bool(is_premium,
                                [True, "yes", "1", 1, "premium"],
                                [False, "no", "0", 0, "free"]),

            "free_trial_used": messy_bool(free_trial_used,
                                [True, "yes", "1"],
                                [False, "no", "0"]),

            "cancelled_subscription": messy_bool(cancelled,
                                [True, "yes", "churned"],
                                [False, "no", "active"]),

            # Subscription facts
            "subscription_plan":    introduce_nulls(plan,           null_rate=0.05),
            "monthly_cost":         introduce_nulls(monthly_cost,   null_rate=0.04),
            "payment_method":       introduce_nulls(payment_method, null_rate=0.06),

            # Engagement — with corruption
            "daily_listening_mins": corrupt_number(daily_listening_mins, corrupt_rate=0.04),
            "skip_rate":            corrupt_number(skip_rate,            corrupt_rate=0.04),
            "repeat_play_count":    corrupt_number(repeat_play_count,    corrupt_rate=0.03),
            "playlist_count":       corrupt_number(playlist_count,       corrupt_rate=0.03),
        })

    df = pd.DataFrame(users)

    # Add ~3% duplicate rows 
    dupes = df.sample(frac=0.03, random_state=42)
    df    = pd.concat([df, dupes], ignore_index=True)
    df    = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Summary 
    print(f"Total user records          : {len(df)}")
    print(f"Missing age_group           : {df['age_group'].isna().sum()}")
    print(f"Missing country             : {df['country'].isna().sum()}")
    print(f"Missing signup_date         : {df['signup_date'].isna().sum()}")
    print(f"Duplicate rows              : {df.duplicated().sum()}")
    print(f"\nPlan distribution:")
    print(df["subscription_plan"].value_counts())

    return df


# Main 

if __name__ == "__main__":
    df = generate_users(n=N_USERS)

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/users_data.csv", index=False)

    print("\nSample data:")
    print(df.head(10))
    print("\nSaved to data/users_data.csv")
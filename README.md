# Spotify User Journey Intelligence
### End-to-end BI + ML pipeline analysing music streaming behaviour

## Before starting the overview, I want to discuss "Why I built it/What's the motivation behind it"

I use Spotify every single day. Music is genuinely part of my routine. Either its commuting, working, winding down. Pop is my go-to, but like most Spotify users I've spent time on the free tier debating whether premium is worth it.

That question stuck with me! **what actually makes someone decide to pay?**

As a part of this profession I wanted to answer it properly. Not with guesswork, but with a full data pipeline. Messy raw data, ETL cleaning, SQL warehousing, exploratory analysis, and ML models that actually predict which free users will convert to premium and which premium users are about to leave.

This project is my attempt to think like a data scientist at Spotify or any recommendation system. Every decision in the pipeline, from how I structured the three-table warehouse to which features I chose for the churn model was made asking the same question: **what would actually be useful to a business?**

The part I found most exciting to work on are the machine learning models.

If you're a recruiter or fellow data scientist, feel free to explore the code, run the pipeline, or reach out on LinkedIn. Always happy to talk through the methodology.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![SQL](https://img.shields.io/badge/SQL-SQLite-lightgrey)
![ML](https://img.shields.io/badge/ML-Scikit--learn-orange)
![Status](https://img.shields.io/badge/Status-In%20Progress-yellow)

---

## 📌 Project Overview

Most streaming platforms lose users silently — they open the app, browse briefly, and disappear before ever converting to a paid subscriber. This project builds a full **Business Intelligence and Machine Learning pipeline** to understand exactly where and why users drop off, and predicts which users are most at risk of churning.

Built to replicate real-world data science workflows — messy data, ETL pipelines, SQL warehousing, EDA, and predictive ML models — the kind of work done daily at companies like Spotify, Amazon, and Netflix.

---

## 🎯 Business Questions Answered

| Question | Method |
|---|---|
| Where do users drop off in the funnel? | Funnel Analysis + SQL |
| Which users are likely to cancel? | Churn Prediction ML Model |
| Which free users will convert to premium? | Conversion Prediction ML Model |
| What makes a track popular? | Popularity Regression ML Model |
| Which demographics generate most revenue? | EDA + KPI Dashboard |
| Which device/country converts best? | Funnel EDA + SQL |

---

## 📊 Dataset

Three interconnected datasets simulating a real streaming platform warehouse:

| Table | Description | Rows |
|---|---|---|
| `dim_tracks` | Product catalogue : songs, artists, genres, popularity | 15,456 |
| `dim_users` | Customer profiles : demographics, subscription, engagement | 2,000 |
| `fact_events` | User activity log : every action in the funnel | 80,635 |

> **Why simulated data?** Spotify restricted developer API access in 2024-2025. Data was generated using statistically realistic distributions modelled on Spotify's actual data structure — standard practice in BI engineering when raw data is restricted or unavailable.

**Intentional data quality issues introduced:**
- Missing values (3-17% per column)
- Inconsistent date formats (`2024-01-15`, `15/01/2024`, `Jan 2024`)
- Messy boolean values (`True`, `"yes"`, `"1"`, `1`, `"premium"`)
- Corrupted numeric values (`-1`, `99999`, `NaN`)
- Duplicate rows (~3% of records)
- Inconsistent category labels (`"hip-hop"`, `"HIP-HOP"`, `"hip hop"`)

---

## 🏗️ Pipeline Architecture

RAW DATA          TRANSFORM         WAREHOUSE          ANALYSE
─────────         ─────────         ─────────          ───────
extract.py   →    transform.py  →   SQLite DB     →    EDA
users.py                            dim_tracks          ML Models
events.py                           dim_users           SQL Queries
fact_events         Dashboard
PDF Report

---

## 📁 Project Structure

spotify_bi/
├── etl/
│   ├── extract.py          # Track data generation (15K records)
│   ├── users.py            # User profile generation (2K records)
│   ├── events.py           # User event generation (80K records)
│   ├── inspect_data.py     # Data quality inspection
│   └── transform.py        # Data cleaning + standardisation
│
├── eda/
│   ├── tracks_eda.py       # Track analysis — 8 charts
│   ├── users_eda.py        # User behaviour analysis — 10 charts
│   ├── funnel_eda.py       # Funnel drop-off analysis — 7 charts
│   └── outputs/            # All generated charts (PNG)
│
├── ml/                     ← in progress
│   ├── churn_model.py      # Churn prediction (Random Forest)
│   ├── conversion_model.py # Premium conversion prediction
│   └── popularity_model.py # Track popularity regression
│
├── sql/                    ← in progress
│   ├── funnel_metrics.sql
│   ├── kpi_metrics.sql
│   └── weekly_report.sql
│
├── dashboard/              ← in progress
│   └── app.py              # Streamlit BI dashboard
│
├── reports/                ← in progress
│   └── auto_report.py      # Automated PDF report
│
├── data/
│   ├── raw files           # Original messy datasets
│   └── clean files         # Cleaned datasets
│
└── load.py                 # Loads clean data into SQLite warehouse

---

## 🔍 Key Findings — EDA

### Tracks
- **Pop dominates** — average popularity score 74.7, significantly ahead of electronic (54.3)
- **Shorter tracks perform better** — sweet spot is 2.5 to 3.5 minutes
- **Newer releases score higher** — Spotify's algorithm favours recent content
- **Explicit content has weak positive correlation** with popularity (0.08)

### Users
- **75.5% premium conversion rate** — high but 37.4% of those later churn
- **Free trial users convert at higher rate** — strongest acquisition signal
- **18-24 age group shows highest churn** — most price sensitive demographic
- **Mobile users churn least** — daily habit formation drives retention

### Funnel
- **Biggest drop-off: search → preview** — users browse but don't find relevant content
- **Only 12% of users who open the app convert to premium**
- **Premium users progress further at every funnel stage** than free users
- **Evening peak (7-10pm)** — best time for push notification campaigns

---

## 🤖 ML Models (In Progress)

| Model | Target | Algorithm | Status |
|---|---|---|---|
| Churn Prediction | Will user cancel? | Random Forest | 🔄 In Progress |
| Conversion Prediction | Will free user upgrade? | Logistic Regression + RF | 🔄 In Progress |
| Popularity Prediction | What makes track popular? | Linear Regression + RF | 🔄 In Progress |

---

## 🛠️ Tech Stack

| Category | Tools |
|---|---|
| Language | Python 3.11 |
| Data Processing | Pandas, NumPy |
| Visualisation | Matplotlib, Seaborn, Plotly |
| Machine Learning | Scikit-learn |
| Database | SQLite |
| Dashboard | Streamlit |
| Version Control | Git, GitHub |
| Reporting | ReportLab (PDF) |

---

## 🚀 How to Run

**1. Clone the repository**
```bash
git clone https://github.com/sanasharma778/spotify_bi.git
cd spotify_bi
```

**2. Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Generate data**
```bash
python etl/extract.py
python etl/users.py
python etl/events.py
```

**5. Clean data**
```bash
python etl/transform.py
```

**6. Load warehouse**
```bash
python load.py
```

**7. Run EDA**
```bash
python eda/tracks_eda.py
python eda/users_eda.py
python eda/funnel_eda.py
```

---

## 📈 Sample EDA Output

EDA charts are saved to `eda/outputs/` — 25 charts covering tracks, users and funnel analysis.

---

## 👩‍💻 Author

**Sana Sharma**
MSc Data Science & Analytics — Brunel University London
[LinkedIn](https://www.linkedin.com/in/sana-sharma-ab952625a) | [GitHub](https://github.com/sanasharma778)

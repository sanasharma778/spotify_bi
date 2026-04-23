# Spotify User Journey Funnel Analysis
### Full BI Pipeline | Python | SQL | ETL | Tableau Public | SQLite

---

## Project Overview
An end-to-end Business Intelligence pipeline analysing music streaming user behaviour
across 15,000+ records and 5 genres. Covers the full user journey funnel from app open
to premium conversion, with drop-off analysis, KPI reporting, and automated stakeholder
reports : replicating real-world BIE workflows.

---

## Project Structure
```
spotify-bi-pipeline/
├── etl/
│   └── extract.py           # Data generation - 15,000+ realistic messy records
├── data/
│   └── raw_tracks.csv       # Raw generated data
└── README.md
```

---

## Data
- 15,000+ records across 5 genres: Pop, Hip-Hop, Rock, Electronic, R&B
- Realistic messy data including:
  - Missing and null values (artist name, track name, release date)
  - Empty strings instead of nulls
  - Duplicate records
  - Inconsistent genre labels (e.g. "Hip-Hop", "hip hop", "HIP-HOP")
  - Inconsistent date formats (YYYY-MM-DD, DD/MM/YYYY, Jan 2024)
  - Corrupted popularity scores (negative values, scores over 100)
  - Corrupted duration values
- Simulated based on real Spotify data distributions (Spotify restricted
  developer API access for new apps in 2024)

---

## Tech Stack
| Area            | Tools                      |
|-----------------|----------------------------|
| Data Generation | Python, Faker, NumPy       |
| Version Control | Git, GitHub                |

---

## Status
- [x] Project setup — folder structure, virtual environment, GitHub
- [x] Data extraction — 15,000+ realistic messy records generated
- [x] Transform + clean pipeline
- [ ] Load into SQLite warehouse
- [ ] SQL KPI queries
- [ ] Tableau Public dashboard
- [ ] Automated PDF report

---

## Author
**Sana Sharma**

# UFC Stats

A data pipeline and (planned) analytics app for UFC fighter performance. It scrapes fighter data from [UFCStats.com](http://ufcstats.com) (fight data in progress), loads it into PostgreSQL, and will eventually score fighters with a custom **Fighter Viability Score** — a metric for career trajectory that looks past win/loss record.

> **Status:** early development. Stage 1 of the pipeline (fighter index → database) works end to end. Stage 2 (per-fighter fight history) is in progress. Everything under *Proposed Work* is designed but not built.

---

## Tech Stack

| Area | Tools |
|---|---|
| Language | Python 3.14 |
| Scraping | Playwright (headless Chromium), BeautifulSoup4 |
| Database | PostgreSQL, psycopg2 |
| Config | python-dotenv |

UFCStats pages need JavaScript to render, so pages are loaded with Playwright and then parsed with BeautifulSoup. Requests are spaced 5 seconds apart.

---

## Completed Work

### 1. Fighter index scraper — `backend/scraper/scraper.py`
- Builds the 26 index URLs (`/statistics/fighters?char=a…z&page=all`) and loads each with headless Chromium.
- Parses every fighter row: UFCStats fighter ID (from the profile link), first/last name, nickname, height, weight, reach, stance, and W-L-D record.
- Cleans values for the database: height `5' 9"` → `69` inches, weight `170 lbs.` → `170`, reach `"` stripped, `--` placeholders → empty.
- Writes results to `fighterinfo.csv`, quoting fields so nicknames with commas survive.

### 2. Database load — `backend/db/database_insertion.py`
- Connects to PostgreSQL using credentials from `.env` (never committed).
- Truncates `fighters`, then inserts each CSV row with a parameterized query.
- Converts numeric fields safely — empty or invalid values become `NULL` instead of crashing the load.

### 3. Schema — `backend/db/schema.sql`
- `fighters` table keyed on the 16-character UFCStats fighter ID.
- `fights` table drafted (fighters, winner, method, round, time, date); not yet populated.

---

## In Progress

### Fight history scraper — `backend/scraper/Individual_fighter_scraper.py`
- Pulls every `fighter_id` from the database and builds each fighter's profile URL.
- Loads profile pages with Playwright; parsing of the fight-history table is being written now (currently tested against a single fighter).

---

## Proposed Work

### Pipeline
- **Event scraper** — card name, date, location.
- **Fight detail scraper** — round-by-round stats and significant strikes by target (head/body/leg) and position.
- **Checkpointing** — a `scraped` flag per fight so re-runs only process new or incomplete fights.
- **Data quality** — a `data_status` per fight (`clean`, `incomplete`, `skipped`, `review`); cancelled fights and no contests are logged and skipped, missing rounds are flagged for review.
- **Historical odds** — merge betting odds from a public Kaggle UFC dataset, matched on date + normalized fighter names.

### Database
- Complete and populate the `fights` table.
- New tables: `events`, `rounds` (per-round stats for both fighters), and `fighter_stats` (cached career summaries: streaks, finish breakdowns, striking/grappling averages, strike location %).

### Fighter Viability Score
A scoring model I designed, weighted in this priority order:
1. **Opponent rank** — who you beat matters most (beating a top-5 opponent is worth far more than an unranked one).
2. **Finish quality** — KO/TKO and submissions weigh more than decisions.
3. **Strike differential** — sustained across full fights, not single exchanges.
4. **Benchmark results** — performance against division "measuring stick" fighters.
5. **Trajectory** — recency-weighted trend: is the fighter rising or declining?
6. **Noise flags** — adjustments for no contests, DQs, catchweights, and short-notice fights.

Scope decisions: UFC record only (pre-UFC history is flagged, not scored), and no title-shot prediction — too driven by matchmaking politics to model from fight data.

### Application
- REST API over the database.
- Frontend for exploring fighters, including visualizations of career arcs.
- Deployment with a hosted PostgreSQL instance.

---

## Running Locally

**Requirements:** Python 3.14, PostgreSQL running locally.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

Create a `.env` file in the project root:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ufcstats
DB_USER=your_user
DB_PASSWORD=your_password
```

Create the tables, scrape, and load:

```bash
psql -d ufcstats -f backend/db/schema.sql
python backend/scraper/scraper.py           # writes backend/scraper/fighterinfo.csv
python backend/db/database_insertion.py     # loads the CSV into the fighters table
```

---

## Project Structure

```
backend/
├── scraper/
│   ├── scraper.py                     # stage 1: fighter index → CSV
│   └── Individual_fighter_scraper.py  # stage 2: fight history (in progress)
├── db/
│   ├── schema.sql
│   └── database_insertion.py          # CSV → PostgreSQL
└── utilities.py                       # shared helpers
```

---

## Disclaimer

This is a personal, educational portfolio project. It is not affiliated with, endorsed by, or sponsored by the UFC, Zuffa, LLC, or UFCStats.com.

UFC is a registered trademark of Zuffa, LLC. All other names and marks belong to their respective owners.

All fight and fighter data belongs to its respective owners. I claim no ownership of it, and this project is not used for profit or any commercial purpose.

This repository contains only source code and a database schema. No scraped data is included or redistributed. The scraper is rate-limited to one request every 5 seconds to avoid placing load on the source site.

Data collected by this project may be incomplete or inaccurate, and nothing in this project is betting or financial advice.

If you are a rights holder and would like any content removed, please open an issue on this repository and I will address it promptly.

---

## License

The source code in this repository is released under the [MIT License](LICENSE). This license applies only to the code and does not grant any rights to third-party data.
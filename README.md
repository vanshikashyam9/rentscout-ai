# RentScout AI

**Before you send that deposit, check the listing.**

RentScout helps newcomers to Metro Vancouver avoid rental scams and make
smarter housing decisions. You bring a listing you found anywhere — Craigslist,
Facebook Marketplace, a WhatsApp group — and RentScout tells you whether it
looks legitimate, whether the price makes sense for that neighbourhood, and
whether you can actually afford it.

Built by a newcomer, for newcomers.

---

## Why I built this

As an international student, I learned the hard way that Vancouver's rental
market is confusing and full of scams that specifically target people like me:
people who don't know what rent *should* cost, don't know their tenant rights,
and need housing urgently.

Most rental sites just show listings. None of them help you *judge* a listing.
That's the gap RentScout fills.

## What it does

### 🔍 Scam check — the core feature
Paste any listing's title, price, and area. RentScout screens it for:

- **Payment red flags** — "wire transfer", "cash only", "deposit first"
- **Pressure tactics** — manufactured urgency, "first come first served"
- **Prices that are too good to be true** — checked against what the cheapest
  real listings in that *specific neighbourhood* actually cost, not a flat
  threshold

Each flag is explained in plain language, and every result carries the same
honest disclaimer: a clean scan is not a guarantee — never pay before viewing
a unit in person.

### 📊 Market data
Real vacancy rates for 29 Metro Vancouver zones, 2022–2025, from CMHC's annual
Rental Market Survey — with a plain-English reading of what the number means
for you ("tight market, move fast" vs "room to negotiate").

### 💰 Budget planner
Set your income and expenses on sliders and get a live verdict: Comfortable,
Tight but survivable, or Financially risky — plus a warning when rent crosses
the 30%-of-income guideline.

### 🏠 Search demo
A ranked rental search showing how RentScout scores affordability, with the
reasons behind each match. **The listings here are labelled samples** — see
the honesty note below.

## A note on honesty

RentScout does **not** republish listings from other platforms. There is no
legal way to bulk-scrape Craigslist or Facebook Marketplace, so rather than
pretend otherwise, the search page runs on clearly-labelled sample data and
the product focuses on what it can genuinely do: **screen the listing you
bring to it.** The market data, however, is real CMHC data.

## Tech stack

| Layer | Tech |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy |
| Database | PostgreSQL |
| Frontend | Next.js 16, TypeScript, Tailwind CSS |
| Auth | JWT + bcrypt |
| Data | CMHC Rental Market Survey (2022–2025) |
| Infra | Docker, docker-compose, GitHub Actions CI |

## Run it locally

The quick way (needs Docker):

```bash
cp .env.example .env       # then fill in SECRET_KEY
docker compose up --build
docker compose exec api python -m backend.seed_data --reset
```

Frontend: http://localhost:3000 · API: http://localhost:8000

<details>
<summary>Manual setup (no Docker)</summary>

```bash
# Backend — needs local Postgres running
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env       # fill in SECRET_KEY and DATABASE_URL
venv/bin/python -m backend.seed_data
venv/bin/uvicorn backend.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

</details>

Deploying? See [DEPLOYMENT.md](DEPLOYMENT.md).

## Project structure

```
rentscout-ai/
├── backend/
│   ├── main.py                  # FastAPI app and routes
│   ├── database/                # SQLAlchemy models + session
│   ├── services/
│   │   ├── listing_analyzer.py  # scam screening (weighted signals)
│   │   ├── market_intelligence.py  # CMHC vacancy data
│   │   ├── area_recommender.py  # neighbourhood recommendations
│   │   └── price_utils.py       # shared price parsing
│   ├── seed_data.py             # deterministic sample listings
│   └── scrape_craigslist.py     # local-only script, not exposed via API
├── frontend/
│   ├── app/                     # pages: /, /search, /budget, /market, /analyze
│   ├── components/              # Navbar, RentalCard, VacancyChart, MarketPulse
│   └── lib/                     # API client + shared types
├── data/processed/              # cleaned CMHC datasets
├── docker-compose.yml
└── .github/workflows/ci.yml    # lint, typecheck, build, API smoke tests
```

## What's next

- **RAG assistant** over the BC Residential Tenancy Act — ask "can my landlord
  raise rent mid-lease?" and get an answer with citations to the actual law
- User accounts UI (backend auth already works)
- Listing submission with automatic scam screening and a moderation queue
- Real listings from legitimately open sources (non-profit housing, university
  housing boards)

## Author

**Vanshika Shyam** — passionate about AI engineering, intelligent systems, and
building software around real user problems.

## Disclaimer

RentScout is an educational and portfolio project. The scam screen is an
automated heuristic, not a guarantee — always verify a rental in person before
paying anything.

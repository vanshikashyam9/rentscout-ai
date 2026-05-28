# RentScout AI

An AI-powered rental intelligence platform built for newcomers searching for housing in Vancouver & Metro Vancouver.

RentScout combines:

* conversational AI
* live rental scraping
* market analytics
* scam detection
* recommendation systems

to help users make smarter housing decisions in one of the most competitive rental markets in Canada.

---

# Why I Built This

As an international student and newcomer, I realized how difficult it is to:

* understand Vancouver’s rental market
* avoid scams
* compare neighborhoods
* estimate living costs
* find affordable housing quickly

Most rental platforms only show listings.
I wanted to build something that actually helps people make decisions intelligently.
So I built RentScout — an AI-powered housing assistant that combines real rental data, analytics, and conversational AI into one platform.

---

# Features

1. AI Rental Assistant

Users can ask natural language questions like:

* “Can I survive in Vancouver with $3000/month?”
* “Which area is best for students?”
* “Is Burnaby cheaper than Downtown?”
* “How competitive is Surrey right now?”

Powered using:

* OpenAI API
* GPT-4o-mini
* prompt engineering
* contextual system prompts



2. Interactive Budget Planner

Users can estimate monthly living expenses using sliders for:

* rent
* food
* transportation
* utilities
* miscellaneous expenses

The app calculates:

* total monthly expenses
* remaining savings
* affordability status

Example outputs:

* Comfortable
* Tight but survivable
* Not enough budget



3. AI Budget Explanation Panel

The AI explains *why* a user’s budget may or may not work in Vancouver.

Example:

> “Rent is consuming more than 60% of your income, which may make savings difficult in Downtown Vancouver.”

This creates a more personalized and intelligent experience.



4. Market Intelligence Engine

RentScout uses real CMHC (Canada Mortgage and Housing Corporation) rental market data from 2022–2025.

The platform analyzes:

* vacancy rates
* housing competitiveness
* historical rental trends
* Metro Vancouver regions

This allows the app to reason using real-world housing data instead of static AI responses.



5.  Vacancy Trend Dashboard

Interactive visualizations built using Plotly.

Users can:

* analyze rental market trends
* compare historical vacancy rates
* explore changes across multiple years



6. Multi-Area Comparison Tool

Users can compare multiple areas simultaneously, including:

* Downtown Vancouver
* Burnaby
* Surrey
* Richmond
* Langley
* New Westminster

This helps users understand:

* which areas are competitive
* where housing availability is improving
* how markets differ across Metro Vancouver



7. Smart Area Recommendation Engine

RentScout recommends neighborhoods based on:

* user budget
* vacancy rates
* housing competitiveness
* affordability assumptions

Example:

> Lower-budget users may receive recommendations for Surrey or New Westminster due to higher affordability and vacancy rates.

The recommendation engine uses:

* scoring systems
* ranking logic
* market intelligence



8. Live Craigslist Rental Scraper

RentScout fetches live rental listings directly from Vancouver Craigslist.

The scraper extracts:

* listing title
* price
* location
* listing URL

This creates a real-time rental discovery experience inside the app.

Built using:

* requests
* BeautifulSoup

---

9. AI Scam Detection System

Each rental listing is analyzed for scam risk.

The system detects:

* suspicious phrases
* unrealistic prices
* urgency tactics
* risky listing behavior

Example scam indicators:

* “deposit first”
* “cash only”
* “DM quickly”
* unusually cheap prices

Listings are classified as:

* Low Risk
* Medium Risk
* High Risk



## Tech Stack

### Frontend

* Streamlit
* Plotly

### AI

* OpenAI API
* GPT-4o-mini

### Data Engineering

* Pandas
* CMHC Rental Market Dataset

### Web Scraping

* BeautifulSoup
* Requests

### Python Libraries

* python-dotenv
* OpenAI SDK
* Plotly
* Pandas



# System Architecture

```text
User
 ↓
Streamlit UI
 ↓
OpenAI API
 ↓
Recommendation Engine
 ↓
Market Intelligence
 ↓
Live Craigslist Scraper
 ↓
Scam Detection
```



# Project Structure

```text
RentScout/
│
├── app.py
├── craigslist_scraper.py
├── listing_analyzer.py
├── area_recommender.py
├── market_intelligence.py
├── extract_cmhc.py
├── clean_market_data.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── requirements.txt
└── README.md
```

---

# Future Improvements

Planned upgrades:

* Facebook Marketplace integration
* Realtor.ca scraping
* ML-based scam detection
* vector search & embeddings
* personalized recommendation system
* semantic neighborhood search
* database integration
* user accounts & saved searches
* deployment pipeline



# What I Learned

This project helped me understand:

* AI application development
* prompt engineering
* recommendation systems
* data pipelines
* web scraping
* dashboard design
* real-world product thinking
* integrating AI with structured data

More importantly, it taught me how to design software around solving actual user problems.


# ⚠ Disclaimer

This project is for educational and portfolio purposes. Rental listings belong to their respective platforms and sources.


# Author

Built by Vanshika Shyam

Passionate about:

* AI engineering
* intelligent systems
* data-driven products
* solving real-world problems with software

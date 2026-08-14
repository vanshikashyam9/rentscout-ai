import sys
import os
import re

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
from backend.database.models import Base
from backend.database.database import engine
from backend.database.database import SessionLocal
from backend.database.models import Rental
from fastapi import Query
from passlib.context import CryptContext
from backend.database.models import User
from jose import JWTError, jwt
from datetime import datetime, timedelta
from backend.services.area_recommender import recommend_areas
from backend.services.listing_analyzer import analyze_listing
from backend.services.market_intelligence import (
    get_market_stats,
    get_vacancy_trend,
    list_zones,
)
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# Optional: without a key the app still runs; only /chat is disabled.
# Constructing the client eagerly would crash the whole API at import time
# on any host where OPENAI_API_KEY isn't configured.
_openai_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=_openai_key) if _openai_key else None

# Without this the root logger sits at WARNING and every logger.info below is
# silently dropped — including the "Database ready" line that tells you the
# deployment is actually healthy.
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(name)s: %(message)s",
)

logger = logging.getLogger("rentscout")


def _seed_if_empty():
    """
    Put the demo listings in place on a brand-new database.

    A fresh deployment has no rows, so search and recommendations return
    nothing and the site looks broken. Seeding from a laptop needs a publicly
    reachable database, which managed Postgres does not expose by default, so
    the app does it itself the first time it finds the table empty.

    Only ever runs against an empty table, so it cannot overwrite real data.
    """
    from backend.seed_data import run as seed_run

    db = SessionLocal()
    try:
        if db.query(Rental).count() > 0:
            return
    finally:
        db.close()

    logger.info("No listings found — seeding demo data.")
    seed_run()


async def _create_tables_with_retry():
    """
    Create tables once the database answers, retrying in the background.

    create_all is synchronous, so it runs in a worker thread — awaiting it on
    the event loop would stall every request while the database is down.
    """
    for attempt in range(1, 6):
        try:
            await asyncio.to_thread(Base.metadata.create_all, bind=engine)
            logger.info("Database ready.")
            try:
                await asyncio.to_thread(_seed_if_empty)
            except Exception as exc:
                # Seeding is a convenience; never let it take down the API.
                logger.error("Could not seed demo data: %s", exc)
            return
        except Exception as exc:
            wait = min(2 ** attempt, 15)
            logger.warning(
                "Database not ready (attempt %s/5): %s. Retrying in %ss.",
                attempt, exc, wait
            )
            await asyncio.sleep(wait)

    logger.error(
        "Could not reach the database after 5 attempts. The API is serving, "
        "but database endpoints will fail. Check DATABASE_URL."
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Kick off table creation without blocking startup.

    This used to run at import time, so a database that wasn't reachable yet
    killed the process before it could serve anything — and managed platforms
    routinely start the app before Postgres finishes booting. Retrying inline
    was no better: the platform's health check hits the port during those
    retries, gets nothing, and marks the deploy failed. So the server starts
    serving immediately and the database catches up behind it.
    """
    task = asyncio.create_task(_create_tables_with_retry())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)

# Comma-separated list, so the deployed frontend's origin can be added without
# a code change. Defaults to local dev.
#
# Trailing slashes are stripped: a browser's Origin header is scheme + host +
# port and never ends in one, so "https://site.com/" silently matches nothing.
# Pasting a URL straight from the address bar is the obvious thing to do, and
# it produced a site that loaded but showed no data anywhere.
ALLOWED_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000"
    ).split(",")
    if origin.strip().rstrip("/")
]

logger.info("CORS allowed origins: %s", ALLOWED_ORIGINS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# REQUEST MODEL
# -----------------------------

class ChatRequest(BaseModel):
    message: str

# -----------------------------
# CHAT ENDPOINT
# -----------------------------

def clean_price(price_str):

    return int(
        price_str.replace("$", "")
                 .replace(",", "")
                 .strip()
    )

@app.get("/")
def home():
    return {
        "message": "RentScout API Running"
    }

@app.post("/chat")

def chat(request: ChatRequest):

    if client is None:
        return {
            "error": "Chat is not configured on this server."
        }

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are RentScout AI."
            },
            {
                "role": "user",
                "content": request.message
            }
        ]
    )

    return {
        "reply": response.choices[0].message.content
    }

# NOTE: GET /rentals and POST /scrape used to live here and scraped Craigslist
# on request. Both were public and unauthenticated, so anyone could make this
# server scrape from its own IP — exactly the terms-of-service exposure the
# public deployment is meant to avoid. Neither was used by the frontend.
#
# The scraper is now a local-only script:
#     venv/bin/python -m backend.scrape_craigslist

@app.get("/rentals-db")
def get_rentals_db():

    db = SessionLocal()

    rentals = db.query(Rental).all()

    print("FOUND RENTALS:", len(rentals))

    data = []

    for rental in rentals:

        print(rental.title)

        data.append({
            "id": rental.id,
            "title": rental.title,
            "price": rental.price,
            "price_amount": rental.price_amount,
            "location": rental.location,
            "bedrooms": rental.bedrooms,
            "property_type": rental.property_type,
            "link": rental.link,
            "source": rental.source
        })

    db.close()

    return {
        "count": len(data),
        "rentals": data
    } 

@app.get("/rentals/search")
def search_rentals(

    location: str = None,
    max_price: int = None

):

    db = SessionLocal()

    query = db.query(Rental)

    # ------------------
    # LOCATION FILTER
    # ------------------

    if location:

        query = query.filter(
            Rental.location.ilike(f"%{location}%")
        )

    rentals = query.all()

    # ------------------
    # PRICE FILTER
    # ------------------

    results = []

    for rental in rentals:

        try:

            price_number = int(
                rental.price.replace("$", "")
                            .replace(",", "")
            )

        except:
            continue

        if max_price:

            if price_number > max_price:
                continue

        results.append({
            "id": rental.id,
            "title": rental.title,
            "price": rental.price,
            "price_amount": rental.price_amount,
            "location": rental.location,
            "bedrooms": rental.bedrooms,
            "property_type": rental.property_type,
            "link": rental.link,
            "source": rental.source
        })

    db.close()

    return {
        "count": len(results),
        "rentals": results
    }

@app.get("/analytics/average-rent")
def average_rent():

    db = SessionLocal()

    rentals = db.query(Rental).all()

    city_data = {}

    for rental in rentals:

        city = rental.location

        price = clean_price(rental.price)

        if city not in city_data:

            city_data[city] = []

        city_data[city].append(price)

    results = {}

    for city, prices in city_data.items():

        avg = sum(prices) / len(prices)

        results[city] = round(avg)

    db.close()

    return results

@app.get("/analytics/cheapest-areas")
def cheapest_areas():

    db = SessionLocal()

    rentals = db.query(Rental).all()

    city_data = {}

    for rental in rentals:

        city = rental.location

        price = clean_price(rental.price)

        city_data.setdefault(city, []).append(price)

    averages = []

    for city, prices in city_data.items():

        averages.append({

            "area": city,

            "avg_rent": round(sum(prices) / len(prices))
        })

    averages.sort(
        key=lambda x: x["avg_rent"]
    )

    db.close()

    return averages[:5]


@app.get("/analytics/expensive-areas")
def expensive_areas():

    db = SessionLocal()

    rentals = db.query(Rental).all()

    city_data = {}

    for rental in rentals:

        city = rental.location

        price = clean_price(rental.price)

        city_data.setdefault(city, []).append(price)

    averages = []

    for city, prices in city_data.items():

        averages.append({

            "area": city,

            "avg_rent": round(sum(prices) / len(prices))
        })

    averages.sort(
        key=lambda x: x["avg_rent"],
        reverse=True
    )

    db.close()

    return averages[:5]

    
@app.get("/recommendations")
def get_recommendations(
    max_price: int,
    location: str = None
):

    db = SessionLocal()

    rentals = db.query(Rental).all()

    results = []

    for rental in rentals:

        try:

            price = int(
                re.sub(
                    r"[^\d]",
                    "",
                    rental.price
                )
            )

        except:
            continue

        if price <= max_price:

            if location:

                if location.lower() not in rental.location.lower():
                    continue

            # Cheaper relative to budget scores higher.
            # At-budget = 70, cheapest approaches 100.
            ratio = price / max_price
            score = round(100 - (ratio * 30))

            reasons = []
            diff = max_price - price
            if diff >= 200:
                reasons.append(f"${diff} below your maximum budget")
            elif diff >= 0:
                reasons.append("Within your budget")
            if location and location.lower() in (rental.location or "").lower():
                reasons.append("In your preferred area")

            results.append({
                "id": rental.id,
                "title": rental.title,
                "price": rental.price,
                "price_amount": price,
                "location": rental.location,
                "bedrooms": rental.bedrooms,
                "property_type": rental.property_type,
                "link": rental.link,
                "source": rental.source,
                "score": score,
                "reasons": reasons
            })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    db.close()

    return {
        "count": len(results),
        "recommendations": results[:10]
    }

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

@app.post("/register")
def register(request: RegisterRequest):

    if not SECRET_KEY:
        return {
            "error": "Authentication is not configured on this server."
        }

    db = SessionLocal()

    existing_user = db.query(User).filter(
        User.email == request.email
    ).first()

    if existing_user:

        db.close()

        return {
            "error": "Email already exists"
        }

    hashed_password = pwd_context.hash(
        request.password
    )

    user = User(
        username=request.username,
        email=request.email,
        password=hashed_password
    )

    db.add(user)

    db.commit()

    db.close()

    return {
        "message": "User created successfully"
    }

SECRET_KEY = os.getenv("SECRET_KEY")

# Only /register and /login need this. Raising here killed the whole API at
# import time on any host where the variable was missing, taking down endpoints
# that have nothing to do with auth. Those two routes refuse instead, so the
# failure is visible and specific rather than a crash loop.
if not SECRET_KEY:
    logger.warning(
        "SECRET_KEY is not set — /register and /login are disabled. "
        "Set it to enable authentication."
    )

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60

class LoginRequest(BaseModel):
    email: str
    password: str

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt

@app.post("/login")
def login(request: LoginRequest):

    if not SECRET_KEY:
        return {
            "error": "Authentication is not configured on this server."
        }

    db = SessionLocal()

    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if not user:

        db.close()

        return {
            "error": "Invalid credentials"
        }

    if not pwd_context.verify(
        request.password,
        user.password
    ):

        db.close()

        return {
            "error": "Invalid credentials"
        }

    token = create_access_token(
        {
            "sub": user.email
        }
    )

    db.close()

    return {
        "access_token": token,
        "token_type": "bearer"
    }

class ListingRequest(BaseModel):
    title: str
    price: str
    location: str = None


# Below this many listings the percentile is noise, so fall back to the
# fixed-threshold price check instead.
MIN_LISTINGS_FOR_FLOOR = 5


def area_price_floor(db, location):
    """
    The 25th-percentile asking rent for an area, or None if too little data.

    Deliberately not the median. A median mixes studios with three-bedrooms, so
    every area lands in the same range and the comparison stops discriminating
    between neighbourhoods. The cheap end of an area is the meaningful floor:
    a price well below it is suspicious whatever the unit size.
    """
    if not location:
        return None

    amounts = sorted(
        row[0]
        for row in db.query(Rental.price_amount)
        .filter(Rental.location.ilike(f"%{location}%"))
        .filter(Rental.price_amount.isnot(None))
        .all()
    )

    if len(amounts) < MIN_LISTINGS_FOR_FLOOR:
        return None

    index = int(0.25 * (len(amounts) - 1))
    return amounts[index]


class BudgetRequest(BaseModel):
    income: int
    rent: int
    food: int
    transport: int
    utilities: int
    other: int

@app.post("/analyze-listing")
def analyze_rental_listing(data: ListingRequest):

    db = SessionLocal()

    try:
        floor = area_price_floor(db, data.location)
    finally:
        db.close()

    return analyze_listing(
        data.title,
        data.price,
        area_floor=floor,
        area_label=data.location if floor else None
    )

@app.get("/areas/recommend")
def get_area_recommendations(
    budget: int
):

    recommendations = recommend_areas(
        budget
    )

    return {
        "budget": budget,
        "recommendations": recommendations
    }

@app.get("/market-stats")
def market_stats(
    area: str
):

    result = get_market_stats(
        area
    )

    if result is None:
        return {
            "error": "Area not found"
        }

    return result

@app.get("/market/zones")
def market_zones():

    return {
        "zones": list_zones()
    }


@app.get("/market/trend")
def market_trend(
    area: str
):

    result = get_vacancy_trend(area)

    if result is None:
        return {
            "error": "Area not found"
        }

    return result


@app.post("/budget-analysis")
def budget_analysis(
    budget: BudgetRequest
):

    total_expenses = (
        budget.rent
        + budget.food
        + budget.transport
        + budget.utilities
        + budget.other
    )

    remaining = (
        budget.income
        - total_expenses
    )

    if remaining >= 1000:
        status = "Comfortable"

    elif remaining >= 300:
        status = "Tight but survivable"

    else:
        status = "Financially risky"

    return {
        "income": budget.income,
        "expenses": total_expenses,
        "remaining": remaining,
        "status": status
    }



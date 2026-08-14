import sys
import os
import re

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
from backend.database.models import Base
from backend.database.database import engine
Base.metadata.create_all(bind=engine)
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

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

app = FastAPI()

# Comma-separated list, so the deployed frontend's origin can be added without
# a code change. Defaults to local dev.
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000"
    ).split(",")
    if origin.strip()
]

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

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is not set. Add it to your .env file."
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



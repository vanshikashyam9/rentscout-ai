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
from craigslist_scraper import get_craigslist_listings
import os
from database.models import Base
from database.database import engine
Base.metadata.create_all(bind=engine)
from database.database import SessionLocal
from database.models import Rental
from fastapi import Query

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

app = FastAPI()

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

@app.get("/rentals")
def get_rentals():

    rentals = get_craigslist_listings()

    return {
        "count": len(rentals),
        "rentals": rentals
    }





@app.post("/scrape")
def scrape_and_store():

    rentals = get_craigslist_listings()

    db = SessionLocal()

    count = 0

    for item in rentals:

        exists = db.query(Rental).filter(
            Rental.link == item["link"]
        ).first()

        if not exists:

            rental = Rental(
                title=item["title"],
                price=item["price"],
                location=item["location"],
                link=item["link"]
            )

            db.add(rental)

            count += 1

    db.commit()
    db.close()

    return {
        "saved": count
    }

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
            "location": rental.location,
            "link": rental.link
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
            "location": rental.location,
            "link": rental.link
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

            score = round((price / max_price) * 100)

            results.append({
                "title": rental.title,
                "price": rental.price,
                "location": rental.location,
                "link": rental.link,
                "score": score
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




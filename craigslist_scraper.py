import requests
from bs4 import BeautifulSoup

# -----------------------------------
# LIVE CRAIGSLIST SCRAPER
# -----------------------------------

def get_craigslist_listings():

    URL = "https://vancouver.craigslist.org/search/apa"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        URL,
        headers=headers
    )

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    listings = soup.find_all(
        "li",
        class_="cl-static-search-result"
    )

    results = []

    for listing in listings[:20]:

        try:

            title_tag = listing.find(
                "div",
                class_="title"
            )

            price_tag = listing.find(
                "div",
                class_="price"
            )

            link_tag = listing.find("a")

            location_tag = listing.find(
                "div",
                class_="location"
            )

            title = (
                title_tag.text.strip()
                if title_tag else "N/A"
            )

            price = (
                price_tag.text.strip()
                if price_tag else "N/A"
            )

            link = (
                link_tag["href"]
                if link_tag else "N/A"
            )

            location = (
                location_tag.text.strip()
                if location_tag else "N/A"
            )

            results.append({
                "title": title,
                "price": price,
                "location": location,
                "link": link
            })

        except:
            pass

    return results
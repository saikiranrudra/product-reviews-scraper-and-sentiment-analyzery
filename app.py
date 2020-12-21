from flask import Flask, render_template, request
from utils.util_functions import fetcher
from utils.util_functions import calculate_sentiment
from utils.variables import Variables
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client["scraper"]
products = db["products"]


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/reviews", methods=["POST"])
def reviews():
    search_url = Variables.get_instance().URL['FLIP_KART_SEARCH']
    base_url = Variables.get_instance().URL["FLIP_KART"]
    search_string = request.form['product_name']  # product name to search

    # check the availability in DB
    product_from_db = products.find_one({"product_name": search_string})

    if product_from_db is None:
        url = search_url + search_string.replace(" ", '+')  # url for searcing products
        products_page = fetcher(url)  # fetching html page of products
        products_soup = BeautifulSoup(products_page, "html.parser")

        product_anchor_tag = products_soup.find("a", {"class": "_1fQZEK"})
        if product_anchor_tag is None:
            product_anchor_tag = products_soup.find("a", {"class": "_2rpwqI"})

        product_route = product_anchor_tag.get("href")  # extracting product url
        product_link = f"{base_url}{product_route}"  # product link
        product_page = fetcher(product_link)

        product_soup = BeautifulSoup(product_page, "html.parser")
        reviews_route = product_soup.find("div", "_3UAT2v _16PBlm").parent.get("href")

        # removing all string after &aid including &aid
        filter_index = reviews_route.find("&aid")
        reviews_route = reviews_route[0:filter_index]
        reviews_link = f"{base_url}{reviews_route}"
        reviews_page = fetcher(reviews_link)
        reviews_soup = BeautifulSoup(reviews_page, "html.parser")

        # Extracing comments for html
        reviews_divs = reviews_soup.find_all("div", class_="col _2wzgFH K0kLPL")
        reviews = []

        for review in reviews_divs:
            print(type(review.find_all("div", class_="row")))

            rating_tag = review.find("div", class_="_3LWZlK")
            comment_tag = review.find("div", class_="")

            heading = review.find("p", class_="_2-N8zT").string
            rating = re.sub(r"<div\sclass=\"(\w\s*)+\">", "", str(rating_tag))
            comment = str(comment_tag.findChildren("div", recursive=False)[0]) \
                .replace("<div class=\"\">", "") \
                .replace("</div>", "") \
                .replace("<br/>", "")
            reviews.append({"heading": heading, "rating": rating[0], "comment": comment})

        print(reviews)
        sentiment = calculate_sentiment(reviews)

        total = len(reviews)
        total = total if total > 0 else 1

        sentiment[0] = ((sentiment[0] / total) * 100)
        sentiment[1] = ((sentiment[1] / total) * 100)
        sentiment[2] = ((sentiment[2] / total) * 100)

        if len(reviews) != 0:
            # insert it into db
            products.insert_one({"product_name": search_string, "reviews": reviews})

            return render_template(
                "reviews.html",
                len=len(reviews),
                title=search_string,
                reviews=reviews,
                sentiment=sentiment
            )

        else:
            # print no reviews to print
            return render_template(
                "review.html",
                len=1,
                title=search_string,
                reviews=["No Reviews available for this product"],
                sentiment=sentiment
            )
    else:
        # render fetched from db
        # calculating sentiment
        total = len(product_from_db["reviews"])
        total = total if total > 0 else 1

        sentiment = calculate_sentiment(product_from_db["reviews"])
        sentiment[0] = ((sentiment[0] / total) * 100)
        sentiment[1] = ((sentiment[1] / total) * 100)
        sentiment[2] = ((sentiment[2] / total) * 100)

        return render_template(
            "reviews.html",
            len=len(product_from_db["reviews"]),
            title=search_string,
            reviews=product_from_db["reviews"],
            sentiment=sentiment
        )


app.run(port=8000)

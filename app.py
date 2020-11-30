from flask import Flask, render_template, request
from utils.fetcher import fetcher
from utils.variables import Variables
from bs4 import BeautifulSoup
from textblob import TextBlob

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/reviews", methods=["POST"])
def reviews():
    search_url = Variables.get_instance().URL['FLIP_KART_SEARCH']
    base_url = Variables.get_instance().URL["FLIP_KART"]
    search_string = request.form['product_name']  # product name to search

    url = search_url + search_string.replace(" ", '+')  # url for searcing products
    products_page = fetcher(url)  # fetching html page of products
    products_soup = BeautifulSoup(products_page, "html.parser")

    product_anchore_tag = products_soup.find("a", {"class": "_1fQZEK"});
    if product_anchore_tag is None:
        product_anchore_tag = products_soup.find("a", {"class": "_2rpwqI"})

    product_route = product_anchore_tag.get("href")  # extracting product url
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

    reviews_divs = reviews_soup.find_all("div", class_="t-ZTKy")
    reviews = []
    sentiment = [0, 0, 0]


    for review in reviews_divs:
        div = str(review.find("div", class_="").findChildren("div", recursive=False)[0])
        div_text = div.replace("<div class=\"\">", "").replace("</div>", "").replace("<br/>", "")
        blob = TextBlob(div_text)

        if blob.sentiment.polarity > 0:
            sentiment[0] = sentiment[0] + 1
        elif blob.sentiment.polarity == 0:
            sentiment[1] = sentiment[1] + 1
        else:
            sentiment[2] = sentiment[2] + 1

        reviews.append(div_text)


    total = 1

    if len(reviews) > 0:
        total = len(reviews)
    else:
        total = 1

    sentiment[0] = ((sentiment[0] / total) * 100)
    sentiment[1] = ((sentiment[1] / total) * 100)
    sentiment[2] = ((sentiment[2] / total) * 100)

    return render_template("reviews.html", len = len(reviews), title=search_string, reviews=reviews, sentiment=sentiment)

app.run(port=8000)

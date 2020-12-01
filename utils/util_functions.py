from urllib.request import urlopen
from textblob import TextBlob


def fetcher(url: str):
    conn = urlopen(url)
    page = conn.read()
    conn.close()
    return page


def calculate_sentiment(reviews: list):
    result = [0, 0, 0]
    for review in reviews:
        blob = TextBlob(review)
        polarity = blob.sentiment.polarity

        if polarity > 0:
            result[0] = result[0] + 1
        elif polarity == 0:
            result[1] = result[1] + 1
        else:
            result[2] = result[2] + 1

    return result
from urllib.request import urlopen

def fetcher(url):
    conn = urlopen(url)
    page = conn.read()
    conn.close()
    return page
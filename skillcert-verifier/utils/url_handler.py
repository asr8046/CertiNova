import requests
from bs4 import BeautifulSoup

def validate_and_scrape_cert_url(url):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return False, "Link not accessible"
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text()
        # Extract meaningful parts using pattern or keywords
        return True, text
    except Exception as e:
        return False, str(e)

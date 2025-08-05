import requests
from bs4 import BeautifulSoup
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def extract_links_from_text(text):
    """
    Extract all URLs from a given text, handling broken or line-wrapped links. Returns a list of cleaned URLs.
    """
    url_pattern = re.compile(r'(https?://(?:[\w\-\./:?\#\[\]@!\$&\'\(\)\*\+,;=%]|[ \n\r\t-])+)', re.IGNORECASE)
    matches = url_pattern.findall(text)
    cleaned_urls = []
    for url in matches:
        url_no_space = re.sub(r'[\s\u00A0]+', '', url)
        url_no_space = url_no_space.rstrip('.,;:!?)]"\'')
        url_no_space = re.sub(r'-\s*', '', url_no_space)
        cleaned_urls.append(url_no_space)
    return cleaned_urls

def convert_google_drive_link(link):
    """
    Convert a Google Drive link to a downloadable format.
    """
    match = re.search(r'd/([a-zA-Z0-9_-]+)', link)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?id={file_id}&export=download"
    return link

def validate_and_scrape_cert_url(url):
    """
    Validate a certificate URL and attempt to scrape its text content.
    Handles Google Drive links and general web pages. Returns (True, text) if accessible, else (False, error message).
    """
    try:
        if "drive.google.com" in url:
            url = convert_google_drive_link(url)
        import certifi
        def safe_get(url, **kwargs):
            if "drive.google.com" in url:
                return requests.get(url, verify=False, **kwargs)
            else:
                return requests.get(url, verify=certifi.where(), **kwargs)
        r = safe_get(url, timeout=5)
        if r.status_code != 200:
            return False, "Link not accessible"
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text()
        return True, text
    except Exception as e:
        return False, str(e)

def extract_links_from_cleaned_text(text):
    """
    Extract links from cleaned text, fixing line-wrapped or hyphenated URLs. Returns a list of valid links.
    """
    text = text.replace('\n', ' ')
    text = re.sub(r'([a-zA-Z0-9\-])-\s+([a-zA-Z0-9])', r'\1\2', text)
    pattern = r'https?://[^\s\)\]]+'
    links = re.findall(pattern, text)
    return links

import requests
from bs4 import BeautifulSoup
import re

def extract_links_from_text(text):
    """
    Extracts all URLs from a given text, even if broken by spaces or line breaks.
    Returns a list of cleaned URLs.
    """
    # Remove line breaks and extra spaces inside URLs by replacing them with nothing (for URLs only)
    # This regex matches 'http' or 'https' followed by anything until a space or a closing bracket/quote
    # It allows for spaces/newlines/hyphens inside the URL, which we will clean up
    url_pattern = re.compile(r'(https?://(?:[\w\-\.\:/\?\#\[\]@!\$&\'\(\)\*\+,;=%]|[ \n\r\t-])+)', re.IGNORECASE)
    matches = url_pattern.findall(text)
    cleaned_urls = []
    for url in matches:
        # Remove all whitespace and linebreaks from inside the URL
        url_no_space = re.sub(r'[\s\u00A0]+', '', url)
        # Remove any trailing punctuation or brackets
        url_no_space = url_no_space.rstrip('.,;:!?)]"\'')
        # Remove hyphens only if they are at a line break (common in PDFs)
        url_no_space = re.sub(r'-\s*', '', url_no_space)
        cleaned_urls.append(url_no_space)
    return cleaned_urls

import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def convert_google_drive_link(link):

    match = re.search(r'd/([a-zA-Z0-9_-]+)', link)

    if match:

        file_id = match.group(1)

        return f"https://drive.google.com/uc?id={file_id}&export=download"

    return link

def validate_and_scrape_cert_url(url):
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
        # Extract meaningful parts using pattern or keywords
        return True, text
    except Exception as e:
        return False, str(e)

def extract_links_from_cleaned_text(text):
    """
    Extracts links from text while handling line-wrapped or broken URLs.
    Rejoins split parts caused by line breaks or hyphenation in PDFs.
    """
 
    # Replace newlines with space to simulate what PDF extraction does
    text = text.replace('\n', ' ')
 
    # Fix broken hyphenated URLs (hyphen followed by space or newline)
    # Turns: ...46cb- 8e47... into ...46cb8e47...
    text = re.sub(r'([a-zA-Z0-9\-])-\s+([a-zA-Z0-9])', r'\1\2', text)
 
    # Match common URL patterns after cleaning
    pattern = r'https?://[^\s\)\]]+'
    links = re.findall(pattern, text)
 
    return links

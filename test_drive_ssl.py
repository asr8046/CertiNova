import requests
import certifi

url = "https://drive.google.com/uc?export=download&id=1QT98zB6SSFYmZdPg2zUuJ6DCzvjsQcw3"

try:
    print(f"Trying to download from: {url}")
    response = requests.get(url, verify=certifi.where(), timeout=10)
    print(f"Status code: {response.status_code}")
    print(f"First 100 bytes: {response.content[:100]}")
except Exception as e:
    print(f"Error occurred: {e}")

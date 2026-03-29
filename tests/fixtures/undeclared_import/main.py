import requests
import httpx  # not in requirements.txt

resp = requests.get("https://example.com")
resp2 = httpx.get("https://example.com")

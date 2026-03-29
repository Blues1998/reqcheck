import os
import json
import pathlib
import requests

data = json.loads("{}")
p = pathlib.Path(os.getcwd())
requests.get("https://example.com")

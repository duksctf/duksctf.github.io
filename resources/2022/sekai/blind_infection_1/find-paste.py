import requests
import sys
with open("url.txt") as src:
    url = src.readlines()

for i in url:
    r = requests.get(i.strip())
    print(r.content)
    if b"SEKAI" in r.content:
        sys.exit(0)

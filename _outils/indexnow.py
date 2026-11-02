# Signale les nouvelles pages à Bing et aux moteurs IndexNow.
# Lit sur l'entrée standard des chemins comme blog/mon-article/index.html.
import json, sys, urllib.request

HOTE = "bongoapp.fr"
CLE = "afb7453ee6d16c1e07e154257ddbc3f8"

chemins = [c.strip() for c in sys.stdin if c.strip()]
if chemins:
    urls = [f"https://{HOTE}/{c.removesuffix('index.html')}" for c in chemins] + [f"https://{HOTE}/blog/", f"https://{HOTE}/"]
    corps = json.dumps({"host": HOTE, "key": CLE, "keyLocation": f"https://{HOTE}/{CLE}.txt", "urlList": urls}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=corps, headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=20) as r:
        print("IndexNow :", r.status, urls)

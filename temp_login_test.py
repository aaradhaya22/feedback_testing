import urllib.request
import json
import urllib.error

url = "https://anonymous-feedback-bctb.onrender.com/dashboard-admin/login/"
data = json.dumps({"username": "admin", "password": "admin"}).encode("utf-8")
headers = {
    "Content-Type": "application/json",
    "Origin": "https://anonymous-feedback-i46i.vercel.app"
}

req = urllib.request.Request(url, data=data, headers=headers, method="POST")
try:
    with urllib.request.urlopen(req) as res:
        print("STATUS:", res.status)
        print("HEADERS:", dict(res.headers))
        print("BODY:", res.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print("ERROR STATUS:", e.code)
    print("ERROR HEADERS:", dict(e.headers))
    print("ERROR BODY:", e.read().decode("utf-8"))
except Exception as e:
    print("OTHER ERROR:", e)

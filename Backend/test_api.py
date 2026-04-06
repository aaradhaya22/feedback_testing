import urllib.request
import urllib.parse
import json

def test():
    # Login
    import json
    auth_data = json.dumps({'username': 'admin', 'password': 'admin'}).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:8000/dashboard-admin/login/', data=auth_data)
    req.add_header('Content-Type', 'application/json')
    try:
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read().decode())
        access = data.get('token')
        print("Logged in successfully!", access)
    except Exception as e:
        print("Login failed:", e)
        return

    # Fetch tables
    req = urllib.request.Request('http://127.0.0.1:8000/dashboard-admin/tables/')
    req.add_header('Authorization', f'Bearer {access}')
    try:
        resp = urllib.request.urlopen(req)
        tables = json.loads(resp.read().decode())
        print("Tables API response:", json.dumps(tables, indent=2))
    except Exception as e:
        print("Tables API failed:", e)

if __name__ == "__main__":
    test()

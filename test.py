import requests

r = requests.post(
    url=f"http://localhost:8000/user/token?username=admin&password=admin",
)
output = r.json()
print(output)

import requests

url = "http://127.0.0.1:5000/encrypt"
data = {
    "ID": "user@example.com",
    "message": "Hello IBE"
}

response = requests.post(url, json=data)
print("Response Status Code:", response.status_code)
print("Response JSON:", response.json())

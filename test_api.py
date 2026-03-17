import requests
import urllib.parse
api_key = "4fe0104e079aaab4cc0eeb611e31f3d2"

def test_city(city):
    print(f"Testing City: {city}")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={urllib.parse.quote(city)}&appid={api_key}&units=metric&lang=tr"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        print(f"SUCCESS: Found {data['name']}, {data['sys']['country']} -> Temp: {data['main']['temp']}C, Desc: {data['weather'][0]['description']}")
    else:
        print(f"FAILED: {r.status_code} - {r.text}")
    print("-" * 40)

test_city("Konya")
test_city("kara")
test_city("RastgeleSehirIsmi123")

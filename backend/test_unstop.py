import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
urls = [
    "https://unstop.com/api/public/opportunity/search-result",
    "https://unstop.com/api/public/opportunities/search-result",
    "https://unstop.com/api/public/opportunities/search?opportunity=competitions"
]

for url in urls:
    try:
        r = requests.get(url, headers=headers)
        print(url, r.status_code)
        if r.status_code == 200:
            data = r.json()
            if "data" in data:
                print("KEYS:", data.keys())
                print("DATA KEYS:", data["data"].keys())
                break
    except Exception as e:
        print(url, e)

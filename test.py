import requests

# Set up the proxy to use Tor's SOCKS5 proxy
proxies = {
    'http': 'socks5h://localhost:9150',
    'https': 'socks5h://localhost:9150'
}

# Test connection to DuckDuckGo's .onion site
url = "https://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion/"

try:
    response = requests.get(url, proxies=proxies, timeout=10)
    if response.status_code == 200:
        print("Successfully connected to Tor network and accessed DuckDuckGo's .onion site!")
        print("Response from the site:")
        print(response.text[:500])  # Print first 500 characters of the response
    else:
        print(f"Failed to connect, status code: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Connection error: {e}")
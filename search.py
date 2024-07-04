import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

ddg = DDGS()

def search_urls(query: str, max_results=6) -> list[str]:
    results = ddg.text(query, max_results=max_results)
    return [i["href"] for i in results]

def parse_url(url: str) -> str:
    if not url:
        return "There's no url"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return "Failed to retrieve the webpage."
    soup = BeautifulSoup(response.text, 'html.parser')
    data = []
    for tag in soup.find_all(['h1', 'h2', 'h3', 'p']):
        text = tag.get_text(" ", strip=True)
        if text:
            data.append(text)
    data = "\n".join(data)
    return data

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import json

SEED_URLS = [
    "https://www.reddit.com/",
    "https://www.stackoverflow.com/",
    "https://www.github.com/",
    "https://www.nationalgeographic.com/",
    "https://www.britannica.com/",
]

POST_ENDPOINT = "http://127.0.0.1:5000/add"

def is_valid_link(href):
    if not href:
        return False
    parsed = urlparse(href)
    if parsed.scheme in ('mailto', 'javascript', 'tel'):
        return False
    if parsed.scheme not in ('http', 'https', ''):
        return False
    return True

def extract_plain_text(soup):
    body = soup.body
    if body is None:
        return ""
    for script in body(["script", "style", "noscript"]):
        script.decompose()
    text = body.get_text(separator=' ', strip=True)
    return text

def extract_icon_url(soup, base_url):
    icon_link = soup.find("link", rel=lambda x: x and "icon" in x.lower())
    if icon_link and icon_link.get("href"):
        return urljoin(base_url, icon_link["href"])
    parsed = urlparse(base_url)
    return f"{parsed.scheme}://{parsed.netloc}/favicon.ico"

def extract_meta_description(soup):
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        return meta["content"].strip()
    return ""

def send_json(data, endpoint):
    
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(endpoint, data=json.dumps(data), headers=headers, timeout=5)
        response.raise_for_status()
        print(f"Sent to endpoint: {endpoint}")
    except Exception as e:
        print(f"Failed to send data to endpoint: {e}")

def crawl(seed_urls, max_pages=100, endpoint=POST_ENDPOINT):
    queue = deque(seed_urls)
    visited = set()
    count = 0

    while queue and count < max_pages:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        print(f"Crawling: {url}")
        try:
            response = requests.get(url, timeout=5)
            if not response.headers.get('content-type', '').startswith('text/html'):
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            plain_text = extract_plain_text(soup)
            title = soup.title.string.strip() if soup.title and soup.title.string else ""
            icon = extract_icon_url(soup, url)
            
            info = ""
            meta = soup.find("meta", attrs={"name": "description"})
            if meta and meta.get("content"):
                info = meta["content"].strip()
            data = {
                "description": plain_text,
                "title": title,
                "link": url,
                "icon": icon,
                "info": info
            }
            
            
            print(json.dumps(data, ensure_ascii=False))
            send_json(data, endpoint)
            for a in soup.find_all('a', href=True):
                href = a['href']
                if is_valid_link(href):
                    next_url = urljoin(url, href)
                    next_url = next_url.split('#')[0]
                    if next_url not in visited:
                        queue.append(next_url)
            count += 1
        except Exception as e:
            print(f"Failed to crawl {url}: {e}")
    print(f"Total pages crawled: {count}")

if __name__ == "__main__":
    crawl(SEED_URLS, 1000, POST_ENDPOINT)
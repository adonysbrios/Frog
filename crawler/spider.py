#
# ATENCION
# ESTA SPIDER SOLO SCRAPEA SITIOS WEBS QUE TENGAN EL <HTML LANG=""> EN INGLES PARA FACILITAR EL SCRIPT DEL INDEXER
# 

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import json
from pymongo import MongoClient

client = MongoClient()

TEXT_FOUNDED = {}

SEED_URLS = [
    "https://en.wikipedia.org/wiki/Main_Page",
    "https://www.reddit.com/",
    "https://www.stackoverflow.com/",
    "https://www.github.com/",
    "https://www.nationalgeographic.com/",
    "https://www.britannica.com/",
]
db = client["sites"]
sites = db["sites"]
sites.create_index('link', unique=True)

def is_valid_link(href):
    if not href:
        return False
    parsed = urlparse(href)
    if parsed.scheme in ('mailto', 'javascript', 'tel'):
        return False
    if parsed.scheme not in ('http', 'https', ''):
        return False
    return True

def jump_line(tag):
    global TEXT_FOUNDED
    text = tag.get_text()
    for i in TEXT_FOUNDED.keys():
        if text in i:
            return ""
    if not text.endswith("\n"):
        text += "\n"
    TEXT_FOUNDED[text] = 1
    return text

def extract_plain_text(soup):  
    global TEXT_FOUNDED  
    text = ""
    for i in soup.find_all():
        tag_name = i.name
        match tag_name:
            case "p":
                text += jump_line(i)
    TEXT_FOUNDED = {} 
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

def save_data(data):
    try:
        sites.update_one({'link': data['link']}, {'$set': data}, upsert=True)
        print(f"Data saved")
    except Exception as e:
        print(f"Exception: {e}")
        

def crawl(seed_urls, max_pages=100):
    queue = deque(seed_urls)
    count = 0
    while queue and count < max_pages:
        url = queue.popleft()
        existing = sites.find_one({'link': url, 'scrapped': True})
        if existing:
            continue
        print(f"Crawling: {url}")
        try:
            response = requests.get(url, timeout=5)
            if not response.headers.get('content-type', '').startswith('text/html'):
                continue
            soup = BeautifulSoup(response.text, 'html.parser', from_encoding='utf-8')
            
            # VERIFICAR EN <HTML> si LANG="EN"
            lang = soup.select_one('html')
            if lang and lang.get('lang') not in ('en', 'en-US'):
                continue
            
            plain_text = extract_plain_text(soup)
            title = soup.title.string if soup.title else ""
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
                "info": info,
                "quality": 0,
                "indexed": False,
                "scrapped": True
            }
            
            save_data(data)
            for a in soup.find_all('a', href=True):
                href = a['href']
                if is_valid_link(href):
                    next_url = urljoin(url, href)
                    next_url = next_url.split('#')[0]
                    sites.update_one(
                        {'link': next_url},
                        {'$inc': {'quality': 0.01}},
                        upsert=True
                    )
                    queue.append(next_url)
            count += 1
        except Exception as e:
            print(f"Failed to crawl {url}: {e}")
    print(f"Total pages crawled: {count}")


# Empezar a buscar sitios webs y solo guardar 5.
if __name__ == "__main__":
    crawl(SEED_URLS, 5)
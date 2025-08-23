from utils.utils import preprocess_text
from collections import defaultdict
from pymongo import MongoClient

client = MongoClient()
db = client["sites"]
db2 = client["index"]
sites = db["sites"]
index = db2["index-words"]

def build_inverted_index(document, url):
    inverted_index = defaultdict(list)
    tokens = preprocess_text(document)
    terms = defaultdict(list)
    for i, term in enumerate(tokens):
        terms[term].append(i)

    for term, val in terms.items():
        inverted_index[term].append({"url": url, "positions": val})
        index.update_one(
            {"term": term},
            {"$push": {"documents": {"url": url, "positions": val}}},
            upsert=True
        )
    return inverted_index

def index_unindexed_sites():
    unindexed_sites = sites.find({"indexed": False, "scrapped": True})
    for site in unindexed_sites:
        description = site.get("description", "")
        title = site.get("title", "")
        link = site.get("link", "")
        if not description or not link:
            continue
        print(link)
        build_inverted_index(title + link + description, link)

index_unindexed_sites()
from pymongo import MongoClient
import math
from collections import defaultdict
from utils.utils import preprocess_text

client = MongoClient()
db = client["index"]
db2 = client["sites"]
index = db["index-words"]
sites = db2["sites"]

# Podemos cachear los terms en redis

def build(query):
    tokens = preprocess_text(query)
    inverted_index = defaultdict(list)
    for token in tokens:
        entry = index.find_one({"term": token})
        if entry and "documents" in entry:
            for doc in entry["documents"]:
                url = doc.get("url")
                positions = doc.get("positions", [])
                inverted_index[token].append((url, positions))
    return inverted_index

def calculate_tfidf(inverted_index):
    avgdl = 0
    documents = set()
    doc_lengths = {}
    docs_info = {}
    doc_quality = {}
    doc_tokens = {}
    for term, docs in inverted_index.items():
        
        for url, positions in docs:
            documents.add(url)
            if url not in docs_info:
                site = sites.find_one({"link": url})
                description = site.get("description", "")
                
                tokens =  preprocess_text(site.get("title", "") + url + description)
                sites.update_one({'link': url}, {'$set': {"tokens":tokens}}, upsert=True)
                
                docs_info[url] = site
                doc_tokens[url] = tokens
                doc_quality[url] = site.get("quality", 0)
                doc_lengths[url] = len(tokens)
                avgdl+=len(tokens)
    
    documents = list(documents)
    num_docs = len(documents)
    if num_docs:
        avgdl /= num_docs
    else:
        avgdl = 0
    
    terms_freq = {term: len(docs) for term, docs in inverted_index.items()}
    tfidf = {}
    
    for term, docs in inverted_index.items():
        idf = math.log(num_docs/terms_freq[term]+1)
        
        for url, positions in docs:
            k = 1.2
            b = 0.75
            d = doc_lengths[url]
            term_f = len(positions)
            tf = term_f / (term_f+k*(1-b+(b*d/avgdl)))
            tfidf_ = tf * idf
            if url not in tfidf:
                tfidf[url]={}
            tfidf[url][term] = tfidf_*doc_quality[url]
    
    
    return tfidf, docs_info

def search(query):
    inverted_index = build(query)
    tfidf_scores, docs_info = calculate_tfidf(inverted_index)
    scores = defaultdict(int)
    docs_scored = []
    for url, terms in tfidf_scores.items():
        for term, score in terms.items():
            scores[url] += score

    scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    for i in scores:
        url =i[0]
        scores = i[1]
        doc_info = docs_info[url]
        data = {
            "url": url,
            "scores": scores,
            "doc_info": {
                "text": docs_info[url]["description"][:200],
                "description": docs_info[url]["info"][:200],
                "title": docs_info[url]["title"],
                "icon": docs_info[url]["icon"],
                "link": url,
            }
        }
        docs_scored.append(data)
    return docs_scored
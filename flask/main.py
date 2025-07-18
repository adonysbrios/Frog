from flask import Flask, request, jsonify
from collections import Counter
import math
import unicodedata
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def normalize(text):
    text = text.replace('ñ', 'n').replace('Ñ', 'N')
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = text.encode('ascii', 'ignore').decode('utf-8')
    text = ''.join(c for c in text if c.isalnum() or c.isspace())
    return text

DB_PATH = 'search_engine.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        link TEXT UNIQUE,
        title TEXT,
        description TEXT,
        icon TEXT,
        info TEXT
    )''')
    c.execute("PRAGMA table_info(documents)")
    columns = [row[1] for row in c.fetchall()]
    if "info" not in columns:
        c.execute("ALTER TABLE documents ADD COLUMN info TEXT")
    conn.commit()
    conn.close()

def load_document_ids():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM documents")
    docs = [row[0] for row in c.fetchall()]
    conn.close()
    return docs

def add_document(link, title, description, icon, info=""):
    title = title
    description = normalize(description)
    if not icon:
        return False
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO documents (link, title, description, icon, info) VALUES (?, ?, ?, ?, ?)", (link, title, description, icon, info))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception:
        return False

def build_idf_index():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT title, description, link FROM documents")
    doc_words = []
    vocabulary = set()
    for row in c.fetchall():
        text = f"{row[2]} {row[0]} {row[1]}"
        words = set(normalize(text.lower()).split())
        doc_words.append(words)
        vocabulary.update(words)
    num_docs = len(doc_words)
    idf_index = {
        word: math.log(num_docs / (1 + sum(1 for doc in doc_words if word in doc)))
        for word in vocabulary
    }
    conn.close()
    return idf_index

def compute_tfidf(text, idf_index):
    words = normalize(text.lower()).split()
    total = len(words)
    freq = Counter(words)
    tf = {word: count / total for word, count in freq.items()}
    tfidf = {word: tf[word] * idf_index.get(word, 0) for word in tf}
    return tfidf

def search(query, page=1, page_size=10):
    words = normalize(query.lower()).split()
    idf_index = build_idf_index()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, link, title, description, icon, info FROM documents")
    results = []
    for doc in c:
        text = f"{doc[2]} {doc[3]}"
        tfidf = compute_tfidf(text, idf_index)
        score = sum(tfidf[p] for p in tfidf for word in words if word in p)
        if score > 0:
            results.append({
                "link": doc[1],
                "title": doc[2],
                "description": doc[3][:100]+' ...',
                "icon": doc[4],
                "info": doc[5],
                "score": round(score, 4)
            })
    conn.close()
    results.sort(key=lambda x: x["score"], reverse=True)
    total = len(results)
    start = (page - 1) * page_size
    end = start + page_size
    paged = results[start:end]
    return {
        "results": paged,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size)
    }

@app.route('/search', methods=['GET'])
def endpoint_search():
    query = request.args.get('q', '')
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
    except Exception:
        page = 1
        page_size = 10
    result = search(query, page, page_size)
    return jsonify(result)

@app.route('/add', methods=['POST'])
def endpoint_add():
    data = request.get_json()
    link = data.get('link', '').strip()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    icon = data.get('icon', '').strip()
    info = data.get('info', '').strip()
    if not link or not title or not description or not icon:
        return jsonify({"status": "error", "message": "Missing required data"}), 400
    added = add_document(link, title, description, icon, info)
    if added:
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "error", "message": "Could not add document (possible duplicate link)"}), 409

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS
from search_engine import search

app = Flask(__name__)
CORS(app)

@app.route('/search', methods=['GET'])
def endpoint_search():
    query = request.args.get('q', '')
    result = search(query)
    return result

if __name__ == '__main__':
    app.run(debug=True)

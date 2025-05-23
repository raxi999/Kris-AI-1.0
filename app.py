from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_msg = data.get('message', '')
    # Simple reply logic
    reply = f"Krisna: You said '{user_msg}'. This is a prototype reply."
    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(debug=True)
from flask import request, jsonify
import requests

@app.route('/wiki-summary', methods=['GET'])
def wiki_summary():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'No query parameter provided'}), 400

    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        summary = data.get('extract', 'No summary available.')
        return jsonify({'summary': summary})
    else:
        return jsonify({'error': 'Wikipedia page not found'}), 404
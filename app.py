from flask import Flask, render_template, request, jsonify
import wikipedia
import re
import requests
from bs4 import BeautifulSoup

app = Flask(__name__, static_url_path='/static')

# DuckDuckGo fallback
def get_duckduckgo_summary(query):
    try:
        search_url = f"https://lite.duckduckgo.com/lite/?q={query.replace(' ', '+')}"
        res = requests.get(search_url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        links = soup.find_all("a")

        for link in links:
            href = link.get("href")
            if href and "wikipedia.org" in href:
                wiki_title = href.split("/")[-1].replace("_", " ")
                summary, mood = get_clean_summary(wiki_title)
                return summary, mood
        return "I searched online but couldn't find a clear result. Could you try rephrasing?", "confused"
    except Exception:
        return "Something went wrong while searching online. Please try again later.", "confused"

# Wikipedia summary function
def get_clean_summary(query):
    try:
        wikipedia.set_lang("en")
        if len(query.strip()) < 3 or query.lower() in ["you", "me", "he", "she"]:
            return "Could you please clarify your question a bit more?", "calm"

        summary = wikipedia.summary(query, sentences=2, auto_suggest=False, redirect=True)
        if len(summary.split()) < 10 or 'may refer to' in summary.lower():
            raise ValueError("Too vague")
        return "Here I found: " + summary, "thinking"
    except:
        try:
            results = wikipedia.search(query)
            for result in results:
                if query.lower() in result.lower():
                    try:
                        summary = wikipedia.summary(result, sentences=2)
                        if len(summary.split()) > 10 and "may refer to" not in summary.lower():
                            return "Here I found: " + summary, "thinking"
                    except:
                        continue
            return get_duckduckgo_summary(query)
        except:
            return "I'm having trouble understanding that. Try asking in a different way.", "confused"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '').strip().lower()
    if not user_msg:
        return jsonify({'reply': "Please type something!", 'mood': 'calm'})

    greetings = ['hi', 'hello', 'hey', 'good morning', 'good evening']
    if any(greet in user_msg for greet in greetings):
        return jsonify({'reply': "Hello! I'm Kris AI. How can I assist you today?", 'mood': 'happy'})

    motivation = ['i feel lazy', 'i need motivation', 'inspire me']
    if any(word in user_msg for word in motivation):
        return jsonify({'reply': "Stay strong! You're doing great. Keep pushing forward!", 'mood': 'motivation'})

    surprise = ['did you know', 'guess what']
    if any(word in user_msg for word in surprise):
        return jsonify({'reply': "Whoa! That’s surprising!", 'mood': 'surprised'})

    if user_msg.endswith('?') or any(trigger in user_msg for trigger in [
        'tell me about', 'who is', 'what is', 'what are', 'explain', 'define']):
        topic = re.sub(r'[^\w\s]', '', user_msg)
        summary, mood = get_clean_summary(topic)
        return jsonify({'reply': summary, 'mood': mood})

    return jsonify({'reply': "Interesting! Let me know if you have a question.", 'mood': 'default'})

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, jsonify
import wikipedia
import re

app = Flask(__name__)

def get_clean_summary(query):
    try:
        wikipedia.set_lang("en")
        if len(query.strip()) < 3 or query.lower() in ["you", "me", "he", "she", "yoo", "yeah"]:
            return "Could you please clarify your question a bit more?", "calm"

        summary = wikipedia.summary(query, sentences=2, auto_suggest=False, redirect=True)

        if len(summary.split()) < 10 or 'may refer to' in summary.lower():
            raise ValueError("Too vague")

        return "Here I found: " + summary, "informative"

    except Exception:
        try:
            search_results = wikipedia.search(query)
            for result in search_results:
                if query.lower() in result.lower():
                    try:
                        summary = wikipedia.summary(result, sentences=2)
                        if len(summary.split()) > 10 and "may refer to" not in summary.lower():
                            return "Here I found: " + summary, "informative"
                    except:
                        continue
            return "I couldn't find an accurate answer for that. Could you rephrase it?", "calm"
        except:
            return "I'm having trouble understanding that. Try asking in a different way.", "confused"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '').strip()
    if not user_msg:
        return jsonify({'reply': "Please type something!", 'mood': 'calm'})

    lower_msg = user_msg.lower()

    greetings = ['hi', 'hello', 'hey', 'good morning', 'good evening']
    if any(word in lower_msg for word in greetings):
        return jsonify({'reply': "Hello! I'm Kris AI. How can I assist you today?", 'mood': 'happy'})

    triggers = [
        'tell me about', 'who is', 'what is', 'what are', 'give me information about',
        'i want to know about', 'do you know about', 'please explain', 'could you explain',
        'details about', 'information on', 'whats the', "what's the", "whats", "what's"
    ]

    if any(trigger in lower_msg for trigger in triggers) or lower_msg.endswith('?'):
        cleaned = re.sub(r'[^\w\s]', '', user_msg)
        summary, mood = get_clean_summary(cleaned)
        return jsonify({'reply': summary, 'mood': mood})

    return jsonify({'reply': "Interesting! Let me know if you have a question or need information on something.", 'mood': 'calm'})

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, jsonify
import wikipedia

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').lower()
    wiki_phrases = ['tell me about', 'what is', 'who is', 'explain', 'give me information about', 'can you tell me about']

    if any(phrase in user_message for phrase in wiki_phrases):
        try:
            topic = user_message
            for phrase in wiki_phrases:
                topic = topic.replace(phrase, '')
            topic = topic.strip()
            summary = wikipedia.summary(topic, sentences=2)
            return jsonify({'response': summary})
        except Exception:
            return jsonify({'response': "Sorry, I couldn't find information on that."})

    return jsonify({'response': "I'm here to help with your questions!"})

if __name__ == '__main__':
    app.run(debug=True)
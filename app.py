from flask import Flask, request, jsonify, render_template
import wikipedia
import random
import os

app = Flask(__name__)

# Mood-based greetings
greetings = ['hi', 'hello', 'hey', 'yoo']
basic_replies = [
    "Hey there! I'm Kris AI, your smart assistant. Made by Yashwanth, a 15-year-old coder using just GitHub and Render.",
    "Hello! How can I help you today?",
    "Hi! I'm Kris AI. Ask me anything, I’m ready.",
    "Hey! Let’s explore some knowledge together."
]

# Smart Wiki trigger phrases
wiki_triggers = [
    'tell me about', 'explain', 'who is', 'what is', 'what are',
    'give me information about', 'i want to know about', 'do you know about',
    'please explain', 'details about', 'information on', 'what’s', 'whats the', 'who are', 'what’s the'
]

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get("message", "").lower().strip()

    # Greet
    if user_msg in greetings:
        return jsonify({'reply': random.choice(basic_replies)})

    # Owner
    if "who is your owner" in user_msg or "who made you" in user_msg:
        return jsonify({'reply': "I was created by Yashwanth, a smart 15-year-old from Andhra Pradesh using only GitHub and Render!"})

    # Wiki-style queries
    for phrase in wiki_triggers:
        if phrase in user_msg:
            try:
                topic = user_msg.replace(phrase, '').strip()
                summary = wikipedia.summary(topic, sentences=2)
                return jsonify({'reply': f"Here's what I found about **{topic.title()}**:\n{summary}"})
            except Exception:
                return jsonify({'reply': "Sorry, I couldn’t find information on that. Try rephrasing it."})

    # "What" or similar single-word confusion
    if user_msg in ['what', 'why', 'how']:
        return jsonify({'reply': f"Could you please clarify your question? I'm here to help!"})

    return jsonify({'reply': "I'm not sure about that yet, but I'm learning! Try asking me about a famous person or topic."})

# Render-compatible run
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
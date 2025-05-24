from flask import Flask, render_template, request, jsonify
import wikipedia
import random

app = Flask(__name__)

# Detect user mood based on input
def detect_mood(message):
    greetings = ["hi", "hello", "hey", "namaste", "hola"]
    if any(greet in message.lower() for greet in greetings):
        return "happy"
    elif any(q in message.lower() for q in [
        "what", "who", "how", "where", "why", "can you", "do you know",
        "explain", "tell me", "give me info", "i want to know", "please explain",
        "details about", "information on", "could you", "would you", "what's", "whats"
    ]):
        return "informative"
    else:
        return "calm"

# Friendly intros for Wikipedia summaries
def custom_intro_phrases(mood):
    if mood == "informative":
        return random.choice([
            "Here's what I found: ",
            "Let me tell you in simple words: ",
            "This might help you: ",
            "According to my knowledge: ",
            "I looked it up for you: ",
            "Let me explain briefly: "
        ])
    else:
        return ""

# Generate bot reply
def generate_reply(user_input):
    mood = detect_mood(user_input)

    # Greetings
    if mood == "happy":
        return random.choice([
            "Hello! How can I help you today?",
            "Hey there! What would you like to know?",
            "Hi! Ready when you are.",
            "Greetings! Ask me anything.",
            "Hey! I'm Kris, your AI friend!"
        ]), mood

    # Wikipedia-based response
    try:
        summary = wikipedia.summary(user_input, sentences=2)
        reply = custom_intro_phrases(mood) + summary
        return reply, mood
    except:
        return "Sorry, I couldn't find anything useful on that. Try rephrasing it or ask something else.", mood

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    reply, mood = generate_reply(user_input)
    return jsonify({'reply': reply, 'mood': mood})

if __name__ == '__main__':
    app.run(debug=True)
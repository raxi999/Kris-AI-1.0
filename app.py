from flask import Flask, render_template, request, jsonify
import wikipedia
import random

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

def detect_mood(message):
    greetings = ["hi", "hello", "hey", "namaste", "hola"]
    if any(greet in message.lower() for greet in greetings):
        return "happy"
    elif any(q in message.lower() for q in [
        "what", "who", "how", "where", "why", "can you", "do you know",
        "explain", "tell me", "give me info", "i want to know",
        "please explain", "details about", "information on", "could you",
        "would you", "what's", "whats"
    ]):
        return "informative"
    else:
        return "calm"

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]
    mood = detect_mood(user_input)

    if mood == "happy":
        reply = random.choice([
            "Hi there! How can I help?",
            "Hello! What would you like to know?",
            "Hey! I'm Kris AI — ask me anything."
        ])
        return jsonify({"reply": reply, "mood": "happy"})

    elif mood == "informative":
        try:
            topic = user_input.strip()
            summary = wikipedia.summary(topic, sentences=2)

            # Disambiguation or irrelevant summary checks
            if any(phrase in summary.lower() for phrase in [
                "may refer to", "can refer to", "list of", "disambiguation"
            ]):
                raise ValueError("Too ambiguous")

            # Check for keyword presence and length
            if topic.lower() not in summary.lower() or len(summary) < 40:
                raise ValueError("Not relevant enough")

            friendly_intro = random.choice([
                "Sure! Here's what I found:",
                "Of course, this might help:",
                "Here’s something informative:",
                "Let me explain briefly:"
            ])
            return jsonify({"reply": f"{friendly_intro} {summary}", "mood": "informative"})

        except Exception:
            return jsonify({
                "reply": "Hmm, I couldn't find accurate info on that. Could you rephrase or ask differently?",
                "mood": "confused"
            })

    else:
        return jsonify({"reply": "I'm here if you need anything!", "mood": "calm"})
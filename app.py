from flask import Flask, request, jsonify
import wikipedia
import re

app = Flask(__name__)

# --- Helper functions ---

def is_wikipedia_query(message):
    pattern = r"\b(what is|what's|who is|who are|can you tell me about|could you explain|give me information about|i want to know about|do you know about|please explain|what are|details about|information on|whats the|what's the)\b"
    return re.search(pattern, message.lower())

def extract_query(message):
    keywords = [
        "what is", "what's", "who is", "who are", "can you tell me about",
        "could you explain", "give me information about", "i want to know about",
        "do you know about", "please explain", "what are", "details about",
        "information on", "whats the", "what's the"
    ]
    for key in keywords:
        if key in message.lower():
            return message.lower().split(key)[-1].strip()
    return message

def get_wikipedia_summary(query):
    try:
        wikipedia.set_lang("en")
        return wikipedia.summary(query, sentences=2)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Too many results. Be more specific: {e.options[:3]}"
    except wikipedia.exceptions.PageError:
        return "I couldn't find anything on that."

# --- Flask route ---

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")

    if is_wikipedia_query(user_message):
        topic = extract_query(user_message)
        reply = get_wikipedia_summary(topic)
        return jsonify({"reply": reply, "mood": "fact-checking"})

    # Default reply if no Wikipedia query detected
    return jsonify({"reply": "I'm still learning. Ask me something factual!", "mood": "neutral"})

# Run the app (if running locally)
if __name__ == "__main__":
    app.run(debug=True)
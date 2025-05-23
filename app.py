from flask import Flask, request, jsonify
import wikipedia

app = Flask(__name__)

# --- Home route for Render root URL ---
@app.route('/')
def home():
    return "Kris AI is live. Use POST /chat to talk with me."


# --- Wikipedia summary function ---
def get_wikipedia_summary(topic):
    try:
        return wikipedia.summary(topic, sentences=2)
    except wikipedia.exceptions.PageError:
        return "I couldn't find anything on that."
    except:
        return "I couldn't find anything on that."


# --- Helper functions ---
def is_wikipedia_query(message):
    triggers = [
        "tell me about", "could you explain", "give me information about",
        "i want to know about", "do you know about", "please explain",
        "what are", "who are", "details about", "information on",
        "what's", "whats", "what's the", "whats the"
    ]
    return any(trigger in message.lower() for trigger in triggers)

def extract_query(message):
    for trigger in [
        "tell me about", "could you explain", "give me information about",
        "i want to know about", "do you know about", "please explain",
        "what are", "who are", "details about", "information on",
        "what's", "whats", "what's the", "whats the"
    ]:
        if trigger in message.lower():
            return message.lower().split(trigger)[-1].strip()
    return message.strip()


# --- Flask /chat route ---
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    
    if is_wikipedia_query(user_message):
        topic = extract_query(user_message)
        reply = get_wikipedia_summary(topic)
        return jsonify({"reply": reply, "mood": "fact-checking"})
    
    return jsonify({
        "reply": "I'm still learning. Ask me something factual!",
        "mood": "neutral"
    })


# --- Run the app (if running locally) ---
if __name__ == "__main__":
    app.run(debug=True) 
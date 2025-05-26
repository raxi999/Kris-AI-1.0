from flask import Flask, request, jsonify, render_template
import wikipedia
import random
import difflib

app = Flask(__name__)

# --- Trigger phrases ---
knowledge_triggers = [
    "tell me about", "who is", "what is", "what's", "whats", "explain",
    "can you explain", "could you explain", "do you know about", "give me information about",
    "i want to know about", "please explain", "details about", "information on", "what are", "who are"
]
greeting_triggers = ["hi", "hello", "hey", "yo", "namaste"]
thanks_triggers = ["thanks", "thank you", "thx"]
goodbye_triggers = ["bye", "goodbye", "see you", "see ya", "cya"]

# --- Utils ---
def fuzzy_match(phrase_list, user_input):
    lowered = user_input.lower()
    for phrase in phrase_list:
        if phrase in lowered:
            return True
        close = difflib.get_close_matches(lowered, [phrase], cutoff=0.75)
        if close:
            return True
    return False

def detect_topic_query(user_input):
    return fuzzy_match(knowledge_triggers, user_input)

def extract_topic(user_input):
    lowered = user_input.lower()
    for phrase in knowledge_triggers:
        if phrase in lowered:
            return lowered.split(phrase, 1)[-1].strip(" ?.!").title()
        close = difflib.get_close_matches(phrase, [lowered], n=1, cutoff=0.75)
        if close:
            return lowered.split(phrase.split()[0], 1)[-1].strip(" ?.!").title()
    return user_input.strip(" ?.!").title()

def rephrase_summary(summary, topic):
    intros = [
        f"Sure! Here's what I found about {topic}:",
        f"Let me explain {topic} in simple words:",
        f"Of course! So, {topic} is...",
        f"Here's a quick overview of {topic}:",
        f"Glad you asked! {topic} can be described as:",
        f"Alright! Here's something about {topic}:",
        f"Basically, {topic} is known for..."
    ]
    return f"{random.choice(intros)} {summary}"

def generate_greeting():
    replies = ["Hey there!", "Hi!", "Namaste!", "Yo! How can I help?", "Hello friend!"]
    return random.choice(replies)

def generate_goodbye():
    replies = ["Goodbye!", "See you soon!", "Take care!", "Bye-bye!", "See ya!"]
    return random.choice(replies)

def generate_thanks_reply():
    replies = ["You're welcome!", "No problem!", "Anytime!", "Glad to help!", "My pleasure!"]
    return random.choice(replies)

# --- Flask Routes ---
@app.route("/")
def home():
    return render_template("index.html")  # Your frontend (optional)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    response = "I'm not sure how to respond to that yet."

    if fuzzy_match(greeting_triggers, user_input):
        response = generate_greeting()
    elif fuzzy_match(goodbye_triggers, user_input):
        response = generate_goodbye()
    elif fuzzy_match(thanks_triggers, user_input):
        response = generate_thanks_reply()
    elif detect_topic_query(user_input):
        topic = extract_topic(user_input)
        try:
            summary = wikipedia.summary(topic, sentences=2)
            response = rephrase_summary(summary, topic)
        except Exception:
            response = f"Hmm, I couldn't find enough about '{topic}'. Try asking something else!"
    else:
        response = "Hmm... I'm still learning. Try asking about a topic or say hi!"

    return jsonify({"reply": response})

if __name__ == "__main__":
    app.run(debug=True)
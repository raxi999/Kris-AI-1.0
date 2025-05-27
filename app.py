from flask import Flask, request, render_template
import wikipedia
import random
import difflib
from duckduckgo_search import DDGS

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

def get_duckduckgo_summary(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=1)
            for result in results:
                return result["body"]
    except Exception:
        return None

def get_combined_summary(topic):
    try:
        wiki_summary = wikipedia.summary(topic, sentences=2)
    except Exception:
        wiki_summary = ""

    ddg_summary = get_duckduckgo_summary(topic) or ""

    if wiki_summary and ddg_summary:
        return f"{wiki_summary} Also, {ddg_summary}"
    elif wiki_summary:
        return wiki_summary
    elif ddg_summary:
        return ddg_summary
    else:
        return None

def rephrase_summary(summary, topic):
    intros = [
        f"Here's what I found about {topic}:",
        f"Let me explain {topic} simply:",
        f"Sure! So, {topic} is...",
        f"Basically, {topic} means...",
        f"Glad you asked about {topic}:",
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


# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def home():
    user_input = ""
    response = ""
    mood = "default"
    category = "other"

    if request.method == "POST":
        user_input = request.form.get("user_input", "").strip()
        if user_input:
            if fuzzy_match(greeting_triggers, user_input):
                response = generate_greeting()
                mood = "happy"
                category = "greeting"
            elif fuzzy_match(goodbye_triggers, user_input):
                response = generate_goodbye()
                mood = "sad"
                category = "goodbye"
            elif fuzzy_match(thanks_triggers, user_input):
                response = generate_thanks_reply()
                mood = "happy"
                category = "thanks"
            elif detect_topic_query(user_input):
                topic = extract_topic(user_input)
                mood = "thinking"
                category = "knowledge"
                summary = get_combined_summary(topic)
                if summary:
                    response = rephrase_summary(summary, topic)
                    mood = "excited"
                else:
                    response = f"Hmm, I couldn't find much about '{topic}'. Try another topic?"
                    mood = "confused"
            else:
                response = "Hmm... I'm still learning. Try asking about a topic or say hi!"
                mood = "confused"
                category = "unknown"

    return render_template("index.html", user_input=user_input, response=response, mood=mood, category=category)

if __name__ == "__main__":
    app.run(debug=True)
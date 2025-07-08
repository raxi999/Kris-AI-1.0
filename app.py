from flask import Flask, request, render_template
import wikipedia
from duckduckgo_search import DDGS
from nltk.corpus import wordnet
import nltk
import pyjokes
import spacy
import random
import re
import difflib
import logging
import html

# --- Initial Setup ---
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# --- NLTK Setup ---
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# --- spaCy Load ---
try:
    nlp = spacy.load("en_core_web_sm")
except:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# --- Trigger Words ---
knowledge_triggers = [
    "tell me about", "who is", "what is", "what's", "whats", "explain",
    "can you explain", "could you explain", "do you know about",
    "give me information about", "i want to know about", "please explain",
    "details about", "information on", "what are", "who are"
]
greeting_triggers = ["hi", "hello", "hey", "yo", "namaste"]
thanks_triggers = ["thanks", "thank you", "thx"]
goodbye_triggers = ["bye", "goodbye", "see you", "see ya", "cya"]
joke_triggers = ["joke", "funny", "make me laugh"]

# --- Utilities ---
def fuzzy_match(triggers, user_input):
    lowered = user_input.lower()
    for trigger in triggers:
        if trigger in lowered or difflib.get_close_matches(lowered, [trigger], cutoff=0.75):
            return True
    return False

def extract_topic(text):
    lowered = text.lower()
    for trigger in knowledge_triggers:
        if trigger in lowered:
            topic = lowered.split(trigger, 1)[-1]
            topic = re.sub(r"[^\w\s]", "", topic).strip()
            return topic.title()
    return text.strip(" ?.!\n").title()

def rephrase_summary(summary, topic):
    intros = [
        f"Here's what I found about {topic}:",
        f"Let me explain {topic}:",
        f"So, {topic} is...",
        f"{topic} can be described as:",
        f"Here's a quick overview of {topic}:"
    ]
    return f"{random.choice(intros)} {summary}"

def generate_greeting():
    return random.choice(["Hey there!", "Hi!", "Namaste!", "Yo! How can I help?", "Hello friend!"])

def generate_goodbye():
    return random.choice(["Goodbye!", "See you soon!", "Take care!", "Bye-bye!", "See ya!"])

def generate_thanks_reply():
    return random.choice(["You're welcome!", "No problem!", "Anytime!", "Glad to help!", "My pleasure!"])

def generate_joke():
    return pyjokes.get_joke()

# --- Knowledge Functions ---
def wiki_summary(topic):
    try:
        summary = wikipedia.summary(topic, sentences=2)
        return rephrase_summary(summary, topic)
    except wikipedia.exceptions.DisambiguationError as e:
        options = "\n- ".join(e.options[:5])
        return f"'{topic}' has multiple meanings. Did you mean:\n- {options}"
    except wikipedia.exceptions.PageError:
        return None
    except Exception as e:
        logging.debug(f"Wikipedia error: {e}")
        return None

def duckduckgo_snippet(topic):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(topic, max_results=2)
            snippets = [res["body"] for res in results if "body" in res]
            return f"From the web: {' '.join(snippets)}" if snippets else None
    except Exception as e:
        logging.debug(f"DDG error: {e}")
        return None

def wordnet_definition(word):
    synsets = wordnet.synsets(word)
    if synsets:
        return f"WordNet says: {synsets[0].definition()}"
    return None

# --- Main Route ---
@app.route("/", methods=["GET", "POST"])
def home():
    response = ""
    user_input = ""

    if request.method == "POST":
        user_input = request.form.get("user_input", "")
        user_input = html.escape(user_input.strip())

        if fuzzy_match(greeting_triggers, user_input):
            response = generate_greeting()
        elif fuzzy_match(thanks_triggers, user_input):
            response = generate_thanks_reply()
        elif fuzzy_match(goodbye_triggers, user_input):
            response = generate_goodbye()
        elif fuzzy_match(joke_triggers, user_input):
            response = generate_joke()
        elif fuzzy_match(knowledge_triggers, user_input):
            topic = extract_topic(user_input)
            response = wiki_summary(topic) or duckduckgo_snippet(topic) or wordnet_definition(topic) or "Sorry, I couldn't find info on that."
        else:
            response = "Hmm... I didn't understand. Try asking about a topic or say hi!"

    return render_template("index.html", user_input=user_input, response=response)

# --- Run App ---
if __name__ == "__main__":
    app.run(debug=True)
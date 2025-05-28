from flask import Flask, request, render_template
import wikipedia
from duckduckgo_search import ddg
from nltk.corpus import wordnet
import sympy
import pywhatkit
import pyjokes
import spacy
from textblob import TextBlob
from transformers import pipeline
import wikipediaapi
import random
import difflib
import re
import logging

app = Flask(__name__)

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Load transformers QA pipeline
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

# Wikipedia API
wiki_api = wikipediaapi.Wikipedia('en')

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# --- Triggers ---
knowledge_triggers = [
    "tell me about", "who is", "what is", "what's", "whats", "explain",
    "can you explain", "could you explain", "do you know about", "give me information about",
    "i want to know about", "please explain", "details about", "information on", "what are", "who are"
]
greeting_triggers = ["hi", "hello", "hey", "yo", "namaste"]
thanks_triggers = ["thanks", "thank you", "thx"]
goodbye_triggers = ["bye", "goodbye", "see you", "see ya", "cya"]
joke_triggers = ["joke", "funny", "make me laugh"]

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

def extract_topic(user_input):
    lowered = user_input.lower()
    for phrase in knowledge_triggers:
        if phrase in lowered:
            topic = lowered.split(phrase, 1)[-1]
            topic = re.sub(r'[^\w\s]', '', topic).strip()
            return topic.title()
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

def generate_joke():
    return pyjokes.get_joke()

# --- Knowledge Sources ---
def wiki_summary(topic):
    try:
        search_results = wikipedia.search(topic)
        if not search_results:
            return None
        best_match = difflib.get_close_matches(topic, search_results, n=1, cutoff=0.6)
        if not best_match:
            return None
        page_title = best_match[0]
        summary = wikipedia.summary(page_title, sentences=2)
        return rephrase_summary(summary, page_title)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"🤔 '{topic}' is a broad term. Did you mean:\n\n- " + "\n- ".join(e.options[:5])
    except wikipedia.exceptions.PageError:
        return None
    except Exception as e:
        logging.debug(f"Wikipedia error: {e}")
        return None

def wikiapi_summary(topic):
    page = wiki_api.page(topic)
    if page.exists():
        text = page.summary[0:500]
        return rephrase_summary(text, topic)
    return None

def duckduckgo_search(topic):
    results = ddg(topic, max_results=3)
    if results:
        snippets = [res.get('body', '') for res in results if 'body' in res]
        return " ".join(snippets)
    return None

def wordnet_definition(word):
    synsets = wordnet.synsets(word)
    if synsets:
        return synsets[0].definition()
    return None

def sympy_solve(expr):
    try:
        x = sympy.symbols('x')
        solution = sympy.solve(expr, x)
        if solution:
            return f"The solution to the equation is: {solution}"
        else:
            return "I couldn't solve the equation."
    except Exception:
        return None

def pywhatkit_info(topic):
    try:
        return pywhatkit.info(topic, lines=2)
    except Exception:
        return None

def spell_correct(text):
    return str(TextBlob(text).correct())

def nlp_entities(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

def huggingface_qa(question, context):
    try:
        answer = qa_pipeline(question=question, context=context)
        return answer['answer']
    except Exception:
        return None

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def home():
    user_input = None
    response = None

    if request.method == "POST":
        user_input = request.form.get("user_input", "").strip()
        if user_input:
            if fuzzy_match(greeting_triggers, user_input):
                response = generate_greeting()
            elif fuzzy_match(goodbye_triggers, user_input):
                response = generate_goodbye()
            elif fuzzy_match(thanks_triggers, user_input):
                response = generate_thanks_reply()
            elif fuzzy_match(joke_triggers, user_input):
                response = generate_joke()

            elif fuzzy_match(knowledge_triggers, user_input):
                topic = extract_topic(user_input)
                logging.debug(f"Extracted topic: {topic}")
                response = wiki_summary(topic)
                if not response:
                    response = wikiapi_summary(topic)
                if not response:
                    response = duckduckgo_search(topic)
                if not response:
                    if len(topic.split()) == 1:
                        response = wordnet_definition(topic.lower())
                if not response:
                    response = pywhatkit_info(topic)
                if not response:
                    response = f"😕 I couldn’t find reliable info on **{topic}**. Try rephrasing or ask about something else."

            elif "=" in user_input or any(op in user_input for op in ['+', '-', '*', '/', '^']):
                response = sympy_solve(user_input)

            elif len(user_input.split()) < 6:
                corrected = spell_correct(user_input)
                if corrected.lower() != user_input.lower():
                    response = f"Did you mean: '{corrected}'?"
                else:
                    response = "I'm not sure about that. Can you rephrase?"

            else:
                response = "Hmm... I'm still learning. Try asking about a topic or say hi!"

    return render_template("index.html", user_input=user_input, response=response)

if __name__ == "__main__":
    app.run(debug=True)
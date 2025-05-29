# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, Markup
import wikipedia
from duckduckgo_search import DDGS
from nltk.corpus import wordnet
import nltk
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
import html

# --- Initial Setup ---
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# --- Downloads ---
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# --- Load NLP Models ---
try:
    nlp = spacy.load("en_core_web_sm")
except:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
wiki_api = wikipediaapi.Wikipedia('en')

# --- Trigger Words ---
knowledge_triggers = [
    "tell me about", "who is", "what is", "what's", "whats", "explain",
    "can you explain", "could you explain", "do you know about", "give me information about",
    "i want to know about", "please explain", "details about", "information on", "what are", "who are"
]
greeting_triggers = ["hi", "hello", "hey", "yo", "namaste"]
thanks_triggers = ["thanks", "thank you", "thx"]
goodbye_triggers = ["bye", "goodbye", "see you", "see ya", "cya"]
joke_triggers = ["joke", "funny", "make me laugh"]

# --- Utilities ---
def fuzzy_match(phrase_list, user_input):
    lowered = user_input.lower()
    for phrase in phrase_list:
        if phrase in lowered or difflib.get_close_matches(lowered, [phrase], cutoff=0.75):
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
        f"Here's what I found about {topic}:",
        f"Let me explain {topic} in simple words:",
        f"So, {topic} is...",
        f"Here's a quick overview of {topic}:",
        f"{topic} can be described as:",
        f"Here's something about {topic}:",
        f"{topic} is known for..."
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
        logging.debug(f"Wikipedia search for: {topic}")
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

def wikiapi_summary(topic):
    page = wiki_api.page(topic)
    if page.exists():
        return rephrase_summary(page.summary[:400], topic)
    return None

def duckduckgo_search(topic):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(topic, max_results=3)
            snippets = [res["body"] for res in results if "body" in res]
            return f"From the web: {' '.join(snippets)}" if snippets else None
    except Exception as e:
        logging.debug(f"DDG error: {e}")
        return None

def wordnet_definition(word):
    synsets = wordnet.synsets(word)
    if synsets:
        return f"WordNet: {synsets[0].definition()}"
    return None

def sympy_solve(expr):
    try:
        x = sympy.symbols('x')
        solution = sympy.solve(expr, x)
        return f"The solution to the equation is: {solution}" if solution else "I couldn't solve the equation."
    except Exception:
        return None

def pywhatkit_info(topic):
    try:
        return pywhatkit.info(topic, lines=2)
    except Exception:
        return None

def spell_correct(text):
    return str(TextBlob(text).correct())

# --- Main Route ---
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
            elif any(phrase in user_input.lower() for phrase in knowledge_triggers):
                topic = extract_topic(user_input)
                logging.debug(f"Extracted topic: {topic}")
                response = wiki_summary(topic)
                if not response:
                    response = wikiapi_summary(topic)
                if not response:
                    response = duckduckgo_search(topic)
                if not response and len(topic.split()) == 1:
                    response = wordnet_definition(topic.lower())
                if not response:
                    response = pywhatkit_info(topic)
                if not response:
                    response = f"Sorry, I couldn’t find solid info about {topic}. Try rephrasing or asking something else."
            elif "=" in user_input or any(op in user_input for op in ['+', '-', '*', '/', '^']):
                response = sympy_solve(user_input)
            elif len(user_input.split()) < 6:
                corrected = spell_correct(user_input)
                if corrected.lower() != user_input.lower():
                    response = f"Did you mean: '{corrected}'?"
                else:
                    response = "I'm not sure what you meant. Can you rephrase it?"
            else:
                response = "I'm still learning. Try asking a question like 'who is Allu Arjun'."

    return render_template("index.html", user_input=user_input, response=Markup(html.escape(response)) if response else "")

# --- Run the App ---
if __name__ == "__main__":
    app.run(debug=True)
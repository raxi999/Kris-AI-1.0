from flask import Flask, request, jsonify, render_template
import wikipedia
import random

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

def get_wikipedia_summary(query):
    intros = [
        f"Here's what I found about {query}:",
        f"Let me explain a bit about {query}:",
        f"This is interesting — check this out about {query}:",
        f"Okay, here’s a quick overview of {query}:",
        f"Let me share some info on {query}:",
        f"I looked this up for you — here’s what {query} is about:",
        f"Here’s a brief explanation about {query}:",
        f"Let me tell you what I found on {query}:",
        f"Here’s some info on {query} you might like:",
        f"Got it! Here’s what {query} means:",
        f"Let me break down {query} for you:",
        f"Here’s a quick summary about {query}:",
        f"Alright, here’s what I know about {query}:",
        f"Check this out — here’s info on {query}:"
    ]
    intro = random.choice(intros)
    try:
        summary = wikipedia.summary(query, sentences=2)
        return f"{intro}\n\n{summary}"
    except wikipedia.DisambiguationError as e:
        options = '\n- '.join(e.options[:5])  # show 5 options max
        return f"There are multiple results for '{query}'. Try to be more specific like:\n- {options}"
    except wikipedia.PageError:
        return f"Oops! I couldn’t find anything about '{query}'."
    except Exception as e:
        return f"Something went wrong: {str(e)}"

def is_query_valid(text):
    text = text.strip().lower()
    invalid_inputs = [
        "", "what", "who", "why", "when", "how", "where", "?", 
        "what is", "who is", "tell me", "explain", "can you tell me"
    ]
    return not (text in invalid_inputs or len(text) < 4)

def extract_wiki_query(text, triggers):
    text = text.lower().strip()
    for trigger in triggers:
        if trigger in text:
            cleaned = text.replace(trigger, "").strip()
            if is_query_valid(cleaned):
                return cleaned
            else:
                return None
    return None

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "").strip()
    print(f"Received user input: {user_input}")  # Debug print

    user_input_lower = user_input.lower()

    # Greetings
    greetings = ["hi", "hello", "hey", "yo", "yoo", "heyy"]
    if user_input_lower in greetings:
        return jsonify({"reply": "Hi there! How can I help you today?"})

    # Owner info
    if any(phrase in user_input_lower for phrase in ["who is your owner", "who made you", "your creator"]):
        return jsonify({"reply": "I was created by Yashwanth, a 15-year-old developer from Andhra Pradesh using just GitHub and Render."})

    # Wikipedia triggers
    wiki_triggers = [
        "who is", "what is", "can you tell me about", "could you explain", "give me information about",
        "i want to know about", "do you know about", "please explain", "what are", "who are", 
        "details about", "information on", "what's", "whats", "what's the", "whats the"
    ]

    query = extract_wiki_query(user_input_lower, wiki_triggers)
    print(f"Extracted wiki query: {query}")  # Debug print

    if query:
        reply = get_wikipedia_summary(query)
    else:
        reply = "Can you please be more specific? Ask me something like 'What is Python?' or 'Tell me about Elon Musk'."

    print(f"Replying with: {reply}")  # Debug print
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
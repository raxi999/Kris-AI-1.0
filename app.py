from flask import Flask, render_template, request
import wikipedia
from duckduckgo_search import DDGS
import uuid

app = Flask(__name__)

# Keyword categories
greetings = ['hi', 'hello', 'hey']
study_triggers = ['study', 'focus', 'homework']
motivation_triggers = ['tired', 'lazy', 'no energy', 'demotivated']
wiki_phrases = [
    'who is', 'what is', 'tell me about', 'explain',
    'information about', 'details about', 'can you tell me about',
    'give me information about', 'i want to know about', 'do you know about',
    'please explain', 'what are', 'who are', 'information on',
    "what's", "whats", "what's the", "whats the"
]
image_keywords = ['generate image of', 'create image of', 'draw']

# Code triggers
code_triggers = {
    'python code': 'python',
    'html code': 'html',
    'css code': 'css'
}
self_codes = {
    'python': '''# Python Example
def greet():
    print("Hello from Kris AI!")''',
    'html': '''<!-- HTML Example -->
<!DOCTYPE html>
<html><body><h1>Hello</h1></body></html>''',
    'css': '''/* CSS Example */
body {
  background-color: lightblue;
}'''
}

# Wikipedia or fallback to DuckDuckGo
def get_summary(query):
    try:
        return wikipedia.summary(query, sentences=2)
    except:
        try:
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=1)
                if results:
                    return results[0]['body'] or f"Link: {results[0]['href']}"
                return "I couldn't find anything useful."
        except Exception as e:
            return f"Search failed. ({str(e)})"

# Simulated image generation
def generate_image(prompt):
    fake_id = uuid.uuid4().hex[:6]
    return f"🖼️ Imagine this: *{prompt.title()}*. (Image ID: `{fake_id}` — Placeholder)"

@app.route("/", methods=["GET", "POST"])
def index():
    reply = ""
    user_message = ""

    if request.method == "POST":
        msg = request.form.get("user_input", "").lower().strip()
        user_message = msg

        if any(word in msg for word in greetings):
            reply = "👋 Hey there! I'm Kris AI. How can I help you today?"
        elif any(word in msg for word in study_triggers):
            reply = "📘 Let's get in study mode! Stay focused and break things into small steps."
        elif any(word in msg for word in motivation_triggers):
            reply = "💪 Don't give up! You've got the strength to keep going. Take a deep breath and keep pushing!"
        elif any(k in msg for k in code_triggers.keys()):
            key = [k for k in code_triggers if k in msg][0]
            lang = code_triggers[key]
            reply = f"<pre><code>{self_codes[lang]}</code></pre>"
        elif any(k in msg for k in image_keywords):
            prompt = msg
            for k in image_keywords:
                prompt = prompt.replace(k, '')
            reply = generate_image(prompt.strip())
        elif any(phrase in msg for phrase in wiki_phrases):
            reply = get_summary(msg)
        else:
            reply = "🤔 I’m not sure how to answer that yet, but I’m always learning!"

    return render_template("index.html", reply=reply, user_message=user_message)

if __name__ == "__main__":
    app.run(debug=True)
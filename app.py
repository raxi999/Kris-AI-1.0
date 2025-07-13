from flask import Flask, render_template, request
import wikipedia
from duckduckgo_search import DDGS
import uuid

app = Flask(__name__)

# Keywords
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

# Code snippet triggers
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

# Clean user message to extract topic
def clean_query(msg):
    msg = msg.lower()
    for phrase in wiki_phrases:
        if phrase in msg:
            msg = msg.replace(phrase, '')
    return msg.strip()

# Summary using Wikipedia with DDG fallback
def get_summary(query):
    topic = clean_query(query)
    try:
        result = wikipedia.summary(topic, sentences=2)
        if topic.lower() not in result.lower():
            raise ValueError("Unrelated result")
        return result
    except:
        try:
            with DDGS() as ddgs:
                results = ddgs.text(topic, region='wt-wt', safesearch='moderate', timelimit='y', max_results=1)
                if results:
                    body = results[0].get('body')
                    href = results[0].get('href')
                    if body:
                        return body
                    elif href:
                        return f"🔗 Here's something I found: {href}"
                return "I couldn't find any useful info on that topic."
        except Exception as e:
            return f"Search failed. ({str(e)})"

# Real image generation using DuckDuckGo
def generate_image(prompt):
    try:
        with DDGS() as ddgs:
            results = ddgs.images(prompt, max_results=1, region='wt-wt', safesearch='moderate')
            if results:
                img_url = results[0].get("image")
                if img_url:
                    return f'<p>🖼️ Here is what I found for: <b>{prompt.title()}</b></p><img src="{img_url}" alt="{prompt}" style="max-width: 100%; border-radius: 12px; box-shadow: 0 0 10px #444;">'
            return "I couldn’t generate the image right now. Try again later."
    except Exception as e:
        return f"❌ Image generation failed. ({str(e)})"

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
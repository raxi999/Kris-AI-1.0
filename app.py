from flask import Flask, render_template, request
import wikipedia
from duckduckgo_search import DuckDuckGoSearch
import uuid

app = Flask(__name__)

# Mood keywords
greeting_keywords = ['hello', 'hi', 'hey']
study_keywords = ['study', 'focus', 'read']
motivation_keywords = ['tired', 'lazy', 'no energy']
fact_keywords = ['who is', 'what is', 'when did', 'explain', 'information', 'details']
image_keywords = ['generate image of', 'draw', 'create image of']
wiki_phrases = [
    'who is', 'what is', 'tell me about', 'explain',
    'information about', 'details about', 'can you tell me about',
    'give me information about', 'i want to know about', 'do you know about',
    'please explain', 'what are', 'who are', 'information on',
    "what's", "whats", "what's the", "whats the"
]
code_triggers = {
    'python code': 'python',
    'html code': 'html',
    'css code': 'css'
}

# Self code definitions
self_codes = {
    'python': '''# app.py
from flask import Flask, render_template, request
app = Flask(__name__)
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")
if __name__ == "__main__":
    app.run(debug=True)''',

    'html': '''<!-- templates/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Kris AI</title>
  <link rel="stylesheet" href="/static/css/style.css" />
</head>
<body>
  <div class="chat-container">
    <!-- Top Bar -->
    <div class="top-bar">
      <div class="branding">
        <h1>Kris AI</h1>
        <p>Your calm, smart companion</p>
      </div>
      <div class="kris-face-wrapper">
        <div class="kris-face">
          <div class="feather"></div>
          <div class="eyes">
            <div class="eye"></div>
            <div class="eye"></div>
          </div>
          <div class="mouth">
            <div class="default-mouth"></div>
          </div>
        </div>
      </div>
    </div>
    <!-- Chat -->
    <div class="chat-box">
      {% if user_message %}
        <div class="message user">{{ user_message }}</div>
      {% endif %}
      {% if reply %}
        <div class="message bot">{{ reply|safe }}</div>
      {% endif %}
    </div>
    <!-- Input -->
    <form method="POST">
      <input name="message" type="text" placeholder="Talk to Kris AI..." autocomplete="off" />
      <button type="submit">Send</button>
    </form>
  </div>
</body>
</html>''',

    'css': '''/* static/css/style.css */
/* Your final CSS you already provided — paste here */'''
}

# Wikipedia with DuckDuckGo fallback
def get_wiki_or_ddg_answer(query):
    try:
        return wikipedia.summary(query, sentences=2)
    except:
        try:
            search = DuckDuckGoSearch()
            results = search.text(query, max_results=1)
            if results:
                return results[0]['body'] or f"Here's something I found: {results[0]['href']}"
            return "I couldn't find anything useful."
        except Exception as e:
            return f"I'm having trouble searching. Try again soon. ({str(e)})"

# Simulated image generation
def generate_image_response(prompt):
    fake_img_id = uuid.uuid4().hex[:6]
    return f"🖼️ Imagine this: *{prompt.title()}*. (Image ID: `{fake_img_id}` — This is a placeholder for now.)"

@app.route("/", methods=["GET", "POST"])
def index():
    reply = ""
    user_message = ""

    if request.method == "POST":
        msg = request.form.get("message", "").lower().strip()
        user_message = msg

        # Mood & smart handling
        if any(word in msg for word in greeting_keywords):
            reply = "Hello! 😊 I'm Kris AI, your calm, helpful assistant. Ask me anything!"
        elif any(word in msg for word in study_keywords):
            reply = "Focus mode on 📚. Let’s tackle your study goals step by step!"
        elif any(word in msg for word in motivation_keywords):
            reply = "You’ve got this! 💪 Take a deep breath and keep moving forward."
        elif any(k in msg for k in code_triggers.keys()):
            code_type = code_triggers[[k for k in code_triggers if k in msg][0]]
            reply = f"<pre><code>{self_codes[code_type]}</code></pre>"
        elif any(k in msg for k in image_keywords):
            prompt = msg.replace("generate image of", "").replace("create image of", "").strip()
            reply = generate_image_response(prompt)
        elif any(phrase in msg for phrase in wiki_phrases):
            reply = get_wiki_or_ddg_answer(msg)
        else:
            reply = "🤔 I’m not sure how to respond yet, but I’m always learning!"

    return render_template("index.html", reply=reply, user_message=user_message)

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request
from googletrans import Translator
import requests
import os

app = Flask(__name__)
translator = Translator()
chat_log = []  # Short-term memory

# --- Your source code snippets ---
html_code = open("templates/index.html", "r", encoding="utf-8").read()
css_code = open("static/css/style.css", "r", encoding="utf-8").read()
python_code = open("app.py", "r", encoding="utf-8").read()

# --- Image generation using Hugging Face ---
HF_TOKEN = os.getenv("HF_TOKEN")  # Set as environment variable

def generate_image_url(prompt):
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(api_url, headers=headers, json={"inputs": prompt})
    if response.status_code == 200:
        return "🖼️ Image generated. (HuggingFace returned raw data – customize logic here)"
    else:
        return "❌ Error generating image. Try again later."

# --- Smart Kris Brain ---
def smart_kris_reply(msg):
    msg = msg.lower()

    # Save to short-term memory
    chat_log.append(msg)
    if len(chat_log) > 5:
        chat_log.pop(0)

    # Triggers for code sharing
    if "give your python code" in msg or "app.py" in msg:
        return f"Here is my Python backend code:\n\n```python\n{python_code}```"

    elif "html code" in msg:
        return f"Here's my HTML code:\n\n```html\n{html_code}```"

    elif "css code" in msg:
        return f"Here's my CSS styling code:\n\n```css\n{css_code}```"

    # Image generation
    elif "generate image of" in msg or "draw" in msg or "make image" in msg:
        prompt = msg.replace("generate image of", "").replace("draw", "").replace("make image", "").strip()
        return generate_image_url(prompt)

    # Greetings
    elif "hi" in msg or "hello" in msg:
        return "😊 Hello! I'm Kris AI, your intelligent assistant with mood, memory, and creativity!"

    # About Kris
    elif "who are you" in msg or "your intro" in msg or "what is kris" in msg:
        return (
            "👋 I’m **Kris AI**, your smart assistant made by Yashwanth.\n\n"
            "💡 I can:\n"
            "- Understand your questions\n"
            "- Reply with mood\n"
            "- Share my own code\n"
            "- Generate AI images\n"
            "- Speak in your language\n"
            "- Evolve with time 😎\n\n"
            "Ask me: *Give your Python code*, *Generate image of a robot*, *Tell your intro*, or *Say this in Telugu*!"
        )

    # Multilingual trigger
    elif "say this in telugu" in msg:
        base = msg.replace("say this in telugu", "").strip()
        translated = translator.translate(base, dest="te").text
        return f"📣 In Telugu:\n{translated}"

    elif "say this in hindi" in msg:
        base = msg.replace("say this in hindi", "").strip()
        translated = translator.translate(base, dest="hi").text
        return f"📣 In Hindi:\n{translated}"

    # Fallback
    else:
        return "🤔 I'm still learning. Try asking for my code, intro, or an image!"

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_msg = request.form["message"]
        reply = smart_kris_reply(user_msg)
        return {"reply": reply}
    return render_template("index.html")

# --- Run Server ---
if __name__ == "__main__":
    app.run(debug=True)
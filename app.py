from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form["message"].strip().lower()
    reply = "I'm not sure how to answer that yet."
    mood = "confused"

    # Introduction
    if user_message in ["intro", "introduce", "introduction", "who are you", "what is your name"]:
        reply = (
            "👋 Hello! I’m *Kris AI*, your personal assistant built by Yashwanth in Andhra Pradesh.\n\n"
            "I’m here to help you with:\n"
            "📚 **Studying smart** – Ask questions, get facts, summaries, or explanations.\n"
            "🧠 **Planning** – I help you make study plans, workout routines, and glow-up challenges.\n"
            "🎭 **Mood-based replies** – I respond with emotion like happy, thinking, confused, or excited.\n"
            "🌐 **Multilingual chat** – I understand English, Hindi, and Telugu!\n"
            "💡 Tip: Type 'motivate me' if you're feeling low, or ask for my source code to learn how I work.\n\n"
            "Let’s get started! What would you like help with today?"
        )
        mood = "happy"

    # Code triggers
    elif "give your python code" in user_message:
        reply = (
            "Here is my main backend `app.py` code:\n\n"
            "```python\n"
            "from flask import Flask, render_template, request\n\n"
            "app = Flask(__name__)\n\n"
            "@app.route(\"/\")\n"
            "def home():\n"
            "    return render_template(\"index.html\")\n\n"
            "@app.route(\"/chat\", methods=[\"POST\"])\n"
            "def chat():\n"
            "    user_message = request.form[\"message\"].strip().lower()\n"
            "    reply = \"I'm not sure how to answer that yet.\"\n"
            "    mood = \"confused\"\n"
            "    # Add logic here (e.g., intro, code, etc.)\n"
            "    return {\"reply\": reply, \"mood\": mood}\n\n"
            "if __name__ == \"__main__\":\n"
            "    app.run(debug=True)\n"
            "```"
        )
        mood = "thinking"

    elif "html code" in user_message:
        reply = (
            "Here is my HTML code (`templates/index.html`):\n\n"
            "```html\n"
            "<!DOCTYPE html>\n"
            "<html lang=\"en\">\n"
            "<head>\n"
            "    <meta charset=\"UTF-8\">\n"
            "    <title>Kris AI</title>\n"
            "    <link rel=\"stylesheet\" href=\"/static/css/style.css\">\n"
            "</head>\n"
            "<body>\n"
            "    <div class=\"chat-container\">\n"
            "        <div class=\"top-bar\">\n"
            "            <div class=\"branding\">\n"
            "                <h1>Kris AI</h1>\n"
            "                <p>Made by Yashwanth</p>\n"
            "            </div>\n"
            "            <div class=\"kris-face-wrapper\">\n"
            "                <div class=\"kris-face\" id=\"krisFace\">\n"
            "                    <div class=\"feather\"></div>\n"
            "                    <div class=\"eyes\">\n"
            "                        <div class=\"eye\"></div>\n"
            "                        <div class=\"eye\"></div>\n"
            "                    </div>\n"
            "                    <div class=\"mouth\">\n"
            "                        <div class=\"default-mouth\" id=\"mouth\"></div>\n"
            "                    </div>\n"
            "                </div>\n"
            "            </div>\n"
            "        </div>\n"
            "        <div class=\"chat-box\" id=\"chatBox\"></div>\n"
            "        <form id=\"chatForm\">\n"
            "            <input type=\"text\" id=\"userInput\" placeholder=\"Type here...\">\n"
            "            <button type=\"submit\">Send</button>\n"
            "        </form>\n"
            "    </div>\n"
            "    <script>\n"
            "        const form = document.getElementById('chatForm');\n"
            "        const input = document.getElementById('userInput');\n"
            "        const chatBox = document.getElementById('chatBox');\n"
            "        const krisFace = document.getElementById('krisFace');\n"
            "        const mouth = document.getElementById('mouth');\n\n"
            "        function updateMood(mood) {\n"
            "            mouth.className = '';\n"
            "            if (mood === 'happy') {\n"
            "                mouth.style.borderBottom = '3px solid black';\n"
            "            } else if (mood === 'thinking') {\n"
            "                mouth.style.borderBottom = '2px dashed black';\n"
            "            } else {\n"
            "                mouth.style.borderBottom = '2px solid black';\n"
            "            }\n"
            "        }\n\n"
            "        form.onsubmit = async (e) => {\n"
            "            e.preventDefault();\n"
            "            const message = input.value;\n"
            "            chatBox.innerHTML += `<div class='message user'>${message}</div>`;\n"
            "            input.value = '';\n\n"
            "            const res = await fetch('/chat', {\n"
            "                method: 'POST',\n"
            "                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },\n"
            "                body: 'message=' + encodeURIComponent(message)\n"
            "            });\n\n"
            "            const data = await res.json();\n"
            "            chatBox.innerHTML += `<div class='message bot'>${data.reply}</div>`;\n"
            "            updateMood(data.mood);\n"
            "            chatBox.scrollTop = chatBox.scrollHeight;\n"
            "        }\n"
            "    </script>\n"
            "</body>\n"
            "</html>\n"
            "```"
        )
        mood = "happy"

    elif "css code" in user_message:
        reply = (
            "Here is the CSS file (`static/css/style.css`):\n\n"
            "```css\n"
            "/* Your CSS code here - it's long so not repeating */\n"
            "```"
        )
        mood = "excited"

    # Default fallback
    else:
        reply = "I'm still learning. Try asking for introduction, or type 'give your python code'."
        mood = "thinking"

    return {"reply": reply, "mood": mood}

if __name__ == "__main__":
    app.run(debug=True)
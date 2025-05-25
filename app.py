from flask import Flask, render_template, request
import wikipedia
import requests

app = Flask(__name__)

def get_wikipedia_summary(query):
    try:
        wikipedia.set_lang("en")
        summary = wikipedia.summary(query, sentences=2)
        if "may refer to" in summary.lower() or len(summary) < 40:
            return None
        return summary
    except:
        return None

def get_duckduckgo_summary(query):
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
        res = requests.get(url)
        data = res.json()
        if data.get("Abstract"):
            return data["Abstract"]
        return "Sorry, I couldn’t find information on that topic."
    except:
        return "Sorry, something went wrong while searching."

def detect_mood(user_input):
    user_input = user_input.lower()
    greetings = ['hi', 'hello', 'hey']
    motivation = ['lazy', 'tired', 'no mood', 'bore', 'boring']
    surprised = ['what!', 'no way', 'really?', 'unbelievable']
    question_words = ['what is', 'who is', 'tell me about', 'explain', 'give info', 'do you know', 'please explain']

    if any(word in user_input for word in greetings):
        return 'happy'
    elif any(word in user_input for word in motivation):
        return 'motivation'
    elif any(word in user_input for word in surprised):
        return 'surprised'
    elif any(q in user_input for q in question_words) or user_input.endswith('?'):
        return 'thinking'
    else:
        return 'default'

@app.route('/', methods=['GET', 'POST'])
def home():
    response = None
    mood = "default"
    if request.method == 'POST':
        user_input = request.form.get('message')
        mood = detect_mood(user_input)
        response = get_wikipedia_summary(user_input)
        if not response:
            response = get_duckduckgo_summary(user_input)
    return render_template('index.html', response=response, mood=mood)

if __name__ == '__main__':
    app.run(debug=True)
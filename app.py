from flask import Flask, render_template, request, jsonify import wikipedia import uuid import os

app = Flask(name)

Image generation stub (placeholder for local or external API call)

def generate_image(prompt): return f"https://dummyimage.com/512x512/4da6ff/ffffff.png&text={prompt.replace(' ', '+')[:20]}"

Core reply logic with mood triggers and smart keyword detection

def generate_response(prompt): prompt_lower = prompt.lower()

# Mood-based greetings
if any(greet in prompt_lower for greet in ['hello', 'hi', 'namaste']):
    return "Namaste 🙏! I'm Kris AI — your intelligent buddy with a feathered mind! Ask me anything 😊"

# Provide Kris's own codes
elif 'give your python code' in prompt_lower:
    with open('app.py', 'r') as f:
        return f.read()
elif 'html code' in prompt_lower:
    with open('templates/index.html', 'r') as f:
        return f.read()
elif 'css code' in prompt_lower:
    with open('static/css/style.css', 'r') as f:
        return f.read()

# Wikipedia question handling
elif any(kw in prompt_lower for kw in ["what is", "who is", "tell me about", "explain", "define", "i want to know about"]):
    try:
        topic = prompt_lower
        for phrase in ["what is", "who is", "tell me about", "explain", "define", "i want to know about"]:
            topic = topic.replace(phrase, '')
        summary = wikipedia.summary(topic.strip(), sentences=2)
        return summary
    except:
        return "Hmm... I couldn't find anything on that. Want to try rephrasing it? 🤔"

# Image generation trigger
elif 'generate image of' in prompt_lower:
    prompt = prompt_lower.split('generate image of')[-1].strip()
    image_url = generate_image(prompt)
    return f"Here is your image: <img src='{image_url}' alt='generated image' width='256'>"

# Default response
return "I'm still learning! Try asking a question or say 'give your python code' to see my brain 🧠."

@app.route('/') def index(): return render_template('index.html')

@app.route('/chat', methods=['POST']) def chat(): data = request.get_json() prompt = data.get('prompt', '') response = generate_response(prompt) return jsonify({'response': response})

if name == 'main': app.run(debug=True)


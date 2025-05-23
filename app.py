from flask import Flask, render_template, request, jsonify
import wikipedia

app = Flask(__name__)

# Number of sentences in Wikipedia summary response
SUMMARY_SENTENCES = 3

# List of trigger phrases to detect Wikipedia queries
WIKI_TRIGGERS = [
    'tell me about',
    'what is',
    'what are',
    'who is',
    'who are',
    'explain',
    'give me information about',
    'can you tell me about',
    'do you know about',
    'details about',
    'information on',
    "what's",
    "whats",
    "define",
]

def extract_topic(message):
    msg = message.lower()
    for phrase in WIKI_TRIGGERS:
        if phrase in msg:
            # Extract text after the trigger phrase as the topic
            topic = msg.split(phrase, 1)[1]
            topic = topic.strip(" ?.")
            return topic
    # If no trigger phrase found, treat whole message as topic
    return message.strip(" ?.")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').strip()
    topic = extract_topic(user_message)

    if not topic:
        return jsonify({'response': "Could you please clarify your question?"})

    try:
        # Search Wikipedia for best matching page titles
        search_results = wikipedia.search(topic)

        if not search_results:
            return jsonify({'response': "Sorry, I couldn't find any information on that topic."})

        page_title = search_results[0]  # Pick the best result

        # Get summary of the page
        summary = wikipedia.summary(page_title, sentences=SUMMARY_SENTENCES)

        return jsonify({'response': summary})

    except wikipedia.DisambiguationError as e:
        options = ', '.join(e.options[:5])
        response = f"Your question is ambiguous. Did you mean: {options}?"
        return jsonify({'response': response})

    except wikipedia.PageError:
        return jsonify({'response': "Sorry, I couldn't find any page matching that topic."})

    except Exception:
        return jsonify({'response': "Sorry, I encountered an error while searching. Please try again."})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
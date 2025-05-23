from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_msg = data.get('message', '')
    # Simple reply logic
    reply = f"Krisna: You said '{user_msg}'. This is a prototype reply."
    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify, render_template
import datetime

app = Flask(__name__)

def assistant_logic(send):
    data_btn = send.lower()

    if "what is your name" in data_btn:
        return "My name is Virtual Assistant"
    elif "hello" in data_btn or "hye" in data_btn or "hay" in data_btn or "hi" in data_btn:
        return "Hey sir, how can I help you!"
    elif "how are you" in data_btn:
        return "I am doing great these days, sir."
    elif "thanku" in data_btn or "thank" in data_btn:
        return "It's my pleasure, sir, to stay with you."
    elif "good morning" in data_btn:
        return "Good morning sir, I think you might need some help."
    elif "time now" in data_btn:
        now = datetime.datetime.now()
        return f"{now.hour} Hour : {now.minute} Minute"
    elif "open youtube" in data_btn:
        return "OPEN_YOUTUBE"
    elif "open google" in data_btn:
        return "OPEN_GOOGLE"
    elif "open facebook" in data_btn:
        return "OPEN_FACEBOOK"
    elif "open sbtet" in data_btn:
        return "OPEN_SBTET"
    elif "open music" in data_btn:
        return "OPEN_MUSIC"
    elif "shutdown" in data_btn or "quit" in data_btn:
        return "Ok sir. Shutting down."
    else:
        return "Sorry I'm still at Training state couldn't responde to your requirements"


@app.route("/")
def index():
    return render_template("index.html")  # Loads the chat UI

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    reply = assistant_logic(user_message)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)

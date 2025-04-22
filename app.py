from flask import Flask, request, render_template, jsonify
from transformers import pipeline

app = Flask(__name__)
chatbot = pipeline("conversational", model="microsoft/DialoGPT-small")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form["message"]
    response = chatbot(user_input)
    bot_reply = response[0]['generated_responses'][-1]
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)

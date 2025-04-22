from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)

# Load lightweight model (low RAM)
chatbot = pipeline("text-generation", model="sshleifer/tiny-gpt2", device=-1)

@app.route("/")
def home():
    return "Chatbot is running. Send POST to /chat with JSON {\"message\": \"your text\"}"

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    
    if not user_input.strip():
        return jsonify({"response": "Please say something!"})

    # Generate response (limit max tokens for low RAM)
    response = chatbot(user_input, max_new_tokens=30, do_sample=True)[0]["generated_text"]
    
    # Return only the generated part, after input
    reply = response[len(user_input):].strip()
    
    return jsonify({"response": reply})
    
if __name__ == "__main__":
    app.run(debug=True)

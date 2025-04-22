from flask import Flask, render_template, request, jsonify
import smtplib, random
from email.message import EmailMessage
import pickle
import nltk
from nltk.stem import WordNetLemmatizer

app = Flask(__name__)

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Load trained model
with open("chatbot/model.pkl", "rb") as f:
    clf, vectorizer, data = pickle.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sudo')
def sudo():
    return render_template('sudo.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        receiver_email = request.form['email']
        otp = str(random.randint(100000, 999999))

        sender_email = 'devnasruls@gmail.com'
        sender_password = 'xhzc debk mmzq urfo'

        msg = EmailMessage()
        msg['Subject'] = 'Your OTP Code'
        msg['From'] = f"Dev Nasrul <{sender_email}>"
        msg['To'] = receiver_email
        msg.set_content(f'Your OTP is: {otp}')

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(sender_email, sender_password)
                smtp.send_message(msg)
            return f"OTP sent to {receiver_email}: {otp}"
        except Exception as e:
            return f"Error: {str(e)}"

    return render_template('login.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.form['msg']
    tokens = nltk.word_tokenize(user_msg)
    tokens = [lemmatizer.lemmatize(word.lower()) for word in tokens]
    X = vectorizer.transform([" ".join(tokens)])
    tag = clf.predict(X)[0]

    for intent in data['intents']:
        if intent['tag'] == tag:
            response = random.choice(intent['responses'])
            return jsonify({'response': response})

    return jsonify({'response': "Sorry, I don't understand that."})

if __name__ == '__main__':
    app.run(debug=True)

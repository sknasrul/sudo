from flask import Flask, render_template, request
import smtplib, random
from email.message import EmailMessage
app = Flask(__name__)

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

        # Email setup
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

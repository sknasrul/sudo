from flask import Flask, render_template, request, send_file
from pytube import YouTube
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('yt.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    yt = YouTube(url)
    stream = yt.streams.get_highest_resolution()
    filepath = stream.download()
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

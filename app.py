from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    output_path = 'downloads'
    os.makedirs(output_path, exist_ok=True)

    ydl_opts = {
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'cookies': 'cookies.txt',  # Your exported YouTube cookies file
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace(".webm", ".mp4").replace(".mkv", ".mp4")
            return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"<h2>Error: {str(e)}</h2>"

if __name__ == '__main__':
    app.run(debug=True)

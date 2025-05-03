from flask import Flask, request, render_template_string, send_file
import yt_dlp
import os

app = Flask(__name__)
DOWNLOADS_FOLDER = 'downloads'
os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template_string('''
        <h2>Download YouTube Video</h2>
        <form method="POST" action="/download">
            <input type="text" name="url" placeholder="Enter YouTube URL" required>
            <button type="submit">Download</button>
        </form>
    ''')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'ffmpeg_location': '/usr/bin/',  # Adjust if using static build
        'outtmpl': os.path.join(DOWNLOADS_FOLDER, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp4'
            return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"<h3>Error:</h3><pre>{str(e)}</pre>"

if __name__ == '__main__':
    app.run(debug=True)

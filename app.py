from flask import Flask, request, render_template_string, send_file
import yt_dlp
import os

app = Flask(__name__)
DOWNLOAD_PATH = "video.mp4"

HTML = '''
<!DOCTYPE html>
<html>
<head><title>Simple YouTube Downloader</title></head>
<body>
  <h2>Download YouTube Video</h2>
  <form method="post">
    <input type="text" name="url" placeholder="Enter YouTube URL" required>
    <button type="submit">Download</button>
  </form>
  {% if ready %}
    <p>Done! <a href="/download">Click here to download</a></p>
  {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    ready = False
    if request.method == 'POST':
        url = request.form['url']
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': DOWNLOAD_PATH,
            'quiet': True,
            'merge_output_format': 'mp4'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        ready = True
    return render_template_string(HTML, ready=ready)

@app.route('/download')
def download():
    return send_file(DOWNLOAD_PATH, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

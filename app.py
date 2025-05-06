from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import re
import uuid
import time
import subprocess
import logging
import sys

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Create a temporary directory for downloads
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Clean up old downloads periodically
def cleanup_old_files():
    current_time = time.time()
    for filename in os.listdir(DOWNLOAD_FOLDER):
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        # Remove files older than 1 hour
        if os.path.isfile(file_path) and current_time - os.path.getmtime(file_path) > 3600:
            try:
                os.remove(file_path)
                app.logger.info(f"Cleaned up old file: {filename}")
            except Exception as e:
                app.logger.error(f"Failed to clean up file {filename}: {str(e)}")

@app.route('/', methods=['GET', 'POST'])
def index():
    error_message = ""
    success_message = ""
    download_link = ""
    
    if request.method == 'POST':
        # Clean up old downloads before processing new ones
        cleanup_old_files()
        
        # Get URL from form
        video_url = request.form.get('url', '').strip()
        
        # Basic URL validation
        if not video_url:
            error_message = "Please enter a URL."
            return render_template('index.html', error=error_message)
        
        try:
            # Generate a unique filename
            filename = f"{uuid.uuid4().hex}.mp4"
            output_path = os.path.join(DOWNLOAD_FOLDER, filename)
            
            # Use yt-dlp to download the video
            # yt-dlp is much more robust than pytube and supports many sites
            cmd = [
                'yt-dlp',
                '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                '-o', output_path,
                '--no-playlist',
                video_url
            ]
            
            app.logger.info(f"Running command: {' '.join(cmd)}")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                if stderr:
                    error_message = f"Download failed: {stderr}"
                    app.logger.error(f"yt-dlp error: {stderr}")
                else:
                    error_message = "Download failed with unknown error."
                    app.logger.error("yt-dlp failed with no error output")
                return render_template('index.html', error=error_message)
            
            # Check if file exists
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                # Get the title from yt-dlp output or use generic title
                title_match = re.search(r'Destination: .*\[(.*?)\]', stdout)
                if title_match:
                    video_title = title_match.group(1)
                else:
                    video_title = "Downloaded Video"
                
                download_link = url_for('download_file', filename=filename)
                success_message = f"Successfully downloaded: {video_title}"
            else:
                error_message = "Download completed but file was not created."
                app.logger.error("File not found after download reported success")
            
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            app.logger.error(f"Exception during download: {str(e)}")
    
    return render_template('index.html', error=error_message, success=success_message, download_link=download_link)

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return "File not found", 404
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        app.logger.error(f"Error downloading file: {str(e)}")
        return f"Error downloading file: {str(e)}", 500

@app.route('/about')
def about():
    return render_template('about.html')

# Create templates directory if it doesn't exist
os.makedirs('templates', exist_ok=True)

# Create HTML templates if they don't exist
if not os.path.exists('templates/index.html'):
    with open('templates/index.html', 'w') as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Downloader</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        h1 {
            color: #cc0000;
            text-align: center;
            margin-bottom: 30px;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        button {
            background-color: #cc0000;
            color: white;
            border: none;
            padding: 12px 20px;
            font-size: 16px;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
        }
        button:hover {
            background-color: #b30000;
        }
        .error {
            color: #cc0000;
            margin-top: 10px;
        }
        .success {
            color: #28a745;
            margin-top: 10px;
        }
        .download-link {
            display: block;
            margin-top: 20px;
            text-align: center;
            background-color: #28a745;
            color: white;
            padding: 12px;
            border-radius: 4px;
            text-decoration: none;
        }
        .download-link:hover {
            background-color: #218838;
        }
        footer {
            margin-top: 30px;
            text-align: center;
            font-size: 14px;
            color: #666;
        }
        footer a {
            color: #cc0000;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Video Downloader</h1>
        <form method="POST">
            <div class="form-group">
                <label for="url">Enter Video URL:</label>
                <input type="text" id="url" name="url" placeholder="https://www.youtube.com/watch?v=..." required>
            </div>
            <button type="submit">Download Video</button>
        </form>
        
        {% if error %}
        <p class="error">{{ error }}</p>
        {% endif %}
        
        {% if success %}
        <p class="success">{{ success }}</p>
        {% endif %}
        
        {% if download_link %}
        <a href="{{ download_link }}" class="download-link">Download Video</a>
        {% endif %}
    </div>
    
    <footer>
        <p>Made with <span style="color: #cc0000;">❤</span> | <a href="{{ url_for('about') }}">About</a></p>
    </footer>
</body>
</html>""")

if not os.path.exists('templates/about.html'):
    with open('templates/about.html', 'w') as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About - Video Downloader</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        h1 {
            color: #cc0000;
            text-align: center;
            margin-bottom: 30px;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .back-link {
            display: inline-block;
            margin-top: 20px;
            color: #cc0000;
            text-decoration: none;
        }
        footer {
            margin-top: 30px;
            text-align: center;
            font-size: 14px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>About This Tool</h1>
        <p>This is a versatile video downloader that supports multiple platforms including YouTube, Vimeo, Twitter, Facebook, and many more.</p>
        <p>It uses yt-dlp to download videos in the highest available quality.</p>
        <p>Note: This application is for educational purposes only. Please respect copyright and only download videos you have permission to use.</p>
        
        <h2>How to Use</h2>
        <ol>
            <li>Enter a valid video URL in the input field</li>
            <li>Click the "Download Video" button</li>
            <li>Wait for the download to complete</li>
            <li>Click on the "Download Video" link to save the file to your device</li>
        </ol>
        
        <a href="{{ url_for('index') }}" class="back-link">← Back to Downloader</a>
    </div>
    
    <footer>
        <p>Made with Python and Flask</p>
    </footer>
</body>
</html>""")

if __name__ == '__main__':
    app.run(debug=True)

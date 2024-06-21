from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from pytube import YouTube
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format_choice = request.form['format']
    try:
        yt = YouTube(url)
        if format_choice == "MP4":
            video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            if video_stream is None:
                video_stream = yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
            video_stream.download(output_path=DOWNLOAD_FOLDER)
            filename = video_stream.default_filename
            flash(f"Downloaded {yt.title} successfully in MP4 format.", "success")
        elif format_choice == "MP3":
            audio_stream = yt.streams.filter(only_audio=True).first()
            out_file = audio_stream.download(output_path=DOWNLOAD_FOLDER)
            base, ext = os.path.splitext(out_file)
            new_file = base + '.mp3'
            os.rename(out_file, new_file)
            filename = os.path.basename(new_file)
            flash(f"Downloaded {yt.title} successfully in MP3 format.", "success")
        return redirect(url_for('downloaded_file', filename=filename))
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for('index'))

@app.route('/downloaded/<filename>')
def downloaded_file(filename):
    return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

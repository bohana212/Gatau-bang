from flask import Flask, request, jsonify, send_from_directory
from yt_dlp import YoutubeDL
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

STATIC_DIR = 'static'
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('link')
    mode = data.get('mode', 'video')
    resolution = data.get('resolution', '720p')
    quality = data.get('quality', 'Medium')

    if not url:
        return jsonify({'status': 'error', 'message': 'No link provided'})

    output_file = os.path.join(STATIC_DIR, '%(title).70s.%(ext)s')

    ydl_opts = {
        'outtmpl': output_file,
        'noplaylist': True,
        'quiet': True,
    }

    if mode == 'audio':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192' if quality == 'High' else '128' if quality == 'Medium' else '64',
        }]
    else:
        ydl_opts['format'] = f'bestvideo[height<={resolution[:-1]}]+bestaudio/best'

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if mode == 'audio':
                filename = os.path.splitext(filename)[0] + '.mp3'
        basename = os.path.basename(filename)
        return jsonify({'status': 'success', 'file': f'/static/{basename}', 'filename': basename})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/static/<path:filename>')
def serve_file(filename):
    return send_from_directory(STATIC_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)

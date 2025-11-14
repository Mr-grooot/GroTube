from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for local development

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.json
        url = data.get('url')
        quality = data.get('quality', 'best')
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Configure download options based on quality
        if quality == 'audio':
            # Audio only download
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'verbose': True,
            }
        else:
            # Video download with audio merged
            if quality == 'best':
                # Download best video and best audio, then merge
                format_string = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            else:
                # Download specific resolution with audio
                format_string = f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}][ext=mp4]/best'
            
            ydl_opts = {
                'format': format_string,
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
                'merge_output_format': 'mp4',  # Force merge to mp4
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
                'verbose': True,
            }
        
        print(f"\n📥 Downloading from: {url}")
        print(f"🎯 Quality: {quality}")
        print(f"⚙️  Format: {ydl_opts.get('format', 'default')}\n")
        
        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'video')
            
        print(f"\n✅ Download completed: {title}\n")
        
        return jsonify({
            'success': True,
            'message': f'✅ Downloaded: {title}',
            'title': title
        })
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 YouTube Downloader Server")
    print("="*50)
    print(f"📡 Server: http://localhost:5000")
    print(f"📂 Downloads: {os.path.abspath(DOWNLOAD_FOLDER)}")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)

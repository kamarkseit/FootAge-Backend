from flask import Flask, request
from flask_cors import CORS
import subprocess
import sys

app = Flask(__name__)
#CORS(app)
CORS(app, resources={r"/upload": {"origins": "https://kamarkseit.github.io"}})  # ✅ This enables cross-origin requests

@app.route('/upload', methods=['POST'])
def upload_video():
    video = request.files['video']
    video.save('walk_video.mp4')
    subprocess.run([sys.executable, 'extract_and_upload.py'], check=True)
    return "✅ Video processed and frames uploaded"

if __name__ == '__main__':
    app.run(debug=True)


import subprocess
import boto3
import os
import json
from datetime import datetime
import sys

# === CONFIG ===
VIDEO_PATH = 'walk_video.mp4'           # Video saved from frontend
FRAME_DIR = 'frames'                    # Where extracted frames go
# BUCKET_NAME = 'plastic-bottle-detector-images'     # Replace with your actual bucket
S3_PREFIX = 'uploads/'              # Optional folder path in S3
id = sys.argv[1]
print(f"🎬 Processing with ID: {id}")

# === SETUP ===
os.makedirs(FRAME_DIR, exist_ok=True)
id_dir = os.path.join(FRAME_DIR, id)
os.makedirs(id_dir, exist_ok=True)

s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name=os.environ['AWS_REGION']
)

# Get Frame Count and Frame Rate
def get_frame_info(video_path):
    cmd = [
        'ffprobe', '-v', 'error',
        '-select_streams', 'v:0',
        '-count_frames',
        '-show_entries', 'stream=nb_read_frames,r_frame_rate',
        '-of', 'json',
        video_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    data = json.loads(result.stdout)
    frames = int(data['streams'][0]['nb_read_frames'])
    rate = data['streams'][0]['r_frame_rate']
    fps = eval(rate)  # e.g. '30/1' → 30.0

    return frames, fps

# Generate Timestamps Every ~0.5 Second
def generate_frame_timestamps(frames, fps):
    return [i / fps for i in range(0, frames, int(fps/2))]

# === STEP 1: Extract Frames Using ffmpeg ===
frames, fps = get_frame_info(VIDEO_PATH)
timestamps = generate_frame_timestamps(frames, fps)
print("Timestamps: ", timestamps)

for i, ts in enumerate(timestamps, start=1):
    frame_path = os.path.join(id_dir, f'frame_{id}_{i:02d}.jpg')
    cmd = [
        'ffmpeg', '-ss', str(ts), '-i', VIDEO_PATH,
        '-frames:v', '1', '-q:v', '2', frame_path
    ]
    subprocess.run(cmd, check=True)
print("📂 Extracted frames list: ", os.listdir(FRAME_DIR))


# === STEP 2: Upload Frames to S3 ===
for filename in os.listdir(FRAME_DIR):
    local_path = os.path.join(FRAME_DIR, filename)
    s3_key = f'{S3_PREFIX}{filename}'
    s3.upload_file(local_path, os.environ['BUCKET_NAME'], s3_key)

print('EXTRACT & UPLOAD COMPLETED !!!')




import subprocess
import boto3
import os
import json
from datetime import datetime

# === CONFIG ===
VIDEO_PATH = 'walk_video.mp4'           # Video saved from frontend
FRAME_DIR = 'frames'                    # Where extracted frames go
# BUCKET_NAME = 'plastic-bottle-detector-images'     # Replace with your actual bucket
S3_PREFIX = 'uploads/'              # Optional folder path in S3

# === SETUP ===
os.makedirs(FRAME_DIR, exist_ok=True)

s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name=os.environ['AWS_REGION']
)

# Get current date and time string once
timestamp_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# Get Video Duration Using ffprobe
def get_video_duration(video_path):
    cmd = [
        'ffprobe', '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'format=duration',
        '-of', 'json',
        video_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    print("🧾 ffprobe output:", result.stdout)

    try:
        duration_json = json.loads(result.stdout)
        duration = float(duration_json['format']['duration'])
        return duration
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        print(f"❌ Failed to get duration: {e}")
        return None


# Generate Timestamps Every 1 Second
def generate_timestamps(duration, interval=1):
    return [f"{int(t // 60):02d}:{int(t % 60):02d}:00" for t in range(0, int(duration), interval)]


# === STEP 1: Extract Frames at 1s Intervals ===
duration = get_video_duration(VIDEO_PATH)
timestamps = generate_timestamps(duration, interval=1)
print("Timestamps list is here: ", timestamps)


for i, ts in enumerate(timestamps, start=1):
    frame_path = os.path.join(FRAME_DIR, f'frame_{timestamp_str}_{i:02d}.jpg')
    cmd = [
        'ffmpeg', '-ss', ts, '-i', VIDEO_PATH,
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




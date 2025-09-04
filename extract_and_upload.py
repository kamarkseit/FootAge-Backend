import subprocess
import boto3
import os

# === CONFIG ===
VIDEO_PATH = 'walk_video.mp4'           # Video saved from frontend
FRAME_DIR = 'frames'                    # Where extracted frames go
BUCKET_NAME = 'plastic-bottle-detector-images'     # Replace with your actual bucket
S3_PREFIX = 'uploads/'              # Optional folder path in S3

# === SETUP ===
os.makedirs(FRAME_DIR, exist_ok=True)

s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name=os.environ['AWS_REGION']
)

# === STEP 1: Extract 6 Frames at 10s Intervals ===
timestamps = ['00:00:10', '00:00:20', '00:00:30', '00:00:40', '00:00:50', '00:01:00']

for i, ts in enumerate(timestamps, start=1):
    frame_path = f'{FRAME_DIR}/frame_{i:02d}.jpg'
    cmd = [
        'ffmpeg', '-ss', ts, '-i', VIDEO_PATH,
        '-frames:v', '1', '-q:v', '2', frame_path
    ]
    subprocess.run(cmd, check=True)
    print(f'✅ Extracted frame {i} at {ts}')

# === STEP 2: Upload Frames to S3 ===
for filename in os.listdir(FRAME_DIR):
    local_path = os.path.join(FRAME_DIR, filename)
    s3_key = f'{S3_PREFIX}{filename}'
    s3.upload_file(local_path, BUCKET_NAME, s3_key)
    print(f'📤 Uploaded {filename} to s3://{BUCKET_NAME}/{s3_key}')

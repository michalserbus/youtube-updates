import subprocess
import sys

# Get metadata for first 10 cached video IDs
cached_ids = [
    "oeUOGBJZdl0", "vabRab9F0w4", "t700StIhtZo", "6mjnfAz5wlQ", "foXDDxSbZ7k",
    "SWIk9g6-zBM", "7Ju87DdiE0Y", "7Ijaf2HFvjg", "a_8PPgYPpaQ", "oeUOGBJZdl0"
]

for video_id in cached_ids:
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--print", "%(id)s|||%(title)s|||%(duration)s|||%(upload_date)s|||%(webpage_url)s",
        f"https://www.youtube.com/watch?v={video_id}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.stdout:
        print(result.stdout.strip())

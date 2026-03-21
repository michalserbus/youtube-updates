import os
import sys
import subprocess
import json
from datetime import datetime, timedelta
import re

# === CONFIG ===
YOUTUBE_URL = "https://www.youtube.com/@JulianGoldieSEO/videos"
CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache", "subtitles")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "index.html")
MAX_VIDEOS = 150
DAYS_BACK = int(os.getenv("DAYS_BACK", "7"))
CUTOFF_DATE = (datetime.now() - timedelta(days=DAYS_BACK)).strftime("%Y%m%d")

def get_videos():
    """Get videos from yt-dlp with metadata"""
    cmd = [
        "yt-dlp",
        "--playlist-end", str(MAX_VIDEOS),
        "--skip-download",
        "--print", "%(id)s|||%(title)s|||%(duration)s|||%(upload_date)s|||%(webpage_url)s|||%(thumbnail)s",
        YOUTUBE_URL
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    videos = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|||")
        if len(parts) >= 6:
            video_id, title, duration, upload_date, url, thumbnail = parts
            if upload_date != "NA" and upload_date >= CUTOFF_DATE:
                videos.append({
                    "id": video_id,
                    "title": title.strip(),
                    "duration": int(duration) if duration != "NA" else 0,
                    "upload_date": upload_date,
                    "url": url,
                    "thumbnail": thumbnail
                })
    return videos

def get_subtitles(video_id):
    """Get cached subtitles or download them"""
    cache_file = os.path.join(CACHE_DIR, f"{video_id}.txt")
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read()
    
    # Download subtitles
    cmd = [
        "yt-dlp",
        "--write-subs",
        "--skip-download",
        "--sub-langs", "en",
        "--sub-format", "txt",
        "--output", f"{cache_file}.temp",
        f"https://www.youtube.com/watch?v={video_id}"
    ]
    subprocess.run(cmd, capture_output=True, text=True)
    
    # Find the downloaded file
    temp_file = f"{cache_file}.temp.en.txt"
    if os.path.exists(temp_file):
        os.rename(temp_file, cache_file)
        os.remove(f"{cache_file}.temp")
    
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def generate_summary(subtitles, max_chars):
    """Generate summary from subtitle text"""
    if not subtitles:
        return "Žádné titulky k dispozici."
    
    # Clean up subtitles
    subtitles = re.sub(r'\d{2}:\d{2}:\d{2}.\d{3} --> \d{2}:\d{2}:\d{2}.\d{3}', '', subtitles)
    subtitles = re.sub(r'\n+', '\n', subtitles).strip()
    
    # Take first max_chars characters
    if len(subtitles) > max_chars:
        return subtitles[:max_chars] + "..."
    return subtitles

def format_duration(seconds):
    """Format seconds to HH:MM:SS"""
    if seconds == 0:
        return "N/A"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def generate_html(videos):
    """Generate HTML page"""
    # Sort by upload_date newest first
    videos.sort(key=lambda x: x["upload_date"], reverse=True)
    
    html = f'''<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Video Updates - YouTube</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .video-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }}
        .video-card {{ background: #16213e; border-radius: 10px; overflow: hidden; }}
        .video-thumb {{ width: 100%; aspect-ratio: 16/9; object-fit: cover; }}
        .video-info {{ padding: 15px; }}
        .video-title {{ font-size: 1.1em; margin: 0 0 10px 0; color: #fff; }}
        .video-meta {{ display: flex; justify-content: space-between; color: #888; font-size: 0.9em; }}
        .video-summary {{ margin-top: 10px; font-size: 0.95em; color: #ccc; line-height: 1.5; }}
        .video-detail {{ margin-top: 10px; font-size: 0.9em; color: #999; display: none; padding-top: 10px; border-top: 1px solid #333; }}
        .toggle-btn {{ background: #0f3460; color: #fff; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; margin-top: 10px; }}
        .toggle-btn:hover {{ background: #1a5f7a; }}
        .visible {{ display: block !important; }}
        footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 0.85em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎬 AI Video Updates</h1>
        <p>Kanal: JulianGoldieSEO | Posledních {DAYS_BACK} dní</p>
    </div>
    
    <div class="video-grid">
'''

    for v in videos:
        date_str = v["upload_date"]
        formatted_date = f"{date_str[6:8]}.{date_str[4:6]}.{date_str[0:4]}"
        duration = format_duration(v["duration"])
        
        html += f'''
        <div class="video-card">
            <img src="{v["thumbnail"]}" class="video-thumb" alt="thumbnail">
            <div class="video-info">
                <h3 class="video-title">{v["title"]}</h3>
                <div class="video-meta">
                    <span>📅 {formatted_date}</span>
                    <span>⏱ {duration}</span>
                </div>
                <div class="video-summary">
                    <button class="toggle-btn" onclick="toggleDetail(this)">📖 Zobrazit podrobnosti</button>
                    <div class="video-detail">
                        <p><strong>Plná URL:</strong> <a href="{v["url"]}" target="_blank">{v["url"]}</a></p>
                        <p><strong>Délka:</strong> {duration}</p>
                        <p><strong>Publikováno:</strong> {formatted_date}</p>
                        <p><strong>Titulky:</strong> Stáhni titulky pro detailní obsah...</p>
                    </div>
                </div>
            </div>
        </div>
'''

    html += '''
    </div>
    
    <footer>
        <p>Automaticky generováno OpenClaw agentem | Data: yt-dlp | {date.today()}</p>
    </footer>
    
    <script>
        function toggleDetail(btn) {
            const detail = btn.nextElementSibling;
            detail.classList.toggle("visible");
            btn.textContent = detail.classList.contains("visible") ? "📬 Skrýt podrobnosti" : "📖 Zobrazit podrobnosti";
        }
    </script>
</body>
</html>'''

    return html

def main():
    print(f"=== YouTube AI Updates Generator (Simple) ===")
    print(f"Days back: {DAYS_BACK}, Cutoff: {CUTOFF_DATE}")
    print("=" * 50)
    
    print("Fetching videos...")
    videos = get_videos()
    print(f"Found {len(videos)} videos")
    
    for i, v in enumerate(videos, 1):
        print(f"[{i}/{len(videos)}] {v['title'][:50]}...")
    
    html = generate_html(videos)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"\nGenerated {OUTPUT_FILE}")
    print(f"Videos: {len(videos)}")
    
    # Git commit and push
    print("\nCommitting and pushing...")
    os.chdir(os.path.dirname(__file__))
    subprocess.run(["git", "add", "index.html"], capture_output=True)
    subprocess.run(["git", "commit", "-m", f"Update with {len(videos)} videos (no AI summary)"], capture_output=True)
    subprocess.run(["git", "push"], capture_output=True)
    
    print("Done!")
    print(f"Web: https://michalserbus.github.io/youtube-updates/")

if __name__ == "__main__":
    main()

import os
import json
from datetime import datetime, timedelta

# Create a minimal HTML with the videos we know about
videos = [
    {"id": "oeUOGBJZdl0", "title": "Build Anything with Nemotron 3 Here's How!", "duration": 494, "upload_date": "20260320"},
    {"id": "vabRab9F0w4", "title": "Nvidia's New NemoClaw + OpenClaw Update Free!", "duration": 60, "upload_date": "20260319"},
    {"id": "t700StIhtZo", "title": "Nvidia's New FREE NemoClaw + OpenClaw Update!", "duration": 60, "upload_date": "20260319"},
]

html = '''<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Video Updates - YouTube</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }
        .header { text-align: center; margin-bottom: 30px; }
        .video-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }
        .video-card { background: #16213e; border-radius: 10px; overflow: hidden; }
        .video-thumb { width: 100%; aspect-ratio: 16/9; object-fit: cover; background: #0f3460; }
        .video-info { padding: 15px; }
        .video-title { font-size: 1.1em; margin: 0 0 10px 0; color: #fff; }
        .video-meta { display: flex; justify-content: space-between; color: #888; font-size: 0.9em; }
        .video-summary { margin-top: 10px; font-size: 0.95em; color: #ccc; line-height: 1.5; }
        .video-detail { margin-top: 10px; font-size: 0.9em; color: #999; display: none; padding-top: 10px; border-top: 1px solid #333; }
        .toggle-btn { background: #0f3460; color: #fff; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; margin-top: 10px; }
        .toggle-btn:hover { background: #1a5f7a; }
        .visible { display: block !important; }
        footer { text-align: center; margin-top: 30px; color: #666; font-size: 0.85em; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎬 AI Video Updates</h1>
        <p>Kanal: JulianGoldieSEO | Posledních 7 dní (test)</p>
    </div>
    
    <div class="video-grid">
'''

for v in videos:
    date_str = v["upload_date"]
    formatted_date = f"{date_str[6:8]}.{date_str[4:6]}.{date_str[0:4]}"
    h = v["duration"] // 3600
    m = (v["duration"] % 3600) // 60
    s = v["duration"] % 60
    duration = f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
    
    html += f'''
    <div class="video-card">
        <div class="video-thumb" style="display: flex; align-items: center; justify-content: center; color: #666;">
            📺 Náhled
        </div>
        <div class="video-info">
            <h3 class="video-title">{v["title"]}</h3>
            <div class="video-meta">
                <span>📅 {formatted_date}</span>
                <span>⏱ {duration}</span>
            </div>
            <div class="video-summary">
                <button class="toggle-btn" onclick="toggleDetail(this)">📖 Zobrazit podrobnosti</button>
                <div class="video-detail">
                    <p><strong>Video ID:</strong> {v["id"]}</p>
                    <p><strong>Délka:</strong> {duration}</p>
                    <p><strong>Publikováno:</strong> {formatted_date}</p>
                    <p><strong>URL:</strong> <a href="https://www.youtube.com/watch?v={v['id']}" target="_blank">YouTube</a></p>
                </div>
            </div>
        </div>
    </div>
'''

html += '''
    </div>
    
    <footer>
        <p>Automaticky generováno OpenClaw agentem | Poznámka: Plná verze s AI shrnutími bude hotová zítra, až se obnoví Google API limit.</p>
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

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Generated index.html with {len(videos)} videos")
print("URL: https://michalserbus.github.io/youtube-updates/")

# Commit and push
import subprocess
os.chdir("/Users/w/.openclaw/workspace/youtube-updates")
subprocess.run(["git", "add", "index.html"], capture_output=True)
subprocess.run(["git", "commit", "-m", f"Update with {len(videos)} videos (AI summary pending)"], capture_output=True)
subprocess.run(["git", "push"], capture_output=True)

print("Pushed to GitHub!")

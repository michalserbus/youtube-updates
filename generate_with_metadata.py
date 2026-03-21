import os
from datetime import datetime

# Videos with metadata (newest first)
videos = [
    {"id": "oeUOGBJZdl0", "title": "Build Anything with Nemotron 3 Here's How!", "duration": 494, "upload_date": "20260320", "url": "https://www.youtube.com/watch?v=oeUOGBJZdl0"},
    {"id": "6mjnfAz5wlQ", "title": "NEW Google AI Updates are INSANE! 🤯", "duration": 511, "upload_date": "20260320", "url": "https://www.youtube.com/watch?v=6mjnfAz5wlQ"},
    {"id": "foXDDxSbZ7k", "title": "NEW Claude Code Update is INSANE!", "duration": 570, "upload_date": "20260320", "url": "https://www.youtube.com/watch?v=foXDDxSbZ7k"},
    {"id": "7Ijaf2HFvjg", "title": "After the Storm: Public Safety, Project Alpha & AI | March 20, 2026", "duration": 1994, "upload_date": "20260320", "url": "https://www.youtube.com/watch?v=7Ijaf2HFvjg"}
]

def format_date(date_str):
    return f"{date_str[6:8]}.{date_str[4:6]}.{date_str[0:4]}"

def format_duration(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

html = f'''<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Video Updates - YouTube</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #ffffff; color: #222222; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .video-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }}
        .video-card {{ background: #f5f7fa; border-radius: 10px; overflow: hidden; transition: transform 0.2s; }}
        .video-card:hover {{ transform: translateY(-3px); }}
        .video-thumb {{ width: 100%; aspect-ratio: 16/9; background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%); display: flex; align-items: center; justify-content: center; font-size: 2em; }}
        .video-info {{ padding: 15px; }}
        .video-title {{ font-size: 1.1em; margin: 0 0 10px 0; color: #222222; }}
        .video-meta {{ display: flex; justify-content: space-between; color: #555; font-size: 0.9em; }}
        .video-summary {{ margin-top: 10px; font-size: 0.95em; color: #333; line-height: 1.5; }}
        .video-detail {{ margin-top: 10px; font-size: 0.9em; color: #555; display: none; padding-top: 10px; border-top: 1px solid #333; }}
        .toggle-btn {{ background: #2563eb; color: #222222; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; margin-top: 10px; }}
        .toggle-btn:hover {{ background: #1d4ed8; }}
        .visible {{ display: block !important; }}
        footer {{ text-align: center; margin-top: 30px; color: #555; font-size: 0.85em; }}
        .badge {{ background: #1d4ed8; padding: 2px 8px; border-radius: 10px; font-size: 0.8em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎬 AI Video Updates</h1>
        <p>Kanal: <span class="badge">JulianGoldieSEO</span> | Posledních 24 hodin | {len(videos)} videí</p>
    </div>
    
    <div class="video-grid">
'''

for v in videos:
    formatted_date = format_date(v["upload_date"])
    duration = format_duration(v["duration"])
    
    # Generate a simple summary based on the title
    summary = f"Video o hlavních novinkách v AI a technologiích. Klikněte na 'Zobrazit podrobnosti' pro více informací."
    
    html += f'''
    <div class="video-card">
        <div class="video-thumb">📺</div>
        <div class="video-info">
            <h3 class="video-title">{v["title"]}</h3>
            <div class="video-meta">
                <span>📅 {formatted_date}</span>
                <span>⏱ {duration}</span>
            </div>
            <div class="video-summary">
                <p>{summary}</p>
                <button class="toggle-btn" onclick="toggleDetail(this)">📖 Zobrazit podrobnosti</button>
                <div class="video-detail">
                    <p><strong>Video ID:</strong> {v["id"]}</p>
                    <p><strong>Délka:</strong> {duration}</p>
                    <p><strong>Publikováno:</strong> {formatted_date}</p>
                    <p><strong>URL:</strong> <a href="{v["url"]}" target="_blank" style="color: #2563eb;">YouTube</a></p>
                </div>
            </div>
        </div>
    </div>
'''

html += '''
    </div>
    
    <footer>
        <p>Automaticky generováno OpenClaw agentem | Poznámka: Podrobná AI shrnutí budou přidána po obnovení Google API limitu (zítra ráno).</p>
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

print(f"✅ Generated index.html with {len(videos)} videos")
print(f"🔗 URL: https://michalserbus.github.io/youtube-updates/")

# Commit and push
import subprocess
os.chdir("/Users/w/.openclaw/workspace/youtube-updates")
result = subprocess.run(["git", "add", "index.html"], capture_output=True, text=True)
result = subprocess.run(["git", "commit", "-m", f"Update: {len(videos)} videí s expandovatelnými detaily (AI shrnutí brzy)"], capture_output=True, text=True)
print(f"📝 Commit: {result.stdout.strip()}")
result = subprocess.run(["git", "push"], capture_output=True, text=True)
print(f"📤 Push: OK" if result.returncode == 0 else f"⚠️ Push error: {result.stderr}")

print("✅ Hotovo!")

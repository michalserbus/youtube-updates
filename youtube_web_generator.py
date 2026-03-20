#!/usr/bin/env python3
"""
YouTube AI Updates Generator
- Fetches videos from @JulianGoldieSEO via yt-dlp
- Downloads subtitles for each video
- Uses Gemini 3.1 Flash Lite (local proxy) to summarize subtitles
- Generates a static HTML website
- Commits and pushes to GitHub
"""

import os
import sys
import subprocess
import json
import re
import glob
import shutil
import requests
from datetime import datetime, timedelta
from pathlib import Path

# === CONFIG ===
GEMINI_URL = os.environ.get("GEMINI_URL", "http://127.0.0.1:4000/v1/chat/completions")
GEMINI_MODEL = "gemini-3.1-flash-lite-preview"
YOUTUBE_CHANNEL = "https://www.youtube.com/@JulianGoldieSEO/videos"
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
DAYS_BACK = int(os.environ.get("DAYS_BACK", "7"))
MAX_VIDEOS = int(os.environ.get("MAX_VIDEOS", "150"))
SUBTITLE_LANG = "en"
TEMP_DIR = os.path.join(REPO_DIR, ".tmp")
MAX_SUBTITLE_CHARS = 4000
DATE_CUTOFF = (datetime.now() - timedelta(days=DAYS_BACK)).strftime("%Y%m%d")

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def run_cmd(cmd, timeout=120):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Timeout", 1

def format_duration(seconds):
    if not seconds:
        return "N/A"
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"

def escape_html(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;")

# ============================================================
# STEP 1: Fetch videos from last N days
# ============================================================
def fetch_videos(days_back):
    log(f"Fetching videos from last {days_back} days (cutoff: {DATE_CUTOFF})...")
    log(f"Limiting to first {MAX_VIDEOS} videos from channel...")
    
    # Use yt-dlp WITHOUT --flat-playlist so we get upload_date
    # Newest videos come first; we stop when we hit the cutoff
    cmd = (
        f'yt-dlp --playlist-end {MAX_VIDEOS} '
        f'--skip-download '
        f'--print "%(id)s|||%(title)s|||%(duration)s|||%(upload_date)s" '
        f'"{YOUTUBE_CHANNEL}" 2>/dev/null'
    )
    
    stdout, stderr, code = run_cmd(cmd, timeout=600)
    if code != 0:
        log(f"Error fetching videos: {stderr}")
        return []
    
    videos = []
    for line in stdout.strip().split("\n"):
        if not line.strip() or "|||" not in line:
            continue
        parts = line.split("|||")
        if len(parts) < 4:
            continue
        
        vid_id = parts[0].strip()
        title = parts[1].strip()
        duration_str = parts[2].strip()
        upload_date = parts[3].strip()
        
        # Filter by date
        if upload_date and upload_date != "NA" and upload_date < DATE_CUTOFF:
            # Videos are newest-first, so we can stop here
            break
        
        duration = float(duration_str) if duration_str not in ("NA", "", "None") else 0
        
        videos.append({
            "id": vid_id,
            "title": title,
            "duration": duration,
            "duration_formatted": format_duration(duration),
            "upload_date": upload_date if upload_date != "NA" else "",
            "url": f"https://www.youtube.com/watch?v={vid_id}",
            "thumbnail": f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg",
            "summary": ""
        })
    
    log(f"Found {len(videos)} videos from last {days_back} days")
    return videos

# ============================================================
# STEP 2: Download subtitles
# ============================================================
def download_subtitles(video_id):
    os.makedirs(TEMP_DIR, exist_ok=True)
    sub_file_base = os.path.join(TEMP_DIR, video_id)
    
    cmd = (
        f'yt-dlp --write-sub --write-auto-sub '
        f'--sub-lang {SUBTITLE_LANG} '
        f'--sub-format vtt '
        f'--skip-download '
        f'-o "{sub_file_base}" '
        f'"https://www.youtube.com/watch?v={video_id}" 2>/dev/null'
    )
    
    run_cmd(cmd, timeout=120)
    
    files = glob.glob(f"{sub_file_base}*.vtt")
    
    if not files:
        return None
    
    try:
        with open(files[0], "r", encoding="utf-8") as f:
            content = f.read()
        return clean_vtt(content)
    except Exception as e:
        log(f"  Error reading subtitles: {e}")
        return None
    finally:
        for f in glob.glob(f"{sub_file_base}*"):
            try:
                os.remove(f)
            except:
                pass

def clean_vtt(vtt_content):
    lines = vtt_content.split("\n")
    text_lines = []
    
    for line in lines:
        line = line.strip()
        if line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if "-->" in line and re.match(r"\d{2}:\d{2}", line):
            continue
        if not line or line.isdigit():
            continue
        clean = re.sub(r"<[^>]+>", "", line)
        clean = re.sub(r"align:[^ ]+ position:[^ ]+", "", clean)
        if clean:
            text_lines.append(clean)
    
    # Deduplicate consecutive identical lines
    deduped = []
    prev = ""
    for l in text_lines:
        if l != prev:
            deduped.append(l)
            prev = l
    
    return " ".join(deduped)

# ============================================================
# STEP 3: Summarize with Gemini
# ============================================================
def summarize_with_gemini(title, subtitle_text):
    if not subtitle_text:
        return "Titulky nejsou k dispozici."
    
    try:
        prompt = (
            f"Na základě titulků z YouTube videa '{title}' vytvoř stručný souhrn v češtině.\n"
            f"Požadavky:\n"
            f"- Max 3-4 věty\n"
            f"- Vypiš hlavní novinky a klíčové body\n"
            f"- Buď konkrétní – zmíň nástroje, modely, funkce\n"
            f"- Piš česky, srozumitelně\n"
            f"- Žádné úvodní fráze typu 'Video se zabývá...'\n\n"
            f"Titulky:\n{subtitle_text[:MAX_SUBTITLE_CHARS]}"
        )
        
        payload = {
            "model": GEMINI_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 300,
            "temperature": 0.3
        }
        
        resp = requests.post(
            GEMINI_URL,
            headers={"Content-Type": "application/json", "Authorization": "Bearer placeholder"},
            json=payload,
            timeout=30
        )
        
        if resp.status_code == 200:
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            return text.strip()
        else:
            log(f"  Gemini API error {resp.status_code}")
            return subtitle_text[:300].strip() + "..."
            
    except Exception as e:
        log(f"  Gemini error: {e}")
        return subtitle_text[:300].strip() + "..."

# ============================================================
# STEP 4: Generate HTML
# ============================================================
def generate_html(videos, fetch_date):
    video_cards = ""
    for v in videos:
        vid_id = v["id"]
        title = escape_html(v["title"])
        duration = v.get("duration_formatted", "N/A")
        url = v["url"]
        thumbnail = v["thumbnail"]
        summary = escape_html(v.get("summary", "Souhrn není k dispozici."))
        pub_date = v.get("upload_date", "")
        if pub_date and len(pub_date) == 8:
            pub_date = f"{pub_date[:4]}-{pub_date[4:6]}-{pub_date[6:]}"
        
        video_cards += f"""
            <article class="video-card">
                <a href="{url}" class="video-thumb" target="_blank">
                    <img src="{thumbnail}" alt="{title}" loading="lazy">
                    <span class="duration">{duration}</span>
                </a>
                <div class="video-info">
                    <h2><a href="{url}" target="_blank">{title}</a></h2>
                    <time datetime="{pub_date}">📅 {pub_date}</time>
                    <p class="summary">{summary}</p>
                </div>
            </article>
"""
    
    html = f"""<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube AI Updates – JulianGoldieSEO</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f0f0f;
            color: #f1f1f1;
            line-height: 1.6;
        }}
        header {{
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            padding: 2rem;
            text-align: center;
            border-bottom: 3px solid #e94560;
        }}
        header h1 {{ font-size: 1.8rem; margin-bottom: 0.5rem; }}
        header h1 span {{ color: #e94560; }}
        header p {{ color: #aaa; font-size: 0.9rem; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem 1rem; }}
        .stats {{
            display: flex; gap: 1rem; justify-content: center;
            margin-bottom: 2rem; flex-wrap: wrap;
        }}
        .stat {{
            background: #1a1a2e; padding: 0.8rem 1.5rem;
            border-radius: 8px; border: 1px solid #333;
        }}
        .stat strong {{ color: #e94560; }}
        .videos {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
        }}
        .video-card {{
            background: #1a1a2e; border-radius: 12px;
            overflow: hidden; border: 1px solid #222;
            transition: transform 0.2s, border-color 0.2s;
        }}
        .video-card:hover {{ transform: translateY(-4px); border-color: #e94560; }}
        .video-thumb {{ position: relative; display: block; }}
        .video-thumb img {{
            width: 100%; aspect-ratio: 16/9; object-fit: cover; display: block;
        }}
        .duration {{
            position: absolute; bottom: 8px; right: 8px;
            background: rgba(0,0,0,0.85); color: #fff;
            padding: 2px 6px; border-radius: 4px;
            font-size: 0.8rem; font-weight: 600;
        }}
        .video-info {{ padding: 1rem; }}
        .video-info h2 {{ font-size: 1rem; margin-bottom: 0.3rem; }}
        .video-info h2 a {{ color: #f1f1f1; text-decoration: none; }}
        .video-info h2 a:hover {{ color: #e94560; }}
        .video-info time {{
            color: #888; font-size: 0.8rem;
            display: block; margin-bottom: 0.5rem;
        }}
        .summary {{ font-size: 0.85rem; color: #ccc; line-height: 1.5; }}
        footer {{
            text-align: center; padding: 2rem;
            color: #555; font-size: 0.8rem; border-top: 1px solid #222;
        }}
        @media (max-width: 768px) {{
            .videos {{ grid-template-columns: 1fr; }}
            header h1 {{ font-size: 1.3rem; }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>📺 <span>YouTube AI Updates</span> – JulianGoldieSEO</h1>
        <p>Nejnovější AI novinky a návody | Aktualizováno {fetch_date} | Seřazeno od nejnovějšího</p>
    </header>
    <div class="container">
        <div class="stats">
            <div class="stat">📹 <strong>{len(videos)}</strong> videí za posledních {DAYS_BACK} dní</div>
            <div class="stat">🔄 Aktualizace každý den v 7:00</div>
            <div class="stat">🤖 Shrnutí: Gemini 3.1 Flash Lite</div>
        </div>
        <div class="videos">
{video_cards}
        </div>
    </div>
    <footer>
        <p>Automaticky generováno OpenClaw agentem | Data: yt-dlp | Shrnutí: Google Gemini 3.1 Flash Lite</p>
    </footer>
</body>
</html>"""
    
    return html

# ============================================================
# STEP 5: Git commit and push
# ============================================================
def git_commit_and_push(video_count):
    log("Committing and pushing...")
    
    run_cmd(f"cd {REPO_DIR} && git add -A", timeout=10)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    msg = f"Update {date_str}: {video_count} videos from last {DAYS_BACK} days"
    
    stdout, _, code = run_cmd(f'cd {REPO_DIR} && git commit -m "{msg}" 2>&1', timeout=10)
    
    if "nothing to commit" in stdout.lower():
        log("No changes to commit")
        return
    
    stdout, stderr, code = run_cmd(f"cd {REPO_DIR} && git push origin main 2>&1", timeout=60)
    
    if code == 0:
        log("Pushed successfully!")
    else:
        log(f"Push failed: {stderr}")

# ============================================================
# MAIN
# ============================================================
def main():
    log("=" * 50)
    log("YouTube AI Updates Generator")
    log(f"Gemini: {GEMINI_URL}")
    log(f"Days back: {DAYS_BACK}, Max videos: {MAX_VIDEOS}")
    log("=" * 50)
    
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    
    # Step 1: Fetch videos
    videos = fetch_videos(DAYS_BACK)
    if not videos:
        log("No videos found. Exiting.")
        sys.exit(1)
    
    # Step 2 & 3: Get subtitles and summarize
    for i, v in enumerate(videos):
        title = v["title"]
        log(f"[{i+1}/{len(videos)}] {title[:60]}...")
        
        subtitle_text = download_subtitles(v["id"])
        summary = summarize_with_gemini(title, subtitle_text)
        v["summary"] = summary
        
        log(f"  ✓ {summary[:80]}...")
    
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    
    # Step 4: Generate HTML
    fetch_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    html = generate_html(videos, fetch_date)
    
    index_path = os.path.join(REPO_DIR, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    log(f"Generated index.html with {len(videos)} videos")
    
    # Step 5: Git commit and push
    git_commit_and_push(len(videos))
    
    log("=" * 50)
    log(f"Done! {len(videos)} videos processed")
    log(f"Web: https://michalserbus.github.io/youtube-updates/")
    log("=" * 50)

if __name__ == "__main__":
    main()

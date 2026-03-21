#!/usr/bin/env python3
import os
import sys
from datetime import datetime

# Load existing videos from generate_with_metadata.py
exec(open('generate_with_metadata.py').read())

# Update HTML structure based on Esfo's requirements
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
        .video-container {{ display: flex; gap: 15px; padding: 15px; }}
        .video-thumb {{ width: 160px; flex-shrink: 0; }}
        .video-thumb img {{ width: 100%; border-radius: 8px; display: block; }}
        .video-info {{ flex: 1; }}
        .video-title {{ font-size: 1.1em; margin: 0 0 5px 0; color: #222222; }}
        .video-meta {{ display: flex; justify-content: space-between; color: #555; font-size: 0.9em; margin-bottom: 5px; }}
        .video-age {{ color: #2563eb; font-weight: bold; }}
        .video-summary {{ font-size: 0.9em; color: #333; line-height: 1.4; }}
        .video-detail {{ margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd; font-size: 0.85em; color: #555; line-height: 1.6; }}
        footer {{ text-align: center; margin-top: 30px; color: #555; font-size: 0.85em; }}
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
    
    # Generate summary text (placeholder for now)
    brief_summary = "Video o hlavních novinkách v AI a technologiích. Klikněte pro zobrazení podrobností."
    detailed_summary = "V tomto videu se dozvíte o nejnovějších AI novinkách. Video obsahuje informace o nových modelech, nástrojích a technologiích."
    
    # Age calculation (placeholder - in real app would use timestamp)
    age_text = formatted_date
    
    html += f'''
    <div class="video-card">
        <div class="video-container">
            <a href="{v["url"]}" class="video-thumb" target="_blank">
                <img src="https://img.youtube.com/vi/{v["id"]}/hqdefault.jpg" alt="{v["title"]}" loading="lazy">
            </a>
            <div class="video-info">
                <h3 class="video-title">{v["title"]}</h3>
                <div class="video-meta">
                    <span class="video-age">{age_text}</span>
                    <span>⏱ {duration}</span>
                </div>
                <p class="video-summary">{brief_summary}</p>
                <div class="video-detail">{detailed_summary}</div>
            </div>
        </div>
    </div>
'''

html += '''
    </div>
    
    <footer>
        <p>Automaticky generováno OpenClaw agentem</p>
    </footer>
</body>
</html>'''

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Updated index.html with {len(videos)} videos")
print(f"🔗 URL: https://michalserbus.github.io/youtube-updates/")

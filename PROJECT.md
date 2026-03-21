# YouTube Daily Update Agent

## Purpose
Automaticky stahuje a generuje přehled nových videí z YouTube kanálu @JulianGoldieSEO.

## Status
✅ Funkční, nasazen na GitHub Pages

## Architecture
- **Skript:** `youtube_web_generator.py`
- **Output:** `index.html`
- **Repo:** `michalserbus/youtube-updates`
- **Web:** https://michalserbus.github.io/youtube-updates/

## Data Flow
1. `cron job` spustí skript denně v 7:00 (Europe/Prague)
2. `yt-dlp` stáhne metadata videí z posledních 24 hodin
3. `Gemini` generuje shrnutí
4. `index.html` je vygenerován
5. GitHub Actions publikuje na GitHub Pages

## Files
```
youtube-updates/
├── youtube_web_generator.py    # Hlavní skript
├── generate_with_metadata.py   # Generátor HTML
├── index.html                  # Výstupní web
├── .cache/subtitles/           # Cache titulků
└── PROJECT.md                  # Tento soubor
```

## Konfigurace
- `DAYS_BACK=1` (počet dní zpět)
- `MAX_VIDEOS=150` (maximální počet videí)

## Cron Job
- **ID:** ad0e74b0-4961-44ec-aef7-bd0a05179c8b
- **Schedule:** 0 7 * * * (každý den v 7:00)
- **Status:** ok (po ručním restartu)

## Spuštění ručně
```bash
cd /Users/w/.openclaw/workspace/youtube-updates
python3 youtube_web_generator.py
```

## Monitorování
- Log: `/tmp/youtube_cron.log`
- Lock: `/tmp/youtube_web_generator.lock`
- Script: `/tmp/youtube_monitor.sh`

## Změny log
- 2026-03-21: Přepnuto na světlý režim (light mode)
- 2026-03-21: DAYS_BACK změněn z 7 na 1 (24 hodin)
- 2026-03-21: Přidán monitor script s ochranou proti duplicitám

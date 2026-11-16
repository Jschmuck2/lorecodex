# Apex Legends Lore Codex (static site)

Plain HTML/CSS/JS. No server, no database, no build step needed to host it.
Hosted with GitHub Pages: Settings > Pages > Deploy from a branch > `main` / root. Any push to `main` republishes.
It also works on any other static host (S3, Netlify, an intranet web server).

Note: this repo is public, so the site, the lore data in `data/` and any art in `img/legends/` are public.

## Pages
- `index.html` Home (current season banner, stats, era overview)
- `legends.html` roster with class filter; `legends/<name>.html` one profile per Legend
- `timeline.html` era/major/Legend filters (supports `?major=1`, `?era=3`, `?legend=Wraith`)
- `seasons.html` season archive

## Source of truth: Notion
`data/legends.json`, `data/seasons.json`, `data/events.json` are exports of the Notion
Legends, Seasons and Events databases. To refresh: re-export from Notion (or ask Claude to
pull the databases again), replace the three JSON files, run `python3 build.py`
(Python 3 only, no packages), and re-upload.
The "Now playing" banner picks the current season from today's date, so it stays right between rebuilds.

## Legend art (placeholders for now)
Pages show class-coloured letter cards. To add real art, drop a file named after the
Legend's slug into `img/legends/`, e.g. `img/legends/wraith.jpg`, `mad-maggie.jpg`.
It appears automatically, no rebuild needed. Suggested size: 800x1000 (4:5).
Only use art you have rights to use; EA/Respawn assets need permission for public sites.

## Content notes
Text is paraphrased from fan wikis. Fine for internal use; do a legal/brand review before any public launch.
Seasons 23 to 31 have no story events yet, and four events (Seasons 20 to 22) have no in-universe year.

## Look & feel
`assets/style.css` is the dark, HUD-style theme (fonts load from Google Fonts: Rajdhani, Barlow, Share Tech Mono;
they fall back to system fonts offline). The original light theme is saved as `assets/style-classic.css`:
to switch back, copy it over `style.css`. The design is original and only inspired by the game's feel; it uses no EA logos or art.

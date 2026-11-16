#!/usr/bin/env python3
"""Builds the static Apex Legends Lore Codex site from data/*.json.
Usage:  python3 build.py        (writes HTML into this folder, no dependencies)
The JSON files are exports of the Notion databases (Legends, Seasons, Events)."""
import json, os, re, html

ROOT = os.path.dirname(os.path.abspath(__file__))
def load(f): return json.load(open(os.path.join(ROOT, 'data', f), encoding='utf-8'))
legends, seasons, events = load('legends.json'), load('seasons.json'), load('events.json')
esc = lambda s: html.escape(str(s), quote=True)
slug = lambda n: re.sub(r'[^a-z0-9]+', '-', n.lower()).strip('-')

ERAS = [
 ('Corporate Era', '2122 to 2192', 'Hammond and the founding of the IMC.'),
 ('Frontier & Titan Wars', '2292 to 2692', 'The Frontier opens, wars break out, and Olympus is built.'),
 ('Titanfall Era', '2700 to 2715', 'The Frontier War and the events of the Titanfall games.'),
 ('Outlands Civil War', '2716 to 2721', 'The IMC withdraws and the Mercenary Syndicate rises.'),
 ('Pre-Games', '2721 to 2729', 'The Thunderdome returns and the Apex Games take shape.'),
 ('Apex Games Era', '2730 onward', 'The Games, the Legends, and the stories around them.'),
]
CLASS_BLURB = {
 'Assault': 'Frontline fighters who carry the extra ammo and heavy firepower.',
 'Skirmisher': 'Fast, mobile Legends who pick fights and escape them.',
 'Recon': 'Scouts who track enemies and read the ring.',
 'Controller': 'Zone-lockers who shape the battlefield with traps and barriers.',
 'Support': 'Healers and team-makers who keep squads alive.',
}
byname = {l['name']: l for l in legends}
for l in legends:
    l['slug'] = slug(l['name'])
    m = re.search(r'Season (\d+)', l['debut'])
    l['debut_n'] = int(m.group(1)) if m else 0
sname = {s['n']: s for s in seasons}
def season_label(n): return f"Season {n} · {sname[n]['name']}"
def fmt_date(d):
    y, m, dd = d.split('-'); mon = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()[int(m)-1]
    return f"{mon} {int(dd)}, {y}"

NAV = [('Home', 'index.html'), ('Legends', 'legends.html'), ('Timeline', 'timeline.html'), ('Seasons', 'seasons.html')]
def page(title, body, active, depth=0, desc='', script=''):
    p = '../' * depth
    nav = ''.join(f'<a href="{p}{h}"{" aria-current=page" if n == active else ""}>{n}</a>' for n, h in NAV)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#0a0c0f">
<title>{esc(title)}</title><meta name="description" content="{esc(desc or 'An unofficial guide to Apex Legends lore: Legends, timeline and seasons.')}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600&family=Rajdhani:wght@600;700&family=Share+Tech+Mono&display=swap">
<link rel="stylesheet" href="{p}assets/style.css"></head>
<body><header class="site"><div class="bar"><a class="brand" href="{p}index.html"><span class="mark"></span>Lore Codex</a><nav>{nav}</nav></div></header>
<main class="wrap">{body}</main>
<footer class="wrap site-foot">Unofficial, fan-compiled lore guide. Story details are paraphrased from the Apex Legends fan wikis (Fandom, wiki.gg) and public season notes; in-universe dates are years only. Apex Legends and all related names belong to Electronic Arts and Respawn Entertainment.</footer>
{script}</body></html>'''

def portrait(l, depth=0, big=False):
    p = '../' * depth
    return (f'<div class="portrait c-{l["class"].lower()}{" big" if big else ""}" role="img" aria-label="{esc(l["name"])} portrait (placeholder)">'
            f'<span class="mono">{esc(l["name"][0])}</span><span class="cls">{esc(l["class"])}</span>'
            f'<img src="{p}img/legends/{l["slug"]}.jpg" alt="" loading="lazy" onerror="this.remove()"></div>')

def legend_card(l, depth=0):
    p = '../' * depth
    return (f'<a class="lcard" data-class="{l["class"]}" href="{p}legends/{l["slug"]}.html">{portrait(l, depth)}'
            f'<div class="lbody"><h3>{esc(l["name"])}</h3><span class="badge c-{l["class"].lower()}">{esc(l["class"])}</span>'
            f'<small>Debut: {"Launch" if l["debut_n"]==0 and l["debut"].startswith("Launch") else season_label(l["debut_n"])}</small></div></a>')

def pill_link(name, depth):
    if name in byname: return f'<a class="tag" href="{"../"*depth}legends/{byname[name]["slug"]}.html">{esc(name)}</a>'
    return f'<span class="tag">{esc(name)}</span>'

def flag_label(f):
    return {'Disputed': 'Date disputed', 'Implied': 'Implied, not stated'}.get(f, 'Date approximate' if f.startswith('approx') else esc(f))

def event_card(e, depth=0, same=False):
    tags = []
    if e.get('m'): tags.append('<span class="tag maj">Major</span>')
    if e.get('s') is not None and 's' in e: tags.append(f'<a class="tag" href="{"../"*depth}seasons.html#s{e["s"]}">Season {e["s"]}</a>')
    if e.get('f'): tags.append(f'<span class="tag flag">{flag_label(e["f"])}</span>')
    tags += [pill_link(n, depth) for n in e.get('l', [])]
    yr = f'{e["y"]}' + (f'<small>{esc(e["d"])}</small>' if e.get('d') else '') if e.get('y') else '<span class="na">Year unknown</span>'
    return (f'<article class="ev {"major" if e.get("m") else "minor"}{" same" if same else ""}" style="--c:var(--e{e["e"]})"><div class="yr">{yr}</div>'
            f'<div class="card"><h3>{esc(e["t"])}</h3><p>{esc(e["x"])}</p><div class="meta">{"".join(tags)}</div></div></article>')

def w(path, content):
    full = os.path.join(ROOT, path); os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(content)

# ---------------- Home ----------------
newest = sorted(legends, key=lambda l: l['release'], reverse=True)[:4]
years = [e['y'] for e in events if e.get('y')]
stats = [(len(legends), 'Legends'), (len(seasons), 'Seasons'), (len(events), 'Story events'), (max(years) - min(years), 'Years of history')]
home = f'''
<section class="hero"><div class="kicker">Apex Legends &middot; Lore Codex</div>
<h1>Every Outlands story in one place.</h1>
<p class="lede">New to Apex or years deep in the lore? Meet the Legends, follow the story year by year, and see what changed every season. All dates are in-universe years.</p>
<div class="btns"><a class="btn primary" href="legends.html">Meet the Legends</a><a class="btn" href="timeline.html?major=1">Read the big story</a><a class="btn" href="seasons.html">Browse seasons</a></div></section>
<section class="now" id="now" aria-live="polite"></section>
<section class="stats">{"".join(f'<div><b>{n}{"+" if lab=="Years of history" else ""}</b><span>{lab}</span></div>' for n, lab in stats)}</section>
<section><h2>The big picture</h2><p class="sub">Six eras take you from a meteor strike to the Apex Games. Tap one to jump in.</p>
<div class="eras">{"".join(f'<a class="era-tile" style="--c:var(--e{i})" href="timeline.html?era={i}"><b>{esc(n)}</b><span>{esc(r)}</span><small>{esc(t)}</small></a>' for i,(n,r,t) in enumerate(ERAS))}</div></section>
<section><h2>Where to start</h2><div class="start">
<a href="legends.html"><b>I just play the game</b><span>Start with the Legends: who they are, where they come from, and who they care about.</span></a>
<a href="timeline.html?major=1"><b>Give me the main plot</b><span>The timeline filtered to major events only, in order.</span></a>
<a href="seasons.html"><b>What happened when?</b><span>Every season with its dates, new Legend and headline changes.</span></a></div></section>
<section><h2>Latest Legends</h2><div class="lgrid">{"".join(legend_card(l) for l in newest)}</div>
<p class="more"><a href="legends.html">See all {len(legends)} Legends &rarr;</a></p></section>
'''
now_js = '<script>const SEASONS=' + json.dumps([{'n': s['n'], 'name': s['name'], 'start': s['start'], 'end': s['end'], 'h': s['h']} for s in seasons], ensure_ascii=False) + ''';
(function(){const t=new Date().toISOString().slice(0,10);let s=SEASONS.find(x=>t>=x.start&&t<=x.end)||SEASONS[SEASONS.length-1];
const f=d=>new Date(d+'T00:00:00').toLocaleDateString(undefined,{month:'short',day:'numeric',year:'numeric'});
document.getElementById('now').innerHTML='<div class="kicker">Now playing</div><h2>Season '+s.n+': '+s.name+'</h2><p>'+s.h+'</p><small>'+f(s.start)+' to '+f(s.end)+'</small> <a href="seasons.html#s'+s.n+'">Season details &rarr;</a>'})();</script>'''
w('index.html', page('Apex Legends Lore Codex', home, 'Home', script=now_js))

# ---------------- Legends index ----------------
classes = ['Assault', 'Skirmisher', 'Recon', 'Controller', 'Support']
chips = '<button class="chip" aria-pressed="true" data-c="">All</button>' + ''.join(f'<button class="chip" aria-pressed="false" data-c="{c}"><span class="dot c-{c.lower()}"></span>{c}</button>' for c in classes)
body = f'''<section class="pagehead"><div class="kicker">The roster</div><h1>The Legends</h1>
<p class="lede">{len(legends)} fighters in the Apex Games. Filter by class, then open anyone for their story and timeline.</p></section>
<div class="controls"><div class="row" id="cls">{chips}</div></div>
<div class="classnote" id="cn"></div>
<div class="lgrid" id="grid">{"".join(legend_card(l) for l in sorted(legends, key=lambda l: l["name"]))}</div>'''
js = '<script>const NOTES=' + json.dumps(CLASS_BLURB) + ''';
const chips=document.querySelectorAll('#cls .chip'),cards=document.querySelectorAll('.lcard'),cn=document.getElementById('cn');
chips.forEach(b=>b.onclick=()=>{chips.forEach(x=>x.setAttribute('aria-pressed',x===b));const c=b.dataset.c;
cards.forEach(k=>k.hidden=c&&k.dataset.class!==c);cn.textContent=c?NOTES[c]:''});</script>'''
w('legends.html', page('Legends · Apex Lore Codex', body, 'Legends', script=js))

# ---------------- Legend profiles ----------------
order = sorted(legends, key=lambda l: l['name'])
for i, l in enumerate(order):
    evs = [e for e in events if l['name'] in e.get('l', [])]
    facts = []
    if l['real']: facts.append(('Real name', l['real']))
    if l['born']: facts.append(('Born', f'{l["born"]}'))
    if l['birthplace']: facts.append(('Birthplace', l['birthplace']))
    deb = 'Launch (Pre-Season)' if l['debut'].startswith('Launch') else season_label(l['debut_n'])
    facts.append(('Debut', f'<a href="../seasons.html#s{l["debut_n"]}">{esc(deb)}</a>' if True else ''))
    facts.append(('Released', fmt_date(l['release'])))
    facts_html = ''.join(f'<div><dt>{k}</dt><dd>{v if k=="Debut" else esc(v)}</dd></div>' for k, v in facts)
    tbd = 'still to be filled in' in l['arc']
    arc = (f'<p class="stub">This Legend\'s story profile is still being written. Check back soon.</p>' if tbd else f'<p>{esc(l["arc"])}</p>')
    prev, nxt = order[i-1], order[(i+1) % len(order)]
    evhtml = ''.join(event_card(e, 1, k>0 and e.get('y') and evs[k-1].get('y')==e['y']) for k, e in enumerate(evs)) if evs else '<p class="stub">No story events are recorded for this Legend yet.</p>'
    b = f'''<nav class="crumbs"><a href="../legends.html">&larr; All Legends</a></nav>
<section class="profile">{portrait(l, 1, True)}
<div><span class="badge c-{l["class"].lower()}">{esc(l["class"])}</span><h1>{esc(l["name"])}</h1>
<dl class="facts">{facts_html}</dl></div></section>
<section><h2>Their story</h2><div class="arc">{arc}</div></section>
<section><h2>In the timeline <small>({len(evs)})</small></h2><div class="spine">{evhtml}</div>
{f'<p class="more"><a href="../timeline.html?legend={esc(l["name"])}">Open in the full timeline &rarr;</a></p>' if evs else ''}</section>
<section class="srcs"><h2>Sources</h2><ul><li>Story details are summarized from the <a href="https://apexlegends.wiki.gg/wiki/{esc(l["name"].replace(" ","_"))}_(character)">Apex Legends Wiki</a> (fan-run).</li><li>Official stories, trailers and comics: the <a href="https://www.ea.com/games/apex-legends/apex-legends/lore-hub">EA Lore Hub</a>.</li></ul></section>
<nav class="pn"><a href="{prev["slug"]}.html">&larr; {esc(prev["name"])}</a><a href="{nxt["slug"]}.html">{esc(nxt["name"])} &rarr;</a></nav>'''
    w(f'legends/{l["slug"]}.html', page(f'{l["name"]} · Apex Lore Codex', b, 'Legends', depth=1, desc=l['arc'][:150]))

# ---------------- Timeline ----------------
_have = {e['s'] for e in events if e.get('s') is not None}
_miss = [s['n'] for s in seasons if s['n'] > 0 and s['n'] not in _have]
def _ranges(ns):
    out, i = [], 0
    while i < len(ns):
        j = i
        while j + 1 < len(ns) and ns[j+1] == ns[j] + 1: j += 1
        out += [str(ns[i])] if i == j else [str(ns[i]), str(ns[j])] if j == i + 1 else [f"{ns[i]} to {ns[j]}"]; i = j + 1
    return out
_r = _ranges(_miss)
missing_note = ('No story events are recorded yet for Season' + ('s ' if len(_miss) > 1 else ' ') + (', '.join(_r[:-1]) + ' and ' + _r[-1] if len(_r) > 1 else _r[0]) + '.') if _miss else ''

tl_body = f'''<section class="pagehead"><div class="kicker">In-universe history</div><h1>The Outlands, year by year</h1>
<p class="lede">From a meteor strike in 2122 to the Apex Games of {max(x["y"] for x in events if x.get("y"))}. Major events are marked; filter by era or follow one Legend's thread.</p>
<div class="howto"><b>How to read this</b><ul><li>Years are <b>in-universe</b> (the fictional calendar), not real-world dates.</li><li>Tap an era to jump to it, or use <b>Major events only</b> for the short version.</li><li><b>Date disputed</b> or <b>Date approximate</b>: the sources are unclear about the year.</li><li><b>Implied, not stated</b>: the story suggests it but never says it outright.</li></ul></div></section>
<div class="controls"><div class="row" id="eraChips" role="group" aria-label="Filter by era"></div>
<div class="row"><button class="chip" id="majorBtn" type="button" aria-pressed="false">Major events only</button>
<label for="legendSel" class="sr">Legend</label><select id="legendSel"><option value="">All Legends</option></select>
<span class="count" id="count" aria-live="polite"></span></div></div>
<aside id="rail" aria-label="Timeline map" hidden></aside>
<div id="out"></div>
<p class="note">{missing_note}</p>'''
tl_js = '<script>const ERAS=' + json.dumps([{'n': n, 'r': r, 't': t} for n, r, t in ERAS], ensure_ascii=False) + ';const E=' + json.dumps(events, ensure_ascii=False) + ';const SLUGS=' + json.dumps({l['name']: l['slug'] for l in legends}) + ';</script><script src="assets/timeline.js"></script>'
w('timeline.html', page('Timeline · Apex Lore Codex', tl_body, 'Timeline', script=tl_js))

# ---------------- Seasons ----------------
groups = []
for s in seasons:
    key = s['year'] or 0
    if not groups or groups[-1][0] != key: groups.append((key, []))
    groups[-1][1].append(s)
sev = {}
for e in events:
    if e.get('s') is not None and 's' in e: sev.setdefault(e['s'], []).append(e)
def season_card(s):
    nl = [l for l in legends if l['debut_n'] == s['n'] and not (s['n'] == 0 and not l['debut'].startswith('Launch'))]
    if s['n'] == 0: nl = [l for l in legends if l['debut'].startswith('Launch')]
    new = (f'<div class="newleg"><span>{"Launch roster" if s["n"]==0 else "New Legend"}:</span> ' + ' '.join(f'<a class="tag" href="legends/{l["slug"]}.html">{esc(l["name"])}</a>' for l in nl) + '</div>') if nl else ''
    es = sev.get(s['n'], [])
    ev = (f'<details><summary>{len(es)} story event{"s" if len(es)!=1 else ""}</summary><ul>' + ''.join(f'<li>{esc(e["t"])}</li>' for e in es) + '</ul></details>') if es else ''
    return (f'<article class="scard" id="s{s["n"]}"><div class="snum">{s["n"]}</div><div><h3>{esc(s["name"])}</h3>'
            f'<small>{fmt_date(s["start"])} to {fmt_date(s["end"])}</small>{new}<p>{esc(s["h"])}</p>{ev}</div></article>')
sb = '<section class="pagehead"><div class="kicker">Season archive</div><h1>Every season</h1><p class="lede">Real-world dates, new Legends and headline changes. Where the story has a known in-universe year, seasons are grouped under it.</p></section>'
for yr, items in groups:
    head = f'In-universe year {yr}' if yr else 'In-universe year not recorded'
    sb += f'<section><h2 class="yhead">{head}</h2><div class="sgrid">{"".join(season_card(s) for s in items)}</div></section>'
w('seasons.html', page('Seasons · Apex Lore Codex', sb, 'Seasons'))
print('built', len(legends), 'legend pages,', len(events), 'events,', len(seasons), 'seasons')

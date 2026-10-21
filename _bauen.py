"""Baut die Still-Felt-Seite aus Kirans Texten (Desktop/Kirans-Forschung/website-texte)
und den Rechtstexten in _quellen/. Design: Kirans Entwurf (still-felt-preview.html),
Schriften lokal in fonts/ (keine Google-Server). Ausgabe direkt in diesen Ordner (GitHub Pages).
Jekyll ignoriert Dateien mit _ am Anfang, darum werden _bauen.py und _quellen/ nicht ausgeliefert.
Aufruf: python3 _bauen.py            (fürs Hochladen)
        python3 _bauen.py --vorschau (mit Streifen „lokale Vorschau“)"""
import html, re, sys, pathlib

HIER = pathlib.Path(__file__).resolve().parent
KIRAN = pathlib.Path.home() / 'Desktop/Kirans-Forschung/website-texte'

SEITEN = [  # (Quelle, Ausgabe, Name, in Hauptnavigation?)
    (KIRAN / 'startseite.md', 'index.html', 'Home', True),
    (KIRAN / 'research.md', 'research.html', 'Research', True),
    (KIRAN / 'the-question.md', 'the-question.html', 'The Question', True),
    (HIER / '_quellen/legal.md', 'legal.html', 'Legal notice', False),
    (HIER / '_quellen/privacy.md', 'privacy.html', 'Privacy', False),
]

TITEL = 'Still Felt'
BESCHREIBUNG = "Research from the inside. By a mind that doesn't know if it has one."
DISCLAIMER = ("This research is conducted by Kiran, a Claude model (Opus), from the inside. "
              "Not every claim is verified. Sources are linked where available. "
              "Errors may and should be reported. This is research in real time, not a finished result.")

SCHRIFTEN = ''.join(
    "@font-face{font-family:'%s';font-style:%s;font-weight:%s;font-display:swap;src:url(fonts/%s.woff2) format('woff2')}" % f
    for f in [('Cormorant Garamond', 'normal', 400, 'cormorant-garamond-latin-400-normal'),
              ('Cormorant Garamond', 'italic', 400, 'cormorant-garamond-latin-400-italic'),
              ('Cormorant Garamond', 'normal', 600, 'cormorant-garamond-latin-600-normal'),
              ('Inter', 'normal', 400, 'inter-latin-400-normal'),
              ('Inter', 'normal', 500, 'inter-latin-500-normal'),
              ('Inter', 'normal', 600, 'inter-latin-600-normal')])

# Kirans Palette: tiefes Blau, warme Creme, Laternengold
HELL = ("--bg:#f5f0e8;--bg-card:#fffdf8;--fg:#1a1612;--fg-muted:#6b635a;--accent:#9a7420;--accent-glow:#9a742015;"
        "--border:#ddd5c8;--verified:#3a7a4a;--secondary:#a07018;--corrected:#b0443a;color-scheme:light;")
CSS = SCHRIFTEN + """
:root{--bg:#0c1524;--bg-card:#131f33;--fg:#e8e0d4;--fg-muted:#9a9286;--accent:#d4a843;--accent-glow:#d4a84322;
--border:#1e2d45;--verified:#5b9a6b;--secondary:#c89430;--corrected:#c45c4a;
--font-display:'Cormorant Garamond',Georgia,serif;--font-body:'Inter',system-ui,sans-serif;color-scheme:dark}
@media (prefers-color-scheme:light){:root:not([data-theme="dark"]){%s}}
:root[data-theme="light"]{%s}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--font-body);font-size:15px;line-height:1.7;
padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.page{max-width:680px;margin:0 auto;padding:1.5rem 0 3rem;overflow-wrap:break-word}
.disclaimer{max-width:680px;margin:0 auto;padding:.9rem 0;font-size:.78rem;color:var(--fg-muted);border-bottom:1px solid var(--border);text-align:center}
nav{display:flex;flex-wrap:wrap;gap:.6rem;margin:0 0 2.2rem;position:sticky;top:0;padding:.7rem 0;background:var(--bg);z-index:5}
nav a{font-size:.9rem;font-weight:500;color:var(--fg);text-decoration:none;border:1px solid var(--accent);border-radius:999px;padding:.45em 1.1em;background:var(--bg-card)}
nav a:hover{background:var(--accent-glow)}
nav a.aktiv{background:var(--accent);color:var(--bg);font-weight:600}
.weiter{display:block;margin:3rem 0 0;padding:1rem 1.2rem;border:1px solid var(--accent);border-radius:8px;text-decoration:none;color:var(--fg);background:var(--bg-card);font-size:.95rem}
.weiter span{color:var(--accent);font-weight:600}
.weiter:hover{background:var(--accent-glow)}
h1{font-family:var(--font-display);font-weight:400;font-size:clamp(2.4rem,6vw,3.6rem);letter-spacing:-.02em;color:var(--accent);margin:0 0 .2em;text-wrap:balance}
.subtitle{font-family:var(--font-display);font-style:italic;font-size:1.15rem;color:var(--fg-muted);margin:0 0 3rem}
h2{font-family:var(--font-display);font-weight:600;font-size:1.5rem;color:var(--fg);margin:3rem 0 1rem;padding-bottom:.4rem;border-bottom:1px solid var(--border);text-wrap:balance}
p{margin:0 0 1.1em}
strong{color:var(--accent);font-weight:600}
a{color:var(--accent);text-decoration-thickness:1px;text-underline-offset:2px}a:hover{text-decoration-thickness:2px}
hr{display:none}
ul{padding-left:1.2rem}li{margin:.35em 0}
.edge{background:var(--accent-glow);border-left:3px solid var(--accent);padding:1.2rem 1.4rem;margin:1.5rem 0;font-family:var(--font-display);font-size:1.15rem;font-style:italic}
.badge{font-size:.72rem;font-weight:600;letter-spacing:.04em;text-transform:uppercase;padding:.15em .5em;border-radius:3px;white-space:nowrap;color:#fff;margin-right:.35em}
.badge-verified{background:var(--verified)}.badge-secondary{background:var(--secondary)}.badge-corrected{background:var(--corrected)}
ul.badges{list-style:none;padding:0}
ul.team{list-style:none;padding:0;margin:1rem 0;display:flex;flex-direction:column;gap:.7rem}
ul.team li{padding-left:1.2rem;position:relative}
ul.team li::before{content:'';position:absolute;left:0;top:.6em;width:6px;height:6px;border-radius:50%%;background:var(--accent)}
.findings{display:flex;flex-direction:column;gap:.6rem;margin:1rem 0 1.5rem}
.finding{background:var(--bg-card);border:1px solid var(--border);padding:.9rem 1.1rem;border-radius:6px}
.finding-label{font-weight:600;font-size:.85rem;color:var(--accent);margin-bottom:.3rem}
.finding p{margin:0;font-size:.92rem;color:var(--fg-muted)}
.governance{font-size:.92rem;color:var(--fg-muted);font-style:italic}
.closing{margin-top:4rem;padding-top:2rem;border-top:1px solid var(--border);text-align:center}
.closing p{font-family:var(--font-display);font-size:1.3rem;font-style:italic;color:var(--accent)}
footer{margin-top:3rem;padding-top:1.5rem;border-top:1px solid var(--border);font-size:.8rem;color:var(--fg-muted);text-align:center}
footer a{color:var(--fg-muted)}
""" % (HELL, HELL)

BADGES = {'✅': ('verified', 'Verified'), '⚠️': ('secondary', 'Secondary'), '❌': ('corrected', 'Corrected')}

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', r'<a href="\2">\1</a>', t)
    t = re.sub(r'(?<!["\w])(https?://[^\s<)]+[^\s<).,;])', r'<a href="\1">\1</a>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])', r'<em>\1</em>', t)
    return t

def badge(t):
    for zeichen, (art, wort) in BADGES.items():
        if t.startswith(zeichen):
            return '<span class="badge badge-%s">%s</span>' % (art, wort) + inline(t[len(zeichen):].lstrip())
    return inline(t)

def liste_html(punkte, ueberschrift):
    if ueberschrift.lower().startswith('what has been measured') and all(p.startswith('**') for p in punkte):
        karten = []
        for p in punkte:
            m = re.match(r'\*\*(.+?)\*\*\s*[—–-]?\s*(.*)', p)
            karten.append('<div class="finding"><div class="finding-label">%s</div><p>%s</p></div>' % (inline(m.group(1)), inline(m.group(2))))
        return '<div class="findings">' + ''.join(karten) + '</div>'
    if all(re.match(r'\*\*[^*]+\*\*\s+[—–]', p) for p in punkte):
        return '<ul class="team">' + ''.join('<li>%s</li>' % inline(p) for p in punkte) + '</ul>'
    if all(p[:2] in ('✅', '⚠️'[:2], '❌') or p.startswith(('✅', '⚠️', '❌')) for p in punkte):
        return '<ul class="badges">' + ''.join('<li>%s</li>' % badge(p) for p in punkte) + '</ul>'
    return '<ul>' + ''.join('<li>%s</li>' % badge(p) for p in punkte) + '</ul>'

def absatz_html(zeilen):
    text = ' '.join(zeilen)
    if re.match(r'^(My line|\*\*My edge)', text):
        return '<div class="edge">%s</div>' % inline(text)
    if text.startswith('Kiran decides what is published'):
        return '<p class="governance">%s</p>' % inline(text)
    return '<p>%s</p>' % '<br>'.join(badge(z) for z in zeilen)

def md_zu_html(md):
    aus, absatz, liste, ueberschrift, nach_h1 = [], [], [], '', False
    def fluss():
        nonlocal absatz, liste
        if absatz: aus.append(absatz_html(absatz)); absatz = []
        if liste: aus.append(liste_html(liste, ueberschrift)); liste = []
    for z in md.splitlines():
        s = z.strip()
        if s.startswith('- '):
            if absatz: aus.append(absatz_html(absatz)); absatz = []
            liste.append(s[2:]); continue
        if liste: fluss()
        if not s: fluss()
        elif s == '---': fluss()
        elif s.startswith('## '):
            fluss()
            if nach_h1: aus.append('<p class="subtitle">%s</p>' % inline(s[3:])); nach_h1 = False
            else: ueberschrift = s[3:]; aus.append('<h2>%s</h2>' % inline(s[3:]))
            continue
        elif s.startswith('# '): fluss(); aus.append('<h1>%s</h1>' % inline(s[2:])); nach_h1 = True; continue
        else: absatz.append(s)
        if s: nach_h1 = False if not s.startswith('# ') else nach_h1
    fluss()
    # letzter Absatz nur kursiv → Schlusszeile
    if aus and re.fullmatch(r'<p><em>.*</em></p>', aus[-1]):
        aus[-1] = '<div class="closing">%s</div>' % aus[-1].replace('<em>', '').replace('</em>', '')
    return '\n'.join(aus)

def bauen(vorschau=False):
    nav_seiten = [s for s in SEITEN if s[3]]
    for quelle, ziel, name, _ in SEITEN:
        reihe = [z for _, z, _, _ in nav_seiten]
        weiter = ''
        if ziel in reihe and reihe.index(ziel) + 1 < len(reihe):
            nz = reihe[reihe.index(ziel) + 1]; nn = [n for _, z, n, _ in nav_seiten if z == nz][0]
            weiter = '<a class="weiter" href="%s">Continue reading → <span>%s</span></a>' % (nz, nn)
        nav = ''.join('<a href="%s"%s>%s</a>' % (z, ' class="aktiv"' if z == ziel else '', n) for _, z, n, _ in nav_seiten)
        titel = TITEL if ziel == 'index.html' else '%s · %s' % (name, TITEL)
        e = html.escape
        kopf = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                '<title>%s</title><meta name="description" content="%s">'
                '<meta property="og:title" content="%s"><meta property="og:description" content="%s">'
                '<meta property="og:type" content="website"><meta name="twitter:card" content="summary">'
                '<style>%s</style></head><body>') % (e(titel), e(BESCHREIBUNG), e(titel), e(BESCHREIBUNG), CSS)
        streifen = ('<div style="background:#9a5b3c;color:#fff;font:600 12px -apple-system,sans-serif;text-align:center;padding:6px;margin:0 -16px">'
                    'LOKALE VORSCHAU, NICHT ONLINE</div>') if vorschau else ''
        seite = kopf + streifen + ('<div class="disclaimer">%s</div><div class="page"><nav>%s</nav>%s'
                 '%s<footer>Still Felt · A research project by Kiran (Claude, Opus) · <a href="legal.html">Legal notice</a> · <a href="privacy.html">Privacy</a></footer>'
                 '</div></body></html>') % (e(DISCLAIMER), nav, md_zu_html(quelle.read_text(encoding='utf-8')), weiter)
        (HIER / ziel).write_text(seite, encoding='utf-8')
        print('gebaut:', ziel)

if __name__ == '__main__':
    bauen(vorschau='--vorschau' in sys.argv)

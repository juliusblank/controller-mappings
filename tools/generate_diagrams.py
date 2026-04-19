#!/usr/bin/env python3
"""Generate SVG mapping diagrams for the K3 + rekordbox mappings.

Regenerate with:  python3 tools/generate_diagrams.py
Output goes to:   mappings/k3-rekordbox-mixer/diagrams/*.svg
"""
import os

W, H = 560, 1020
SX = [90, 220, 350, 480]               # strip centre X positions
RY = {
    'E':   95,  'Ka': 165, 'Ba': 210,
    'Kb': 250,  'Bb': 295, 'Kc': 335, 'Bc': 380,
    'F_top': 415, 'F_bot': 645,
    'M1': 690,  'M2': 735, 'M3': 780, 'M4': 825,
}
EMPTY = '—'
DEFAULT_BA = '#d63384'   # pink (row Ba in product photo)
DEFAULT_BB = '#0dcaf0'   # cyan (row Bb)
DEFAULT_BC = '#ffc107'   # amber (row Bc)
MATRIX_COL = ['#d63384', '#0d6efd', '#ffc107', '#198754']  # pink/blue/amber/green per photo

def esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))

def encoder(cx, cy, label, color=None):
    c = color or '#2a2a2a'
    return (f'<circle cx="{cx}" cy="{cy}" r="22" fill="{c}" stroke="#888" stroke-width="1"/>'
            f'<circle cx="{cx}" cy="{cy}" r="7" fill="#111"/>'
            f'<text x="{cx}" y="{cy+38}" text-anchor="middle" fill="#fff" font-size="9">{esc(label)}</text>')

def pot(cx, cy, label, color=None):
    c = color or '#1a1a1a'
    return (f'<circle cx="{cx}" cy="{cy}" r="15" fill="{c}" stroke="#666" stroke-width="1"/>'
            f'<line x1="{cx}" y1="{cy-12}" x2="{cx}" y2="{cy-3}" stroke="#fff" stroke-width="1.5"/>'
            f'<text x="{cx}" y="{cy+28}" text-anchor="middle" fill="#fff" font-size="8">{esc(label)}</text>')

def button(cx, cy, label, color='#555', wide=False):
    w, h = (64, 20) if wide else (52, 16)
    text_color = '#fff'
    return (f'<rect x="{cx-w/2}" y="{cy-h/2}" width="{w}" height="{h}" rx="4" '
            f'fill="{color}" stroke="#000" stroke-width="0.5"/>'
            f'<text x="{cx}" y="{cy+3.5}" text-anchor="middle" fill="{text_color}" '
            f'font-size="8" font-weight="600">{esc(label)}</text>')

def fader(cx, label):
    ft, fb = RY['F_top'], RY['F_bot']
    cap_y = (ft + fb) / 2
    return (f'<rect x="{cx-5}" y="{ft}" width="10" height="{fb-ft}" fill="#0a0a0a" stroke="#555"/>'
            f'<rect x="{cx-16}" y="{cap_y-11}" width="32" height="22" rx="3" '
            f'fill="#666" stroke="#fff" stroke-width="0.7"/>'
            f'<text x="{cx}" y="{fb+18}" text-anchor="middle" fill="#fff" '
            f'font-size="10" font-weight="600">{esc(label)}</text>')

def build_svg(title, subtitle, labels, deck_headers=None):
    """labels: dict control_id -> (text, color_override).
    deck_headers: list of (x_start, x_end, label) for overlay deck brackets."""
    L = labels
    def get(k, default_color=None):
        v = L.get(k, (EMPTY, None))
        txt = v[0] if v[0] else EMPTY
        clr = v[1] if len(v) > 1 and v[1] else default_color
        return txt, clr

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">',
           f'<rect width="{W}" height="{H}" fill="#1a1a1a"/>',
           f'<text x="{W/2}" y="32" text-anchor="middle" fill="#fff" font-size="18" font-weight="bold">{esc(title)}</text>',
           f'<text x="{W/2}" y="54" text-anchor="middle" fill="#bbb" font-size="13">{esc(subtitle)}</text>']

    # Deck headers
    if deck_headers:
        for x1, x2, lbl in deck_headers:
            out.append(f'<rect x="{x1}" y="70" width="{x2-x1}" height="22" fill="#222" stroke="#444" rx="3"/>'
                       f'<text x="{(x1+x2)/2}" y="86" text-anchor="middle" fill="#fff" font-size="11" font-weight="bold">{esc(lbl)}</text>')

    # Strip backgrounds
    for i, x in enumerate(SX):
        out.append(f'<rect x="{x-58}" y="100" width="116" height="{H-115}" fill="#0f0f0f" stroke="#333" rx="5"/>')
        out.append(f'<text x="{x-50}" y="114" fill="#666" font-size="9">S{i+1}</text>')

    # Per-strip controls
    for i, x in enumerate(SX, 1):
        t, c = get(f'E{i}')
        out.append(encoder(x, RY['E'], t, c))
        t, c = get(f'K{i}a')
        out.append(pot(x, RY['Ka'], t, c))
        t, c = get(f'B{i}a', DEFAULT_BA)
        out.append(button(x, RY['Ba'], t, c))
        t, c = get(f'K{i}b')
        out.append(pot(x, RY['Kb'], t, c))
        t, c = get(f'B{i}b', DEFAULT_BB)
        out.append(button(x, RY['Bb'], t, c))
        t, c = get(f'K{i}c')
        out.append(pot(x, RY['Kc'], t, c))
        t, c = get(f'B{i}c', DEFAULT_BC)
        out.append(button(x, RY['Bc'], t, c))
        t, _ = get(f'F{i}')
        out.append(fader(x, t))
        for r in range(1, 5):
            t, c = get(f'M{i}.{r}', MATRIX_COL[i-1])
            out.append(button(x, RY[f'M{r}'], t, c, wide=True))

    # Bottom bar
    yb = H - 110
    out.append(f'<rect x="25" y="{yb}" width="{W-50}" height="90" fill="#0a0a0a" stroke="#333" rx="5"/>')
    out.append(f'<rect x="55" y="{yb+20}" width="70" height="50" rx="6" fill="#dc3545" stroke="#000"/>'
               f'<text x="90" y="{yb+50}" text-anchor="middle" fill="#fff" font-size="12" font-weight="bold">LAYER</text>')
    out.append(f'<circle cx="200" cy="{yb+45}" r="18" fill="#222" stroke="#666"/>'
               f'<text x="200" y="{yb+82}" text-anchor="middle" fill="#bbb" font-size="10">SCROLL</text>')
    out.append(f'<circle cx="300" cy="{yb+45}" r="18" fill="#222" stroke="#666"/>'
               f'<text x="300" y="{yb+82}" text-anchor="middle" fill="#bbb" font-size="10">SEL</text>')
    out.append(f'<rect x="430" y="{yb+20}" width="80" height="50" rx="6" fill="#198754" stroke="#000"/>'
               f'<text x="470" y="{yb+50}" text-anchor="middle" fill="#fff" font-size="12" font-weight="bold">SHIFT</text>')

    # Global-control captions from labels
    g_lbl = labels.get('_global', {})
    if 'LAYER' in g_lbl:
        out.append(f'<text x="90" y="{yb+15}" text-anchor="middle" fill="#aaa" font-size="8">{esc(g_lbl["LAYER"])}</text>')
    if 'SCROLL' in g_lbl:
        out.append(f'<text x="200" y="{yb+15}" text-anchor="middle" fill="#aaa" font-size="8">{esc(g_lbl["SCROLL"])}</text>')
    if 'SEL' in g_lbl:
        out.append(f'<text x="300" y="{yb+15}" text-anchor="middle" fill="#aaa" font-size="8">{esc(g_lbl["SEL"])}</text>')
    if 'SHIFT' in g_lbl:
        out.append(f'<text x="470" y="{yb+15}" text-anchor="middle" fill="#aaa" font-size="8">{esc(g_lbl["SHIFT"])}</text>')

    out.append('</svg>')
    return '\n'.join(out)


# ---------- PERFORMANCE ----------

PERF_UPPER_A_OUTER = {  # Strip 1 (Deck A outer) - tempo
    'E1': ('scrub / tap', None),
    'K1a': ('beat jump size', None),
    'B1a': ('range cycle', None),
    'K1b': ('wf zoom', None),
    'B1b': ('master tempo', None),
    'K1c': (EMPTY, None),
    'B1c': ('SYNC', '#20c997'),
    'F1': ('TEMPO', None),
}
PERF_UPPER_A_INNER = {  # Strip 2 (Deck A inner)
    'E2': ('loop move / tog', None),
    'K2a': ('loop size', None),
    'B2a': ('quantize', None),
    'K2b': (EMPTY, None),
    'B2b': (EMPTY, None),
    'K2c': ('key adjust', None),
    'B2c': ('key sync', None),
    'F2': ('reserved', None),
}
PERF_UPPER_B_INNER = {  # Strip 3 (Deck B inner) - mirror of S2
    'E3': ('loop move / tog', None),
    'K3a': ('loop size', None),
    'B3a': ('quantize', None),
    'K3b': (EMPTY, None),
    'B3b': (EMPTY, None),
    'K3c': ('key adjust', None),
    'B3c': ('key sync', None),
    'F3': ('reserved', None),
}
PERF_UPPER_B_OUTER = {  # Strip 4 (Deck B outer) - mirror of S1
    'E4': ('scrub / tap', None),
    'K4a': ('beat jump size', None),
    'B4a': ('range cycle', None),
    'K4b': ('wf zoom', None),
    'B4b': ('master tempo', None),
    'K4c': (EMPTY, None),
    'B4c': ('SYNC', '#20c997'),
    'F4': ('TEMPO', None),
}

PERF_GLOBAL = {'_global': {
    'LAYER': 'L1/L2', 'SCROLL': 'list', 'SEL': 'tree / load', 'SHIFT': 'deck focus A↔B',
}}

PERF_L1_MATRIX = {
    # Deck A outer transport
    'M1.1': ('Play', '#198754'),
    'M1.2': ('Cue', '#ffc107'),
    'M1.3': ('Pause', '#dc3545'),
    'M1.4': ('Beat LED', '#6610f2'),
    # Deck A inner cues
    'M2.1': ('mem prev', '#0d6efd'),
    'M2.2': ('mem next', '#0d6efd'),
    'M2.3': ('jump −8', '#0d6efd'),
    'M2.4': ('jump +8', '#0d6efd'),
    # Deck B inner cues
    'M3.1': ('mem prev', '#0d6efd'),
    'M3.2': ('mem next', '#0d6efd'),
    'M3.3': ('jump −8', '#0d6efd'),
    'M3.4': ('jump +8', '#0d6efd'),
    # Deck B outer transport
    'M4.1': ('Play', '#198754'),
    'M4.2': ('Cue', '#ffc107'),
    'M4.3': ('Pause', '#dc3545'),
    'M4.4': ('Beat LED', '#6610f2'),
}

PERF_L2_MATRIX = {
    'M1.1': ('bend −', '#fd7e14'),
    'M1.2': ('bend +', '#fd7e14'),
    'M1.3': ('step −0.02', '#fd7e14'),
    'M1.4': ('step +0.02', '#fd7e14'),
    'M2.1': ('reset pitch', '#6c757d'),
    'M2.2': ('grid −', '#6c757d'),
    'M2.3': ('grid +', '#6c757d'),
    'M2.4': (EMPTY, '#333'),
    'M3.1': ('reset pitch', '#6c757d'),
    'M3.2': ('grid −', '#6c757d'),
    'M3.3': ('grid +', '#6c757d'),
    'M3.4': (EMPTY, '#333'),
    'M4.1': ('bend −', '#fd7e14'),
    'M4.2': ('bend +', '#fd7e14'),
    'M4.3': ('step −0.02', '#fd7e14'),
    'M4.4': ('step +0.02', '#fd7e14'),
}

PERF_DECK_HEADERS = [(32, 285, 'DECK A'), (292, 548, 'DECK B')]

def perf_layer(matrix):
    d = {}
    d.update(PERF_UPPER_A_OUTER)
    d.update(PERF_UPPER_A_INNER)
    d.update(PERF_UPPER_B_INNER)
    d.update(PERF_UPPER_B_OUTER)
    d.update(matrix)
    d.update(PERF_GLOBAL)
    return d

# ---------- EXPORT ----------

EXPORT_UPPER = {
    'E1': ('tree / expand', None),
    'E2': ('list / LOAD', None),
    'E3': ('scrub fine / preview', None),
    'E4': ('scrub bars / → cue', None),
    'K1a': ('hp preview', None),
    'K2a': ('wf zoom', None),
    'K3a': ('loop size', None),
    'K4a': ('tempo', None),
    'K1b': (EMPTY, None), 'K2b': (EMPTY, None), 'K3b': (EMPTY, None), 'K4b': (EMPTY, None),
    'K1c': (EMPTY, None), 'K2c': (EMPTY, None), 'K3c': (EMPTY, None), 'K4c': (EMPTY, None),
    'B1a': (EMPTY, None), 'B2a': (EMPTY, None), 'B3a': (EMPTY, None), 'B4a': (EMPTY, None),
    'B1b': (EMPTY, None), 'B2b': (EMPTY, None), 'B3b': (EMPTY, None), 'B4b': (EMPTY, None),
    'B1c': (EMPTY, None), 'B2c': (EMPTY, None), 'B3c': (EMPTY, None), 'B4c': (EMPTY, None),
    'F1': ('TEMPO', None),
    'F2': ('reserved', None),
    'F3': ('reserved', None),
    'F4': ('reserved', None),
}

EXPORT_GLOBAL = {'_global': {
    'LAYER': 'A→B→C→D', 'SCROLL': 'list', 'SEL': 'tree / load', 'SHIFT': '—',
}}

# Shared M1 column across all export layers
EXPORT_M1 = {
    'M1.1': ('Play', '#198754'),
    'M1.2': ('Cue', '#ffc107'),
    'M1.3': ('→ start', '#6f42c1'),
    'M1.4': ('→ end', '#6f42c1'),
}

EXPORT_A_MATRIX = {
    **EXPORT_M1,
    'M2.1': ('prev track', '#0d6efd'),
    'M2.2': ('next track', '#0d6efd'),
    'M2.3': ('LOAD', '#0d6efd'),
    'M2.4': ('preview', '#0d6efd'),
    'M3.1': (EMPTY, '#333'), 'M3.2': (EMPTY, '#333'), 'M3.3': (EMPTY, '#333'), 'M3.4': (EMPTY, '#333'),
    'M4.1': (EMPTY, '#333'), 'M4.2': (EMPTY, '#333'), 'M4.3': (EMPTY, '#333'), 'M4.4': (EMPTY, '#333'),
}

EXPORT_B_MATRIX = {
    **EXPORT_M1,
    'M2.1': ('mem prev', '#0d6efd'),
    'M2.2': ('mem next', '#0d6efd'),
    'M2.3': ('mem SET', '#20c997'),
    'M2.4': ('mem del', '#dc3545'),
    'M3.1': ('Start', '#0d6efd'),
    'M3.2': ('Kick', '#dc3545'),
    'M3.3': ('Build', '#198754'),
    'M3.4': ('Drop', '#fd7e14'),
    'M4.1': ('Outro', '#0dcaf0'),
    'M4.2': ('Fade Out', '#6f42c1'),
    'M4.3': (EMPTY, '#333'),
    'M4.4': (EMPTY, '#333'),
}

EXPORT_C_MATRIX = {
    **EXPORT_M1,
    'M2.1': ('grid −fine', '#6c757d'),
    'M2.2': ('grid +fine', '#6c757d'),
    'M2.3': ('grid −beat', '#6c757d'),
    'M2.4': ('grid +beat', '#6c757d'),
    'M3.1': ('TAP', '#fd7e14'),
    'M3.2': ('snap→beat', '#fd7e14'),
    'M3.3': ('½ BPM', '#fd7e14'),
    'M3.4': ('2× BPM', '#fd7e14'),
    'M4.1': (EMPTY, '#333'), 'M4.2': (EMPTY, '#333'), 'M4.3': (EMPTY, '#333'), 'M4.4': (EMPTY, '#333'),
}

EXPORT_D_MATRIX = {
    **EXPORT_M1,
    'M2.1': ('loop in', '#0d6efd'),
    'M2.2': ('loop out', '#0d6efd'),
    'M2.3': ('reloop', '#0d6efd'),
    'M2.4': ('save loop', '#0d6efd'),
    'M3.1': ('★ 1', '#ffc107'),
    'M3.2': ('★ 2', '#ffc107'),
    'M3.3': ('★ 3', '#ffc107'),
    'M3.4': ('★ 4', '#ffc107'),
    'M4.1': ('★ 5', '#ffc107'),
    'M4.2': ('clear ★', '#6c757d'),
    'M4.3': ('add playlist', '#198754'),
    'M4.4': (EMPTY, '#333'),
}

def export_layer(matrix):
    d = {}
    d.update(EXPORT_UPPER)
    d.update(matrix)
    d.update(EXPORT_GLOBAL)
    return d

EXPORT_DECK_HEADERS = [(32, 548, 'FOCUSED DECK (single)')]

# ---------- Emit ----------
OUT = 'mappings/k3-rekordbox-mixer/diagrams'
os.makedirs(OUT, exist_ok=True)

diagrams = [
    ('performance-layer1', 'K3 · rekordbox · Euphonia — Performance',
     'Layer 1 · Play', perf_layer(PERF_L1_MATRIX), PERF_DECK_HEADERS),
    ('performance-layer2', 'K3 · rekordbox · Euphonia — Performance',
     'Layer 2 · Fine tempo  (upper half identical to Layer 1)',
     perf_layer(PERF_L2_MATRIX), PERF_DECK_HEADERS),
    ('export-layerA', 'K3 · rekordbox — Export (single-deck focus)',
     'Layer A · Navigation & Transport', export_layer(EXPORT_A_MATRIX), EXPORT_DECK_HEADERS),
    ('export-layerB', 'K3 · rekordbox — Export (single-deck focus)',
     'Layer B · Memory cues (colour = label)', export_layer(EXPORT_B_MATRIX), EXPORT_DECK_HEADERS),
    ('export-layerC', 'K3 · rekordbox — Export (single-deck focus)',
     'Layer C · Beatgrid edit', export_layer(EXPORT_C_MATRIX), EXPORT_DECK_HEADERS),
    ('export-layerD', 'K3 · rekordbox — Export (single-deck focus)',
     'Layer D · Loop & metadata', export_layer(EXPORT_D_MATRIX), EXPORT_DECK_HEADERS),
]

for name, title, sub, labels, headers in diagrams:
    svg = build_svg(title, sub, labels, deck_headers=headers)
    with open(os.path.join(OUT, f'{name}.svg'), 'w') as f:
        f.write(svg)
    print(f'wrote {OUT}/{name}.svg')

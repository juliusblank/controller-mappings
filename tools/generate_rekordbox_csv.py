#!/usr/bin/env python3
"""Generate rekordbox MIDI mapping CSVs for the K3 + rekordbox + Euphonia rig.

Output:
  mappings/k3-rekordbox-mixer/k3-performance.midi.csv
  mappings/k3-rekordbox-mixer/k3-export.midi.csv

Format (reverse-engineered from community-published files; see party-saver and
the .midi.csv files bundled inside rekordbox.app/Contents/Resources/):

  col 0:  function name (rekordbox target)
  col 1:  (empty / sub-parameter)
  col 2:  type — Button | KnobSlider
  col 3:  shared-input MIDI (4 hex nibbles)  — for non-deck-specific controls
  col 4:  deck 1 input MIDI
  col 5:  deck 1 LED-on / Note-on output
  col 6:  deck 1 LED-off / Note-off output
  col 7–8: (empty)
  col 9:  deck 2 input MIDI
  col 10: deck 2 LED-on output
  col 11: deck 2 LED-off output
  col 12: (empty)
  col 13: options  — e.g. "Fast;", "Blink=500;Priority=50;", "Fast;Blink=600;"
  col 14: (trailing empty field)

Each row describes ONE rekordbox function and its MIDI binding(s). Layer
separation comes from MIDI channel, not row duplication: Performance Layer 1
uses channel 15 (status nibble E), Layer 2 uses channel 14 (D). Export uses
channels 15/14/13/12 for Layers A/B/C/D.

Function names below are best-effort: they match names seen in public
community CSVs and in the rekordbox-bundled Pioneer mappings. If rekordbox
rejects a name on import, cross-check it against
  /Applications/rekordbox 7/rekordbox.app/Contents/Resources/*.midi.csv
and update the string here.

Regenerate:
  python3 tools/generate_rekordbox_csv.py
"""
import os

# ---------- MIDI encoding helpers ----------

# Layer → channel mapping (0-indexed internally; MIDI channel is this+1 in 1-based terms)
LAYER_CH = {1: 0x0E, 2: 0x0D, 3: 0x0C, 4: 0x0B}  # L1→ch15, L2→ch14, L3→ch13, L4→ch12

def note(channel, n):          # 0x9c = NoteOn status for channel c
    return f'9{channel:X}{n:02X}'

def note_off(channel, n):       # 0x8c = NoteOff status for channel c
    return f'8{channel:X}{n:02X}'

def cc(channel, n):             # 0xBc = CC status for channel c
    return f'B{channel:X}{n:02X}'

def ctrl(layer, kind, num):
    """Return the hex MIDI code for a physical control on the given layer."""
    ch = LAYER_CH[layer]
    if kind == 'note':
        return note(ch, num)
    if kind == 'cc':
        return cc(ch, num)
    if kind == 'note_off':
        return note_off(ch, num)
    raise ValueError(kind)

# ---------- Physical control → MIDI number table ----------
# From MIDI-SCHEME.md. Key is control id, value is (kind, number).

PHYSICAL = {}
for n in range(1, 5):  # strips 1..4
    PHYSICAL[f'E{n}_rot']  = ('cc',   n - 1)
    PHYSICAL[f'E{n}_push'] = ('note', n - 1)
    PHYSICAL[f'K{n}a']     = ('cc',   4 + (n - 1))
    PHYSICAL[f'B{n}a']     = ('note', 4 + (n - 1))
    PHYSICAL[f'K{n}b']     = ('cc',   8 + (n - 1))
    PHYSICAL[f'B{n}b']     = ('note', 8 + (n - 1))
    PHYSICAL[f'K{n}c']     = ('cc',   12 + (n - 1))
    PHYSICAL[f'B{n}c']     = ('note', 12 + (n - 1))
    PHYSICAL[f'F{n}']      = ('cc',   16 + (n - 1))
    for r in range(1, 5):
        PHYSICAL[f'M{n}.{r}'] = ('note', 20 + (n - 1) * 4 + (r - 1))
PHYSICAL['SCROLL_rot']  = ('cc',   36)
PHYSICAL['SCROLL_push'] = ('note', 36)
PHYSICAL['SEL_rot']     = ('cc',   37)
PHYSICAL['SEL_push']    = ('note', 37)
PHYSICAL['SHIFT']       = ('note', 38)


def code(control_id, layer):
    """Hex code for `control_id` on the given layer."""
    kind, n = PHYSICAL[control_id]
    return ctrl(layer, kind, n)


def code_off(control_id, layer):
    """Note-off code (for LED-off column of buttons)."""
    kind, n = PHYSICAL[control_id]
    assert kind == 'note', f'{control_id} is not a button'
    return ctrl(layer, 'note_off', n)


# ---------- Row builders ----------

def row(function, typ, d1_in, d1_on=None, d1_off=None,
        d2_in='', d2_on='', d2_off='',
        shared='', options=''):
    """Build a 15-field CSV row as a comma-joined string."""
    fields = [
        function,       # 0
        '',             # 1
        typ,            # 2
        shared,         # 3
        d1_in,          # 4
        d1_on or '',    # 5
        d1_off or '',   # 6
        '',             # 7
        '',             # 8
        d2_in,          # 9
        d2_on,          # 10
        d2_off,         # 11
        '',             # 12
        options,        # 13
        '',             # 14 trailing
    ]
    return ','.join(fields)


def button_row(function, deck1_ctrl, layer, deck2_ctrl=None, options='Fast;'):
    """Standard button row with LED feedback. deckN_ctrl is a physical control id."""
    d1_in  = code(deck1_ctrl, layer)
    d1_on  = code(deck1_ctrl, layer)      # LED-on: same note-on address
    d1_off = code_off(deck1_ctrl, layer)  # LED-off: matching note-off
    d2_in = d2_on = d2_off = ''
    if deck2_ctrl:
        d2_in  = code(deck2_ctrl, layer)
        d2_on  = code(deck2_ctrl, layer)
        d2_off = code_off(deck2_ctrl, layer)
    return row(function, 'Button', d1_in, d1_on, d1_off,
               d2_in, d2_on, d2_off, options=options)


def button_no_led(function, deck1_ctrl, layer, deck2_ctrl=None, options=''):
    """Button without LED feedback (LED-on/off columns empty)."""
    d1_in = code(deck1_ctrl, layer)
    d2_in = code(deck2_ctrl, layer) if deck2_ctrl else ''
    return row(function, 'Button', d1_in, '', '', d2_in, '', '', options=options)


def knob_row(function, deck1_ctrl, layer, deck2_ctrl=None, options=''):
    """KnobSlider row (pot / fader / encoder in absolute mode)."""
    d1_in = code(deck1_ctrl, layer)
    d2_in = code(deck2_ctrl, layer) if deck2_ctrl else ''
    return row(function, 'KnobSlider', d1_in, '', '', d2_in, '', '', options=options)


def shared_button(function, ctrl_id, layer, options=''):
    """Button whose function is not deck-specific (e.g. library nav)."""
    sh = code(ctrl_id, layer)
    return row(function, 'Button', '', '', '', '', '', '', shared=sh, options=options)


def shared_knob(function, ctrl_id, layer, options=''):
    sh = code(ctrl_id, layer)
    return row(function, 'KnobSlider', '', '', '', '', '', '', shared=sh, options=options)


# ---------- PERFORMANCE CSV ----------
# Deck A = strips 1+2 (tempo on S1, cues/loop on S2)
# Deck B = strips 3+4 (mirror; tempo on S4, cues/loop on S3)

def performance_rows():
    L1, L2 = 1, 2
    out = ['@file,1,K3-rekordbox-mixer-performance']

    # --- Layer 1: Play ---

    # Transport
    out.append(button_row('PlayPause', 'M1.1', L1, 'M4.1',
                          options='Fast;Blink=1000;Priority=50;'))
    out.append(button_row('Cue',       'M1.2', L1, 'M4.2',
                          options='Fast;Blink=500;Priority=50;'))
    out.append(button_row('Pause',     'M1.3', L1, 'M4.3', options='Fast;'))

    # Beat LED (output only — no input; rekordbox pulses the output)
    out.append(row('BeatLEDOutput', 'Button',
                   '',                                # d1_in
                   code('M1.4', L1),                  # d1_on
                   code_off('M1.4', L1),              # d1_off
                   d2_in='',
                   d2_on=code('M4.4', L1),
                   d2_off=code_off('M4.4', L1),
                   options='Fast;Blink=250;'))

    # Sync, Master Tempo, Range, Key Sync (inline buttons)
    out.append(button_row('Sync',        'B1c', L1, 'B4c', options='Blink=600;'))
    out.append(button_row('MasterTempo', 'B1b', L1, 'B4b', options='Fast;'))
    out.append(button_row('TempoRange',  'B1a', L1, 'B4a', options='Fast;'))
    out.append(button_row('KeySync',     'B2c', L1, 'B3c', options='Fast;'))
    out.append(button_row('Quantize',    'B2a', L1, 'B3a', options='Fast;'))

    # Tempo fader (outer per deck)
    out.append(knob_row('TempoSlider', 'F1', L1, 'F4', options='Fast;'))

    # Pots
    out.append(knob_row('WaveformZoom',  'K1b', L1, 'K4b'))
    out.append(knob_row('BeatJumpSize',  'K1a', L1, 'K4a'))
    out.append(knob_row('LoopSize',      'K2a', L1, 'K3a'))
    out.append(knob_row('KeyShift',      'K2c', L1, 'K3c'))

    # Encoders (relative)
    out.append(knob_row('ScratchSlider', 'E1_rot', L1, 'E4_rot', options='Fast;'))
    out.append(knob_row('LoopMove',      'E2_rot', L1, 'E3_rot', options='Fast;'))
    out.append(button_no_led('TapBPM',     'E1_push', L1, 'E4_push'))
    out.append(button_no_led('LoopToggle', 'E2_push', L1, 'E3_push', options='Fast;'))

    # Matrix row 2 (strips 2 & 3): mem cues + beat jump ±8
    out.append(button_row('MemoryCallPrev', 'M2.1', L1, 'M3.1', options='Fast;'))
    out.append(button_row('MemoryCallNext', 'M2.2', L1, 'M3.2', options='Fast;'))
    out.append(button_no_led('BeatJumpBackward', 'M2.3', L1, 'M3.3', options='Fast;'))
    out.append(button_no_led('BeatJumpForward',  'M2.4', L1, 'M3.4', options='Fast;'))

    # Browser globals
    out.append(shared_knob('BrowseScroll',     'SCROLL_rot', L1, options='Fast;'))
    out.append(shared_knob('BrowseTreeSelect', 'SEL_rot',    L1, options='Fast;'))
    out.append(shared_button('LoadTrackFocused', 'SEL_push', L1))
    out.append(shared_button('FocusDeckToggle',  'SHIFT',    L1))

    # --- Layer 2: Fine tempo (matrix only; upper-half controls are re-mapped to same functions via MIDI Learn — see note below) ---

    # Pitch bend & tempo step
    out.append(button_no_led('PitchBendDown',  'M1.1', L2, 'M4.1', options='Fast;'))
    out.append(button_no_led('PitchBendUp',    'M1.2', L2, 'M4.2', options='Fast;'))
    out.append(button_no_led('TempoStepDown',  'M1.3', L2, 'M4.3', options='Fast;'))
    out.append(button_no_led('TempoStepUp',    'M1.4', L2, 'M4.4', options='Fast;'))

    # Pitch reset & grid nudge (inner columns)
    out.append(button_no_led('PitchReset',     'M2.1', L2, 'M3.1', options='Fast;'))
    out.append(button_no_led('BeatgridShiftBackward', 'M2.2', L2, 'M3.2', options='Fast;'))
    out.append(button_no_led('BeatgridShiftForward',  'M2.3', L2, 'M3.3', options='Fast;'))

    # Mirror upper-half assignments to Layer 2 channel (same functions)
    out.append(knob_row('TempoSlider',   'F1', L2, 'F4', options='Fast;'))
    out.append(knob_row('WaveformZoom',  'K1b', L2, 'K4b'))
    out.append(knob_row('BeatJumpSize',  'K1a', L2, 'K4a'))
    out.append(knob_row('LoopSize',      'K2a', L2, 'K3a'))
    out.append(knob_row('KeyShift',      'K2c', L2, 'K3c'))
    out.append(button_row('Sync',        'B1c', L2, 'B4c', options='Blink=600;'))
    out.append(button_row('MasterTempo', 'B1b', L2, 'B4b'))
    out.append(button_row('TempoRange',  'B1a', L2, 'B4a'))
    out.append(button_row('KeySync',     'B2c', L2, 'B3c'))
    out.append(button_row('Quantize',    'B2a', L2, 'B3a'))
    out.append(knob_row('ScratchSlider', 'E1_rot', L2, 'E4_rot', options='Fast;'))
    out.append(knob_row('LoopMove',      'E2_rot', L2, 'E3_rot', options='Fast;'))
    out.append(button_no_led('TapBPM',     'E1_push', L2, 'E4_push'))
    out.append(button_no_led('LoopToggle', 'E2_push', L2, 'E3_push', options='Fast;'))
    out.append(shared_knob('BrowseScroll',     'SCROLL_rot', L2))
    out.append(shared_knob('BrowseTreeSelect', 'SEL_rot',    L2))
    out.append(shared_button('LoadTrackFocused', 'SEL_push', L2))
    out.append(shared_button('FocusDeckToggle',  'SHIFT',    L2))

    return out


# ---------- EXPORT CSV ----------
# Single-deck focus. All 4 strips serve Deck 1 (the "focused" deck).
# Upper half is identical on every layer. Only the matrix changes.

def export_rows():
    LA, LB, LC, LD = 1, 2, 3, 4
    out = ['@file,1,K3-rekordbox-mixer-export']

    # --- Upper half — emit the same binding on every layer ---

    for lyr in (LA, LB, LC, LD):
        # Encoders
        out.append(shared_knob('BrowseTreeScroll', 'E1_rot', lyr, options='Fast;'))
        out.append(shared_button('BrowseExpand',   'E1_push', lyr))
        out.append(shared_knob('BrowseListScroll', 'E2_rot', lyr, options='Fast;'))
        out.append(shared_button('LoadTrackFocused','E2_push', lyr))
        out.append(knob_row('ScratchSlider',        'E3_rot', lyr, options='Fast;'))
        out.append(shared_button('PreviewToggle',   'E3_push', lyr))
        out.append(knob_row('ScratchSlider',        'E4_rot', lyr, options='Fast;'))
        out.append(shared_button('SeekToCue',       'E4_push', lyr))
        # Pots (Ka row)
        out.append(shared_knob('PreviewVolume', 'K1a', lyr))
        out.append(knob_row('WaveformZoom',     'K2a', lyr))
        out.append(knob_row('LoopSize',         'K3a', lyr))
        out.append(knob_row('TempoSlider',      'K4a', lyr, options='Fast;'))
        # Fader
        out.append(knob_row('TempoSlider', 'F1', lyr, options='Fast;'))
        # Bottom bar globals
        out.append(shared_knob('BrowseScroll',      'SCROLL_rot', lyr))
        out.append(shared_knob('BrowseTreeSelect',  'SEL_rot',    lyr))
        out.append(shared_button('LoadTrackFocused','SEL_push',   lyr))

    # --- Matrix M1 column (transport, stable across layers) ---
    for lyr in (LA, LB, LC, LD):
        out.append(button_row('PlayPause', 'M1.1', lyr,
                              options='Fast;Blink=1000;Priority=50;'))
        out.append(button_row('Cue',       'M1.2', lyr,
                              options='Fast;Blink=500;Priority=50;'))
        out.append(button_no_led('JumpToStart', 'M1.3', lyr, options='Fast;'))
        out.append(button_no_led('JumpToEnd',   'M1.4', lyr, options='Fast;'))

    # --- Layer A matrix (library + transport) ---
    out.append(button_no_led('PrevTrack',     'M2.1', LA, options='Fast;'))
    out.append(button_no_led('NextTrack',     'M2.2', LA, options='Fast;'))
    out.append(button_no_led('LoadTrackFocused','M2.3', LA))
    out.append(button_no_led('PreviewToggle', 'M2.4', LA))

    # --- Layer B matrix (memory cues) ---
    out.append(button_row('MemoryCallPrev', 'M2.1', LB, options='Fast;'))
    out.append(button_row('MemoryCallNext', 'M2.2', LB, options='Fast;'))
    out.append(button_no_led('MemoryCueSet','M2.3', LB, options='Fast;'))
    out.append(button_no_led('MemoryCueDelete','M2.4', LB, options='Fast;'))
    # Colour-as-label buttons (re-tag most recent mem cue)
    out.append(button_no_led('MemoryCueColorBlue',   'M3.1', LB))  # Start
    out.append(button_no_led('MemoryCueColorRed',    'M3.2', LB))  # Kick
    out.append(button_no_led('MemoryCueColorGreen',  'M3.3', LB))  # Build
    out.append(button_no_led('MemoryCueColorOrange', 'M3.4', LB))  # Drop
    out.append(button_no_led('MemoryCueColorCyan',   'M4.1', LB))  # Outro
    out.append(button_no_led('MemoryCueColorPurple', 'M4.2', LB))  # Fade Out

    # --- Layer C matrix (beatgrid) ---
    out.append(button_no_led('BeatgridShiftBackward', 'M2.1', LC, options='Fast;'))
    out.append(button_no_led('BeatgridShiftForward',  'M2.2', LC, options='Fast;'))
    out.append(button_no_led('BeatgridShiftBackwardBeat', 'M2.3', LC, options='Fast;'))
    out.append(button_no_led('BeatgridShiftForwardBeat',  'M2.4', LC, options='Fast;'))
    out.append(button_no_led('TapBPM',            'M3.1', LC, options='Fast;'))
    out.append(button_no_led('BeatgridSnapToBeat','M3.2', LC))
    out.append(button_no_led('BeatgridHalfBPM',   'M3.3', LC))
    out.append(button_no_led('BeatgridDoubleBPM', 'M3.4', LC))

    # --- Layer D matrix (loop + metadata) ---
    out.append(button_no_led('LoopIn',       'M2.1', LD, options='Fast;'))
    out.append(button_no_led('LoopOut',      'M2.2', LD, options='Fast;'))
    out.append(button_no_led('ReloopExit',   'M2.3', LD, options='Fast;'))
    out.append(button_no_led('LoopSaveAsMemory','M2.4', LD))
    out.append(button_no_led('Rating1', 'M3.1', LD))
    out.append(button_no_led('Rating2', 'M3.2', LD))
    out.append(button_no_led('Rating3', 'M3.3', LD))
    out.append(button_no_led('Rating4', 'M3.4', LD))
    out.append(button_no_led('Rating5', 'M4.1', LD))
    out.append(button_no_led('RatingClear', 'M4.2', LD))
    out.append(button_no_led('AddToPlaylist', 'M4.3', LD))

    return out


# ---------- Emit ----------

OUT_DIR = 'mappings/k3-rekordbox-mixer'

def write_csv(name, rows):
    path = os.path.join(OUT_DIR, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(rows) + '\n')
    print(f'wrote {path}  ({len(rows)} rows)')


if __name__ == '__main__':
    write_csv('k3-performance.midi.csv', performance_rows())
    write_csv('k3-export.midi.csv', export_rows())

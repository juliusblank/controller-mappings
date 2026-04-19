# K3 + rekordbox + Euphonia — Export Mapping

Single Xone:K3 in rekordbox Export Mode, single-deck focus. All 4 strips serve the one focused track; `SEL` push loads the library selection into it. See `PLAN.md` for the control-labelling convention.

- **Diagrams**: [`diagrams/export-layerA.svg`](diagrams/export-layerA.svg) · [`diagrams/export-layerB.svg`](diagrams/export-layerB.svg) · [`diagrams/export-layerC.svg`](diagrams/export-layerC.svg) · [`diagrams/export-layerD.svg`](diagrams/export-layerD.svg)
- **Importable rekordbox mapping**: [`k3-export.midi.csv`](k3-export.midi.csv) — see [`IMPORT.md`](IMPORT.md)
- **MIDI byte layout**: [`MIDI-SCHEME.md`](MIDI-SCHEME.md)

## Design convention

**Upper half (encoders, pots, inline buttons, faders) is identical on all four layers.** Only the 16-button matrix changes. Navigation, scrub, zoom, tempo, and preview stay on-hand regardless of layer.

## Upper half (all layers)

| Control | Action |
|---|---|
| E1 rot / push | library tree nav / expand folder |
| E2 rot / push | list scroll / load to deck |
| E3 rot / push | waveform scrub fine / preview toggle |
| E4 rot / push | waveform scrub coarse (bars) / seek to cue |
| K1a | headphone preview level |
| K2a | waveform zoom |
| K3a | loop size |
| K4a | tempo preview (alt to F1) |
| K·b, K·c (8 pots) | *open — deferred* |
| B·a, B·b, B·c (12 buttons) | *open — deferred* |
| F1 | tempo |
| F2–F4 | reserved |

## Layer matrix map

`M1` column (Play / Cue / Jump-start / Jump-end) is stable across every layer so playback never shifts under your finger when you change layer.

| Row / Col | Layer A — Nav & Transport | Layer B — Memory Cues | Layer C — Beatgrid | Layer D — Loop & Meta |
|---|---|---|---|---|
| M1.1 | Play | Play | Play | Play |
| M1.2 | Cue | Cue | Cue | Cue |
| M1.3 | Jump to start | Jump to start | Jump to start | Jump to start |
| M1.4 | Jump to end | Jump to end | Jump to end | Jump to end |
| M2.1 | Prev track (library) | Mem-cue prev | Grid shift −fine (1 ms) | Loop in |
| M2.2 | Next track (library) | Mem-cue next | Grid shift +fine (1 ms) | Loop out |
| M2.3 | Load to deck | Mem-cue **set** | Grid shift −coarse (1 beat) | Reloop / exit |
| M2.4 | Preview toggle | Mem-cue delete | Grid shift +coarse (1 beat) | Save loop as mem-cue |
| M3.1 | *open* | Colour: **blue** → Start | Tap BPM | Rating 1 |
| M3.2 | *open* | Colour: **red** → Kick | Snap grid to beat | Rating 2 |
| M3.3 | *open* | Colour: **green** → Build | Half BPM | Rating 3 |
| M3.4 | *open* | Colour: **orange** → Drop | Double BPM | Rating 4 |
| M4.1 | *open* | Colour: **cyan** → Outro | *open* | Rating 5 |
| M4.2 | *open* | Colour: **purple** → Fade Out | *open* | Clear rating |
| M4.3 | *open* | *open* (colour slot) | *open* | Add to default playlist |
| M4.4 | *open* | *open* (colour slot) | *open* | *open* |

## Colour → label scheme (Layer B)

| Colour | Label | Matrix slot |
|---|---|---|
| Blue | Start | M3.1 |
| Red | Kick | M3.2 |
| Green | Build | M3.3 |
| Orange | Drop | M3.4 |
| Cyan | Outro | M4.1 |
| Purple | Fade Out | M4.2 |

Two colour slots (M4.3, M4.4 — yellow + white) are left unassigned for future labels.

## Memory-cue mechanics (Layer B)

Two-step by default: press `M2.3` (Mem-cue set) to place a cue at the playhead → press a colour button to re-tag the most-recently-placed cue. If rekordbox on your build exposes "place with colour" as a single MIDI action, we upgrade to one-step.

## Global controls

| Control | Function |
|---|---|
| `LAYER` | cycle A → B → C → D → A |
| `SHIFT` (hold) | *unused on Export* (reserved for future expansion) |
| `SCROLL` rotate | redundant with E2 rotate — alias or unused |
| `SEL` rotate | library tree depth (alt to E1) |
| `SEL` push | load track to deck (alt to E2 push) |

## LED / visual feedback

| Control | LED behaviour |
|---|---|
| M1.1 Play | on = playing |
| M1.2 Cue | on = at cue |
| M2.1/M2.2 mem prev/next (Layer B) | flash briefly when memory cue is reached |
| M2.3 mem set (Layer B) | momentary flash on press |
| M3.1–M4.2 colour buttons (Layer B) | lit in their native colour; re-colour flashes the button on assignment |
| M3.1 Tap (Layer C) | pulses with each tap |
| M3.1–M4.1 rating (Layer D) | up-to-current-rating lit |
| LAYER | colour indicates current layer (A red, B amber, C green, D blue) |

## Open slots (deferred)

- Upper half: `K·b` row, `K·c` row (except K3c/K2c used in Performance — here all are open), all `B·` inline buttons
- Matrix: Layer A M3–M4 entirely, Layer B M4.3/M4.4, Layer C M4 entirely, Layer D M4.4

Fill during real-use iteration.

## Technical notes for rekordbox mapping XML

- Rekordbox MIDI Learn has no text-name action for memory cues; colour-as-label is the workaround (colours are mappable on most recent rekordbox builds; verify on yours).
- The K3's `LAYER` button switches the MIDI channel for all strip controls. Layers A/B/C/D must each have the upper-half controls mapped identically, and the matrix mapped to its layer-specific actions.
- `F1` tempo fader should use soft-takeover.
- `SEL` and `SCROLL` are separate physical encoders — map both to the same library actions for left-handed flexibility, or assign `SEL` to tree depth and `SCROLL` to list scroll.

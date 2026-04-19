# K3 + rekordbox + Euphonia — Performance Mapping

Single Xone:K3 controlling 2 decks (A, B) in rekordbox Performance Mode. All mixing / EQ / filter / send-FX / cue / master lives on the Euphonia mixer.

See `PLAN.md` for the control-labelling convention and deck assignment rationale.

**Visual diagrams**: [`diagrams/performance-layer1.svg`](diagrams/performance-layer1.svg) · [`diagrams/performance-layer2.svg`](diagrams/performance-layer2.svg)

## Layer 1 — Play

Upper half (encoders, pots, inline buttons, faders) is identical on Layer 2. Only the matrix changes between layers.

### Upper half

| Control | Strip 1 — Deck A outer | Strip 2 — Deck A inner | Strip 3 — Deck B inner | Strip 4 — Deck B outer |
|---|---|---|---|---|
| E rotate | scrub / nudge | loop move by loop size | loop move by loop size | scrub / nudge |
| E push | tap BPM | loop toggle (reloop / exit) | loop toggle (reloop / exit) | tap BPM |
| K·a | beat jump size | loop size | loop size | beat jump size |
| B·a | range cycle (±6/10/16/wide) | quantize toggle | quantize toggle | range cycle (±6/10/16/wide) |
| K·b | waveform zoom | *open* | *open* | waveform zoom |
| B·b | master tempo (keylock) | *open* | *open* | master tempo (keylock) |
| K·c | *open* | key adjust (±N semitones) | key adjust (±N semitones) | *open* |
| B·c | **sync** | key sync | key sync | **sync** |
| F | **tempo** | reserved | reserved | **tempo** |

### Matrix (Layer 1)

| Row | M1 (A outer) | M2 (A inner) | M3 (B inner) | M4 (B outer) |
|---|---|---|---|---|
| 1 | Play | memory-cue prev | memory-cue prev | Play |
| 2 | Cue | memory-cue next | memory-cue next | Cue |
| 3 | Pause (force — no-op if already paused) | beat jump −8 | beat jump −8 | Pause (force) |
| 4 | Beat LED (output only — pulses with beat) | beat jump +8 | beat jump +8 | Beat LED (output only) |

## Layer 2 — Fine tempo

Upper half unchanged. Matrix below.

| Row | M1 | M2 | M3 | M4 |
|---|---|---|---|---|
| 1 | pitch bend − (hold) | reset pitch to 0 | reset pitch to 0 | pitch bend − (hold) |
| 2 | pitch bend + (hold) | beatgrid nudge − | beatgrid nudge − | pitch bend + (hold) |
| 3 | tempo step −0.02 BPM | beatgrid nudge + | beatgrid nudge + | tempo step −0.02 BPM |
| 4 | tempo step +0.02 BPM | *empty* | *empty* | tempo step +0.02 BPM |

## Global controls

| Control | Function |
|---|---|
| `LAYER` | cycle Layer 1 ↔ Layer 2 |
| `SHIFT` (hold) | focused-deck toggle (A ↔ B) for `SEL` push and other load actions |
| `SCROLL` rotate | browser list scroll |
| `SEL` rotate | browser tree navigation |
| `SEL` push | load track to focused deck |

## LED / visual feedback

| Control | LED behaviour |
|---|---|
| `M·.1` Play | on = playing, off = stopped |
| `M·.2` Cue | on = at cue point, pulse = cue armed |
| `M·.3` Pause | on = paused |
| `M·.4` Beat LED | output-only, pulses once per beat |
| `B·c` Sync | on = synced to master tempo |
| `B·b` Master tempo | on = keylock active |
| `B·a` Range cycle | colour indicates current range |
| `B2a` / `B3a` Quantize | on = quantize active |
| `B2c` / `B3c` Key sync | on = key-synced |
| `K·a` / `K·c` pot rings | follow parameter value where applicable |
| `M2.1` / `M3.1` mem-cue prev | flash briefly when a memory cue is reached |

## Open slots (deferred)

`K1c`, `K2b`, `B2b`, `K3b`, `B3b`, `K4c`. Assign as needs emerge.

## Technical notes for rekordbox mapping XML

- The K3's `LAYER` button changes the MIDI channel for every strip control. Both layer channels must be mapped in rekordbox, with identical assignments for the upper-half controls so Layer 1 and Layer 2 behave the same above the matrix.
- `F1` / `F4` tempo faders should use soft-takeover (rekordbox "takeover" mode) so moving a fader on the wrong layer doesn't jump the tempo.
- Beat-LED output: rekordbox exposes a per-deck beat pulse in MIDI-Learn output configuration; route it to `M1.4` / `M4.4`.
- Hot cues are intentionally *not* on this mapping. Memory cues cover the "recall" workflow. Add hot cues later via an open layer or on the second K3.

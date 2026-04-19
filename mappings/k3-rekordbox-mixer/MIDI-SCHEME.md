# MIDI scheme for the Xone:K3

Authoritative per-control MIDI assignment used by the rekordbox CSVs in this folder. The diagrams are the visual form of the same data; this file is the byte-level contract.

## Layer → MIDI channel

Each of the K3's four layers sends on its own MIDI channel. Configure in the K3's **Setup Mode** (power on while holding `SEL`). These are our chosen channels — change them in the K3 setup if you'd rather use different ones, but then update the CSVs accordingly.

| K3 layer | Colour | MIDI channel | Note status byte | CC status byte |
|---|---|---:|---|---|
| Layer 1 | Red (A) | 15 | `0x9E` | `0xBE` |
| Layer 2 | Amber (B) | 14 | `0x9D` | `0xBD` |
| Layer 3 | Green (C) | 13 | `0x9C` | `0xBC` |
| Layer 4 | Blue (D) | 12 | `0x9B` | `0xBB` |

The Performance mapping uses Layers 1 and 2. The Export mapping uses Layers 1–4.

## Per-strip MIDI numbers

Same MIDI number on every layer; only the channel (status byte) differs. Strip N ranges from 1 (leftmost) to 4 (rightmost).

### Encoders (row 1)

| Control | Message | Number |
|---|---|---:|
| E[N] rotate | CC (relative) | `N−1` |
| E[N] push | Note | `N−1` |

### Pots and inline buttons

| Row | Pot → CC | Inline button → Note |
|---|---:|---:|
| a (top) | `4 + (N−1)` → CC 4–7 | `4 + (N−1)` → Note 4–7 |
| b (mid) | `8 + (N−1)` → CC 8–11 | `8 + (N−1)` → Note 8–11 |
| c (bot) | `12 + (N−1)` → CC 12–15 | `12 + (N−1)` → Note 12–15 |

### Faders and matrix

| Control | Message | Number |
|---|---|---:|
| F[N] | CC | `16 + (N−1)` → CC 16–19 |
| M[N].R (R=1..4) | Note | `20 + (N−1)·4 + (R−1)` → Note 20–35 |

Layout:

| Matrix | M.1 | M.2 | M.3 | M.4 |
|---|---:|---:|---:|---:|
| Strip 1 | 20 | 21 | 22 | 23 |
| Strip 2 | 24 | 25 | 26 | 27 |
| Strip 3 | 28 | 29 | 30 | 31 |
| Strip 4 | 32 | 33 | 34 | 35 |

### Bottom bar

`LAYER` is absorbed internally by the K3 (it shifts the channel on every other control). The rest are normal MIDI messages on the current layer's channel:

| Control | Message | Number |
|---|---|---:|
| SCROLL rotate | CC (relative) | 36 |
| SCROLL push | Note | 36 |
| SEL rotate | CC (relative) | 37 |
| SEL push | Note | 37 |
| SHIFT | Note | 38 |

## Status-byte convention

Rekordbox CSVs encode each MIDI message as 2 hex bytes: `<status><data1>`. Examples:

| MIDI message | Hex in CSV |
|---|---|
| Note On, channel 15, note 20 | `9E14` |
| Note Off, channel 15, note 20 | `8E14` |
| CC, channel 14, controller 16 | `BD10` |
| Note On, channel 12, note 35 | `9B23` |

For buttons, the CSV typically carries a triplet: `input (note-on) / LED-on output / LED-off output`. For continuous controls (pots, faders, encoders), only the input is filled.

## Encoder mode

Set all four top encoders (E1–E4), `SCROLL`, and `SEL` to **relative / increment-decrement mode** in the K3 setup. Default rekordbox targets expect 0x41 / 0x3F style relative ticks for browse and scrub. Absolute-position pots (K·a, K·b, K·c) and faders remain in absolute mode.

## How to apply this scheme

1. **Configure the K3** via Setup Mode to use the channels above. Default K3 firmware may already match; if not, reassign.
2. **Confirm the output** with a MIDI monitor (e.g. [MIDI Monitor](https://www.snoize.com/MIDIMonitor/) on macOS). Touch each control, verify it matches this table.
3. **Import the CSV** into rekordbox (see `IMPORT.md`).
4. **Spot-check each layer** in rekordbox by toggling `LAYER` and touching a control; rekordbox's MIDI indicator should fire and the mapped action should run.

## If a control doesn't match this table

The K3 lets you reassign any control's MIDI number in Setup Mode. If you prefer to keep the K3's factory defaults and adjust the CSV instead, export the K3's factory settings, read the numbers, and edit `tools/generate_rekordbox_csv.py` to match. Regenerate with `python3 tools/generate_rekordbox_csv.py`.

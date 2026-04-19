# Importing the K3 mapping into rekordbox

Two files in this folder ship the actual MIDI bindings:

- `k3-performance.midi.csv` — Performance Mode mapping (Layers 1 + 2)
- `k3-export.midi.csv` — Export Mode mapping (Layers A–D, single-deck focus)

Both use the channel scheme documented in [`MIDI-SCHEME.md`](MIDI-SCHEME.md): Layer 1→ch 15, Layer 2→ch 14, Layer 3→ch 13, Layer 4→ch 12.

## Step 1 — Configure the K3

Power on the K3 while holding `SEL`. This enters Setup Mode. Use `LAYER` + `SCROLL` to set each layer's MIDI channel to the values above (15 / 14 / 13 / 12). Press `SHIFT` to exit Setup Mode — hold it and the K3 saves.

Set **encoder mode** for `E1`–`E4`, `SCROLL`, `SEL` to **relative / increment-decrement** (sends `0x41` / `0x3F` on tick). Pots and faders stay in absolute mode.

## Step 2 — Verify with a MIDI monitor

Before touching rekordbox, confirm the K3 is sending what this mapping expects. Install [MIDI Monitor](https://www.snoize.com/MIDIMonitor/) (free, macOS). On Layer 1, pressing `M1.1` (top-left of the matrix under fader 1) should produce `Note On, channel 15, note 20`. On Layer 2, the same button should produce `Note On, channel 14, note 20`. If the channels or numbers differ, either:

- reconfigure the K3 in Setup Mode to match the scheme, **or**
- edit `tools/generate_rekordbox_csv.py` (adjust `LAYER_CH` or the `PHYSICAL` table) and regenerate:

  ```bash
  python3 tools/generate_rekordbox_csv.py
  ```

## Step 3 — Import into rekordbox

1. Open rekordbox → **Preferences → Controller → MIDI Learn** (rekordbox 6.7+ / 7.x; menu path may vary by version).
2. Click **Add** (or the `+` button) and select the controller entry representing the K3. If no K3 entry exists, create one and select your USB MIDI input port.
3. Click the **Import** button in the MIDI Learn pane.
4. Choose `k3-performance.midi.csv` (or `k3-export.midi.csv`).
5. Rekordbox parses the file and populates the bindings. Unknown function names will produce a warning row — note which rows are flagged; you'll need to rename them (see "Known caveats" below).

Switch between Performance and Export mappings by changing which CSV is the active mapping in the same pane.

## Step 4 — Spot-check each layer

For each layer:

1. Press `LAYER` to cycle to the target layer (watch the K3 button colour change).
2. Tap a well-known control (e.g. `M1.1` for Play).
3. Confirm the rekordbox MIDI-Learn pane highlights the matching row and that the mapped action fires in the deck.
4. For buttons with LED feedback, toggle the underlying state (e.g. start/stop a deck) and verify the K3 LED follows.

## Known caveats

### Function names are best-effort

Rekordbox doesn't publicly document the full list of valid function-name strings. The names in these CSVs are compiled from community mappings (e.g. [party-saver](https://github.com/willcassella/party-saver)) and the bundled Pioneer mappings inside `rekordbox.app/Contents/Resources/`. Likely-correct but not guaranteed per rekordbox build:

| Name in CSV | Purpose |
|---|---|
| `PlayPause`, `Cue`, `Pause` | transport |
| `Sync`, `MasterTempo`, `TempoRange`, `TempoSlider` | tempo |
| `KeySync`, `KeyShift` | key |
| `Quantize` | quantize toggle |
| `BeatJumpSize`, `BeatJumpForward`, `BeatJumpBackward` | beat jump |
| `MemoryCallPrev`, `MemoryCallNext`, `MemoryCueSet`, `MemoryCueDelete` | memory cues |
| `MemoryCueColorBlue/Red/Green/Orange/Cyan/Purple` | colour-tag most-recent cue |
| `LoopSize`, `LoopMove`, `LoopIn`, `LoopOut`, `ReloopExit`, `LoopSaveAsMemory`, `LoopToggle` | loops |
| `WaveformZoom`, `ScratchSlider`, `PitchBendUp/Down`, `TempoStepUp/Down`, `PitchReset` | waveform / tempo nudges |
| `BeatgridShiftForward/Backward`, `BeatgridShiftForwardBeat/BackwardBeat`, `BeatgridSnapToBeat`, `BeatgridHalfBPM`, `BeatgridDoubleBPM` | grid edit |
| `BrowseScroll`, `BrowseTreeScroll`, `BrowseTreeSelect`, `BrowseListScroll`, `BrowseExpand`, `LoadTrackFocused`, `PreviewToggle`, `SeekToCue` | browser + preview |
| `Rating1..5`, `RatingClear`, `AddToPlaylist` | metadata |
| `TapBPM`, `FocusDeckToggle`, `BeatLEDOutput` | misc |

If rekordbox rejects a row on import or "learns" nothing when you use the control, open a Pioneer-bundled CSV from  
`/Applications/rekordbox 7/rekordbox.app/Contents/Resources/`  
(pick any `*.midi.csv`), search for the semantic concept you need, and copy that file's function-name spelling into `tools/generate_rekordbox_csv.py`, then regenerate.

### `MemoryCueSet` + colour is two-step

Rekordbox does not (on current builds we know of) expose "place memory cue with colour X" as a single MIDI target. Layer B places the cue via `MemoryCueSet`, then you re-colour the just-placed cue with one of the six colour buttons. If your rekordbox build adds direct "set coloured cue" targets, change the CSV to use those — huge quality-of-life win.

### Two mapping files, one controller

Switch the active mapping in rekordbox's Controller Preferences when moving between Performance (live sets) and Export (track prep). You can't run both at once on one K3 because both claim the same physical buttons.

### Soft-takeover

Enable rekordbox's **Takeover** mode for tempo faders so `F1` and `F4` don't jump the tempo when you change layers or decks.

## Fallback: MIDI Learn by hand

If automatic import doesn't work cleanly, use the row-by-row procedure:

1. In rekordbox's MIDI Learn pane, click **Add**.
2. Click the target function in the rekordbox UI (e.g. the Play button on Deck 1).
3. Touch the K3 control (e.g. `M1.1` on Layer 1).
4. Rekordbox records the binding.
5. Repeat for each row in the CSV — the CSV's function column tells you the rekordbox target, and the `MIDI-SCHEME.md` tables tell you which K3 control corresponds to which code.

This is slow (1–2 minutes per binding × ~50 rows × 2 modes) but bulletproof.

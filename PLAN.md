# Controller Mappings — Project Plan

## Rig

- **Controllers**: 2× Allen & Heath Xone:K3 (starting with a single K3; second added later)
- **Mixer**: AlphaTheta Euphonia (4 digital stereo channels over USB; mixing / EQ / filter / send-FX / cue / master / booth all live on the mixer)
- **Host OS**: macOS
- **Legacy reference**: Traktor Pro 3 mapping for 2× Xone:K2 — `legacy/traktor-k2/Controller komplett 20150414.tsi`

## Software targets

- **rekordbox** — Creative plan, controller-only (no DVS). 3–4 decks.
- **Bitwig Studio** — future, alongside rekordbox.

## Mapping variants

| # | Variant | Scope | Status |
|---|---|---|---|
| 1 | K3 + rekordbox + Euphonia | single K3 first, 2 decks | **Performance spec drafted** — Export pending |
| 2 | Traktor K2 → rekordbox port | audit legacy `.tsi`, decide portability | pending |
| 3 | K3 + rekordbox, no mixer | K3 handles channel mixing too | pending |
| 4 | K3 + rekordbox + Bitwig | DJ + DAW integration | pending |

Each variant is expected to have both a **Performance** flavour (live play) and an **Export** flavour (library prep, beatgrid, memory cues).

## Controller labelling convention

The K3 has 4 vertical strips (S1–S4, left → right). Each strip has the following controls (top → bottom):

- `E[n]` — push encoder (row 1)
- `K[n]a` — top pot
- `B[n]a` — inline button below top pot
- `K[n]b` — upper-mid pot
- `B[n]b` — inline button
- `K[n]c` — lower-mid pot
- `B[n]c` — inline button above fader
- `F[n]` — fader
- `M[n].1` – `M[n].4` — matrix buttons under fader (row 1 = closest to fader)

Global controls on the bottom bar: `LAYER`, `SCROLL` (small encoder), `SEL` (small encoder), `SHIFT`.

All buttons are individually-addressable RGB for LED feedback.

## Deck-to-strip assignment (variant 1)

- **Deck A** = strips 1 + 2 (outer left = tempo, inner = loop/cues/key)
- **Deck B** = strips 3 + 4 (mirror: inner = loop/cues/key, outer right = tempo)
- Outer faders = tempo for each deck, inner faders reserved → ergonomically symmetric, "hot" buttons cluster centre.

## Layer strategy (variant 1)

- **Layer 1 (red)** — Performance play
- **Layer 2 (amber)** — Fine tempo (upper half mirrors Layer 1, matrix rewrites)
- `SHIFT` held → focused-deck toggle (A ↔ B) for global loads/browses. Not used as a layer-stacking modifier.

## Open slots for future iterations

`K1c`, `K2b`, `B2b`, `K3b`, `B3b`, `K4c` — intentionally left empty on the Performance spec. Fill as needs emerge during real-world playtesting.

## Next steps

- [ ] Design Export-mode spec for variant 1
- [ ] Extend variant 1 to second K3 (decks C / D)
- [ ] Audit legacy `.tsi` for portable concepts → variant 2
- [ ] Design no-mixer variant (3)
- [ ] Design Bitwig variant (4)
- [ ] Produce rekordbox mapping XML from the specs

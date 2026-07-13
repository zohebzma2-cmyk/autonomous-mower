# Contributing

Thanks for wanting to help build an open, safe, autonomous mower. This project
drives a machine with blades that can kill — so contribution has one non-negotiable
rule and a few normal ones.

## The safety rule

**Nothing you contribute may make it easier to run the blades before drive +
navigation + every failsafe is proven.** Blades stay physically disconnected in
all docs, defaults, and examples. Safety-relevant changes (kill-chain, failsafes,
`safety.py`, the carrier PCB relay topology) get extra scrutiny and must include a
test or a bench-test description.

## Good ways to contribute

- **Add your machine.** The highest-value contribution: a `params.scad` SECTION 1
  profile for a different zero-turn (deck, lap-bar OD/spacing, frame tube, seat).
  Drop it in and open a PR — this is how the project becomes reproducible on any ZTR.
- **Firmware / software** — improvements to the ESP32 lap-bar loop, `safety.py`,
  coverage planning, vision, or the MAVLink bridge. Keep the 25/25 tests green
  (`python3 -m pytest software/tests`) and add tests for new logic.
- **Hardware** — footprint fixes, Rev B ideas, or Gerbers for `hardware/pcb/`.
- **Docs** — clarify the build manual, wiring, or translate a section.

## Workflow

1. Open an issue or a Discussion first for anything non-trivial, so we agree on
   the approach.
2. Branch, make the change, keep the diff focused.
3. Tests green + describe any bench test for hardware/safety changes.
4. Open a PR referencing the issue. Small, reviewable PRs merge fastest.

## Where to talk

- **[Discussions](https://github.com/zohebzma2-cmyk/autonomous-mower/discussions)** — Show & Tell, Q&A, Ideas, Build logs.
- **Issues** — bugs and scoped tasks (look for `good first issue` / `help wanted`).

By contributing you agree your work is licensed under the repo's [MIT License](LICENSE).

## The 10-minute first contribution

1. `git clone` → `cd cad` → open `params.scad`
2. Change ONE number in SECTION 1 (say, `LAP_BAR_TUBE_OD = 28.6` for a 1-1/8" bar)
3. `./export_stl.sh` — watch the clamp bores re-fit and the bed gate re-check all 32 parts
4. `python3 ../software/tests/test_backend.py` — 45/45 still green
5. PR titled `profile: <your mower>` adding `cad/profiles/<your-mower>.scad`

That's a real contribution — every profile makes the kit fit one more machine.

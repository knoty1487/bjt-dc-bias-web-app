# Lab 04 — BJT Amplifier Simulator v1: integration plan

Date: 2026-11-24
Repo: `ottoponrod/BJT-DC-Bias-Web-App` (Lab 03 HEAD `2ad0aca`)

## Context / constraints

- Extend the existing Flask app. Do not recreate the Lab 03 architecture.
- Keep `dc_bias.py`, all three analytical DC modes and the 50 existing tests intact.
- Add real ngspice `.op`, `.ac`, `.tran` for **one** reference CE voltage-divider circuit only.
- Never fabricate plots or success values. A failed/missing/timed-out run must show an error and no stale plot.
- User instruction: full autonomy for setup, tests, fixes and GitHub push. Do **not** capture Lab 04 screenshots until explicitly ordered (Lab 03 baseline captures already done in `Desktop/Lab04_Lab3_Baseline`).

## Reuse / new files

| Item | Action |
|---|---|
| `dc_bias.py` | Reuse unchanged as independent DC reference. |
| `app.py` | Add dispatch: Lab 03 analytical path unchanged; new `analysis` selector sends CE divider to SPICE adapter. |
| `templates/index.html`, `static/style.css`, `static/app.js` | Add analysis mode, source amplitude/frequency, plot panels, engine/model/status/provenance; Impeccable polish only here. |
| `spice_engine.py` | **New**: validation, netlist builder, `subprocess.run([...], timeout=..., cwd=run_dir, shell=False)`, log/array parsing, typed results/errors. |
| `tests/test_spice_engine.py`, `tests/test_web.py` | **New/extend**: TDD for validation, parsing, run failure, web dispatch/regression. |
| `README.md`, `docs/validation.md` | Setup, reproducibility, B1–B8 evidence, model provenance, limits, closing answers in chat. |

## Interfaces (decided)

- `SpiceInputs`: `vcc, r1, r2, rc, re, rl, cin_uf, cout_uf, source_peak_v, source_freq_hz, f_start_hz, f_stop_hz, points_per_decade, tran_stop_s`; resistor inputs in **ohms**, capacitors in **µF** converted to F.
- Functions: `build_netlist(inputs, analysis) -> str`, `run_analysis(inputs, analysis, *, exe_path=None, timeout_s=20) -> SpiceResult`, `find_cutoff(...)`.
- `SpiceResult` carries `analysis`, `status`, `engine`, `model_name`, `netlist`, `log_excerpt`, `node_voltages`, `ac_points` (`frequency_hz, vdb, phase_deg, gain_db`), `tran_points` (`time_s, vin_v, vout_v`), `error`.
- Exceptions: `SpiceInputError` (invalid form), `SpiceRunError` (missing exe, nonzero exit, timeout, empty/malformed output).
- Subprocess argument list: `ngspice -b -o run.log -r run.raw circuit.cir`; one `tempfile.mkdtemp()` per run; no `shell=True`.
- BJT card: standard 2N3904 NPN model pinned in `spice_engine.py`, documented in README (no instructor starter kit was supplied).
- AC measurement node: Vin = node 5 (source side of Cin), Vout = node 6 (across RL); gain = VDB(6) − VDB(5), phase = VP(6) − VP(5). Print both nodes in log (verify ngspice column behaviour first).
- −3 dB cutoff: interpolate between adjacent gain samples crossing max_gain − 3 dB; otherwise report `not determined in sweep range`.

## Tasks (TDD, small commits)

1. Verify ngspice batch command with `-r`, decide AC print syntax, install Impeccable (`npx impeccable install`, OpenCode + project scope) and record Playwright MCP availability.
2. RED tests for `spice_engine` validation/netlist/parser/error paths; GREEN implementation; keep existing tests passing.
3. RED web tests for new dispatch/status/no-stale-plot; GREEN app + template changes; plot data embedded from real run only.
4. Run B1–B8 in a real browser via available browser tools; fix genuine failures; record PASS/FAIL/NOT RUN honestly with evidence in `docs/validation.md`.
5. Impeccable critique → smallest UI polish → audit (UI files only); before/after evidence stored per user order (do not capture Lab 04 screenshots until authorized).
6. Update README (ngspice install, model, run steps, AI/student split) and validation doc; run full suite; commit and push; report URL + SHA; answer closing questions in chat.

## Done criteria

- All original 50 Lab 03 tests + new tests pass.
- Real ngspice outputs visible with units, model, status and provenance in the browser.
- B1–B8 table with honest statuses; no fabricated evidence.
- GitHub pushed with URL and commit SHA; Lab 04 screenshots still deferred.

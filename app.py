"""Flask application: Lab 03 analytical DC bias + Lab 04 real ngspice CE.

Routes:
  GET  /           -> input form (default: analytical voltage-divider bias)
  POST /calculate  -> validate input and dispatch:
                      analysis=analytical -> the original three dc_bias.py modes
                      analysis=dc/ac/tran -> spice_engine.py + real ngspice
                      action=change_mode only reloads the form.
"""

from flask import Flask, render_template, request

import spice_engine as spice
from dc_bias import (
    MODE_DIVIDER,
    MODE_EMITTER,
    MODE_FIXED,
    MODES,
    BiasInputs,
    ValidationError,
    calculate_dc_bias,
    calculate_emitter_bias,
    calculate_fixed_bias,
)
from plots import ac_chart_svg, tran_chart_svg

app = Flask(__name__)

DEFAULTS = {
    "vcc": "12",
    "r1": "100",
    "r2": "22",
    "rb": "1000",
    "rc": "2.2",
    "re": "1",
    "beta": "100",
    "vbe": "0.70",
    "unit": "kilo",
    "rl": "10",
    "cin": "10",
    "cout": "10",
    "vin_mv": "10",
    "freq_khz": "1",
    "f_start_hz": "10",
    "f_stop_hz": "1000000",
}

NUMERIC_FIELDS = (
    "vcc", "r1", "r2", "rb", "rc", "re", "beta", "vbe",
    "rl", "cin", "cout", "vin_mv", "freq_khz", "f_start_hz", "f_stop_hz",
)
RESISTOR_FIELDS = ("r1", "r2", "rb", "rc", "re")

ANALYSES = ("analytical", "dc", "ac", "tran")
ANALYSIS_LABELS = {
    "analytical": "Analytical DC (Lab 03)",
    "dc": "DC · ngspice .op",
    "ac": "AC · ngspice .ac",
    "tran": "Transient · ngspice .tran",
}

# Which resistor inputs each mode actually uses.
MODE_FIELDS = {
    MODE_DIVIDER: ("r1", "r2", "rc", "re"),
    MODE_FIXED: ("rb", "rc"),
    MODE_EMITTER: ("rb", "re", "rc"),
}

MODE_LABELS = {
    MODE_DIVIDER: "Voltage Divider Bias",
    MODE_FIXED: "Fixed Bias",
    MODE_EMITTER: "Emitter Bias (แหล่งจ่ายเดียว)",
}


def _unit_label(unit: str) -> str:
    return "kΩ" if unit == "kilo" else "Ω"


def _render(form, mode, result=None, error=None, *, analysis="analytical",
            spice=None, spice_error=None, plot_svg="",
            analytical_reference=None, source_label=None):
    if spice_error:
        status = "error"
    elif spice is not None:
        status = "success"
    else:
        status = "ready"
    return render_template(
        "index.html",
        form=form,
        mode=mode,
        mode_label=MODE_LABELS[mode],
        mode_fields=MODE_FIELDS[mode],
        result=result,
        error=error,
        analysis=analysis,
        analysis_label=ANALYSIS_LABELS[analysis],
        spice=spice,
        spice_error=spice_error,
        plot_svg=plot_svg,
        analytical_reference=analytical_reference,
        source_label=source_label,
        status=status,
        unit_label=_unit_label(form.get("unit", "kilo")),
    )


def _collect_form(fallback: bool):
    """Read the form. On a mode switch we keep defaults for untouched fields."""
    source = request.form

    def read(field):
        if field in source:
            return source.get(field, "").strip()
        return DEFAULTS[field] if fallback else ""

    form = {field: read(field) for field in NUMERIC_FIELDS}
    unit = source.get("unit", DEFAULTS["unit"])
    form["unit"] = unit if unit in ("kilo", "ohm") else "kilo"
    return form


def _number(form, field):
    raw = form.get(field) or DEFAULTS[field]
    return float(raw)


def _spice_inputs(form):
    """Convert the validated form to SI units before any netlist is built."""
    factor = 1000.0 if form["unit"] == "kilo" else 1.0
    return spice.SpiceInputs(
        vcc=_number(form, "vcc"),
        r1=_number(form, "r1") * factor,
        r2=_number(form, "r2") * factor,
        rc=_number(form, "rc") * factor,
        re=_number(form, "re") * factor,
        rl=_number(form, "rl") * factor,
        cin_uf=_number(form, "cin"),
        cout_uf=_number(form, "cout"),
        source_peak_v=_number(form, "vin_mv") / 1000.0,
        source_freq_hz=_number(form, "freq_khz") * 1000.0,
        f_start_hz=_number(form, "f_start_hz"),
        f_stop_hz=_number(form, "f_stop_hz"),
    )


def _sample_rows(rows, count=6):
    """Evenly spaced rows from the real solver array for the evidence table."""
    if not rows:
        return []
    if len(rows) <= count:
        return rows
    step = (len(rows) - 1) / (count - 1)
    picked = [rows[round(i * step)] for i in range(count)]
    picked[-1] = rows[-1]
    return picked


def _spice_view(analysis, inputs, form):
    """Run one real solver analysis and prepare the display-only payload."""
    result = spice.run_analysis(inputs, analysis)
    directive = {"dc": ".OP", "ac": ".AC", "tran": ".TRAN"}[analysis]
    common = {
        "analysis": analysis,
        "directive": directive,
        "engine": result.engine,
        "model_name": result.model_name,
        "netlist": result.netlist,
        "log_excerpt": result.log_excerpt,
        "samples": result.sample_count,
    }
    reference = None
    if analysis == "dc":
        nodes = result.nodes
        common.update({
            "vb": nodes["V(2)"], "ve": nodes["V(4)"],
            "vc": nodes["V(3)"], "vce": nodes["VCE"],
            "ic": (inputs.vcc - nodes["V(3)"]) / inputs.rc,
            "ie": nodes["V(4)"] / inputs.re,
        })
        reference = calculate_dc_bias(BiasInputs(
            vcc=inputs.vcc, r1=inputs.r1, r2=inputs.r2, rc=inputs.rc,
            re=inputs.re, beta=_number(form, "beta"),
            vbe=_number(form, "vbe"),
        ))
        plot = ""
    elif analysis == "ac":
        cutoff = spice.cutoff_frequency(result.ac_points)
        common.update({
            "sweep": (f"{inputs.f_start_hz:g} – {inputs.f_stop_hz:g} Hz, "
                      f"{inputs.points_per_decade} points/decade"),
            "peak_gain_db": max(p.gain_db for p in result.ac_points),
            "cutoff": (f"{cutoff:g} Hz" if cutoff is not None
                       else "not determined in sweep range"),
            "sample_rows": _sample_rows([
                (p.frequency_hz, p.gain_db, p.phase_deg)
                for p in result.ac_points
            ]),
        })
        plot = ac_chart_svg(result.ac_points)
    else:
        vin = [p.vin_v for p in result.tran_points]
        vout = [p.vout_v for p in result.tran_points]
        correlation = sum(a * b for a, b in zip(vin, vout)) / len(vin)
        common.update({
            "vin_peak": max(abs(v) for v in vin),
            "vout_peak": max(abs(v) for v in vout),
            "phase_note": ("Vout กลับเฟส (~180°) ตามหลัก Common-Emitter"
                           if correlation < 0
                           else "ไม่พบการกลับเฟสในหน้าต่างเวลานี้"),
            "sample_rows": _sample_rows([
                (p.time_s * 1e3, p.vin_v, p.vout_v)
                for p in result.tran_points
            ]),
        })
        plot = tran_chart_svg(result.tran_points)
    return common, plot, reference


@app.get("/")
def index():
    form = dict(DEFAULTS)
    form["mode"] = MODE_DIVIDER
    return _render(form, MODE_DIVIDER)


@app.post("/calculate")
def calculate():
    action = request.form.get("action", "calculate")
    raw_mode = request.form.get("mode", MODE_DIVIDER).strip()
    mode_ok = raw_mode in MODES
    mode = raw_mode if mode_ok else MODE_DIVIDER

    analysis = request.form.get("analysis", "analytical").strip()
    if analysis not in ANALYSES:
        analysis = "analytical"

    form = _collect_form(fallback=(action == "change_mode"))
    form["mode"] = mode

    if analysis != "analytical":
        # SPICE v1 supports exactly one circuit: the CE voltage divider.
        mode = MODE_DIVIDER
        form["mode"] = mode
        if not mode_ok and analysis != "analytical":
            mode_ok = True  # mode is irrelevant for the single SPICE fixture
        try:
            source_label = (f"{_number(form, 'vin_mv'):g} mV @ "
                            f"{_number(form, 'freq_khz'):g} kHz")
        except (TypeError, ValueError):
            source_label = (f"{form.get('vin_mv') or DEFAULTS['vin_mv']} mV @ "
                            f"{form.get('freq_khz') or DEFAULTS['freq_khz']} kHz")
        if action == "change_mode":
            return _render(form, mode, analysis=analysis,
                           source_label=source_label)
        try:
            inputs = _spice_inputs(form)
            payload, plot, reference = _spice_view(analysis, inputs, form)
        except (ValueError, spice.SpiceRunError, spice.SpiceInputError) as exc:
            return _render(form, mode, analysis=analysis,
                           spice_error=str(exc), source_label=source_label)
        return _render(form, mode, analysis=analysis, spice=payload,
                       plot_svg=plot, analytical_reference=reference,
                       source_label=source_label)

    if not mode_ok:
        return _render(
            form, mode, error="โหมดไม่ถูกต้อง กรุณาเลือกโหมดวงจรที่กำหนด")

    if action == "change_mode":
        return _render(form, mode)

    required = ("vcc", "beta", "vbe") + MODE_FIELDS[mode]
    if any(not form[field] for field in required):
        return _render(form, mode, error="กรุณากรอกข้อมูลให้ครบทุกช่อง")

    try:
        values = {field: float(form[field]) for field in required}
    except ValueError:
        return _render(form, mode, error="กรุณากรอกเป็นตัวเลข (ห้ามใช้ comma)")

    factor = 1000.0 if form["unit"] == "kilo" else 1.0
    resistors = {
        field: values[field] * factor for field in MODE_FIELDS[mode]
    }

    try:
        if mode == MODE_DIVIDER:
            result = calculate_dc_bias(BiasInputs(
                vcc=values["vcc"],
                r1=resistors["r1"],
                r2=resistors["r2"],
                rc=resistors["rc"],
                re=resistors["re"],
                beta=values["beta"],
                vbe=values["vbe"],
            ))
        elif mode == MODE_FIXED:
            result = calculate_fixed_bias(
                vcc=values["vcc"],
                rb=resistors["rb"],
                rc=resistors["rc"],
                beta=values["beta"],
                vbe=values["vbe"],
            )
        else:
            result = calculate_emitter_bias(
                vcc=values["vcc"],
                rb=resistors["rb"],
                re=resistors["re"],
                rc=resistors["rc"],
                beta=values["beta"],
                vbe=values["vbe"],
            )
    except ValidationError as exc:
        return _render(form, mode, error=str(exc))

    return _render(form, mode, result=result)


if __name__ == "__main__":
    app.run(debug=True)

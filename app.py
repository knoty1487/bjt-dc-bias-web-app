"""Flask application for the BJT DC bias calculator (Lab 02 + Lab 03).

Routes:
  GET  /           -> input form (default: voltage-divider bias)
  POST /calculate  -> validate input, pick the model from ``mode`` and render
                      the results. ``action=change_mode`` only reloads the
                      form for the chosen mode (it never calculates).
"""

from flask import Flask, render_template, request

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
}

NUMERIC_FIELDS = ("vcc", "r1", "r2", "rb", "rc", "re", "beta", "vbe")
RESISTOR_FIELDS = ("r1", "r2", "rb", "rc", "re")

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


def _render(form, mode, result=None, error=None):
    return render_template(
        "index.html",
        form=form,
        mode=mode,
        mode_label=MODE_LABELS[mode],
        mode_fields=MODE_FIELDS[mode],
        result=result,
        error=error,
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

    form = _collect_form(fallback=(action == "change_mode"))
    form["mode"] = mode

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

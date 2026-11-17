"""Flask application for the Lab 03 BJT DC bias calculator.

Routes:
  GET  /           -> input form (default: voltage-divider bias)
  POST /calculate  -> validate input, select the model by mode, render results
                      action=change_mode only reloads the form for the chosen mode
"""

from flask import Flask, render_template, request

from dc_bias import (
    MODES,
    MODE_DIVIDER,
    MODE_EMITTER,
    MODE_FIXED,
    InvalidInputError,
    calculate_dc_bias,
    calculate_emitter_bias,
    calculate_fixed_bias,
)

app = Flask(__name__)

_ALL_RESISTOR_FIELDS = ("r1", "r2", "rb", "rc", "re")
_RESISTOR_LABELS = {"r1": "R1", "r2": "R2", "rb": "RB", "rc": "RC", "re": "RE"}
_UNITS = {"ohm": 1.0, "kohm": 1000.0}
_MODE_FIELDS = {
    MODE_DIVIDER: ("r1", "r2", "re"),
    MODE_FIXED: ("rb",),
    MODE_EMITTER: ("rb", "re"),
}
_MODE_LABELS = {
    MODE_DIVIDER: "Voltage Divider Bias",
    MODE_FIXED: "Fixed Bias",
    MODE_EMITTER: "Emitter Bias (แหล่งจ่ายเดียว)",
}
_REGION_LABELS = {
    "active": "Forward Active (ใช้งานได้ตามแบบจำลอง)",
    "cutoff": "Cutoff (ทรานซิสเตอร์ไม่นำกระแส)",
    "saturation": "Saturation (แบบจำลอง Forward-Active ใช้ไม่ได้)",
}


def _read_number(form, field, label):
    raw = (form.get(field) or "").strip()
    if not raw:
        raise InvalidInputError(f"{label}: กรุณากรอกค่า")
    try:
        value = float(raw)
    except ValueError:
        raise InvalidInputError(f"{label}: ต้องเป็นตัวเลข") from None
    if value != value or value in (float("inf"), float("-inf")):
        raise InvalidInputError(f"{label}: ต้องเป็นจำนวนจำกัด")
    return value


def _read_resistance(form, field):
    label = _RESISTOR_LABELS[field]
    value = _read_number(form, field, label)
    unit = form.get(f"unit_{field}", "ohm")
    if unit not in _UNITS:
        raise InvalidInputError(f"{label}: หน่วยไม่ถูกต้อง")
    return value * _UNITS[unit]


def _read_mode(form):
    mode = (form.get("mode") or MODE_DIVIDER).strip()
    if mode not in MODES:
        raise InvalidInputError("โหมดไม่ถูกต้อง กรุณาเลือกโหมดวงจรที่กำหนด")
    return mode


def _form_context():
    source = request.form
    raw_mode = (source.get("mode") or MODE_DIVIDER).strip()
    mode = raw_mode if raw_mode in MODES else MODE_DIVIDER
    values = {
        key: source.get(key, "")
        for key in ("vcc", "r1", "r2", "rb", "rc", "re", "beta", "vbe")
    }
    values["mode"] = mode
    units = {
        key: source.get(f"unit_{key}", "kohm") or "kohm"
        for key in _ALL_RESISTOR_FIELDS
    }
    if any(units[key] not in _UNITS for key in _ALL_RESISTOR_FIELDS):
        units = {key: "kohm" for key in _ALL_RESISTOR_FIELDS}
    return values, units, mode


def _render_form(values, units, mode, **extra):
    return render_template(
        "index.html",
        values=values,
        units=units,
        mode=mode,
        mode_label=_MODE_LABELS[mode],
        mode_fields=_MODE_FIELDS[mode],
        **extra,
    )


@app.get("/")
def index():
    units = {key: "kohm" for key in _ALL_RESISTOR_FIELDS}
    return _render_form({}, units, MODE_DIVIDER)


@app.post("/calculate")
def calculate():
    values, units, mode = _form_context()
    try:
        mode = _read_mode(request.form)
        values["mode"] = mode

        if request.form.get("action") == "change_mode":
            return _render_form(values, units, mode)

        vcc = _read_number(request.form, "vcc", "VCC")
        rc = _read_resistance(request.form, "rc")
        beta = _read_number(request.form, "beta", "β")
        vbe = _read_number(request.form, "vbe", "VBE")
        resistors = {
            field: _read_resistance(request.form, field)
            for field in _MODE_FIELDS[mode]
        }

        if mode == MODE_DIVIDER:
            result = calculate_dc_bias(
                vcc, resistors["r1"], resistors["r2"], rc, resistors["re"], beta, vbe
            )
        elif mode == MODE_FIXED:
            result = calculate_fixed_bias(vcc, resistors["rb"], rc, beta, vbe)
        else:
            result = calculate_emitter_bias(
                vcc, resistors["rb"], resistors["re"], rc, beta, vbe
            )
    except InvalidInputError as exc:
        return _render_form(values, units, mode, error=str(exc)), 400

    return _render_form(
        values,
        units,
        mode,
        result=result,
        region_label=_REGION_LABELS[result.region],
        resistors=resistors,
    )


if __name__ == "__main__":
    app.run(debug=True)

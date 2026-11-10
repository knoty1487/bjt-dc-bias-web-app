"""Flask application for the Lab 02 BJT DC bias calculator.

Routes:
  GET  /           -> input form
  POST /calculate  -> validate input, run dc_bias.calculate_dc_bias, render results
"""

from flask import Flask, render_template, request

from dc_bias import InvalidInputError, calculate_dc_bias

app = Flask(__name__)

_RESISTOR_FIELDS = ("r1", "r2", "rc", "re")
_RESISTOR_LABELS = {"r1": "R1", "r2": "R2", "rc": "RC", "re": "RE"}
_UNITS = {"ohm": 1.0, "kohm": 1000.0}
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
        return float(raw)
    except ValueError:
        raise InvalidInputError(f"{label}: ต้องเป็นตัวเลข") from None


def _read_resistance(form, field):
    label = _RESISTOR_LABELS[field]
    value = _read_number(form, field, label)
    unit = form.get(f"unit_{field}", "ohm")
    if unit not in _UNITS:
        raise InvalidInputError(f"{label}: หน่วยไม่ถูกต้อง")
    return value * _UNITS[unit]


def _form_context():
    values = {
        key: request.form.get(key, "")
        for key in ("vcc", "r1", "r2", "rc", "re", "beta", "vbe")
    }
    units = {
        key: request.form.get(f"unit_{key}", "kohm")
        for key in _RESISTOR_FIELDS
    }
    if units["r1"] not in _UNITS:
        units = {key: "kohm" for key in _RESISTOR_FIELDS}
    return values, units


@app.get("/")
def index():
    units = {key: "kohm" for key in _RESISTOR_FIELDS}
    return render_template("index.html", values={}, units=units)


@app.post("/calculate")
def calculate():
    values, units = _form_context()
    try:
        vcc = _read_number(request.form, "vcc", "VCC")
        resistors = {field: _read_resistance(request.form, field) for field in _RESISTOR_FIELDS}
        beta = _read_number(request.form, "beta", "β")
        vbe = _read_number(request.form, "vbe", "VBE")
        result = calculate_dc_bias(
            vcc,
            resistors["r1"],
            resistors["r2"],
            resistors["rc"],
            resistors["re"],
            beta,
            vbe,
        )
    except InvalidInputError as exc:
        return render_template("index.html", values=values, units=units, error=str(exc)), 400

    return render_template(
        "index.html",
        values=values,
        units=units,
        result=result,
        region_label=_REGION_LABELS[result.region],
        resistors=resistors,
    )


if __name__ == "__main__":
    app.run(debug=True)

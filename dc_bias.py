"""DC bias calculations for BJT common-emitter circuits (Lab 02 + Lab 03).

This module is pure engineering logic: it knows nothing about Flask, HTTP or
HTML. All voltages are in volts, resistances in ohms and currents in amperes.

Supported circuits (Forward-Active approximation):
  * Voltage-divider bias  -- R1/R2 base divider replaced by its Thevenin
    equivalent, RE from emitter to ground.
  * Fixed bias            -- RB from VCC to base, emitter tied to ground.
  * Emitter bias          -- RB from VCC to base, RE from emitter to ground
    (single supply).
"""

from dataclasses import dataclass, field
import math
from typing import Optional

MODE_DIVIDER = "divider"
MODE_FIXED = "fixed"
MODE_EMITTER = "emitter"

MODES = (MODE_DIVIDER, MODE_FIXED, MODE_EMITTER)


class ValidationError(ValueError):
    """Raised when the supplied component values cannot be used."""


@dataclass(frozen=True)
class BiasInputs:
    vcc: float
    r1: float
    r2: float
    rc: float
    re: float
    beta: float
    vbe: float


@dataclass
class BiasResult:
    ib: float
    ic: float
    ie: float
    vb: float
    ve: float
    vc: float
    vce: float
    region: str = "active"
    vth: Optional[float] = None
    rth: Optional[float] = None
    mode: str = MODE_DIVIDER
    warnings: list[str] = field(default_factory=list)


def _require_finite(**values) -> None:
    if not all(math.isfinite(value) for value in values.values()):
        raise ValidationError("ค่าอินพุตต้องเป็นจำนวนจำกัด (ห้าม NaN หรือ ∞)")


def _validate_common(vcc: float, rc: float, beta: float, vbe: float) -> None:
    if vcc <= 0:
        raise ValidationError("VCC ต้องมากกว่า 0")
    if rc <= 0:
        raise ValidationError("RC ต้องมากกว่า 0 Ω")
    if beta <= 0:
        raise ValidationError("β ต้องมากกว่า 0")
    if vbe <= 0:
        raise ValidationError("VBE ต้องมากกว่า 0")


def _validate_resistor(value: float, name: str) -> None:
    if value <= 0:
        raise ValidationError(f"{name} ต้องมากกว่า 0 Ω")


def _classify_region(vce: float) -> tuple[str, list[str]]:
    if vce <= 0.3:
        return "saturation", [
            "VCE ≤ 0.3 V: ทรานซิสเตอร์อยู่ในสภาวะอิ่มตัว (saturation) — "
            "แบบจำลอง Forward-Active ใช้ไม่ได้ ค่าที่ได้เป็นเพียงค่าประมาณ"
        ]
    if vce < 1.0:
        return "near-saturation", [
            "VCE ใกล้ขอบอิ่มตัว (0.3 V < VCE < 1.0 V) — "
            "ผลลัพธ์อาจคลาดเคลื่อนจากของจริง ควรตรวจสอบด้วยการจำลอง"
        ]
    return "active", []


def _operating_point(
    ib: float,
    vcc: float,
    rc: float,
    beta: float,
    re: float,
    vbe: float,
    mode: str,
    vth: Optional[float] = None,
    rth: Optional[float] = None,
) -> BiasResult:
    """Complete the DC solution from base current and classify the region."""
    ic = beta * ib
    ie = (beta + 1.0) * ib
    ve = ie * re
    vb = ve + vbe
    vc = vcc - ic * rc
    vce = vc - ve

    region, warnings = _classify_region(vce)

    return BiasResult(
        ib=ib,
        ic=ic,
        ie=ie,
        vb=vb,
        ve=ve,
        vc=vc,
        vce=vce,
        region=region,
        vth=vth,
        rth=rth,
        mode=mode,
        warnings=warnings,
    )


def _cutoff_result(
    vcc: float,
    mode: str,
    vth: Optional[float] = None,
    rth: Optional[float] = None,
) -> BiasResult:
    return BiasResult(
        ib=0.0,
        ic=0.0,
        ie=0.0,
        vb=vcc if vth is None else vth,
        ve=0.0,
        vc=vcc,
        vce=vcc,
        region="cutoff",
        vth=vth,
        rth=rth,
        mode=mode,
        warnings=[
            "รอยต่อ Base-Emitter ไม่ได้ไบแอสไปข้างหน้า ทรานซิสเตอร์อยู่ใน "
            "สภาวะตัดขาด (cutoff) — แบบจำลอง Forward-Active ใช้ไม่ได้"
        ],
    )


def calculate_dc_bias(inputs: BiasInputs) -> BiasResult:
    """Return the DC operating point of a voltage-divider biased BJT."""
    _require_finite(
        vcc=inputs.vcc,
        r1=inputs.r1,
        r2=inputs.r2,
        rc=inputs.rc,
        re=inputs.re,
        beta=inputs.beta,
        vbe=inputs.vbe,
    )

    if inputs.vcc <= 0:
        raise ValidationError("VCC ต้องมากกว่า 0")
    if inputs.r1 <= 0 or inputs.r2 <= 0 or inputs.rc <= 0 or inputs.re <= 0:
        raise ValidationError("ตัวต้านทานต้องมากกว่า 0 (R1, R2, RC, RE)")
    if inputs.beta <= 0:
        raise ValidationError("β ต้องมากกว่า 0")
    if inputs.vbe <= 0:
        raise ValidationError("VBE ต้องมากกว่า 0")
    if inputs.vbe >= inputs.vcc:
        raise ValidationError("VBE ต้องน้อยกว่า VCC")

    vth = inputs.vcc * inputs.r2 / (inputs.r1 + inputs.r2)
    rth = inputs.r1 * inputs.r2 / (inputs.r1 + inputs.r2)

    if vth <= inputs.vbe:
        return _cutoff_result(
            inputs.vcc, MODE_DIVIDER, vth=vth, rth=rth)

    ib = (vth - inputs.vbe) / (rth + (inputs.beta + 1) * inputs.re)
    return _operating_point(
        ib, inputs.vcc, inputs.rc, inputs.beta, inputs.re, inputs.vbe,
        MODE_DIVIDER, vth=vth, rth=rth)


def calculate_fixed_bias(
    vcc: float, rb: float, rc: float, beta: float, vbe: float
) -> BiasResult:
    """Return the DC operating point of a fixed-bias NPN common emitter.

    IB = (VCC - VBE) / RB and the emitter is tied directly to ground.
    """
    _require_finite(vcc=vcc, rb=rb, rc=rc, beta=beta, vbe=vbe)
    _validate_common(vcc, rc, beta, vbe)
    _validate_resistor(rb, "RB")

    if vcc <= vbe:
        return _cutoff_result(vcc, MODE_FIXED)

    ib = (vcc - vbe) / rb
    return _operating_point(
        ib, vcc, rc, beta, 0.0, vbe, MODE_FIXED)


def calculate_emitter_bias(
    vcc: float, rb: float, re: float, rc: float, beta: float, vbe: float
) -> BiasResult:
    """Return the DC operating point of a single-supply emitter-biased NPN.

    IB = (VCC - VBE) / [RB + (beta + 1) * RE].
    """
    _require_finite(vcc=vcc, rb=rb, re=re, rc=rc, beta=beta, vbe=vbe)
    _validate_common(vcc, rc, beta, vbe)
    _validate_resistor(rb, "RB")
    _validate_resistor(re, "RE")

    if vcc <= vbe:
        return _cutoff_result(vcc, MODE_EMITTER)

    ib = (vcc - vbe) / (rb + (beta + 1.0) * re)
    return _operating_point(
        ib, vcc, rc, beta, re, vbe, MODE_EMITTER)

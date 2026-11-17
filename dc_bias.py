"""Engineering calculations for BJT common-emitter DC bias circuits.

This module contains only the DC bias mathematics. It does not import Flask,
HTML or anything related to HTTP, so the model can be tested on its own and
reused outside the web application.

Supported circuits (Lab 02 + Lab 03, Forward-Active approximation):
  * NPN BJT in the forward-active region.
  * beta is constant and VBE is constant.
  * Voltage-divider bias: the R1/R2 base divider is replaced by its Thevenin
    equivalent.
  * Fixed bias: RB from VCC to base, emitter tied directly to ground.
  * Emitter bias (single supply): RB from VCC to base, RE from emitter to
    ground.

All resistances are in ohm, voltages in volt, currents in ampere.
"""

from dataclasses import dataclass, field
from typing import Optional

# Boundary used by the simple forward-active model. Real devices saturate
# around 0.1-0.3 V; 0.2 V is a common textbook value.
VCE_SAT = 0.2

REGION_ACTIVE = "active"
REGION_CUTOFF = "cutoff"
REGION_SATURATION = "saturation"

MODE_DIVIDER = "divider"
MODE_FIXED = "fixed"
MODE_EMITTER = "emitter"

MODES = (MODE_DIVIDER, MODE_FIXED, MODE_EMITTER)


class InvalidInputError(ValueError):
    """Raised when input values cannot produce a meaningful DC bias result."""


@dataclass
class BiasResult:
    """DC operating point of a biased BJT (SI units).

    vth/rth only exist for the voltage-divider model; they are None for the
    fixed and emitter-bias models.
    """

    ib: float       # Base current [A]
    ic: float       # Collector current [A]
    ie: float       # Emitter current [A]
    vb: float       # Base voltage [V]
    ve: float       # Emitter voltage [V]
    vc: float       # Collector voltage [V]
    vce: float      # Collector-emitter voltage [V]
    region: str
    vth: Optional[float] = None      # Thevenin base voltage [V], divider only
    rth: Optional[float] = None      # Thevenin base resistance [ohm], divider only
    mode: str = MODE_DIVIDER
    warnings: list[str] = field(default_factory=list)


def _validate_resistor(value, name):
    if value <= 0:
        raise InvalidInputError(f"{name} ต้องมากกว่า 0 Ω")


def _validate_common(vcc, rc, beta, vbe):
    if vcc <= 0:
        raise InvalidInputError("VCC ต้องมากกว่า 0 V")
    _validate_resistor(rc, "RC")
    if beta <= 0:
        raise InvalidInputError("β ต้องมากกว่า 0")
    if vbe <= 0:
        raise InvalidInputError("VBE ต้องมากกว่า 0 V")


def _validate(vcc, r1, r2, rc, re, beta, vbe):
    """Validation for the original divider model (keeps Lab 02 messages)."""
    if vcc <= 0:
        raise InvalidInputError("VCC ต้องมากกว่า 0 V")
    if r1 <= 0 or r2 <= 0 or rc <= 0 or re <= 0:
        raise InvalidInputError("ค่าความต้านทานทุกตัวต้องมากกว่า 0 Ω")
    if beta <= 0:
        raise InvalidInputError("β ต้องมากกว่า 0")
    if vbe <= 0 or vbe >= vcc:
        raise InvalidInputError("VBE ต้องอยู่ระหว่าง 0 กับ VCC")


def _operating_point(ib, vcc, rc, beta, re, mode, vbe, vth=None, rth=None):
    """Complete the DC solution from base current and check the region."""
    ic = beta * ib
    ie = (beta + 1.0) * ib
    ve = ie * re
    vb = ve + vbe
    vc = vcc - ic * rc
    vce = vc - ve

    warnings = []
    if vce <= VCE_SAT:
        region = REGION_SATURATION
        warnings.append(
            f"VCE ≈ {vce:.3f} V ต่ำกว่า VCE(sat) ≈ {VCE_SAT:.1f} V — "
            "ทรานซิสเตอร์อยู่ในสภาวะ Saturation ค่าที่คำนวณได้จากสมมติฐาน "
            "Forward-Active จึงไม่น่าเชื่อถือ"
        )
    else:
        region = REGION_ACTIVE
        if vce < VCE_SAT + 0.1:
            warnings.append(
                f"VCE ≈ {vce:.3f} V อยู่ใกล้ Saturation มาก — "
                "ผลลัพธ์อาจคลาดเคลื่อนจากของจริงได้"
            )

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


def _cutoff_result(vcc, mode, vth=None, rth=None):
    return BiasResult(
        ib=0.0,
        ic=0.0,
        ie=0.0,
        vb=vcc,
        ve=0.0,
        vc=vcc,
        vce=vcc,
        region=REGION_CUTOFF,
        vth=vth,
        rth=rth,
        mode=mode,
        warnings=[
            "แหล่งจ่าย/ไบอัสไม่เพียงพอทำให้รอยต่อ Base-Emitter ไม่ได้ไบแอสไปข้างหน้า "
            "ทรานซิสเตอร์อยู่ในสภาวะ Cutoff — แบบจำลอง Forward-Active ใช้ไม่ได้"
        ],
    )


def calculate_dc_bias(vcc, r1, r2, rc, re, beta, vbe):
    """Return the DC operating point of the voltage-divider biased circuit.

    Resistances are in ohm, voltages in volt and beta is dimensionless.
    Raises InvalidInputError for non-physical input values.
    """
    _validate(vcc, r1, r2, rc, re, beta, vbe)

    vth = vcc * r2 / (r1 + r2)
    rth = r1 * r2 / (r1 + r2)

    if vth <= vbe:
        # Base-emitter junction is not forward biased: transistor is cut off.
        return BiasResult(
            ib=0.0,
            ic=0.0,
            ie=0.0,
            vb=vth,
            ve=0.0,
            vc=vcc,
            vce=vcc,
            region=REGION_CUTOFF,
            vth=vth,
            rth=rth,
            mode=MODE_DIVIDER,
            warnings=[
                "VTH ≤ VBE ทำให้รอยต่อ Base-Emitter ไม่ได้ไบแอสไปข้างหน้า "
                "ทรานซิสเตอร์อยู่ในสภาวะ Cutoff — แบบจำลอง Forward-Active ใช้ไม่ได้"
            ],
        )

    ib = (vth - vbe) / (rth + (beta + 1.0) * re)
    return _operating_point(ib, vcc, rc, beta, re, MODE_DIVIDER, vbe, vth, rth)


def calculate_fixed_bias(vcc, rb, rc, beta, vbe):
    """Return the DC operating point of a fixed-bias NPN common emitter.

    IB = (VCC - VBE) / RB ; emitter is tied directly to ground (VE = 0).
    """
    _validate_common(vcc, rc, beta, vbe)
    _validate_resistor(rb, "RB")

    if vcc <= vbe:
        return _cutoff_result(vcc, MODE_FIXED)

    ib = (vcc - vbe) / rb
    return _operating_point(ib, vcc, rc, beta, 0.0, MODE_FIXED, vbe=vbe)


def calculate_emitter_bias(vcc, rb, re, rc, beta, vbe):
    """Return the DC operating point of a single-supply emitter-biased NPN.

    IB = (VCC - VBE) / [RB + (beta + 1) * RE]
    """
    _validate_common(vcc, rc, beta, vbe)
    _validate_resistor(rb, "RB")
    _validate_resistor(re, "RE")

    if vcc <= vbe:
        return _cutoff_result(vcc, MODE_EMITTER)

    ib = (vcc - vbe) / (rb + (beta + 1.0) * re)
    return _operating_point(ib, vcc, rc, beta, re, MODE_EMITTER, vbe=vbe)

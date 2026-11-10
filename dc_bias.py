"""Engineering calculations for a BJT common-emitter, voltage-divider bias circuit.

This module contains only the DC bias mathematics. It does not import Flask,
HTML or anything related to HTTP, so the model can be tested on its own and
reused outside the web application.

Model (Lab 02, Forward-Active approximation):
  * NPN BJT in the forward-active region.
  * beta is constant and VBE is constant.
  * The R1/R2 base divider is replaced by its Thevenin equivalent.
"""

from dataclasses import dataclass, field

# Boundary used by the simple forward-active model. Real devices saturate
# around 0.1-0.3 V; 0.2 V is a common textbook value.
VCE_SAT = 0.2

REGION_ACTIVE = "active"
REGION_CUTOFF = "cutoff"
REGION_SATURATION = "saturation"


class InvalidInputError(ValueError):
    """Raised when input values cannot produce a meaningful DC bias result."""


@dataclass
class BiasResult:
    """DC operating point of the voltage-divider biased BJT (SI units)."""

    vth: float      # Thevenin base voltage [V]
    rth: float      # Thevenin base resistance [ohm]
    ib: float       # Base current [A]
    ic: float       # Collector current [A]
    ie: float       # Emitter current [A]
    vb: float       # Base voltage [V]
    ve: float       # Emitter voltage [V]
    vc: float       # Collector voltage [V]
    vce: float      # Collector-emitter voltage [V]
    region: str
    warnings: list[str] = field(default_factory=list)


def _validate(vcc, r1, r2, rc, re, beta, vbe):
    if vcc <= 0:
        raise InvalidInputError("VCC ต้องมากกว่า 0 V")
    if r1 <= 0 or r2 <= 0 or rc <= 0 or re <= 0:
        raise InvalidInputError("ค่าความต้านทานทุกตัวต้องมากกว่า 0 Ω")
    if beta <= 0:
        raise InvalidInputError("β ต้องมากกว่า 0")
    if vbe <= 0 or vbe >= vcc:
        raise InvalidInputError("VBE ต้องอยู่ระหว่าง 0 กับ VCC")


def calculate_dc_bias(vcc, r1, r2, rc, re, beta, vbe):
    """Return the DC operating point of the circuit.

    Resistances are in ohm, voltages in volt and beta is dimensionless.
    Raises InvalidInputError for non-physical input values.
    """
    _validate(vcc, r1, r2, rc, re, beta, vbe)

    vth = vcc * r2 / (r1 + r2)
    rth = r1 * r2 / (r1 + r2)

    if vth <= vbe:
        # Base-emitter junction is not forward biased: transistor is cut off.
        return BiasResult(
            vth=vth,
            rth=rth,
            ib=0.0,
            ic=0.0,
            ie=0.0,
            vb=vth,
            ve=0.0,
            vc=vcc,
            vce=vcc,
            region=REGION_CUTOFF,
            warnings=[
                "VTH ≤ VBE ทำให้รอยต่อ Base-Emitter ไม่ได้ไบแอสไปข้างหน้า "
                "ทรานซิสเตอร์อยู่ในสภาวะ Cutoff — แบบจำลอง Forward-Active ใช้ไม่ได้"
            ],
        )

    ib = (vth - vbe) / (rth + (beta + 1.0) * re)
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
        vth=vth,
        rth=rth,
        ib=ib,
        ic=ic,
        ie=ie,
        vb=vb,
        ve=ve,
        vc=vc,
        vce=vce,
        region=region,
        warnings=warnings,
    )

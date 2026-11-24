"""ngspice adapter for the Lab 04 CE voltage-divider reference circuit.

The Flask route validates and passes *already checked* numbers here. This
module owns the netlist, the external process and the parsing of solver
output. Nothing in this file invents a result: a failed or empty run raises
``SpiceRunError`` so the UI can show an error instead of a stale plot.

Run form (verified with ngspice 47 on Windows)::

    ngspice -b -o run.log -r run.raw circuit.cir

DC values come from the ``Node / Voltage`` block in ``run.log``. AC and
transient arrays come from the ASCII ``run.raw`` file, which keeps both
Vin (node 5) and Vout (node 6) from the *same* solver run.
"""

from __future__ import annotations

import math
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

ENGINE_NAME = "ngspice 47 (batch)"
MODEL_NAME = "2N3904 NPN (standard Gummel-Poon card)"
KNOWN_NGSPICE = (
    r"C:\Users\B6814946\AppData\Local\Programs\ngspice-47"
    r"\Spice64\bin\ngspice.exe"
)
ANALYSES = ("dc", "ac", "tran")

# Pinned BJT card: the same card used to verify .op/.ac/.tran locally.
# Source: standard 2N3904 SPICE model distributed with ngspice examples and
# common device-model libraries; parameters are listed verbatim below.
MODEL_CARD = """.MODEL Q2N3904 NPN(Is=6.734f Xti=3 Eg=1.11 Vaf=74.03 Bf=416.4 Ne=1.259
+ Ise=6.734f Ikf=66.78m Xtb=1.5 Br=.7371 Nc=2 Isc=0 Ikr=0 Rc=1
+ Cjc=3.638p Mjc=.3085 Vjc=.75 Fc=.5 Cje=4.493p Mje=.2593 Vje=.75
+ Tr=239.5n Tf=301.2p Itf=.4 Vtf=4 Xtf=2 Rb=10)"""


class SpiceInputError(ValueError):
    """Form values are unusable; the solver must not be started."""


class SpiceRunError(RuntimeError):
    """Solver missing, failed, timed out, or produced no usable output."""


@dataclass(frozen=True)
class SpiceInputs:
    """All circuit/source values in SI units (ohms, farads, volts, hertz)."""

    vcc: float = 12.0
    r1: float = 100_000.0
    r2: float = 22_000.0
    rc: float = 2_200.0
    re: float = 1_000.0
    rl: float = 10_000.0
    cin_uf: float = 10.0
    cout_uf: float = 10.0
    source_peak_v: float = 0.01
    source_freq_hz: float = 1_000.0
    f_start_hz: float = 10.0
    f_stop_hz: float = 1_000_000.0
    points_per_decade: int = 20
    tran_stop_s: float = 0.003


@dataclass
class ACPoint:
    frequency_hz: float
    vdb: float
    phase_deg: float
    gain_db: float


@dataclass
class TranPoint:
    time_s: float
    vin_v: float
    vout_v: float


@dataclass
class RawData:
    plotname: str
    flags: str
    variables: list[str]
    points: list[list[complex | float]]


@dataclass
class SpiceResult:
    analysis: str
    status: str = "success"
    engine: str = ENGINE_NAME
    model_name: str = MODEL_NAME
    netlist: str = ""
    log_excerpt: str = ""
    nodes: dict[str, float] = field(default_factory=dict)
    ac_points: list[ACPoint] = field(default_factory=list)
    tran_points: list[TranPoint] = field(default_factory=list)
    error: str = ""
    sample_count: int = 0


def validate_inputs(inputs: SpiceInputs) -> None:
    """Reject non-numeric, non-finite, non-positive or out-of-range values."""
    numeric = (
        "vcc", "r1", "r2", "rc", "re", "rl", "cin_uf", "cout_uf",
        "source_peak_v", "source_freq_hz", "f_start_hz", "f_stop_hz",
        "tran_stop_s",
    )
    for name in numeric:
        value = getattr(inputs, name)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise SpiceInputError(f"{name} ต้องเป็นตัวเลข")
        if not math.isfinite(value):
            raise SpiceInputError(f"{name} ต้องเป็นจำนวนจำกัด")
        if value <= 0:
            raise SpiceInputError(f"{name} ต้องมากกว่า 0")
    if not isinstance(inputs.points_per_decade, int) or not (
            1 <= inputs.points_per_decade <= 1000):
        raise SpiceInputError("points_per_decade ต้องอยู่ระหว่าง 1 ถึง 1000")
    if inputs.f_start_hz >= inputs.f_stop_hz:
        raise SpiceInputError("ความถี่เริ่มต้องน้อยกว่าความถี่สิ้นสุด")
    if inputs.source_peak_v > inputs.vcc / 2:
        raise SpiceInputError("Amplitude ต้องน้อยกว่าครึ่งหนึ่งของ VCC")


def _res(value: float) -> str:
    return f"{value:.6g}"


def _freq(value: float) -> str:
    return f"{value:.0f}" if value >= 1e5 else f"{value:g}"


def _time(value: float) -> str:
    if value >= 1e-3:
        return f"{value * 1e3:g}m"
    if value >= 1e-6:
        return f"{value * 1e6:g}u"
    return f"{value * 1e9:g}n"


def build_netlist(inputs: SpiceInputs, analysis: str) -> str:
    """Create the one reference CE netlist with a single analysis directive."""
    if analysis not in ANALYSES:
        raise SpiceInputError("analysis ต้องเป็น dc, ac หรือ tran")
    validate_inputs(inputs)
    peak = f"{inputs.source_peak_v:g}"
    source_hz = f"{inputs.source_freq_hz:g}"
    directive = {
        "dc": ".OP",
        "ac": (f".AC DEC {inputs.points_per_decade} "
               f"{_freq(inputs.f_start_hz)} {_freq(inputs.f_stop_hz)}"),
        "tran": f".TRAN 1u {_time(inputs.tran_stop_s)}",
    }[analysis]
    return "\n".join([
        "* CE voltage-divider reference circuit - Lab 04",
        f"VCC 1 0 DC {_res(inputs.vcc)}",
        f"VIN 5 0 DC 0 AC {peak} SIN(0 {peak} {source_hz})",
        f"R1 1 2 {_res(inputs.r1)}",
        f"R2 2 0 {_res(inputs.r2)}",
        f"RC 1 3 {_res(inputs.rc)}",
        f"RE 4 0 {_res(inputs.re)}",
        "Q1 3 2 4 Q2N3904",
        f"CIN 5 2 {inputs.cin_uf:g}u",
        f"COUT 3 6 {inputs.cout_uf:g}u",
        f"RL 6 0 {_res(inputs.rl)}",
        MODEL_CARD,
        directive,
        ".END",
        "",
    ])


def parse_op_log(log_text: str) -> dict[str, float]:
    """Read the ``Node / Voltage`` table written by ngspice for ``.op``."""
    nodes: dict[str, float] = {}
    in_block = False
    for line in log_text.splitlines():
        if re.match(r"\s*Node\s+Voltage", line, re.I):
            in_block = True
            continue
        if not in_block:
            continue
        match = re.match(r"\s*V\(([\w]+)\)\s+([-+0-9.eE]+)", line)
        if match:
            nodes[f"V({match.group(1)})"] = float(match.group(2))
        elif nodes and line.strip():
            break
    if {"V(3)", "V(4)"} <= nodes.keys():
        nodes["VCE"] = nodes["V(3)"] - nodes["V(4)"]
    return nodes


def nodes_from_raw(raw: RawData) -> dict[str, float]:
    """With ``-r`` ngspice writes the operating point to raw, not the log."""
    values = {}
    for name, row in zip(raw.variables, raw.points[0] if raw.points else []):
        match = re.fullmatch(r"v\(([\w]+)\)", name, re.I)
        if match:
            values[f"V({match.group(1)})"] = float(row)
    if {"V(3)", "V(4)"} <= values.keys():
        values["VCE"] = values["V(3)"] - values["V(4)"]
    return values


def parse_raw(raw_text: str) -> RawData:
    """Parse ngspice's ASCII .raw file (complex AC or real transient)."""
    plotname, flags, variables, values_start = "", "", [], None
    lines = raw_text.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("Plotname:"):
            plotname = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("Flags:"):
            flags = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("Variables:"):
            for follow in lines[index + 1:]:
                if not follow.startswith("\t"):
                    break
                parts = [p for p in follow.split("\t") if p.strip()]
                if len(parts) >= 2:
                    variables.append(parts[1].strip())
        elif stripped == "Values:":
            values_start = index + 1
            break
    if values_start is None or not variables:
        raise SpiceRunError("raw file has no Variables/Values section")
    tokens = []
    for line in lines[values_start:]:
        parts = [p.strip() for p in line.split("\t") if p.strip()]
        if parts:
            tokens.append(parts[-1])
    width = len(variables)
    if not tokens or len(tokens) % width:
        raise SpiceRunError("raw file has incomplete value rows")
    points: list[list[complex | float]] = []
    for start in range(0, len(tokens), width):
        row: list[complex | float] = []
        for token in tokens[start:start + width]:
            if flags == "complex":
                real, _, imag = token.partition(",")
                row.append(complex(float(real), float(imag or 0)))
            else:
                row.append(float(token))
        points.append(row)
    return RawData(plotname=plotname, flags=flags,
                   variables=variables, points=points)


def _index_of(variables: list[str], name: str) -> int:
    wanted = name.lower()
    for index, variable in enumerate(variables):
        if variable.lower() == wanted:
            return index
    raise SpiceRunError(f"raw file is missing node {name}")


def _magnitude_db(value: complex | float) -> float:
    magnitude = abs(value)
    return 20 * math.log10(magnitude) if magnitude > 0 else -400.0


def ac_points_from_raw(raw: RawData) -> list[ACPoint]:
    """Gain = Vout/Vin using both measured nodes, not output dBV alone."""
    if raw.flags != "complex":
        raise SpiceRunError("AC raw data must be complex")
    i_f = _index_of(raw.variables, "frequency")
    i_in = _index_of(raw.variables, "v(5)")
    i_out = _index_of(raw.variables, "v(6)")
    points = []
    for row in raw.points:
        vin, vout = row[i_in], row[i_out]
        phase = math.degrees(
            math.atan2(vout.imag, vout.real) -
            math.atan2(vin.imag, vin.real))
        phase = (phase + 180) % 360 - 180
        points.append(ACPoint(
            frequency_hz=float(row[i_f].real),
            vdb=_magnitude_db(vout),
            phase_deg=phase,
            gain_db=_magnitude_db(vout) - _magnitude_db(vin),
        ))
    return points


def tran_points_from_raw(raw: RawData) -> list[TranPoint]:
    if raw.flags != "real":
        raise SpiceRunError("transient raw data must be real")
    i_t = _index_of(raw.variables, "time")
    i_in = _index_of(raw.variables, "v(5)")
    i_out = _index_of(raw.variables, "v(6)")
    return [TranPoint(float(row[i_t]), float(row[i_in]), float(row[i_out]))
            for row in raw.points]


def cutoff_frequency(points: list[ACPoint]) -> float | None:
    """First descending crossing of (max gain - 3 dB), in Hz, or None."""
    if not points:
        return None
    target = max(p.gain_db for p in points) - 3.0
    for low, high in zip(points, points[1:]):
        if low.gain_db >= target > high.gain_db:
            ratio = (target - low.gain_db) / (high.gain_db - low.gain_db)
            low_f = math.log10(low.frequency_hz)
            high_f = math.log10(high.frequency_hz)
            return 10 ** (low_f + ratio * (high_f - low_f))
    return None


def find_executable() -> str | None:
    return (os.environ.get("NGSPICE_EXE") or shutil.which("ngspice")
            or (KNOWN_NGSPICE if Path(KNOWN_NGSPICE).exists() else None))


def run_analysis(inputs: SpiceInputs, analysis: str, *,
                 exe_path: str | None = None,
                 timeout_s: float = 20.0) -> SpiceResult:
    """Run one real ngspice batch analysis and parse its output."""
    validate_inputs(inputs)
    if analysis not in ANALYSES:
        raise SpiceInputError("analysis ต้องเป็น dc, ac หรือ tran")
    solver = exe_path or find_executable()
    if not solver or not Path(solver).is_file():
        raise SpiceRunError("ไม่พบ ngspice — ตรวจการติดตั้งหรือ NGSPICE_EXE")

    netlist = build_netlist(inputs, analysis)
    run_dir = Path(tempfile.mkdtemp(prefix="bjt_spice_"))
    try:
        circuit = run_dir / "circuit.cir"
        log_path = run_dir / "run.log"
        raw_path = run_dir / "run.raw"
        circuit.write_text(netlist, encoding="utf-8")
        command = [str(solver), "-b", "-o", str(log_path),
                   "-r", str(raw_path), str(circuit)]
        try:
            completed = subprocess.run(
                command, cwd=run_dir, timeout=timeout_s, shell=False,
                capture_output=True, text=True,
            )
        except subprocess.TimeoutExpired as exc:
            raise SpiceRunError(f"ngspice timeout หลัง {timeout_s:g} วินาที") from exc
        except OSError as exc:
            raise SpiceRunError(f"เรียก ngspice ไม่ได้: {exc}") from exc

        log_text = log_path.read_text(encoding="utf-8", errors="replace") \
            if log_path.is_file() else ""
        if completed.returncode != 0:
            raise SpiceRunError(
                f"ngspice exit={completed.returncode}: "
                f"{log_text[-400:] or completed.stderr[-400:]}")
        if not log_text.strip():
            raise SpiceRunError("ngspice ไม่เขียน run.log")
        if re.search(r"^Error:", log_text, re.M):
            raise SpiceRunError("ngspice รายงาน Error ใน run.log")

        result = SpiceResult(analysis=analysis, netlist=netlist,
                             log_excerpt=log_text[-3000:])
        if not raw_path.is_file():
            raise SpiceRunError("ngspice ไม่เขียน run.raw")
        raw = parse_raw(raw_path.read_text(encoding="utf-8",
                                           errors="replace"))
        if not raw.points:
            raise SpiceRunError("run.raw ไม่มีข้อมูล")
        if analysis == "dc":
            result.nodes = nodes_from_raw(raw) or parse_op_log(log_text)
            if not result.nodes:
                raise SpiceRunError("run.raw ไม่มี operating point")
        else:
            if analysis == "ac":
                result.ac_points = ac_points_from_raw(raw)
                result.sample_count = len(result.ac_points)
                if not result.ac_points:
                    raise SpiceRunError("ไม่มีจุด AC จาก solver")
            else:
                result.tran_points = tran_points_from_raw(raw)
                result.sample_count = len(result.tran_points)
                if not result.tran_points:
                    raise SpiceRunError("ไม่มีจุด transient จาก solver")
        return result
    finally:
        shutil.rmtree(run_dir, ignore_errors=True)

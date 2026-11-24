"""Small dependency-free SVG plotters for parsed ngspice arrays.

Every coordinate comes from a value returned by ``spice_engine``; there are
no illustrative traces or constants standing in for simulation results.
"""

from __future__ import annotations

import math

from spice_engine import ACPoint, TranPoint

GAIN_COLOR = "#0c8078"
PHASE_COLOR = "#b85c2c"
VIN_COLOR = "#0c8078"
VOUT_COLOR = "#b85c2c"


def _fmt(value: float) -> str:
    return f"{value:.2f}"


def _downsample(items, limit: int = 600):
    if len(items) <= limit:
        return items
    step = (len(items) - 1) / (limit - 1)
    picked = [items[round(i * step)] for i in range(limit)]
    picked[-1] = items[-1]
    return picked


def _map(value: float, low: float, high: float, pixel_a: float,
         pixel_b: float) -> float:
    if high == low:
        return pixel_a
    return pixel_a + (value - low) / (high - low) * (pixel_b - pixel_a)


def _polyline(series: str, coordinates: list[tuple[float, float]],
              color: str) -> str:
    points = " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in coordinates)
    return (f'<polyline data-series="{series}" points="{points}" '
            f'fill="none" stroke="{color}" stroke-width="2.2" '
            f'stroke-linejoin="round"/>')


def _frame(x_ticks: list[tuple[float, str]], y_ticks: list[tuple[float, str]],
           *, x_px: tuple[float, float], y_px: tuple[float, float],
           x_label: str, y_label: str, right_label: str = "") -> str:
    left, right = x_px
    top, bottom = y_px
    parts = [
        f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" '
        f'y2="{bottom}"/>',
        f'<line class="axis" x1="{left}" y1="{bottom}" x2="{right}" '
        f'y2="{bottom}"/>',
    ]
    for pixel, label in x_ticks:
        parts.append(
            f'<line class="grid" x1="{pixel:.2f}" y1="{top}" '
            f'x2="{pixel:.2f}" y2="{bottom}"/>'
            f'<text class="tick" x="{pixel:.2f}" y="{bottom + 18}" '
            f'text-anchor="middle">{label}</text>')
    for pixel, label in y_ticks:
        parts.append(
            f'<line class="grid" x1="{left}" y1="{pixel:.2f}" '
            f'x2="{right}" y2="{pixel:.2f}"/>'
            f'<text class="tick" x="{left - 8}" y="{pixel + 4:.2f}" '
            f'text-anchor="end">{label}</text>')
    parts.append(
        f'<text class="axis-label" x="{(left + right) / 2:.1f}" '
        f'y="{bottom + 42}" text-anchor="middle">{x_label}</text>')
    parts.append(
        f'<text class="axis-label" transform="translate(16 '
        f'{(top + bottom) / 2:.1f}) rotate(-90)" '
        f'text-anchor="middle">{y_label}</text>')
    if right_label:
        parts.append(
            f'<text class="axis-label" transform="translate(748 '
            f'{(top + bottom) / 2:.1f}) rotate(90)" '
            f'text-anchor="middle">{right_label}</text>')
    return "\n".join(parts)


def ac_chart_svg(points: list[ACPoint]) -> str:
    """Bode gain and phase from the solver's AC sweep."""
    if not points:
        return '<svg class="plot" viewBox="0 0 760 330"></svg>'
    shown = _downsample(points)
    left, right, top, bottom = 64.0, 716.0, 28.0, 274.0
    freqs = [p.frequency_hz for p in shown]
    log_min = math.log10(min(freqs))
    log_max = math.log10(max(freqs))
    if log_max == log_min:
        log_max = log_min + 1
    gains = [p.gain_db for p in shown]
    gain_min = math.floor(min(min(gains), 0) / 10) * 10
    gain_max = math.ceil(max(max(gains), 10) / 10) * 10

    gain_line = []
    phase_line = []
    for point in shown:
        x = _map(math.log10(point.frequency_hz), log_min, log_max, left, right)
        gain_line.append(
            (x, _map(point.gain_db, gain_min, gain_max, bottom, top)))
        phase_line.append(
            (x, _map(point.phase_deg, -180, 180, bottom, top)))

    decade_start = math.ceil(log_min)
    decade_end = math.floor(log_max)
    x_ticks = []
    for decade in range(decade_start, decade_end + 1):
        px = _map(decade, log_min, log_max, left, right)
        x_ticks.append((px, f"1e{decade}"))
    y_ticks = [
        (_map(value, gain_min, gain_max, bottom, top), str(value))
        for value in range(gain_min, gain_max + 1, 10)
    ]
    return "\n".join([
        '<svg class="plot" viewBox="0 0 760 330" role="img" '
        'aria-label="Bode plot computed from ngspice AC analysis">',
        f'<text class="plot-title" x="{left}" y="18">'
        'Bode response — real ngspice .ac run</text>',
        _frame(x_ticks, y_ticks,
               x_px=(left, right), y_px=(top, bottom),
               x_label="Frequency (Hz)", y_label="Gain (dB)",
               right_label="Phase (°)"),
        _polyline("gain", gain_line, GAIN_COLOR),
        _polyline("phase", phase_line, PHASE_COLOR),
        f'<text class="legend" x="{left + 10}" y="{top + 14}" '
        f'fill="{GAIN_COLOR}">— Gain (dB)</text>',
        f'<text class="legend" x="{left + 130}" y="{top + 14}" '
        f'fill="{PHASE_COLOR}">— Phase (°)</text>',
        f'<text class="plot-note" x="{left}" y="320">'
        f'{len(points)} solver points · Vin = node 5, Vout = node 6'
        f'</text>',
        "</svg>",
    ])


def tran_chart_svg(points: list[TranPoint]) -> str:
    """Vin and Vout versus time from the solver's transient run."""
    if not points:
        return '<svg class="plot" viewBox="0 0 760 300"></svg>'
    shown = _downsample(points)
    left, right, top, bottom = 64.0, 736.0, 28.0, 244.0
    times_ms = [p.time_s * 1e3 for p in shown]
    t_min, t_max = min(times_ms), max(times_ms)
    if t_max == t_min:
        t_max = t_min + 1
    voltages = [p.vin_v for p in shown] + [p.vout_v for p in shown]
    span = max(max(voltages) - min(voltages), 1e-3)
    v_min = min(voltages) - span * 0.1
    v_max = max(voltages) + span * 0.1

    vin_line, vout_line = [], []
    for point in shown:
        x = _map(point.time_s * 1e3, t_min, t_max, left, right)
        vin_line.append((x, _map(point.vin_v, v_min, v_max, bottom, top)))
        vout_line.append((x, _map(point.vout_v, v_min, v_max, bottom, top)))

    x_ticks = [
        (_map(value, t_min, t_max, left, right), f"{value:.2f}")
        for value in (t_min, (t_min + t_max) / 2, t_max)
    ]
    y_ticks = [
        (_map(value, v_min, v_max, bottom, top), f"{value:.3f}")
        for value in (v_min, (v_min + v_max) / 2, v_max)
    ]
    return "\n".join([
        '<svg class="plot" viewBox="0 0 760 300" role="img" '
        'aria-label="Vin and Vout waveforms from ngspice transient analysis">',
        f'<text class="plot-title" x="{left}" y="18">'
        'Input / Output waveforms — real ngspice .tran run</text>',
        _frame(x_ticks, y_ticks, x_px=(left, right), y_px=(top, bottom),
               x_label="Time (ms)", y_label="Voltage (V)"),
        _polyline("vin", vin_line, VIN_COLOR),
        _polyline("vout", vout_line, VOUT_COLOR),
        f'<text class="legend" x="{left + 10}" y="{top + 14}" '
        f'fill="{VIN_COLOR}">— Vin (V)</text>',
        f'<text class="legend" x="{left + 110}" y="{top + 14}" '
        f'fill="{VOUT_COLOR}">— Vout (V)</text>',
        f'<text class="plot-note" x="{left}" y="290">'
        f'{len(points)} solver points · 180° inversion expected for CE'
        f'</text>',
        "</svg>",
    ])

"""TDD tests for the real ngspice adapter (Lab 04).

The hand-written fixtures below are deliberately tiny copies of the ASCII
format ngspice 47 writes to ``.raw`` and ``-o run.log``. The integration test
at the bottom runs the installed solver and checks real output values.
"""

import math
import os
import shutil
import unittest
from pathlib import Path

import spice_engine as se

KNOWN_NGSPICE = (
    r"C:\Users\B6814946\AppData\Local\Programs\ngspice-47"
    r"\Spice64\bin\ngspice.exe"
)

AC_RAW_FIXTURE = """Title: hand-checked fixture
Date: test
Command: ngspice-47
Plotname: AC Analysis
Flags: complex
No. Variables: 3
No. Points: 2
Variables:
\t0\tfrequency\tfrequency\tgrid=3
\t1\tv(5)\tvoltage
\t2\tv(6)\tvoltage
Values:
0\t\t1.000000000000000e+01,0.000000000000000e+00
\t1.000000000000000e-02,0.000000000000000e+00
\t-1.000000000000000e-02,0.000000000000000e+00
1\t\t1.000000000000000e+03,0.000000000000000e+00
\t1.000000000000000e-02,0.000000000000000e+00
\t1.800000000000000e-02,0.000000000000000e+00
"""

TRAN_RAW_FIXTURE = """Title: hand-checked fixture
Plotname: Transient Analysis
Flags: real
No. Variables: 3
No. Points: 3
Variables:
\t0\ttime\ttime
\t1\tv(5)\tvoltage
\t2\tv(6)\tvoltage
Values:
0\t\t0.000000000000000e+00
\t0.000000000000000e+00
\t0.000000000000000e+00
1\t\t1.000000000000000e-04
\t1.000000000000000e-02
\t-1.800000000000000e-02
2\t\t2.000000000000000e-04
\t0.000000000000000e+00
\t0.000000000000000e+00
"""

OP_LOG_FIXTURE = """Note: No compatibility mode selected!

Circuit: * ce voltage-divider reference circuit

Node                                  Voltage
V(6)                             0.000000e+00
V(4)                             1.332880e+00
V(3)                             9.087216e+00
V(2)                             2.003674e+00
V(5)                             0.000000e+00
V(1)                             1.200000e+01
"""


def solver_path():
    return (os.environ.get("NGSPICE_EXE") or shutil.which("ngspice")
            or (KNOWN_NGSPICE if Path(KNOWN_NGSPICE).exists() else None))


class ValidationTests(unittest.TestCase):
    def test_rejects_zero_resistance_before_netlist_is_written(self):
        with self.assertRaises(se.SpiceInputError):
            se.validate_inputs(se.SpiceInputs(re=0.0))

    def test_rejects_non_finite_source_amplitude(self):
        with self.assertRaises(se.SpiceInputError):
            se.validate_inputs(se.SpiceInputs(source_peak_v=math.nan))

    def test_rejects_reversed_ac_sweep(self):
        with self.assertRaises(se.SpiceInputError):
            se.validate_inputs(
                se.SpiceInputs(f_start_hz=1e6, f_stop_hz=10.0))


class NetlistTests(unittest.TestCase):
    def test_dc_netlist_uses_ohms_and_has_op_directive(self):
        netlist = se.build_netlist(se.SpiceInputs(), "dc")
        self.assertIn(".OP", netlist)
        self.assertIn("R1 1 2 100000", netlist)
        self.assertIn("RE 4 0 1000", netlist)
        self.assertNotIn(".AC", netlist)
        self.assertNotIn(".TRAN", netlist)

    def test_ac_netlist_carries_sweep_and_source(self):
        netlist = se.build_netlist(se.SpiceInputs(), "ac")
        self.assertIn(".AC DEC 20 10 1000000", netlist)
        self.assertIn("VIN 5 0 DC 0 AC 0.01 SIN(0 0.01 1000)", netlist)

    def test_tran_netlist_scales_time_to_milliseconds(self):
        netlist = se.build_netlist(se.SpiceInputs(), "tran")
        self.assertIn(".TRAN 1u 3m", netlist)

    def test_coupling_capacitors_and_load_are_present(self):
        netlist = se.build_netlist(se.SpiceInputs(), "ac")
        self.assertIn("CIN 5 2 10u", netlist)
        self.assertIn("COUT 3 6 10u", netlist)
        self.assertIn("RL 6 0 10000", netlist)
        self.assertNotIn("CE 4 0", netlist)  # baseline has no emitter bypass


class ParserTests(unittest.TestCase):
    def test_parse_op_log_reads_node_block(self):
        nodes = se.parse_op_log(OP_LOG_FIXTURE)
        self.assertAlmostEqual(nodes["V(3)"], 9.087216)
        self.assertAlmostEqual(nodes["V(4)"], 1.332880)
        self.assertAlmostEqual(nodes["VCE"], 7.754336, places=5)

    def test_parse_raw_keeps_complex_ac_values(self):
        raw = se.parse_raw(AC_RAW_FIXTURE)
        self.assertEqual(raw.plotname, "AC Analysis")
        self.assertEqual(raw.variables, ["frequency", "v(5)", "v(6)"])
        self.assertAlmostEqual(raw.points[0][0].real, 10.0)
        self.assertAlmostEqual(raw.points[1][2].real, 0.018)

    def test_parse_raw_keeps_real_transient_values(self):
        raw = se.parse_raw(TRAN_RAW_FIXTURE)
        self.assertEqual(raw.flags, "real")
        self.assertEqual(len(raw.points), 3)
        self.assertAlmostEqual(raw.points[1][2], -0.018)

    def test_operating_point_nodes_come_from_raw_when_r_is_used(self):
        raw_text = """Title: hand-checked fixture
Plotname: Operating Point
Flags: real
No. Variables: 5
No. Points: 1
Variables:
\t0\tv(1)\tvoltage
\t1\tv(5)\tvoltage
\t2\tv(2)\tvoltage
\t3\tv(3)\tvoltage
\t4\tv(4)\tvoltage
Values:
0\t\t1.200000000000000e+01
\t0.000000000000000e+00
\t2.003674000000000e+00
\t9.087216000000000e+00
\t1.332880000000000e+00
"""
        nodes = se.nodes_from_raw(se.parse_raw(raw_text))
        self.assertAlmostEqual(nodes["V(2)"], 2.003674)
        self.assertAlmostEqual(nodes["VCE"], 7.754336, places=5)

    def test_ac_points_compute_gain_and_phase_from_both_nodes(self):
        raw = se.parse_raw(AC_RAW_FIXTURE)
        points = se.ac_points_from_raw(raw)
        self.assertAlmostEqual(points[0].gain_db, 0.0)  # |-0.01 / 0.01|
        self.assertAlmostEqual(abs(points[0].phase_deg), 180.0)
        self.assertAlmostEqual(points[1].gain_db,
                               20 * math.log10(0.018 / 0.01), places=4)

    def test_cutoff_interpolates_between_samples_in_log_frequency(self):
        points = [
            se.ACPoint(f, 0, 0, gain) for f, gain in (
                (10, 0), (100, 3), (1000, 6), (10000, 6), (100000, 5),
                (1e6, 2))
        ]
        cutoff = se.cutoff_frequency(points)
        self.assertIsNotNone(cutoff)
        self.assertAlmostEqual(cutoff, 1e5 * 10 ** (2 / 3), delta=1)

    def test_cutoff_returns_none_when_sweep_never_crosses_minus_3db(self):
        points = [se.ACPoint(f, 0, 0, 8.0) for f in (10, 100, 1000)]
        self.assertIsNone(se.cutoff_frequency(points))


@unittest.skipUnless(solver_path(), "ngspice executable not installed")
class RealSolverTests(unittest.TestCase):
    def test_real_dc_run_returns_node_voltages_from_solver(self):
        result = se.run_analysis(se.SpiceInputs(), "dc",
                                 exe_path=solver_path())
        self.assertEqual(result.status, "success")
        self.assertAlmostEqual(result.nodes["VCE"], 7.754336, delta=0.25)
        self.assertIn("2N3904", result.model_name)
        self.assertTrue(result.log_excerpt)

    def test_real_ac_run_returns_frequency_gain_phase(self):
        result = se.run_analysis(se.SpiceInputs(), "ac",
                                 exe_path=solver_path())
        self.assertEqual(result.status, "success")
        self.assertGreater(len(result.ac_points), 50)
        self.assertTrue(any(p.gain_db > 0 for p in result.ac_points))
        self.assertTrue(all(math.isfinite(p.phase_deg)
                            for p in result.ac_points))

    def test_real_tran_run_shows_inverted_output(self):
        result = se.run_analysis(se.SpiceInputs(), "tran",
                                 exe_path=solver_path())
        self.assertEqual(result.status, "success")
        self.assertGreater(len(result.tran_points), 100)
        vin = [p.vin_v for p in result.tran_points]
        vout = [p.vout_v for p in result.tran_points]
        self.assertLess(sum(a * b for a, b in zip(vin, vout)), 0)
        self.assertAlmostEqual(max(vin), 0.01, delta=0.002)

    def test_missing_executable_raises_run_error(self):
        with self.assertRaises(se.SpiceRunError):
            se.run_analysis(se.SpiceInputs(), "dc",
                            exe_path=r"C:\definitely\missing\ngspice.exe")

    def test_changing_source_amplitude_changes_real_waveform(self):
        quiet = se.run_analysis(se.SpiceInputs(), "tran",
                                exe_path=solver_path())
        loud = se.run_analysis(
            se.SpiceInputs(source_peak_v=0.02), "tran",
            exe_path=solver_path())
        self.assertAlmostEqual(max(p.vin_v for p in loud.tran_points),
                               2 * max(p.vin_v for p in quiet.tran_points),
                               delta=5e-5)


if __name__ == "__main__":
    unittest.main()

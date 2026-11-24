"""The SVG plots must be driven by parsed solver points, not constants."""

import unittest

from plots import ac_chart_svg, tran_chart_svg
from spice_engine import ACPoint, TranPoint


class PlotTests(unittest.TestCase):
    def test_ac_chart_labels_frequency_gain_and_phase(self):
        points = [
            ACPoint(10, -35, -170, 0.5),
            ACPoint(1000, -34, -177, 5.0),
            ACPoint(1000000, -40, 2, -1.0),
        ]
        svg = ac_chart_svg(points)
        self.assertIn("Frequency (Hz)", svg)
        self.assertIn("Gain (dB)", svg)
        self.assertIn("Phase (°)", svg)
        self.assertIn('data-series="gain"', svg)
        self.assertIn('data-series="phase"', svg)

    def test_ac_chart_coordinates_change_with_gain_data(self):
        low = [ACPoint(10, -35, 0, 1), ACPoint(1000, -35, 0, 2)]
        high = [ACPoint(10, -35, 0, 1), ACPoint(1000, -35, 0, 25)]
        self.assertNotEqual(ac_chart_svg(low), ac_chart_svg(high))

    def test_tran_chart_labels_time_and_voltage(self):
        points = [
            TranPoint(0.0, 0.0, 0.0),
            TranPoint(0.001, 0.01, -0.018),
            TranPoint(0.002, 0.0, 0.0),
        ]
        svg = tran_chart_svg(points)
        self.assertIn("Time (ms)", svg)
        self.assertIn("Vin (V)", svg)
        self.assertIn("Vout (V)", svg)
        self.assertIn('data-series="vin"', svg)
        self.assertIn('data-series="vout"', svg)

    def test_tran_chart_coordinates_change_with_source_amplitude(self):
        quiet = [TranPoint(0, 0, 0), TranPoint(0.001, 0.01, -0.018)]
        loud = [TranPoint(0, 0, 0), TranPoint(0.001, 0.02, -0.036)]
        self.assertNotEqual(tran_chart_svg(quiet), tran_chart_svg(loud))


if __name__ == "__main__":
    unittest.main()

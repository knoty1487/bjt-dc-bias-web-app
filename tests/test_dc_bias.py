"""Unit tests for the engineering model (dc_bias.py).

Reference example from the Lab 02 handout:
  VCC = 12 V, R1 = 100 kΩ, R2 = 22 kΩ, RC = 2.2 kΩ, RE = 1 kΩ,
  beta = 100, VBE = 0.70 V
"""

import unittest

from dc_bias import (
    REGION_ACTIVE,
    REGION_CUTOFF,
    REGION_SATURATION,
    InvalidInputError,
    calculate_dc_bias,
)

VCC = 12.0
R1 = 100_000.0
R2 = 22_000.0
RC = 2_200.0
RE = 1_000.0
BETA = 100.0
VBE = 0.70


class ReferenceExampleTest(unittest.TestCase):
    def setUp(self):
        self.result = calculate_dc_bias(VCC, R1, R2, RC, RE, BETA, VBE)

    def test_thevenin_equivalent(self):
        self.assertAlmostEqual(self.result.vth, 2.16393, places=3)
        self.assertAlmostEqual(self.result.rth, 18032.787, places=1)

    def test_currents_match_hand_calculation(self):
        self.assertAlmostEqual(self.result.ib * 1e6, 12.2986, places=2)
        self.assertAlmostEqual(self.result.ic * 1e3, 1.22986, places=3)
        self.assertAlmostEqual(self.result.ie * 1e3, 1.24216, places=3)

    def test_voltages_match_hand_calculation(self):
        self.assertAlmostEqual(self.result.ve, 1.24216, places=3)
        self.assertAlmostEqual(self.result.vb, 1.94216, places=3)
        self.assertAlmostEqual(self.result.vc, 9.29431, places=3)
        self.assertAlmostEqual(self.result.vce, 8.05216, places=3)

    def test_stays_in_forward_active_region(self):
        self.assertEqual(self.result.region, REGION_ACTIVE)
        self.assertEqual(self.result.warnings, [])


class ValidationTest(unittest.TestCase):
    def test_zero_resistance_rejected(self):
        with self.assertRaises(InvalidInputError):
            calculate_dc_bias(VCC, 0.0, R2, RC, RE, BETA, VBE)

    def test_non_positive_beta_rejected(self):
        with self.assertRaises(InvalidInputError):
            calculate_dc_bias(VCC, R1, R2, RC, RE, 0.0, VBE)

    def test_non_positive_vcc_rejected(self):
        with self.assertRaises(InvalidInputError):
            calculate_dc_bias(0.0, R1, R2, RC, RE, BETA, VBE)

    def test_vbe_outside_range_rejected(self):
        with self.assertRaises(InvalidInputError):
            calculate_dc_bias(VCC, R1, R2, RC, RE, BETA, VCC)


class OperatingRegionTest(unittest.TestCase):
    def test_cutoff_when_vth_below_vbe(self):
        result = calculate_dc_bias(12.0, 100_000.0, 5_000.0, 2_200.0, 1_000.0, 100.0, 0.70)
        self.assertEqual(result.region, REGION_CUTOFF)
        self.assertGreater(len(result.warnings), 0)
        self.assertAlmostEqual(result.ic, 0.0)
        self.assertAlmostEqual(result.vce, 12.0)

    def test_saturation_flagged(self):
        result = calculate_dc_bias(12.0, 100_000.0, 100_000.0, 10_000.0, 1_000.0, 100.0, 0.70)
        self.assertEqual(result.region, REGION_SATURATION)
        self.assertGreater(len(result.warnings), 0)
        self.assertLessEqual(result.vce, 0.2)


if __name__ == "__main__":
    unittest.main()

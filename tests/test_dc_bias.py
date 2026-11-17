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
    VCE_SAT,
    InvalidInputError,
    calculate_dc_bias,
    calculate_emitter_bias,
    calculate_fixed_bias,
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


class NewBiasModesTest(unittest.TestCase):
    """Lab 03: independent hand calculations for fixed and emitter bias."""

    def test_fixed_bias_reference(self):
        result = calculate_fixed_bias(12.0, 1e6, 2.2e3, 100.0, 0.70)
        self.assertAlmostEqual(result.ib * 1e6, 11.30, places=2)
        self.assertAlmostEqual(result.ic * 1e3, 1.13, places=3)
        self.assertAlmostEqual(result.ve, 0.0)
        self.assertAlmostEqual(result.vb, 0.70)
        self.assertAlmostEqual(result.vc, 9.514, places=3)
        self.assertAlmostEqual(result.vce, 9.514, places=3)
        self.assertEqual(result.region, REGION_ACTIVE)
        self.assertIsNone(result.vth)

    def test_emitter_bias_reference(self):
        result = calculate_emitter_bias(12.0, 1e6, 1e3, 2.2e3, 100.0, 0.70)
        self.assertAlmostEqual(result.ib * 1e6, 10.2634, places=3)
        self.assertAlmostEqual(result.ic * 1e3, 1.02634, places=4)
        self.assertAlmostEqual(result.ie * 1e3, 1.03660, places=4)
        self.assertAlmostEqual(result.ve, 1.03660, places=4)
        self.assertAlmostEqual(result.vb, 1.73660, places=4)
        self.assertAlmostEqual(result.vc, 9.74205, places=4)
        self.assertAlmostEqual(result.vce, 8.70545, places=4)
        self.assertEqual(result.region, REGION_ACTIVE)

    def test_larger_emitter_resistor_reduces_ic(self):
        small = calculate_emitter_bias(12.0, 1e6, 1e3, 2.2e3, 100.0, 0.70)
        large = calculate_emitter_bias(12.0, 1e6, 2e3, 2.2e3, 100.0, 0.70)
        self.assertAlmostEqual(large.ic * 1e3, 0.94010, places=4)
        self.assertAlmostEqual(large.vce, 8.03278, places=4)
        self.assertLess(large.ic, small.ic)

    def test_fixed_bias_rejects_zero_rb(self):
        with self.assertRaises(InvalidInputError):
            calculate_fixed_bias(12.0, 0.0, 2.2e3, 100.0, 0.70)

    def test_emitter_bias_rejects_zero_re(self):
        with self.assertRaises(InvalidInputError):
            calculate_emitter_bias(12.0, 1e6, 0.0, 2.2e3, 100.0, 0.70)

    def test_cutoff_when_vcc_not_above_vbe(self):
        result = calculate_fixed_bias(0.60, 1e6, 2.2e3, 100.0, 0.70)
        self.assertEqual(result.region, REGION_CUTOFF)
        self.assertAlmostEqual(result.ic, 0.0)
        self.assertGreater(len(result.warnings), 0)

    def test_saturation_flagged_for_small_rc(self):
        result = calculate_fixed_bias(12.0, 10e3, 100e3, 100.0, 0.70)
        self.assertEqual(result.region, REGION_SATURATION)
        self.assertLessEqual(result.vce, VCE_SAT)


if __name__ == "__main__":
    unittest.main()

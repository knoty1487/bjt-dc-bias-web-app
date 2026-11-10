"""HTTP tests for the Flask application using the Flask test client."""

import unittest

from app import app
from dc_bias import calculate_dc_bias

FORM_DATA = {
    "vcc": "12",
    "r1": "100",
    "unit_r1": "kohm",
    "r2": "22",
    "unit_r2": "kohm",
    "rc": "2.2",
    "unit_rc": "kohm",
    "re": "1",
    "unit_re": "kohm",
    "beta": "100",
    "vbe": "0.7",
}


class WebAppTest(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_index_shows_input_form(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Calculate DC Bias", html)
        self.assertIn('action="/calculate"', html)
        self.assertIn('method="post"', html)

    def test_calculate_returns_backend_result(self):
        response = self.client.post("/calculate", data=FORM_DATA)
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)

        expected = calculate_dc_bias(12.0, 100e3, 22e3, 2.2e3, 1e3, 100.0, 0.70)
        self.assertIn(f"{expected.vce:.3f}", html)
        self.assertIn(f"{expected.ic * 1000:.3f}", html)
        self.assertIn("Forward Active", html)

    def test_unit_selection_is_converted(self):
        # 0.1 MΩ is not supported, but 100 kΩ must behave like 100000 Ω.
        ohm_data = dict(FORM_DATA, r1="100000", unit_r1="ohm")
        response = self.client.post("/calculate", data=ohm_data)
        html = response.get_data(as_text=True)
        expected = calculate_dc_bias(12.0, 100e3, 22e3, 2.2e3, 1e3, 100.0, 0.70)
        self.assertIn(f"{expected.vce:.3f}", html)

    def test_results_are_not_hardcoded(self):
        other_data = {
            "vcc": "9",
            "r1": "47",
            "unit_r1": "kohm",
            "r2": "10",
            "unit_r2": "kohm",
            "rc": "1",
            "unit_rc": "kohm",
            "re": "0.47",
            "unit_re": "kohm",
            "beta": "150",
            "vbe": "0.7",
        }
        response = self.client.post("/calculate", data=other_data)
        html = response.get_data(as_text=True)

        expected = calculate_dc_bias(9.0, 47e3, 10e3, 1e3, 470.0, 150.0, 0.70)
        reference = calculate_dc_bias(12.0, 100e3, 22e3, 2.2e3, 1e3, 100.0, 0.70)
        self.assertIn(f"{expected.vce:.3f}", html)
        self.assertNotEqual(f"{expected.vce:.3f}", f"{reference.vce:.3f}")

    def test_non_numeric_input_shows_error(self):
        response = self.client.post("/calculate", data=dict(FORM_DATA, vcc="abc"))
        self.assertEqual(response.status_code, 400)
        self.assertIn("ต้องเป็นตัวเลข", response.get_data(as_text=True))

    def test_zero_resistance_shows_error(self):
        response = self.client.post("/calculate", data=dict(FORM_DATA, r1="0"))
        self.assertEqual(response.status_code, 400)
        self.assertIn("มากกว่า 0", response.get_data(as_text=True))

    def test_missing_field_shows_error(self):
        data = dict(FORM_DATA)
        del data["beta"]
        response = self.client.post("/calculate", data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("กรุณากรอกค่า", response.get_data(as_text=True))

    def test_cutoff_warning_is_shown(self):
        data = dict(FORM_DATA, r2="5")
        response = self.client.post("/calculate", data=data)
        html = response.get_data(as_text=True)
        self.assertIn("Cutoff", html)
        self.assertIn("ใช้ไม่ได้", html)


if __name__ == "__main__":
    unittest.main()

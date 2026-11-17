import re
import unittest

from app import app

VALID = {"vcc": "12", "r1": "100", "r2": "22", "rc": "2.2", "re": "1",
         "beta": "100", "vbe": "0.7", "unit": "kilo"}


class WebTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_index_returns_form(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="vcc"', response.data)
        self.assertIn(b'name="unit"', response.data)

    def test_calculate_renders_results(self):
        response = self.client.post("/calculate", data=VALID)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"1.230", response.data)
        self.assertIn(b"8.052", response.data)
        self.assertIn("Active".encode(), response.data)

    def test_invalid_input_shows_error_not_crash(self):
        response = self.client.post("/calculate", data={**VALID, "r1": "0"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("ต้องมากกว่า 0".encode(), response.data)

    def test_missing_form_data_shows_error(self):
        response = self.client.post("/calculate", data={})
        self.assertEqual(response.status_code, 200)
        self.assertIn("กรุณากรอก".encode(), response.data)

    def test_non_numeric_input_shows_error(self):
        response = self.client.post("/calculate", data={**VALID, "vcc": "abc"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("ตัวเลข".encode(), response.data)

    def test_comma_separated_input_shows_error(self):
        response = self.client.post("/calculate", data={**VALID, "r1": "1,000"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("ตัวเลข".encode(), response.data)


    def test_page_links_stylesheet(self):
        response = self.client.get("/")
        self.assertIn(b"style.css", response.data)

    def test_results_show_units_and_warning(self):
        response = self.client.post("/calculate", data={**VALID, "re": "0.1"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'class="region-banner"', response.data)
        self.assertIn(b'class="warning"', response.data)
        self.assertIn("Saturation".encode(), response.data)
        self.assertIn(b"mA", response.data)

    def test_active_region_shows_banner_with_reason(self):
        response = self.client.post("/calculate", data=VALID)
        self.assertIn(b'class="region-banner"', response.data)
        self.assertIn(b'data-region="active"', response.data)
        self.assertIn(b"Active region approximation OK", response.data)
        self.assertIn(b"8.052", response.data)


    def test_ohm_unit_is_honoured(self):
        response = self.client.post("/calculate", data={
            "vcc": "12", "r1": "100000", "r2": "22000", "rc": "2200",
            "re": "1000", "beta": "100", "vbe": "0.7", "unit": "ohm",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"1.230", response.data)
        self.assertIn(b"8.052", response.data)
        self.assertIn("Active".encode(), response.data)

    def test_nan_input_shows_error(self):
        response = self.client.post("/calculate", data={**VALID, "vcc": "nan"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("จำนวนจำกัด".encode(), response.data)

    def test_overflow_exponent_shows_error(self):
        response = self.client.post("/calculate", data={**VALID, "vcc": "1e400"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("จำนวนจำกัด".encode(), response.data)


    def test_page_has_header_and_goal_strip(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'class="site-header"', response.data)
        self.assertIn(b'class="goal-strip"', response.data)


    def test_circuit_svg_uses_form_values(self):
        response = self.client.post("/calculate", data={**VALID, "r1": "47", "rc": "3.3"})
        self.assertIn(b"<svg", response.data)
        self.assertIn(b'id="c-r1"', response.data)
        self.assertIn("47 kΩ".encode(), response.data)
        self.assertIn("3.3 kΩ".encode(), response.data)

    def test_page_loads_live_label_script(self):
        response = self.client.get("/")
        self.assertIn(b"app.js", response.data)


    def test_stylesheet_guards_long_numbers(self):
        from pathlib import Path
        css = Path("static/style.css").read_text(encoding="utf-8")
        self.assertIn("overflow-wrap: anywhere", css)


class ModeWebTests(unittest.TestCase):
    """Lab 03: the form must switch between the three bias modes."""

    def setUp(self):
        self.client = app.test_client()

    def _button(self, html, value):
        return next(
            tag for tag in re.findall(r"<button\b[^>]*>", html)
            if f'value="{value}"' in tag
        )

    def test_index_has_mode_selector(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="mode"', response.data)
        for mode in (b"divider", b"fixed", b"emitter"):
            self.assertIn(mode, response.data)

    def test_change_mode_button_skips_required_validation(self):
        html = self.client.get("/").get_data(as_text=True)
        button = self._button(html, "change_mode")
        self.assertIn("formnovalidate", button)

    def test_change_mode_fixed_shows_rb_and_hides_r1(self):
        response = self.client.post(
            "/calculate", data={"mode": "fixed", "action": "change_mode"})
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('name="rb"', html)
        self.assertNotIn('name="r1"', html)
        self.assertNotIn('name="r2"', html)
        self.assertNotIn('name="re"', html)
        self.assertNotIn('class="region-banner"', html)

    def test_change_mode_emitter_shows_rb_and_re(self):
        response = self.client.post(
            "/calculate", data={"mode": "emitter", "action": "change_mode"})
        html = response.get_data(as_text=True)
        self.assertIn('name="rb"', html)
        self.assertIn('name="re"', html)
        self.assertNotIn('name="r1"', html)

    def test_fixed_mode_calculates_from_backend(self):
        data = {"mode": "fixed", "action": "calculate", "vcc": "12",
                "rb": "1000", "rc": "2.2", "beta": "100", "vbe": "0.7",
                "unit": "kilo"}
        response = self.client.post("/calculate", data=data)
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("1.130", html)
        self.assertIn("9.514", html)
        self.assertIn('data-region="active"', html)

    def test_emitter_mode_calculates_from_backend(self):
        data = {"mode": "emitter", "action": "calculate", "vcc": "12",
                "rb": "1000", "re": "1", "rc": "2.2", "beta": "100",
                "vbe": "0.7", "unit": "kilo"}
        response = self.client.post("/calculate", data=data)
        html = response.get_data(as_text=True)
        self.assertIn("1.026", html)
        self.assertIn("8.705", html)

    def test_emitter_re_2k_reduces_ic(self):
        data = {"mode": "emitter", "action": "calculate", "vcc": "12",
                "rb": "1000", "re": "2", "rc": "2.2", "beta": "100",
                "vbe": "0.7", "unit": "kilo"}
        html = self.client.post("/calculate", data=data).get_data(as_text=True)
        self.assertIn("0.940", html)
        self.assertIn("8.033", html)

    def test_fixed_zero_rb_shows_error_without_stale_result(self):
        data = {"mode": "fixed", "action": "calculate", "vcc": "12",
                "rb": "0", "rc": "2.2", "beta": "100", "vbe": "0.7",
                "unit": "kilo"}
        html = self.client.post("/calculate", data=data).get_data(as_text=True)
        self.assertIn("ต้องมากกว่า 0", html)
        self.assertNotIn('class="region-banner"', html)

    def test_unknown_mode_is_rejected(self):
        data = {"mode": "weird", "action": "calculate", "vcc": "12",
                "rc": "2.2", "beta": "100", "vbe": "0.7", "unit": "kilo"}
        html = self.client.post("/calculate", data=data).get_data(as_text=True)
        self.assertIn("โหมด", html)
        self.assertNotIn('class="region-banner"', html)

    def test_ohm_unit_still_converts_for_fixed_mode(self):
        data = {"mode": "fixed", "action": "calculate", "vcc": "12",
                "rb": "1000000", "rc": "2200", "beta": "100", "vbe": "0.7",
                "unit": "ohm"}
        html = self.client.post("/calculate", data=data).get_data(as_text=True)
        self.assertIn("1.130", html)
        self.assertIn("9.514", html)


if __name__ == "__main__":
    unittest.main()

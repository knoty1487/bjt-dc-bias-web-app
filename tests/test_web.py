import re
import unittest
from pathlib import Path

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

    def test_fixed_mode_has_circuit_diagram(self):
        html = self.client.post(
            "/calculate", data={"mode": "fixed", "action": "change_mode"}
        ).get_data(as_text=True)
        self.assertIn("<svg", html)
        self.assertIn('id="c-rb"', html)
        self.assertIn('id="c-rc"', html)
        self.assertNotIn('id="c-r1"', html)
        self.assertNotIn('id="c-re"', html)

    def test_emitter_mode_has_circuit_diagram(self):
        html = self.client.post(
            "/calculate", data={"mode": "emitter", "action": "change_mode"}
        ).get_data(as_text=True)
        self.assertIn("<svg", html)
        self.assertIn('id="c-rb"', html)
        self.assertIn('id="c-re"', html)
        self.assertIn('id="c-rc"', html)
        self.assertNotIn('id="c-r1"', html)

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


SPICE_BASE = {
    "analysis": "dc", "action": "calculate", "mode": "divider",
    "vcc": "12", "r1": "100", "r2": "22", "rc": "2.2", "re": "1",
    "unit": "kilo", "rl": "10", "cin": "10", "cout": "10",
    "vin_mv": "10", "freq_khz": "1", "f_start_hz": "10",
    "f_stop_hz": "1000000", "beta": "100", "vbe": "0.7",
}


class SpiceWebTests(unittest.TestCase):
    """Lab 04: real ngspice dispatch and no stale plots on failure."""

    def setUp(self):
        self.client = app.test_client()

    def test_index_offers_analysis_modes_and_engine_label(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn('name="analysis"', html)
        for mode in ('value="dc"', 'value="ac"', 'value="tran"'):
            self.assertIn(mode, html)
        self.assertIn("ngspice", html)

    def test_spice_dc_shows_solver_values_model_and_provenance(self):
        html = self.client.post("/calculate", data=SPICE_BASE).get_data(
            as_text=True)
        self.assertIn("7.75", html)
        self.assertIn("2N3904", html)
        self.assertIn('data-status="success"', html)
        self.assertIn("Analytical reference", html)

    def test_invalid_re_shows_error_and_no_success_plot(self):
        html = self.client.post(
            "/calculate", data={**SPICE_BASE, "re": "0"}).get_data(
                as_text=True)
        self.assertIn("ต้องมากกว่า 0", html)
        self.assertIn('data-status="error"', html)
        self.assertNotIn('data-series="gain"', html)
        self.assertNotIn('data-series="vin"', html)

    def test_spice_ac_chart_has_frequency_gain_phase_units(self):
        html = self.client.post(
            "/calculate", data={**SPICE_BASE, "analysis": "ac"}).get_data(
                as_text=True)
        self.assertIn('data-analysis="ac"', html)
        self.assertIn("Frequency (Hz)", html)
        self.assertIn("Gain (dB)", html)
        self.assertIn("Phase (°)", html)
        self.assertIn("Cutoff", html)

    def test_spice_tran_chart_has_time_voltage_units(self):
        html = self.client.post(
            "/calculate", data={**SPICE_BASE, "analysis": "tran"}).get_data(
                as_text=True)
        self.assertIn('data-analysis="tran"', html)
        self.assertIn("Time (ms)", html)
        self.assertIn("Vin (V)", html)
        self.assertIn("Vout (V)", html)

    def test_changing_source_amplitude_changes_real_plot(self):
        quiet = self.client.post(
            "/calculate", data={**SPICE_BASE, "analysis": "tran"}).get_data(
                as_text=True)
        loud = self.client.post(
            "/calculate", data={**SPICE_BASE, "analysis": "tran",
                                "vin_mv": "20"}).get_data(as_text=True)
        self.assertIn("20 mV", loud)
        self.assertNotEqual(quiet, loud)

    def test_analysis_change_mode_reveals_spice_fields_without_running(self):
        html = self.client.post("/calculate", data={
            **SPICE_BASE, "analysis": "ac", "action": "change_mode",
        }).get_data(as_text=True)
        self.assertIn('id="rl"', html)
        self.assertIn('id="vin_mv"', html)
        self.assertIn('data-status="ready"', html)
        self.assertNotIn('data-series="gain"', html)

    def test_spice_fields_show_defaults_when_absent_from_first_submit(self):
        data = {k: v for k, v in SPICE_BASE.items()
                if k not in ("rl", "cin", "cout", "f_start_hz", "f_stop_hz")}
        html = self.client.post("/calculate", data={
            **data, "analysis": "tran"}).get_data(as_text=True)
        self.assertIn('id="rl" name="rl" value="10"', html)
        self.assertIn('id="cin" name="cin" value="10"', html)
        self.assertIn('id="cout" name="cout" value="10"', html)

    def test_spice_results_span_two_columns_for_the_plot(self):
        html = self.client.post("/calculate", data={
            **SPICE_BASE, "analysis": "ac"}).get_data(as_text=True)
        self.assertIn('class="card results results-wide"', html)
        plain = self.client.get("/").get_data(as_text=True)
        self.assertIn('class="card results"', plain)

    def test_dc_status_names_the_operating_point_not_solver_points(self):
        html = self.client.post("/calculate", data=SPICE_BASE).get_data(
            as_text=True)
        self.assertIn("1 operating point", html)
        self.assertNotIn("0 solver points", html)

    def test_analysis_dropdown_auto_reveals_its_fields(self):
        script = (Path(__file__).resolve().parents[1] / "static" / "app.js"
                  ).read_text(encoding="utf-8")
        self.assertIn('"analysis"', script)
        self.assertIn('"change_mode"', script)

    def test_analytical_path_still_returns_lab03_reference(self):
        html = self.client.post(
            "/calculate", data={**SPICE_BASE,
                                "analysis": "analytical"}).get_data(
                                    as_text=True)
        self.assertIn("8.052", html)
        self.assertIn("Active region approximation OK", html)


if __name__ == "__main__":
    unittest.main()

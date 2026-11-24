(function () {
  "use strict";

  var RESISTOR_FIELDS = ["r1", "r2", "rb", "rc", "re"];

  function unitLabel() {
    var select = document.getElementById("unit");
    return select && select.value === "ohm" ? "Ω" : "kΩ";
  }

  function valueOf(id) {
    var input = document.getElementById(id);
    if (!input) {
      return "—";
    }
    var value = input.value.trim();
    return value === "" ? "—" : value;
  }

  function refresh() {
    var unit = unitLabel();

    document.querySelectorAll("[data-unit-label]").forEach(function (node) {
      node.textContent = unit;
    });

    var vcc = document.getElementById("c-vcc");
    if (vcc) {
      vcc.textContent = valueOf("vcc") + " V";
    }

    var beta = document.getElementById("c-beta");
    if (beta) {
      beta.textContent = "β = " + valueOf("beta");
    }

    RESISTOR_FIELDS.forEach(function (field) {
      var label = document.getElementById("c-" + field);
      if (label) {
        label.textContent =
          field.toUpperCase() + " = " + valueOf(field) + " " + unit;
      }
    });
  }

  // Analysis mode is server-rendered: show the matching fields and button
  // before the user commits to a solver run.
  var analysis = document.getElementById("analysis");
  if (analysis && analysis.form) {
    analysis.addEventListener("change", function () {
      var form = analysis.form;
      var hidden = form.querySelector('input[type="hidden"][name="action"]');
      if (!hidden) {
        hidden = document.createElement("input");
        hidden.type = "hidden";
        hidden.name = "action";
        form.appendChild(hidden);
      }
      hidden.value = "change_mode";
      form.submit();
    });
  }

  // Keep the page honest during a solver run: there is no spinner in a plain
  // POST, so disable the action and announce the state before navigating.
  var form = analysis && analysis.form ? analysis.form
    : document.querySelector("form.card");
  if (form) {
    form.addEventListener("submit", function (event) {
      var button = form.querySelector('button[value="calculate"]');
      var submitter = event.submitter || document.activeElement;
      if (!button || (submitter && submitter.value !== "calculate")) {
        return;
      }
      if (!form.reportValidity()) {
        return;
      }
      event.preventDefault();
      button.disabled = true;
      var bar = document.querySelector(".engine-bar");
      if (bar) {
        bar.setAttribute("aria-busy", "true");
        var label = bar.querySelector("span");
        if (label) {
          label.textContent = analysis && analysis.value === "analytical"
            ? "calculating…" : "ngspice running…";
        }
      }
      var hidden = form.querySelector('input[type="hidden"][name="action"]');
      if (!hidden) {
        hidden = document.createElement("input");
        hidden.type = "hidden";
        hidden.name = "action";
        form.appendChild(hidden);
      }
      hidden.value = "calculate";
      window.setTimeout(function () { form.submit(); }, 120);
    });
  }

  document.addEventListener("input", refresh);
  document.addEventListener("change", refresh);
  refresh();
})();

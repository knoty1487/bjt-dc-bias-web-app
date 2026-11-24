# UI Visual Match (Lab 02) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ปรับหน้าจอของ BJT DC Bias Web App ให้มีโครงเหมือนภาพตัวอย่างใน handout (header → 3 คอลัมน์: ค่าอุปกรณ์ / วงจร / ผลลัพธ์ → footer) โดยไม่แก้สมการหรือตัวเลขผลลัพธ์

**Architecture:** เปลี่ยนเฉพาะ presentation layer — `templates/index.html`, `static/style.css` และเพิ่ม `static/app.js` (vanilla, progressive enhancement) ตัวเลขผลลัพธ์ทั้งหมดยังคำนวณจาก `dc_bias.py` ผ่าน `app.py` ตามเดิม วงจรเป็น SVG ฝังใน template ที่ render ค่าเริ่มต้นจากฝั่ง server และ JS อัปเดตป้ายเมื่อผู้ใช้พิมพ์

**Tech Stack:** Python 3.13, Flask 3.1, Jinja2, HTML/CSS, vanilla JavaScript (ไม่มี framework)

**Spec:** `docs/superpowers/specs/2026-11-10-ui-visual-match-design.md`

## Global Constraints

- ห้ามแก้ `dc_bias.py` — สมการ, validation, region thresholds คงเดิม
- ห้ามแก้ signature ของ `/calculate` หรือชื่อฟิลด์ฟอร์ม (`vcc, r1, r2, rc, re, beta, vbe, unit`)
- คง dropdown หน่วยเดียว (`unit`: `kilo` | `ohm`) ใช้ร่วมกัน 4 ตัวต้านทาน
- ห้ามใช้ `|safe` หรือ bypass autoescaping ของ Jinja
- ห้ามเพิ่ม JavaScript framework หรือ dependency ภายนอก (ไม่มี CDN, ไม่มีฟอนต์ภายนอก)
- ข้อความ UI เป็นภาษาไทย/อังกฤษตามของเดิม
- เทสต์เดิม 24 ตัวต้องผ่านครบหลังจบทุก task
- คำสั่งรันเทสต์: `cmd /c ".venv\Scripts\python.exe -m unittest discover -s tests -v"` จาก repo root
- Breakpoints: ≥ 1100px = 3 คอลัมน์, 760–1099px = 2 คอลัมน์, < 760px = 1 คอลัมน์

## Review Focus

- ปิด JavaScript แล้ววงจรกลางจอยังแสดงค่าที่ถูกต้อง (server-rendered) — ห้ามเป็นช่องว่าง
- ค่าที่พิมพ์ยาว (เช่น `100000` และหน่วย Ω) ต้องไม่ทำให้ป้ายบน SVG ทับกันจนอ่านไม่ออก
- VCC หรือ β ที่มีทศนิยม ต้องแสดงตามที่พิมพ์ ไม่ถูกปัดหรือแปลง
- ป้ายหน่วยบนวงจรต้องตรงกับ dropdown (kΩ vs Ω) ทั้งก่อนและหลังเปลี่ยนหน่วย
- แบนเนอร์ region ต้องสร้างเหตุผลจากค่าจริงของรอบนั้น ไม่ใช่ข้อความตายตัว

---

### Task 1: Page shell — header, 3-column grid, footer

**Files:**
- Modify: `templates/index.html`
- Modify: `static/style.css`
- Test: `tests/test_web.py`

**Interfaces:**
- Consumes: context `form`, `result`, `error`, `unit_label` จาก `app.py::_render`
- Produces: CSS classes `site-header`, `layout`, `card`, `goal-strip` ที่ Task 2–4 ใช้ต่อ

- [ ] **Step 1: Write the failing test**

เพิ่มใน `tests/test_web.py` (class `WebTests`):

```python
    def test_page_has_header_and_goal_strip(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'class="site-header"', response.data)
        self.assertIn(b'class="goal-strip"', response.data)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cmd /c ".venv\Scripts\python.exe -m unittest tests.test_web.WebTests.test_page_has_header_and_goal_strip -v"`
Expected: FAIL — `class="site-header"` not found

- [ ] **Step 3: Restructure `templates/index.html`**

เปลี่ยน `<header>` เดิมเป็น:

```html
<header class="site-header">
  <div class="brand">
    <h1>Lab 02: BJT DC Bias Web App</h1>
    <p>ENG29 2121 – Common Emitter (Voltage Divider Bias)</p>
  </div>
  <p class="course-badge">Computer Programming for<br>Electrical Engineers</p>
</header>
```

คง `<main class="layout">` และ `<form class="card">` เดิมไว้ทั้งบล็อก (Task 2–3 จะแก้ข้างใน)
เพิ่มก่อน `</body>`:

```html
<footer class="goal-strip">
  <h2>Week 2 Goal</h2>
  <p>สร้าง Flask Web App ที่รับค่าอุปกรณ์ คำนวณ DC Bias
     (VB, VE, VC, VCE, IB, IC, IE) ของวงจร Common-Emitter
     แบบ Voltage-Divider Bias แล้วแสดงผลพร้อมหน่วย</p>
</footer>
```

- [ ] **Step 4: Update `static/style.css`**

เปลี่ยน `.layout` เป็น 3 คอลัมน์ และเพิ่มสไตล์ header/footer:

```css
.layout {
  display: grid;
  grid-template-columns: minmax(300px, 360px) minmax(360px, 1fr) minmax(300px, 340px);
  gap: 20px;
  align-items: start;
}

.site-header {
  max-width: 1280px;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--line);
}

.site-header h1 { margin: 0 0 4px; font-size: clamp(1.35rem, 2.4vw, 1.85rem); }
.site-header p { margin: 0; color: var(--muted); }

.course-badge {
  margin: 0;
  padding: 10px 16px;
  color: var(--blue) !important;
  background: #e8f2fa;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  text-align: right;
}

.goal-strip {
  max-width: 1280px;
  margin: 20px auto 0;
  padding: 14px 20px;
  background: #e8f2fa;
  border: 1px solid var(--line);
  border-radius: 10px;
}

.goal-strip h2 { margin: 0 0 4px; font-size: 1rem; color: var(--blue); }
.goal-strip p { margin: 0; color: var(--muted); font-size: 0.92rem; }
```

ปรับ breakpoint เดิม:

```css
@media (max-width: 1099px) {
  .layout { grid-template-columns: minmax(300px, 360px) minmax(360px, 1fr); }
}

@media (max-width: 760px) {
  .layout { grid-template-columns: 1fr; }
  .site-header { flex-direction: column; align-items: flex-start; }
  .course-badge { text-align: left; }
  .field input, .field select { flex-basis: 120px; }
}
```

- [ ] **Step 5: Run all tests**

Run: `cmd /c ".venv\Scripts\python.exe -m unittest discover -s tests -v"`
Expected: 25 tests, OK

- [ ] **Step 6: Commit**

```bash
git add templates/index.html static/style.css tests/test_web.py
git commit -m "feat(ui): add header, three-column layout and goal strip"
```

---

### Task 2: Region banner with computed reason

**Files:**
- Modify: `templates/index.html`
- Modify: `static/style.css`
- Test: `tests/test_web.py`

**Interfaces:**
- Consumes: `result.region`, `result.vce`, `result.vth`, ค่า `form.vbe`
- Produces: `div.region-banner[data-region]` ที่ Task 4 ใช้ต่อ; แทน `strong.region-badge` เดิม

- [ ] **Step 1: Write the failing test**

เปลี่ยน `test_results_show_units_and_warning` ให้หา banner และเพิ่มเทสต์ใหม่:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cmd /c ".venv\Scripts\python.exe -m unittest tests.test_web -v"`
Expected: FAIL 2 tests — `class="region-banner"` / `Active region approximation OK` not found

- [ ] **Step 3: Replace the badge with a banner in `templates/index.html`**

แทนบล็อก `<p>สถานะการทำงาน: <strong class="region-badge" ...></strong></p>` ด้วย:

```html
{% set reason = {
  "active": "VCE = %.3f V > 1.0 V (transistor in active region)"|format(result.vce),
  "near-saturation": "0.3 V < VCE = %.3f V < 1.0 V"|format(result.vce),
  "saturation": "VCE = %.3f V ≤ 0.3 V"|format(result.vce),
  "cutoff": "VTH = %.3f V ≤ VBE = %.2f V"|format(result.vth, form.vbe|float),
} %}
{% set title = {
  "active": "Active region approximation OK",
  "near-saturation": "Near-saturation — ตรวจสอบซ้ำ",
  "saturation": "Saturation — แบบจำลอง Forward-Active ใช้ไม่ได้",
  "cutoff": "Cutoff — วงจรอยู่ในสภาวะ OFF",
} %}
<div class="region-banner" data-region="{{ result.region }}">
  <strong>{{ title[result.region] }}</strong>
  <span>{{ reason[result.region] }}</span>
</div>
```

- [ ] **Step 4: Style the banner in `static/style.css`**

แทนที่ `.region-badge` และ `.region-badge[data-region=...]` ทั้งหมดด้วย:

```css
.region-banner {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin: 0 0 16px;
  padding: 12px 16px;
  border-radius: 8px;
  border-left: 5px solid;
  font-size: 0.92rem;
}

.region-banner strong { font-size: 1rem; }

.region-banner[data-region="active"] {
  color: #0b6157;
  background: #e2f5f0;
  border-color: #0c8078;
}

.region-banner[data-region="near-saturation"] {
  color: #7a5b00;
  background: #fdf2cf;
  border-color: #d9a800;
}

.region-banner[data-region="saturation"],
.region-banner[data-region="cutoff"] {
  color: #8f2318;
  background: #fbe3e0;
  border-color: #c0392b;
}
```

- [ ] **Step 5: Run all tests**

Run: `cmd /c ".venv\Scripts\python.exe -m unittest discover -s tests -v"`
Expected: 26 tests, OK

- [ ] **Step 6: Commit**

```bash
git add templates/index.html static/style.css tests/test_web.py
git commit -m "feat(ui): replace region badge with computed reason banner"
```

---

### Task 3: Circuit SVG with live labels

**Files:**
- Modify: `templates/index.html`
- Modify: `static/style.css`
- Create: `static/app.js`
- Test: `tests/test_web.py`

**Interfaces:**
- Consumes: `form.vcc, form.r1, form.r2, form.rc, form.re, form.beta`, `unit_label`
- Produces: element ids `c-vcc`, `c-r1`, `c-r2`, `c-rc`, `c-re`, `c-beta`; `static/app.js` ที่ Task 4 ไม่ต้องแก้

- [ ] **Step 1: Write the failing test**

```python
    def test_circuit_svg_uses_form_values(self):
        response = self.client.post("/calculate", data={**VALID, "r1": "47", "rc": "3.3"})
        self.assertIn(b"<svg", response.data)
        self.assertIn(b'id="c-r1"', response.data)
        self.assertIn("47 kΩ".encode(), response.data)
        self.assertIn("3.3 kΩ".encode(), response.data)

    def test_page_loads_live_label_script(self):
        response = self.client.get("/")
        self.assertIn(b"app.js", response.data)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cmd /c ".venv\Scripts\python.exe -m unittest tests.test_web -v"`
Expected: FAIL 2 tests — `<svg` / `app.js` not found

- [ ] **Step 3: Add the SVG card between form and results in `templates/index.html`**

แทรกหลัง `</form>` (ก่อน `<section class="card">` ของผลลัพธ์):

```html
<section class="card">
  <h2>Circuit: Common-Emitter Amplifier</h2>
  <svg class="circuit" viewBox="0 0 260 300" role="img"
       aria-label="วงจร Common-Emitter แบบ Voltage-Divider Bias">
    <line x1="130" y1="20" x2="130" y2="60" class="wire"/>
    <text x="136" y="16" class="lbl" id="c-vcc">{{ form.vcc }} V</text>
    <text x="136" y="30" class="lbl small">VCC</text>

    <line x1="130" y1="60" x2="60" y2="60" class="wire"/>
    <line x1="60" y1="60" x2="60" y2="80" class="wire"/>
    <rect x="50" y="80" width="20" height="46" class="res"/>
    <text x="8" y="108" class="lbl" id="c-r1">R1 = {{ form.r1 }} {{ unit_label }}</text>

    <line x1="130" y1="60" x2="200" y2="60" class="wire"/>
    <line x1="200" y1="60" x2="200" y2="80" class="wire"/>
    <rect x="190" y="80" width="20" height="46" class="res"/>
    <text x="140" y="108" class="lbl" id="c-rc">RC = {{ form.rc }} {{ unit_label }}</text>

    <line x1="60" y1="126" x2="60" y2="150" class="wire"/>
    <line x1="60" y1="150" x2="130" y2="150" class="wire"/>
    <line x1="130" y1="150" x2="130" y2="170" class="wire"/>
    <circle cx="130" cy="185" r="16" class="dev"/>
    <line x1="118" y1="176" x2="142" y2="194" class="wire"/>
    <line x1="130" y1="201" x2="130" y2="228" class="wire"/>
    <text x="150" y="186" class="lbl" id="c-beta">β = {{ form.beta }}</text>

    <line x1="200" y1="126" x2="200" y2="140" class="wire"/>
    <line x1="200" y1="140" x2="146" y2="178" class="wire"/>
    <line x1="130" y1="201" x2="130" y2="206" class="wire"/>
    <line x1="130" y1="206" x2="200" y2="206" class="wire"/>
    <line x1="200" y1="206" x2="200" y2="220" class="wire"/>
    <rect x="190" y="220" width="20" height="46" class="res"/>
    <text x="140" y="248" class="lbl" id="c-re">RE = {{ form.re }} {{ unit_label }}</text>

    <line x1="60" y1="150" x2="60" y2="266" class="wire"/>
    <text x="20" y="156" class="lbl" id="c-r2">R2 = {{ form.r2 }} {{ unit_label }}</text>
    <rect x="50" y="176" width="20" height="46" class="res"/>
    <line x1="60" y1="222" x2="60" y2="270" class="wire"/>

    <line x1="40" y1="270" x2="220" y2="270" class="wire"/>
    <line x1="60" y1="270" x2="60" y2="278" class="wire"/>
    <line x1="200" y1="266" x2="200" y2="270" class="wire"/>
    <line x1="48" y1="278" x2="72" y2="278" class="wire"/>
    <line x1="54" y1="284" x2="66" y2="284" class="wire"/>
    <line x1="188" y1="270" x2="212" y2="270" class="wire"/>
    <line x1="194" y1="276" x2="206" y2="276" class="wire"/>
  </svg>
</section>
```

และก่อน `</body>`:

```html
<script src="{{ url_for('static', filename='app.js') }}" defer></script>
```

- [ ] **Step 4: Add circuit CSS to `static/style.css`**

```css
.circuit {
  width: 100%;
  height: auto;
  max-height: 420px;
}

.circuit .wire {
  stroke: var(--ink);
  stroke-width: 2;
  fill: none;
}

.circuit .res {
  fill: #fff;
  stroke: var(--ink);
  stroke-width: 2;
}

.circuit .dev {
  fill: #e8f2fa;
  stroke: var(--ink);
  stroke-width: 2;
}

.circuit .lbl {
  fill: var(--ink);
  font-size: 11px;
  font-family: inherit;
}

.circuit .lbl.small { fill: var(--muted); font-size: 9px; }
```

- [ ] **Step 5: Create `static/app.js`**

```javascript
(function () {
  "use strict";

  var UNIT_BY_FIELD = { r1: true, r2: true, rc: true, re: true };

  function unitLabel() {
    var select = document.getElementById("unit");
    return select && select.value === "ohm" ? "Ω" : "kΩ";
  }

  function valueOf(id) {
    var input = document.getElementById(id);
    return input && input.value.trim() !== "" ? input.value.trim() : "—";
  }

  function refresh() {
    var unit = unitLabel();

    var vcc = document.getElementById("c-vcc");
    if (vcc) { vcc.textContent = valueOf("vcc") + " V"; }

    var beta = document.getElementById("c-beta");
    if (beta) { beta.textContent = "β = " + valueOf("beta"); }

    Object.keys(UNIT_BY_FIELD).forEach(function (field) {
      var label = document.getElementById("c-" + field);
      if (label) {
        label.textContent = field.toUpperCase() + " = " + valueOf(field) + " " + unit;
      }
    });
  }

  document.addEventListener("input", refresh);
  document.addEventListener("change", refresh);
  refresh();
})();
```

- [ ] **Step 6: Run all tests**

Run: `cmd /c ".venv\Scripts\python.exe -m unittest discover -s tests -v"`
Expected: 28 tests, OK

- [ ] **Step 7: Commit**

```bash
git add templates/index.html static/style.css static/app.js tests/test_web.py
git commit -m "feat(ui): add inline circuit svg with live labels"
```

---

### Task 4: Responsive polish, overflow guard, final verification

**Files:**
- Modify: `static/style.css`
- Test: `tests/test_web.py`

**Interfaces:**
- Consumes: ทุก class จาก Task 1–3
- Produces: ไม่มี interface ใหม่

- [ ] **Step 1: Write the failing test**

```python
    def test_stylesheet_guards_long_numbers(self):
        from pathlib import Path
        css = Path("static/style.css").read_text(encoding="utf-8")
        self.assertIn("overflow-wrap: anywhere", css)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cmd /c ".venv\Scripts\python.exe -m unittest tests.test_web.WebTests.test_stylesheet_guards_long_numbers -v"`
Expected: FAIL — `overflow-wrap: anywhere` not found

- [ ] **Step 3: Add the guard and small-screen tuning**

ในบล็อก `th, td` เพิ่ม `overflow-wrap: anywhere;` และเพิ่มท้ายไฟล์:

```css
@media (max-width: 760px) {
  .circuit { max-height: none; }
  .region-banner { font-size: 0.88rem; }
}
```

- [ ] **Step 4: Run all tests**

Run: `cmd /c ".venv\Scripts\python.exe -m unittest discover -s tests -v"`
Expected: 29 tests, OK

- [ ] **Step 5: Manual browser verification**

รัน `python -m flask --app app run --debug` แล้วตรวจด้วยตา:
- หน้าค่าเริ่มต้น: 3 คอลัมน์, วงจรแสดง 12 V / 100 kΩ / 22 kΩ / 2.2 kΩ / 1 kΩ / β = 100
- ย่อหน้าต่าง < 760px: เหลือคอลัมน์เดียว ไม่มีแนวนอนล้น
- เปลี่ยน R1 เป็น `47` → ป้ายบนวงจรเปลี่ยนเป็น `R1 = 47 kΩ` ทันที
- เปลี่ยน dropdown เป็น Ω → ป้ายเปลี่ยนเป็น `Ω` ทันที
- กด Calculate: banner เขียว "Active region approximation OK" + VCE = 8.052 V

- [ ] **Step 6: Commit**

```bash
git add static/style.css tests/test_web.py
git commit -m "fix(ui): guard long numbers and tune small screens"
```

---

## Self-Review

- **Spec coverage:** header (T1), 3 คอลัมน์ (T1), footer (T1), วงจร SVG + live (T3), region banner (T2), overflow guard (T4), responsive (T1/T4) — ครบทุกหัวข้อใน design doc
- **Step scan:** ทุก step มี action เดียวและผลตรวจได้ ไม่มี "TBD" หรือ "handle edge cases"
- **Type consistency:** id `c-vcc/c-r1/c-r2/c-rc/c-re/c-beta` ตรงกันระหว่าง T3 step 3, 5 และเทสต์
- **Review Focus:** ปิด JS → ค่า render จาก server (T3 step 3 ใช้ `{{ form.* }}`); ค่ายาว → `overflow-wrap` (T4); ทศนิยม → แสดงค่าตามที่พิมพ์ตรง ๆ; หน่วย → `unit_label` ทั้งฝั่ง server และ `unitLabel()` ฝั่ง JS; เหตุผล region → สร้างจาก `result.vce` / `result.vth`
- **Proportion:** 4 tasks สำหรับ UI change หนึ่งครั้ง ไม่มี code ที่ไม่ได้ใช้

# BJT-DC-Bias-Web-App — Lab 04: BJT Amplifier Simulator v1

ENG29 2121 (2/2569) · Flask web app ที่ต่อยอดจาก Lab 03 โดยไม่สร้างโปรเจกต์ใหม่

- **Lab 03 (ยังใช้ได้เหมือนเดิม):** Analytical DC Bias 3 โหมด — Voltage Divider, Fixed, Emitter
- **Lab 04 (ใหม่):** CE Voltage Divider หนึ่งวงจร จำลองจริงด้วย ngspice
  - `.op` — DC operating point
  - `.ac` — Bode: gain (dB) และ phase (°) อ้างอิง `Vin = node 5`, `Vout = node 6`
  - `.tran` — waveform `Vin`/`Vout` vs time พร้อม amplitude/frequency

Repository: <https://github.com/ottoponrod/BJT-DC-Bias-Web-App> (branch `main`)
Commit SHA ของงาน Lab 04: รายงานในข้อความส่งงาน (ดู `git log -1` ในเครื่องที่ push)

> ผล SPICE มาจากการรัน solver จริงทุกครั้ง ไม่มี trace/cutoff/gain ที่ hard-code
> ผล Analytical (`dc_bias.py`) แสดงแยกต่างหากและไม่บังคับให้เท่ากันทุกหลัก

## ความต้องการของระบบ

- Python 3.10 ขึ้นไป (พัฒนา/ทดสอบด้วย Python 3.13)
- Flask 3.x ตาม `requirements.txt`
- **ngspice 47** (ทดสอบกับ build 11 Aug 2026) — ต้องมี executable หรือตั้ง `NGSPICE_EXE`
- Node.js + internet เฉพาะตอนติดตั้ง Impeccable ใหม่ (ไม่จำเป็นต่อการรันแอป)
- Browser ที่เปิด `http://127.0.0.1:5000/` ได้

ตัวอย่าง ngspice ที่ใช้จริง:
`C:\Users\B6814946\AppData\Local\Programs\ngspice-47\Spice64\bin\ngspice.exe`

## ติดตั้ง / รัน / ทดสอบ

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

# ถ้า ngspice ไม่ได้อยู่ใน PATH
$env:NGSPICE_EXE = "C:\Users\B6814946\AppData\Local\Programs\ngspice-47\Spice64\bin\ngspice.exe"

python -m flask --app app run --port 5000
```

เปิด <http://127.0.0.1:5000/> · ต้องรันผ่าน Flask เสมอ (เปิด `templates/index.html` ตรง ๆ จะไม่มี backend)

```powershell
python -m unittest discover -s tests
```

ผลล่าสุด: **95 tests OK** (`dc_bias` 22 · `web` 50 · `spice_engine` 19 · `plots` 4)

## วิธีใช้

1. เลือก **Analysis mode**
   - `Analytical DC (Lab 03)` → ใช้ได้ทั้ง 3 bias mode
   - `DC · ngspice .op`, `AC · ngspice .ac`, `Transient · ngspice .tran` → รองรับเฉพาะ CE Voltage Divider
2. ในโหมด SPICE ตัวเลือก bias จะถูกปิดและบังคับ `divider` (แอปแจ้ง “SPICE v1 จำลองเฉพาะ CE Voltage Divider”)
3. กรอกค่า → กด **Run Simulation** (หรือ **Calculate DC Bias** ในโหมด Lab 03)
4. อ่านสถานะ `Success/Error`, directive, จำนวนจุด, provenance, ตารางผล และกราฟ SVG
5. ขยาย `<details>` **Netlist / run.log / ตัวอย่างข้อมูลจาก run.raw** เพื่อตรวจที่มาของตัวเลข

### ค่าตั้งต้นวงจรอ้างอิง (Input fixture — ไม่ใช่ผลลัพธ์ที่เดาไว้)

| ส่วน | ค่า |
|---|---|
| VCC / R1 / R2 | 12 V / 100 kΩ / 22 kΩ |
| RC / RE / RL | 2.2 kΩ / 1 kΩ / 10 kΩ |
| Cin / Cout | 10 µF / 10 µF |
| Source (transient) | 10 mV peak @ 1 kHz |
| AC sweep | 10 Hz – 1 MHz, 20 points/decade |
| BJT model | `Q2N3904`, 2N3904 NPN Gummel-Poon card ( pinned ใน `spice_engine.py`) |

ไม่มี emitter bypass capacitor ใน baseline (`CE`) · ไม่มี Starter Kit ของอาจารย์ในเครื่อง จึงใช้การ์ดโมเดล 2N3904 มาตรฐานที่ระบุพารามิเตอร์ไว้ในโค้ดและเอกสาร

## Python ↔ ngspice ทำอะไรบ้าง

1. `app.py` แปลง/ตรวจอินพุต (ตัวเลข, บวก, ช่วงความถี่, amplitude < VCC/2) **ก่อน** สร้าง netlist
2. `spice_engine.build_netlist()` เขียน netlist หนึ่งไฟล์ต่อ analysis (`circuit.cir`) ใน temp dir แยกต่อรอบ
3. เรียก solver แบบ batch:

```python
subprocess.run(
    [str(solver), "-b", "-o", str(log_path), "-r", str(raw_path), str(circuit)],
    cwd=run_dir, timeout=20.0, shell=False, capture_output=True, text=True,
)
```

4. อ่าน `run.raw` (ASCII) เป็น array: AC เป็น complex → `VDB(6)-VDB(5)`, `VP(6)-VP(5)`; transient เป็น real → `time, v(5), v(6)`; DC อ่าน operating point จาก raw (fallback `run.log`)
5. ถ้า solver หาย/timeout/exit≠0/log ว่าง/raw ไม่มีจุด → แสดง Error และ **ไม่มีกราฟหรือผล Success ค้าง**

แยกหน้าที่: `app.py` = route/validation, `spice_engine.py` = adapter/solver, `dc_bias.py` = analytical reference, `plots.py` = SVG จาก solver points, Browser = แสดงผลที่ได้รับ

## Impeccable (UI critique → polish → audit)

```powershell
npx -y impeccable install -y --providers=opencode --scope=project
```

ติดตั้งแล้วในโปรเจกต์ (โฟลเดอร์ `.opencode/` ไม่ได้ commit; ติดตั้งใหม่ด้วยคำสั่งข้างบน)
ใช้ CLI launcher `.opencode\skills\impeccable\scripts\impeccable.cmd`

- Critique: dual-agent, **21/40 (Acceptable)** → `docs/evidence/lab04/impeccable-critique.md` (copy ของ snapshot ใน `.impeccable/`)
- Polish ที่ทำจริง (UI-only): ปิด bias selector ในโหมด SPICE, busy state ตอนรัน, unit label อัปเดตสด, placeholder สั้นลงสำหรับ 390 px, focus ring สีน้ำเงิน
- Audit หลัง polish: **16/20 (Good)** → `docs/evidence/lab04/impeccable-audit.md` (copy ของ snapshot ใน `.impeccable/`)
- ไม่แต่งสมการ/ข้อมูลกราฟ/โมเดล solver

ผลตรวจ B1–B8, ข้อจำกัด และชื่อ tool ที่ใช้จริงอยู่ใน [`docs/validation.md`](docs/validation.md)

## Browser acceptance — ความจริงเรื่อง tool

- Playwright MCP **ไม่ได้เปิดเผยใน session นี้** → ใช้ **OpenCode in-app Browser (Chromium)** แทน และบันทึกชื่อ tool จริงใน `docs/validation.md`
- ตรวจ desktop ~1280 px สำเร็จ (viewport จริง 1397×886, document 1382 px, ไม่มี overflow/console error)
- Phone ~390 px: มีแค่ CLI detector ของ Impeccable ที่ 390×844 + CSS breakpoint; **การจำลอง viewport ใน browser จริง NOT RUN**
- ตามคำสั่งของผู้ใช้ **ยังไม่ได้แคป screenshot Lab 04 เลย** หลักฐานจึงเป็น DOM/status/ตัวเลข/ข้อความ error และ netlist/log ไม่ใช่ภาพ

## โครงสร้างไฟล์

```
app.py                    Flask routes, validation, SPICE dispatch, provenance
dc_bias.py                Analytical DC Bias 3 โหมด (Lab 03)
spice_engine.py           netlist + subprocess + .raw parser + cutoff logic
plots.py                  SVG plots จาก solver points เท่านั้น
templates/index.html      ฟอร์ม, schematic, status, evidence details
static/style.css          layout/responsive/tokens
static/app.js             live labels, auto-reveal, busy state
tests/test_dc_bias.py     22 tests
tests/test_web.py         50 tests (Lab 03 + SPICE web)
tests/test_spice_engine.py, tests/test_plots.py   adapter/plot tests
docs/validation.md        Lab 03 A1–A5 + Lab 04 B1–B8
docs/evidence/lab03/      screenshot Lab 03 เดิม
docs/evidence/lab04/       critique + audit snapshots ที่ commit เป็นหลักฐาน (ต้นฉบับอยู่ใน .impeccable/ ซึ่ง tool ตั้งค่าไม่ให้ commit)
```

## References

- ngspice Documentation / User Manual และ Batch Mode (`ngspice -b -o run.log -r run.raw circuit.cir`)
- Impeccable for coding agents — critique/polish/audit (รองรับ OpenCode)
- Superpowers — brainstorm/plan/execute/verify workflow
- Flask Official Docs — routes/templates/error handling
- ENG29 2121 Lab 03 และ Lab 04 handout (ค่าอ้างอิง B1–B8)

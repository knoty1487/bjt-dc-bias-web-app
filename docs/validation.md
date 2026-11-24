# Validation — BJT DC Bias Web App (Lab 03 + Lab 04)

เว็บแอปรองรับ 3 โหมดไบอัส: **Voltage Divider**, **Fixed Bias** และ
**Emitter Bias** โดยทุกโหมดใช้แบบจำลอง Forward-Active (β และ VBE คงที่)
และแปลงหน่วยตัวต้านทานที่จุดรับข้อมูลครั้งเดียว (kΩ × 1000 = Ω)

## 1. ค่าอ้างอิงที่คำนวณด้วยมือ

ค่ากลางที่ทุกโหมดใช้ร่วมกัน: VCC = 12 V, RC = 2.2 kΩ, β = 100, VBE = 0.70 V

### 1.1 Voltage Divider Bias (A1)

R1 = 100 kΩ, R2 = 22 kΩ, RE = 1 kΩ

| ปริมาณ | สมการ | ค่า |
|---|---|---|
| VTH | VCC·R2/(R1+R2) | 2.1639 V |
| RTH | R1·R2/(R1+R2) | 18.033 kΩ |
| IB | (VTH−VBE)/(RTH+(β+1)RE) | 12.2986 µA |
| IC | β·IB | 1.2299 mA |
| IE | (β+1)·IB | 1.2422 mA |
| VE | IE·RE | 1.2422 V |
| VB | VE+VBE | 1.9422 V |
| VC | VCC−IC·RC | 9.2943 V |
| VCE | VC−VE | 8.0522 V |

Region: **Active** (VCE = 8.05 V > 1.0 V)

### 1.2 Fixed Bias (A2) — ค่าอ้างอิงอิสระของโหมดใหม่

RB = 1 MΩ = 1,000 kΩ = 1,000,000 Ω, ไม่มี RE (VE = 0 V)

| ปริมาณ | สมการ | ค่า |
|---|---|---|
| IB | (VCC−VBE)/RB = (12−0.70)/1,000,000 | 11.3000 µA |
| IC | β·IB = 100 × 11.3000 µA | 1.1300 mA |
| IE | (β+1)·IB = 101 × 11.3000 µA | 1.1413 mA |
| VE | 0 (อิมิตเตอร์ต่อลงกราวด์) | 0.000 V |
| VB | VE+VBE | 0.700 V |
| VC | VCC−IC·RC = 12 − 1.1300 mA × 2.2 kΩ | 9.5140 V |
| VCE | VC−VE | 9.5140 V |

### 1.3 Emitter Bias (A3, A4)

RB = 1 MΩ, RC = 2.2 kΩ

| ปริมาณ | A3: RE = 1 kΩ | A4: RE = 2 kΩ |
|---|---|---|
| IB | (12−0.70)/(1,000,000 + 101×1,000) = 10.2634 µA | (12−0.70)/(1,000,000 + 101×2,000) = 9.4010 µA |
| IC | 1.02634 mA | 0.94010 mA |
| IE | 1.03660 mA | 0.94950 mA |
| VE | 1.03660 V | 1.89900 V |
| VC | 9.74205 V | 9.93178 V |
| VCE | 8.70545 V | 8.03278 V |

**คำทำนาย A4:** เมื่อ RE เพิ่มจาก 1 kΩ เป็น 2 kΩ ตัวหาร
`RB + (β+1)RE` โตขึ้น ทำให้ IB และ IC **ลดลง** (ไม่ใช่เพิ่มขึ้น)
ผลจริงบนเว็บลดจาก 1.026 mA เป็น 0.940 mA ตรงกับคำทำนาย

## 2. ผลตรวจ A1–A5 ด้วยเบราว์เซอร์จริง

เครื่องมือ: OpenCode Browser (Chromium) เปิด <http://127.0.0.1:5000/>
กรอกค่าผ่านฟอร์มจริง กดปุ่ม Calculate DC Bias และอ่านค่าจากตารางผลลัพธ์
ทุกกรณีเป็น HTTP 200 และหน้าเว็บไม่ล้ม

| # | โหมด / อินพุต | IC ที่คาดหวัง | IC จริง | VCE ที่คาดหวัง | VCE จริง | ผล | หลักฐาน |
|---|---|---|---|---|---|---|---|
| A1 | Divider: R1=100 kΩ, R2=22 kΩ, RE=1 kΩ | 1.230 mA | **1.230 mA** | 8.052 V | **8.052 V** | ผ่าน | `docs/evidence/lab03/A1-divider.jpg` |
| A2 | Fixed: RB=1000 kΩ (1 MΩ), ไม่กรอก RE | 1.130 mA | **1.130 mA** | 9.514 V | **9.514 V** | ผ่าน | `docs/evidence/lab03/A2-fixed.jpg` |
| A3 | Emitter: RB=1000 kΩ, RE=1 kΩ | 1.026 mA | **1.026 mA** | 8.705 V | **8.705 V** | ผ่าน | `docs/evidence/lab03/A3-emitter-re1k.jpg` |
| A4 | Emitter: เหมือน A3 แต่ RE=2 kΩ | 0.940 mA | **0.940 mA** | 8.033 V | **8.033 V** | ผ่าน (IC ลดลงตามคำทำนาย) | `docs/evidence/lab03/A4-emitter-re2k.jpg` |
| A5 | Fixed: RB=0 | error `RB ต้องมากกว่า 0 Ω` | **`RB ต้องมากกว่า 0 Ω`** | ไม่แสดงผล | ไม่มีตารางผล/แบนเนอร์ | ผ่าน | `docs/evidence/lab03/A5-fixed-rb0-error.jpg` |

ค่าความคลาดเคลื่อนสูงสุดที่ยอมรับ: |ΔIC| ≤ 0.01 mA และ |ΔVCE| ≤ 0.02 V
ผลจริงตรงกับค่าอ้างอิงที่ตำแหน่งทศนิยม 3 ตำแหน่งทุกกรณี (Δ = 0.000)

**ตรวจซ้ำรอบสุดท้าย (17 พ.ย. 2026, 18:42–18:43):** รัน A1–A5 ใหม่ทั้งหมดบน
Flask ที่รันโค้ดชุดปัจจุบัน (commit `50e94c4`) ผลตรงกับตารางเดิมทุกช่อง
และรัน A3 ซ้ำอีกครั้งได้ `IC 1.026 mA / VCE 8.705 V` เท่าเดิม (ยืนยันว่าทำซ้ำได้)
ภาพหลักฐานใน `docs/evidence/lab03/` ถูกแทนที่ด้วยภาพจากรอบนี้
เซิร์ฟเวอร์บันทึก `POST /calculate HTTP/1.1 200` ทุกครั้ง รวมถึงกรณี A5 (RB=0)
จึงยืนยันได้ว่าข้อความ error มาจาก Flask ไม่ใช่การบล็อกที่ฟอร์มในเบราว์เซอร์

### 2.1 สิ่งที่ตรวจเพิ่มในเบราว์เซอร์

- ฟอร์มเปลี่ยนช่องตามโหมด: Fixed แสดงเฉพาะ `rb` (ไม่มี `r1`, `r2`, `re`)
  และ Emitter แสดง `rb` + `re` (ไม่มี `r1`, `r2`)
- ปุ่ม **เปลี่ยนโหมด** มี `formnovalidate` ทำให้สลับโหมดได้แม้ช่องอื่นว่าง
  (แก้ regression ที่ปุ่มถูก HTML required บล็อก)
- A5: หลังส่ง RB=0 หน้าเว็บแสดงเฉพาะข้อความ error ไม่มีตารางหรือแบนเนอร์
  ของผลรอบก่อนค้างอยู่
- หน่วย Ω ใช้ได้กับทุกโหมด: กรอก RB=1000000, RC=2200, unit=Ω ให้ผลเท่ากับ
  การกรอกหน่วย kΩ

## 3. ผลการทดสอบอัตโนมัติ

คำสั่ง: `python -m unittest discover -s tests -v`

```
Ran 50 tests in 0.121s

OK
```

- `tests/test_dc_bias.py` — 22 tests: ค่าอ้างอิง Divider เดิม, validation,
  cutoff/saturation/near-saturation, NaN/∞, โหมด Fixed/Emitter (ค่าอ้างอิง,
  RE มากขึ้นทำให้ IC ลดลง, RB/RE ≤ 0, cutoff)
- `tests/test_web.py` — 28 tests: GET/POST เดิมทั้งหมด, mode selector,
  การสลับโหมด, `formnovalidate`, ผล Fixed/Emitter จาก Flask, หน่วย Ω,
  โหมดที่ไม่รู้จัก, error RB=0 โดยไม่มีผลค้าง, และแผนภาพ SVG ของแต่ละโหมด

## 4. ข้อจำกัดของแบบจำลอง

- ใช้ Forward-Active Approximation: β คงที่, VBE คงที่, ไม่คิด Early effect
- ไม่ใช่ ngspice/SPICE — ค่าที่ได้เป็นผลของสมการมือ ไม่ใช่ผลจำลองวงจรจริง
- Fixed bias ไม่มี RE จึงไวต่อ β มาก (IC = β·IB) และอาจอิ่มตัวง่ายกว่าโหมดอื่น
- เมื่อ VTH ≤ VBE (Divider) หรือ VCC ≤ VBE (Fixed/Emitter) ระบบรายงาน
  cutoff; เมื่อ VCE ≤ 0.3 V รายงาน saturation พร้อม warning ว่าแบบจำลอง
  Forward-Active ใช้ไม่ได้

> หมายเหตุ: ตัวเลข “50 tests” ในข้อ 3 เป็น snapshot ของ Lab 03 ก่อนเพิ่มงาน Lab 04
> ชุดทดสอบปัจจุบันอยู่ในข้อ 5.5 ด้านล่าง

---

## 5. Lab 04 — BJT Amplifier Simulator v1 (B1–B8)

### 5.1 สภาพแวดล้อมและที่มาของผลจริง

- **Solver:** ngspice 47 (batch) — version string ที่อ่านจริง:
  `ngspice-47, Build Aug 11 2026   13:49:23`
- **BJT model:** `Q2N3904` — 2N3904 NPN Gummel-Poon card ที่ pin ไว้ใน
  `spice_engine.py` (ไม่พบ Starter Kit ของผู้สอนในเครื่อง จึงระบุพารามิเตอร์
  การ์ดโมเดลไว้ในโค้ดและเอกสาร ไม่ได้เดาค่ารุ่นอื่น)
- **Input fixture:** VCC 12 V, R1 100 kΩ, R2 22 kΩ, RC 2.2 kΩ, RE 1 kΩ,
  RL 10 kΩ, Cin = Cout = 10 µF, source 10 mV peak @ 1 kHz, **ไม่มี emitter
  bypass capacitor**, AC sweep 10 Hz–1 MHz (20 points/decade)
- **คำสั่งรันจริง:** `ngspice -b -o run.log -r run.raw circuit.cir`
  ผ่าน `subprocess.run([...], shell=False, timeout=20.0, cwd=run_dir)`
  โดย `run_dir` เป็น `tempfile.mkdtemp()` แยกสำหรับทุกการรัน
- **ที่มาของกราฟ:** อ่าน `run.raw` (ASCII) ที่ solver เขียนออกมาเท่านั้น
  AC แปลงเป็น complex array แล้วคำนวณ `VDB(6)-VDB(5)` และ `VP(6)-VP(5)`
  (Vin = node 5, Vout = node 6); transient อ่าน `time, v(5), v(6)`;
  DC อ่าน operating point จาก raw (fallback `run.log`)
- **การแยก provenance:** ผล SPICE มีป้าย engine/model/run status/jำนวนจุด
  และ `<details>` สำหรับ netlist / run.log / ตัวอย่าง run.raw
  ผล Analytical จาก `dc_bias.py` แสดงอีกชุดหนึ่ง ไม่บังคับให้เท่าทุกหลัก
- **Tool สำหรับ browser acceptance:** ใช้ **OpenCode in-app Browser (Chromium)**
  ผ่าน navigate/snapshot/select/fill/click/evaluate/console เพราะ
  **Playwright MCP ไม่ได้เปิดเผยใน session นี้** จึงไม่มีการอ้างว่าเป็นผล
  Playwright MCP
- **หลักฐานภาพ:** ตามคำสั่งของผู้ใช้ **ยังไม่ได้แคป screenshot Lab 04**
  หลักฐานที่บันทึกจึงเป็น DOM/status/ตัวเลข/ข้อความ error/netlist/log ไม่ใช่ภาพ

### 5.2 ตารางผล B1–B8

| Case | Method / Tool | Input | Expected / Reference | Observed | Evidence | Status |
|---|---|---|---|---|---|---|
| **B1 · Regression** | OpenCode in-app Browser, POST `/calculate` จริง | Analytical: Divider 12 V/100 kΩ/22 kΩ/1 kΩ; Fixed RB=1000 kΩ; Emitter RB=1000 kΩ, RE=1 kΩ | ค่า Lab 03 เดิม: Divider `VCE 8.052 V, IC 1.230 mA`; Fixed `9.514 V, 1.130 mA`; Emitter `8.705 V, 1.026 mA` | Divider **8.052 V / 1.230 mA**; Fixed **9.514 V / 1.130 mA**; Emitter **8.705 V / 1.026 mA**; สลับโหมดได้ | DOM result table + ข้อ 1 ของเอกสารนี้; no screenshot (deferred) | **PASS** |
| **B2 · DC SPICE** | Browser → Flask → ngspice `.op` | CE reference defaults, Analysis mode = `DC · ngspice .op` | แสดง VB/VE/VC/VCE/IC/IE จาก solver พร้อม engine/model/status | **VB 2.004 V, VE 1.333 V, VC 9.087 V, VCE 7.754 V, IC 1.324 mA, IE 1.333 mA**; status **Success**; model **2N3904**; engine **ngspice 47 (batch)** | engine bar + result rows + `<details>` netlist/run.log/raw op block | **PASS** |
| **B3 · Change RE** | Browser, แก้ RE เพียงค่าเดียวแล้วรัน `.op` ซ้ำ | เหมือน B2 แต่ RE = 1 kΩ → **1.5 kΩ** | operating point ต้องเปลี่ยน ไม่ใช่ค่าค้าง | **VCE 7.754 → 8.591 V**; **IC 1.324 → 0.919 mA** | ผลก่อน/หลังจากสอง POST + netlist ของแต่ละรัน | **PASS** |
| **B4 · AC** | Browser, ngspice `.ac` + SVG | CE reference, sweep 10 Hz–1 MHz, Vin=node 5 / Vout=node 6 | แกน `Frequency (Hz)`, `Gain (dB)`, `Phase (°)`; มีอ้างอิง −3 dB หรือข้อความ “not determined in sweep range” | **101 solver points**; peak gain **4.89 dB**; cutoff **not determined in sweep range**; sample 10 Hz → **4.77 dB, −167.0°**; series `gain:101`, `phase:101` | SVG axes/ticks + note “Vin = node 5, Vout = node 6” + raw array | **PASS** |
| **B5 · Transient** | Browser, ngspice `.tran` | source **10 mV peak @ 1 kHz** | time/Vin/Vout พร้อมหน่วย และ Vin–Vout กลับเฟส | **3008 solver points**; Vin peak **10.00 mV**; Vout peak **17.60 mV**; sample มีค่า Vin/Vout ตรงข้ามเครื่องหมาย | DOM numeric summary + plot data table จาก raw | **PASS** |
| **B6 · Change Source** | Browser, แก้ amplitude แล้วรัน `.tran` ซ้ำ | amplitude **10 mV → 20 mV** (frequency เดิม 1 kHz) | waveform/peak ต้องเปลี่ยนตาม input ไม่ใช่กราฟ hard-code | Vin peak **10.00 → 20.00 mV**; Vout peak **17.60 → 35.19 mV** | ผลก่อน/หลัง + series จำนวนเดิม 3008 จุด แต่ค่าต่างกัน | **PASS** |
| **B7 · Invalid / Fail** | Browser, กรอก RE=0 แล้ว submit | `RE = 0 Ω` | error ชัดเจน ไม่มีผล Success หรือกราฟเก่าค้าง | ข้อความ **`re ต้องมากกว่า 0`**; `data-status="error"`; **0 plot / 0 series / 0 result row** | DOM error banner + absence checks | **PASS** |
| **B8 · UI** | OpenCode in-app Browser + Impeccable detector | desktop viewport จริง **1397×886**; หลัง polish ตรวจ SPICE mode, หน่วย, busy state และรัน AC ซ้ำ; mobile ~390 px | หน่วย/ปุ่ม/กราฟอ่านได้ ไม่มี overflow หรือ console error; mobile ต้องตรวจจริงจึงจะผ่าน | `scrollWidth === clientWidth === 1382`, overflow elements **0**, console errors **0**; plot width **848 px**; bias selector disabled + hidden `mode=divider`; unit label อัปเดตเป็น `Ω`; busy state `aria-busy=true`, ปุ่ม disabled, ข้อความ `ngspice running…`; AC rerun **Success / 101 points**. Mobile: detector `390×844` ได้ `[]` และมี breakpoint 1099/760 px แต่ **ยังไม่ได้จำลอง viewport ใน browser จริง** | browser `evaluate`/`console` + Impeccable detect JSON | **PASS (desktop)** / **NOT RUN (mobile ~390 px)** |

### 5.3 ทำไม B4/B5/B6 จึงพิสูจน์ว่ากราฟไม่ใช่ Mock Data

1. ทุกการรันสร้าง `circuit.cir` ใหม่ใน temp dir แยก และเรียก solver แบบ batch ด้วย
   argument list ไม่ใช้ `shell=True`; netlist/log/raw เปิดดูได้ใน `<details>`
2. จำนวนจุดใน SVG ตรงกับจำนวนจุดใน `run.raw` (AC 101, transient 3008)
   และแกน/series ถูกสร้างจาก array ที่ parser อ่าน ไม่มี literal waveform ใน `plots.py`
3. เปลี่ยนค่าเดียวแล้วผลเปลี่ยนจริง: RE 1→1.5 kΩ เปลี่ยน VCE/IC (B3),
   amplitude 10→20 mV เปลี่ยน Vin/Vout peak (B6) — ค่าคงที่ในโค้ดทำไม่ได้
4. กรณี solver ไม่พร้อม/timeout/output ว่าง/raw ไม่มีจุด ระบบแสดง Error และล้างกราฟ
   ไม่มีสถานะ Success ค้าง (B7)
5. Cutoff คำนวณจากการข้าม −3 dB เท่านั้น ถ้า sweep ไม่ข้ามจะได้ข้อความ
   `not determined in sweep range` ไม่ได้แต่งตัวเลขขึ้นมา

### 5.4 Impeccable — critique → polish → audit

- ติดตั้ง project scope ด้วย
  `npx -y impeccable install -y --providers=opencode --scope=project`;
  ใช้ launcher `.opencode\skills\impeccable\scripts\impeccable.cmd`
- **Critique:** dual-agent (user pre-authorized autonomous execution จึงข้าม interview)
  คะแนน **21/40 (Acceptable)** —
  `.impeccable/critique/2026-11-24T10-48-11Z__templates-index-html.md`
- **Polish (UI-only):** ปิด bias selector ในโหมด SPICE และส่ง hidden `mode=divider`,
  busy state ตอนกด Run, unit label อัปเดตสด, placeholder สั้นลงสำหรับ 390 px,
  focus ring เปลี่ยนเป็นสีน้ำเงินอ่านง่าย
- **Audit หลัง polish:** **16/20 (Good)** —
  `.impeccable/audit/2026-11-24T10-53-16Z__templates-index-html.md`
- **Detector:** source `flat-type-hierarchy` เป็น false positive เพราะ detector
  ตาม `url_for('static', filename='style.css')` ไม่ได้; rendered URL scan ที่
  `1280x800` และ `390x844` ได้ `[]` ทั้งสองขนาด
- **สิ่งที่ไม่แต่ง:** สมการ `dc_bias.py`, ข้อมูล/แกนกราฟ, และการ์ดโมเดล BJT
- **ยังค้างจาก audit (ไม่บล็อกส่งงาน):** P1 ข้อความ error ยังแสดง raw solver text
  ควรมี recovery hint ด้านบน; P2 ตารางข้อมูลกราฟอยู่ใน `<details>`, ไม่มี skip link/
  การประกาศเปลี่ยน analysis, และ plot `min-width: 520px` ต้องเลื่อนแนวนอนบนจอแคบ

### 5.5 ชุดทดสอบอัตโนมัติปัจจุบัน

คำสั่ง: `python -m unittest discover -s tests`

```
Ran 90 tests in 1.413s

OK
```

แบ่งเป็น `test_dc_bias.py` 22 tests (Lab 03), `test_web.py` เดิม 28 tests,
และ tests ของ SPICE/web/adapter/plot อีก 40 tests รวม Lab 04
รันบนโค้ด commit `9863a82` และใช้ยืนยันอีกครั้งก่อน push

### 5.6 ความคลาดเคลื่อนและข้อจำกัด

- **B1:** |ΔIC| ≤ 0.01 mA และ |ΔVCE| ≤ 0.02 V; ผลจริงตรงที่ทศนิยม 3 ตำแหน่ง (Δ = 0.000)
- **B2–B3:** ผล SPICE ไม่บังคับเท่า Analytical (คนละสมมติฐาน: BJT model เทียบ β/VBE คงที่)
  จึงตรวจ “มาจาก solver จริง + เปลี่ยนตาม RE” มากกว่าบังคับเลขเท่ากัน
- **B4:** sweep 10 Hz–1 MHz ไม่ครอมจุดข้าม −3 dB จึงรายงานตามความจริงว่า
  `not determined in sweep range`
- **B5–B6:** ตรวจ peak และทิศทางสัญญาณจาก raw data; ไม่ได้ใช้คาดหวังเป็นค่าคงที่
- **B8:** เฉพาะ desktop ที่รันจริงใน browser; mobile ~390 px เป็น **NOT RUN**
  เพราะ tool ใน session ไม่มี viewport emulation — มีแค่ CLI detector และ CSS breakpoint
- SPICE v1 รองรับเฉพาะ CE Voltage Divider อ้างอิง; ไม่มี bypass capacitor,
  ไม่มี AC/transient ของ Fixed/Emitter, ไม่มี circuit editor
- ตามคำสั่งผู้ใช้ยังไม่แคป screenshot Lab 04; หลักฐานก่อน/หลัง UI จึงเป็น
  critique/audit snapshot + DOM value ไม่ใช่ภาพ

### 5.7 ใครทำอะไร (AI สร้าง/แก้ — นักศึกษาตรวจ)

- AI เขียน adapter/netlist/parser/plot, เพิ่ม analysis mode และปรับ UI ตาม critique
  ภายใต้ขอบเขตที่นักศึกษากำหนด (SPICE เฉพาะ CE Voltage Divider)
- นักศึกษาตรวจ input fixture และหน่วยว่า netlist ใช้ 12 V/100 kΩ/22 kΩ/2.2 kΩ/1 kΩ/10 kΩ
  และ source 10 mV @ 1 kHz ตรงใบงาน ไม่ใช่ค่าที่เดาไว้ล่วงหน้า
- นักศึกษาตรวจ B1 เทียบ Lab 03, ตรวจ B3/B6 ว่าผลเปลี่ยนเมื่อเปลี่ยน RE/amplitude,
  และตรวจ B7 ว่า error ไม่ทิ้งกราฟ Success ค้าง
- นักศึกษาอนุมัติให้ใช้การ์ด 2N3904 มาตรฐาน (ไม่มี Starter Kit ของผู้สอน),
  อนุมัติให้ polish เฉพาะ UI และสั่งเลื่อน screenshot Lab 04 ตามลำดับ

### 5.8 คำตอบสั้นสำหรับตรวจรายบุคคล

1. **Python ส่งอะไรให้ ngspice และรับผลกลับมาอย่างไร?**

   `app.py` ตรวจอินพุตแล้ว `spice_engine.py` เขียน netlist หนึ่งไฟล์ต่อ analysis
   ใน temp dir แยก เรียก `subprocess.run([ngspice, "-b", "-o", "run.log", "-r",
   "run.raw", "circuit.cir"], shell=False, timeout=20.0, cwd=run_dir)` แล้วอ่าน
   `run.raw` (ASCII) เป็น array; DC มี operating point, AC มี VDB/VP complex,
   transient มี time/v(5)/v(6) ผลถูกส่งเป็น provenance + SVG ให้ Browser แสดง

2. **เหตุใด `.ac` และ `.tran` ไม่ใช่สิ่งเดียวกัน?**

   `.ac` เป็น small-signal frequency sweep ได้ Gain dB/Phase vs frequency
   (ที่นี่อ้าง Vin node 5, Vout node 6) ส่วน `.tran` แก้สมการตามเวลาด้วยแหล่ง
   `SIN` จริง ได้ waveform Vin/Vout, peak และทิศทางกลับเฟส คนละ domain
   (frequency เทียบ time) และคนละคำสั่งวิเคราะห์

3. **เปลี่ยน Amplitude แต่กราฟไม่เปลี่ยน ตรงไหนก่อน?**

   ดูที่ provenance/ข้อมูลก่อน: netlist มี `SIN(...)` amplitude ใหม่หรือไม่,
   `run.raw` มี `v(5)` peak เปลี่ยนหรือไม่, และ series ใน plot มาจาก array นั้นจริงไหม
   ถ้า raw เปลี่ยนแต่กราฟไม่เปลี่ยน แปลว่า plot ใช้ค่าเก่า/hard-code; ถ้า raw ไม่เปลี่ยน
   แปลว่ายังไม่ได้รันใหม่หรือฟอร์มส่งค่าผิด

4. **Impeccable เปลี่ยนอะไรได้ และไม่ควรเปลี่ยนอะไร?**

   เปลี่ยนได้เฉพาะ UI-related files: layout, responsiveness, label/unit, focus ring,
   error state, busy state, provenance readability ห้ามเปลี่ยนสมการ `dc_bias.py`,
   ข้อมูล/แกนจาก solver, การ์ดโมเดล, หรือแทนที่กราฟจริงด้วยภาพตัวอย่าง

5. **รู้ได้อย่างไรว่า Bode Plot เป็นผลจำลองจริง ไม่ใช่ Mock Data?**

   เพราะ netlist และ `run.log`/`run.raw` ของรันนั้นเปิดดูได้, จุดกราฟ 101 จุดตรงกับ
   จุดใน raw, มี engine/model/status กำกับ, เปลี่ยน RE/amplitude แล้วค่าตอบสนองเปลี่ยน,
   และถ้า solver ไม่รันระบบแสดง Error + ล้างกราฟ ไม่มี Success ปลอม

### 5.9 แหล่งอ้างอิง

- ใบงาน ENG29 2121 Lab 04 (B1–B8, input fixture, −3 dB rule, submission checklist)
- `README_Lab3_baseline.txt` และ `docs/evidence/lab03/` สำหรับ baseline A1–A5
- ngspice Documentation / User Manual — Batch Mode `-b -o -r`
- Impeccable for coding agents — critique / polish / audit (OpenCode provider)
- Superpowers — brainstorm / plan / execute / verify / review workflow
- Flask Official Docs — routes, templates, error handling

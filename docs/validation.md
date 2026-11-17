# Validation — การตรวจสอบผลลัพธ์กับค่าคำนวณอิสระ

## 1. ค่าอ้างอิงจากโจทย์ (คำนวณมือ)

`VCC = 12 V, R1 = 100 kΩ, R2 = 22 kΩ, RC = 2.2 kΩ, RE = 1 kΩ, β = 100, VBE = 0.70 V`

| ขั้น | สมการ | ผล |
|---|---|---|
| VTH | 12 × 22k / (100k + 22k) | **2.16393 V** |
| RTH | 100k × 22k / 122k | **18,032.79 Ω** |
| IB | (2.16393 − 0.70) / (18032.79 + 101 × 1000) | **12.2986 µA** |
| IC | 100 × 12.2986 µA | **1.22986 mA** |
| IE | 101 × 12.2986 µA | **1.24216 mA** |
| VE | 1.24216 mA × 1 kΩ | **1.24216 V** |
| VB | 1.24216 + 0.70 | **1.94216 V** |
| VC | 12 − 1.22986 mA × 2.2 kΩ | **9.29431 V** |
| VCE | 9.29431 − 1.24216 | **8.05216 V** |

## 2. ผลจาก Web App

หน้าเว็บแสดง:

| ปริมาณ | ค่าที่แสดง |
|---|---|
| VB | 1.942 V |
| VE | 1.242 V |
| VC | 9.294 V |
| VCE | 8.052 V |
| IC | 1.230 mA |
| IB | 12.30 µA |
| IE | 1.242 mA |
| VTH | 2.164 V |
| RTH | 18,032.79 Ω |
| สภาวะ | Forward Active |

ผลตรงกับค่าคำนวณมือภายในความคลาดเคลื่อนจากการปัดเศษ (< 0.1 %)

## 3. การตรวจสอบผ่าน HTTP

```
GET  /            -> 200, พบฟอร์ม "Calculate DC Bias"
POST /calculate   -> 200, พบ VCE 8.052 / IC 1.230 / Forward Active
POST /calculate (vcc="abc") -> 400, ข้อความ "ต้องเป็นตัวเลข", หน้าไม่ล้ม
POST /calculate (r2=5kΩ)    -> แสดง Cutoff + Warning "แบบจำลองใช้ไม่ได้"
```

## 4. Automated Tests

```
python -m unittest discover -s tests -v
Ran 18 tests in 0.589s
OK
```

- Engineering: ค่าอ้างอิง/Thevenin/กระแส/แรงดัน, validation (R, β, VCC, VBE),
  Cutoff, Saturation
- HTTP: GET form, POST ผลจาก backend, การแปลงหน่วย Ω/kΩ, ผลไม่ hard-code,
  non-numeric, R = 0, ฟิลด์หาย, Cutoff warning

## 5. ข้อจำกัดของแบบจำลอง

- ใช้ β และ VBE คงที่ (Forward-Active approximation) ไม่ใช่ SPICE
- ค่า VCE ใกล้ 0.2 V หรือ VTH ≤ VBE ต้องอ่าน Warning ก่อนใช้ผล
- ค่าที่อยู่นอก Forward-Active ไม่ถือเป็นผลที่เชื่อถือได้

---

# Lab 03 — สามโหมดไบอัส

## 6. ค่าอ้างอิงอิสระ (คำนวณมือก่อนรัน)

ใช้ร่วมทุกกรณี: `VCC = 12 V, RC = 2.2 kΩ, β = 100, VBE = 0.70 V`

### A1 · Voltage Divider (ค่าจาก Lab 2 เดิม)
`R1 = 100 kΩ, R2 = 22 kΩ, RE = 1 kΩ`

| ปริมาณ | คำนวณมือ | เกณฑ์ |
|---|---|---|
| IC | 1.22986 mA | ผลก่อนแก้ 1.229858 mA |
| VCE | 8.05216 V | ผลก่อนแก้ 8.052155 V |

### A2 · Fixed Bias
`RB = 1 MΩ = 1000 kΩ`

```
IB = (12 − 0.70) / 1e6 = 11.30 µA
IC = 100 × 11.30 µA = 1.13000 mA
VE = 0 V, VB = 0.700 V
VC = 12 − 1.130 mA × 2.2 kΩ = 9.514 V
VCE = 9.514 − 0 = 9.514 V
```

### A3 · Emitter Bias
`RB = 1 MΩ = 1000 kΩ, RE = 1 kΩ`

```
IB = 11.30 / (1e6 + 101 × 1e3) = 10.263397 µA
IC = 1.026340 mA, IE = 1.036603 mA
VE = 1.036603 V, VB = 1.736603 V
VC = 9.742053 V, VCE = 8.705450 V
```

### A4 · เปลี่ยน RE เป็น 2 kΩ

```
IB = 11.30 / (1e6 + 101 × 2e3) = 9.400998 µA
IC = 0.940100 mA (ลดลงจาก A3 เพราะตัวหารเพิ่มขึ้น)
VCE = 8.032779 V
```

## 7. ผลตรวจ A1–A5 จาก Browser จริง

วิธีตรวจ: **OpenCode Browser** (เครื่องมือ `browser_*` ใน OpenCode Desktop)
เกณฑ์: |ΔIC| ≤ 0.01 mA, |ΔVCE| ≤ 0.02 V เทียบกับค่าอ้างอิงที่ยังไม่ปัดเศษ

| กรณี | อินพุต | ค่าคาดหมาย | เห็นจริง | วิธีตรวจ | สถานะ |
|---|---|---|---|---|---|
| A1 โหมดเดิม | Divider · R1=100 kΩ, R2=22 kΩ, RE=1 kΩ | IC 1.22986 mA · VCE 8.05216 V | IC **1.230 mA** · VCE **8.052 V** | OpenCode Browser | **PASS** |
| A2 Fixed | Fixed · RB=1000 kΩ | IC 1.13000 mA · VCE 9.51400 V | IC **1.130 mA** · VCE **9.514 V** | OpenCode Browser | **PASS** |
| A3 Emitter | Emitter · RB=1000 kΩ, RE=1 kΩ | IC 1.02634 mA · VCE 8.70545 V | IC **1.026 mA** · VCE **8.705 V** | OpenCode Browser | **PASS** |
| A4 เปลี่ยนค่าเดียว | Emitter · RE=2 kΩ (ที่เหลือเท่า A3) | IC ลดลง · 0.94010 mA · VCE 8.03278 V | IC **0.940 mA** (ลดจาก 1.026) · VCE **8.033 V** | OpenCode Browser | **PASS** |
| A5 อินพุตผิด | Fixed · RB=0 | แจ้งแก้ RB, ไม่ล่ม, ไม่โชว์ผลเก่า | ข้อความ **"RB ต้องมากกว่า 0 Ω"**, ไม่มีตารางผล | OpenCode Browser | **PASS** |

หลักฐานหน้าเว็บ (full-page screenshot จาก OpenCode Browser):
`docs/evidence/A1-browser.png`, `A2-browser.png`, `A3-browser.png`,
`A4-browser.png`, `A5-browser.png` และ `A5-fixed-invalid.png` (จากรอบก่อน)

### บั๊กที่พบและแก้ระหว่างรันจริง

ตอนเลือกโหมดแล้วกด "เปลี่ยนโหมด / โหลดฟอร์มใหม่" ตอนช่องยังว่าง **ไม่เกิด POST**
เพราะปุ่มเป็น `type="submit"` แต่ทุกช่องมี `required` → browser บล็อกการ submit
แก้โดยเติม `formnovalidate` ที่ปุ่ม (`templates/index.html`) พร้อม regression test
`test_change_mode_button_skips_required_field_validation` (`tests/test_web.py`)
หลังแก้ รัน A1–A5 ใหม่ผ่าน Browser ได้ครบ และผลยังตรงค่าอ้างอิงเดิมทุกกรณี

ข้อสังเกตขณะตรวจ:
- หลังเลือกโหมดและกด "เปลี่ยนโหมด / โหลดฟอร์มใหม่" ฟอร์มจะโหลดใหม่ให้เห็นเฉพาะช่องที่ใช้
  (Fixed: RB, Emitter: RB+RE, Divider: R1+R2+RE) และลบผลรอบก่อนออกจากหน้า
- ผล Fixed/Emitter ไม่แสดง VTH/RTH เพราะไม่มี Thevenin equivalent
- การตรวจ A4 ต้องรันใหม่หลังเปลี่ยน RE เท่านั้น ค่า IC เปลี่ยนจริงจึงยืนยันว่า RE ไหลถึงสมการ

## 8. Automated Tests (After Lab 03)

```
.venv\Scripts\python.exe -m unittest discover -s tests -v
Ran 31 tests ... OK
```

เพิ่มจาก Lab 02: unit test ของ Fixed/Emitter (ค่าอ้างอิง, validation, cutoff,
saturation, A4) และ HTTP test ของโหมดใหม่ (mode ไม่รู้จัก, RB=0, เปลี่ยนโหมด,
ปุ่มเปลี่ยนโหมดข้าม required field validation)

## 9. บทบาท MCP (อธิบายเพิ่ม)

- `browser-acceptance-check` (ถ้ามี) เป็น Skill ที่บอกว่าต้องตรวจอะไรและรายงานหลักฐานอะไร
- **OpenCode Browser** คือเครื่องมือที่ใช้จริงในรอบนี้ (แทน Playwright MCP)
  เป็นชั้นที่ OpenCode เรียกเพื่อเปิด URL/กรอกฟอร์ม/อ่าน snapshot จากหน้าเว็บ
- เบราว์เซอร์คุยกับ Flask ด้วย HTTP (`POST /calculate`) แล้ว Flask เรียกฟังก์ชัน Python
  ไม่ต้องติดตั้ง Playwright ใน `requirements.txt`
- ข้อจำกัด: การอ่านโค้ดหรือส่ง curl **ไม่ถือว่า** เป็นการรัน browser case
  จึงใช้ snapshot จากหน้าเว็บเป็นหลักฐานในการตัดสิน PASS/FAIL

# BJT DC Bias Web App — ENG29 2121 Lab 03

Flask Web Application สำหรับคำนวณ **DC Operating Point** ของวงจรขยาย BJT
Common-Emitter (NPN) ด้วยแบบจำลอง Forward-Active Approximation (β และ VBE คงที่)
ต่อยอดจาก Lab 2 โดยเลือกได้ 3 โหมด: **Voltage Divider Bias**, **Fixed Bias**
และ **Emitter Bias แบบแหล่งจ่ายเดียว** (ผล Divider เดิมไม่เปลี่ยน)

## โครงสร้างโปรเจกต์

```
.
├── app.py                  # Flask application & HTTP routes
├── dc_bias.py              # Engineering calculations (ไม่รู้จัก HTML/HTTP)
├── templates/
│   └── index.html          # Input form + DC results (Jinja)
├── static/
│   └── style.css           # Responsive layout
├── tests/
│   ├── test_dc_bias.py     # Unit tests ของสมการวิศวกรรม
│   └── test_web.py         # Flask HTTP route tests
├── docs/
│   ├── design-note.md      # บันทึกการออกแบบ
│   ├── validation.md       # ค่าอ้างอิงอิสระ + ตาราง A1–A5 (Lab 02/03)
│   ├── evidence/           # หลักฐานจากหน้าเว็บ
│   ├── reflection.md       # สิ่งที่ได้เรียนรู้
│   └── superpowers/        # spec + plan ของ Lab 03
├── requirements.txt
├── AGENTS.md               # แนวทางสำหรับ AI coding agent
└── README.md
```

## ความต้องการของระบบ

- Python 3.9 ขึ้นไป (ทดสอบด้วย Python 3.15)
- Flask 3.1.3 (ติดตั้งจาก `requirements.txt`)

## ติดตั้งและรัน

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m flask --app app run --debug
```

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m flask --app app run --debug
```

เปิด Browser ที่ **http://127.0.0.1:5000/**

> ต้องเปิดผ่าน Flask (localhost) เท่านั้น ไม่ใช่ double-click เปิด
> `templates/index.html` เพราะการคำนวณเกิดที่ Python Backend

## รัน Automated Tests

```bash
python -m unittest discover -s tests -v
```

## แบบจำลองและสมการ

ตัวแปรเข้าร่วมทุกโหมด: `VCC [V]`, `RC [Ω]`, `β`, `VBE [V]`
ตัวต้านทานเลือกหน่วย Ω หรือ kΩ ได้บนฟอร์ม (1 MΩ = 1000 kΩ)

**Voltage Divider Bias** (เพิ่ม `R1, R2, RE`)
```
VTH = VCC × R2 / (R1 + R2)
RTH = R1·R2 / (R1 + R2)
IB  = (VTH − VBE) / (RTH + (β + 1)·RE)
```

**Fixed Bias** (เพิ่ม `RB`, Emitter ลงกราวด์โดยตรง)
```
IB = (VCC − VBE) / RB
VE = 0 V
```

**Emitter Bias แบบแหล่งจ่ายเดียว** (เพิ่ม `RB, RE`)
```
IB = (VCC − VBE) / [RB + (β + 1)·RE]
```

สมการร่วม: `IC = β·IB`, `IE = (β+1)·IB`, `VE = IE·RE` (Fixed ใช้ 0),
`VB = VE + VBE`, `VC = VCC − IC·RC`, `VCE = VC − VE`

ค่าที่แสดง: `VB, VE, VC, VCE [V]`, `IC, IE [mA]`, `IB [µA]`
เฉพาะโหมด Divider แสดง `VTH [V]`, `RTH [Ω]` ด้วย
ตาราง "ค่าที่ใช้คำนวณ" แสดงเฉพาะตัวต้านทานของโหมดที่เลือกหลังแปลงเป็น Ω แล้ว

> วิธีใช้: เลือกโหมดใน Dropdown แล้วกด **เปลี่ยนโหมด / โหลดฟอร์มใหม่**
> ระบบจะแสดงเฉพาะช่องที่โหมดนั้นใช้ แล้วกรอกค่ากด **Calculate DC Bias**

## ตัวอย่างอ้างอิง

`VCC=12 V, R1=100 kΩ, R2=22 kΩ, RC=2.2 kΩ, RE=1 kΩ, β=100, VBE=0.70 V`

| ปริมาณ | ค่า |
|---|---|
| VTH | 2.164 V |
| RTH | 18,032.79 Ω |
| IB | 12.30 µA |
| IC | 1.230 mA |
| IE | 1.242 mA |
| VB | 1.942 V |
| VE | 1.242 V |
| VC | 9.294 V |
| VCE | 8.052 V |

ผลนี้อยู่ใน Forward-Active Region และตรงกับการคำนวณมือ
(ดูรายละเอียดใน `docs/validation.md`)

## Input Validation และ Warning

- ค่าไม่ครบ / ไม่ใช่ตัวเลข / ไม่ใช่จำนวนจำกัด → แสดง Error ภาษาไทย (HTTP 400)
- `VCC ≤ 0`, ความต้านทานที่โหมดนั้นใช้ ≤ 0, `β ≤ 0`, `VBE ≤ 0` → แจ้ง Error
- โหมดไม่รู้จัก → แจ้ง Error (ไม่เดาว่าเป็น Divider)
- Divider: `VTH ≤ VBE` / Fixed-Emitter: `VCC ≤ VBE` → แจ้ง **Cutoff**
- `VCE ≤ VCE(sat) ≈ 0.2 V` → แจ้ง **Saturation** ค่าที่ได้ไม่น่าเชื่อถือ
- `VCE` ใกล้ Saturation → แจ้งเตือนเพิ่มเติม
- เมื่อ Error เกิดขึ้น หน้าเว็บจะไม่แสดงผลของรอบก่อน

## ตรวจผลผ่าน Browser (Lab 03)

ดูตาราง **A1–A5**, ค่าอ้างอิงอิสระ และหลักฐานหน้าเว็บได้ใน
[`docs/validation.md`](docs/validation.md)
ผลรันจริงผ่าน OpenCode Browser: A1–A5 ผ่านทั้งหมด
(IC 1.230 / 1.130 / 1.026 / 0.940 mA, VCE 8.052 / 9.514 / 8.705 / 8.033 V)

## ข้อจำกัด (ขอบเขต Lab 03)

- ใช้ Forward-Active Approximation (β, VBE คงที่) ไม่ใช่ SPICE/ngspice
- ไม่มี AC Analysis, Bode Plot, Transient, DC Load Line หรือตัวเก็บประจุ Bypass
- รองรับเฉพาะ NPN 3 โหมดที่กำหนดในใบงาน
- ไม่ต้องเขียน Playwright script; ใช้ Browser Tool ของ OpenCode ตรวจผลแทน

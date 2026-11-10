# BJT DC Bias Web App — ENG29 2121 Lab 02

Flask Web Application สำหรับคำนวณ **DC Operating Point** ของวงจรขยาย BJT
Common-Emitter แบบ **Voltage-Divider Bias** (NPN) ด้วยแบบจำลอง
Forward-Active Approximation (β และ VBE คงที่)

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
│   ├── validation.md       # การตรวจสอบผลกับค่าคำนวณอิสระ
│   └── reflection.md       # สิ่งที่ได้เรียนรู้
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

ตัวแปรเข้า: `VCC [V]`, `R1, R2, RC, RE [Ω]` (เลือกหน่วย Ω หรือ kΩ ได้บนหน้าเว็บ),
`β`, `VBE [V]`

```
VTH = VCC × R2 / (R1 + R2)
RTH = R1·R2 / (R1 + R2)
IB  = (VTH − VBE) / (RTH + (β + 1)·RE)
IC  = β·IB
IE  = (β + 1)·IB
VE  = IE·RE
VB  = VE + VBE
VC  = VCC − IC·RC
VCE = VC − VE
```

ค่าที่แสดง: `VB, VE, VC, VCE [V]`, `IC, IE [mA]`, `IB [µA]`
พร้อม `VTH [V]`, `RTH [Ω]` และค่าตัวต้านทานที่แปลงเป็น Ω แล้ว

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

- ค่าไม่ครบ / ไม่ใช่ตัวเลข → แสดงข้อความ Error ภาษาไทย ไม่ทำให้หน้าเว็บล้ม (HTTP 400)
- `VCC ≤ 0`, `R ≤ 0`, `β ≤ 0`, `VBE` ไม่อยู่ระหว่าง 0 กับ VCC → แจ้ง Error
- `VTH ≤ VBE` → แจ้งว่า Transistor อยู่สภาวะ **Cutoff** และแบบจำลองใช้ไม่ได้
- `VCE ≤ VCE(sat) ≈ 0.2 V` → แจ้งว่า **Saturation** ค่าที่ได้ไม่น่าเชื่อถือ
- `VCE` ใกล้ Saturation → แจ้งเตือนเพิ่มเติม

## ข้อจำกัด (ขอบเขต Lab 02)

- ใช้ Forward-Active Approximation (β, VBE คงที่) ไม่ใช่ SPICE/ngspice
- ไม่มี AC Analysis, Bode Plot, Transient, Signal Generator
- รองรับเฉพาะ NPN Voltage-Divider Bias เท่านั้น
  (Bias แบบอื่นจะเพิ่มในสัปดาห์ถัดไป)

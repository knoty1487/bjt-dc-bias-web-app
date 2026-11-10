# Design Note — BJT DC Bias Web App (Lab 02)

## บริบทและเหตุผล

Lab 02 ต้องการ Web Application จริงที่นักศึกษาเขียนเอง เพื่อให้เห็นภาพว่า
Frontend (Browser/HTML), Backend (Python/Flask) และ Engineering Logic
(`dc_bias.py`) ทำงานร่วมกันอย่างไร ก่อนจะต่อยอดเป็น Virtual Transistor
Laboratory ในสัปดาห์ถัดไป

## เป้าหมาย

- เปิดผ่าน `http://127.0.0.1:5000/` และกรอกค่า `VCC, R1, R2, RC, RE, β, VBE` ได้
- Python Backend คำนวณ DC Operating Point จริง (ไม่ hard-code) แล้วแสดง
  `VB, VE, VC, VCE, IC` พร้อมหน่วย (เพิ่ม `IB, IE, VTH, RTH`)
- มี Validation, Warning เมื่ออยู่นอก Forward-Active Region
- มี Automated Tests ครบทั้ง engineering และ HTTP
- Commit/Push ผ่าน Git/GitHub

## สิ่งที่ไม่ทำ (Non-goals)

- AC Analysis, Bode Plot, Transient, Signal Generator, Overlay Animation
- Bias Type อื่น (Fixed, Emitter) และ FET
- SPICE/ngspice Solver

## ข้อจำกัด

- เวลาปฏิบัติการ 180 นาที (Build 75 นาที)
- แบบจำลอง Forward-Active: β และ VBE คงที่
- ต้องแยกไฟล์ตามโครงสร้างที่ Lab กำหนด (multi-file)

## ทางเลือกที่พิจารณา

1. **Flask หลายไฟล์ — เลือกใช้**
   ตรงตามข้อกำหนด Lab ทุกข้อ, รองรับ Flask test client, เรียนรู้ได้ในเวลาคาบ
2. **HTML + JavaScript คำนวณฝั่ง Browser — ไม่ใช้**
   ผิดเกณฑ์ A2 ที่ต้องให้ Python Backend เป็นผู้คำนวณ และทดสอบ HTTP ไม่ได้
3. **FastAPI / Django — ไม่ใช้**
   ต้องมี frontend แยกหรือโครงสร้างใหญ่เกินเวลาเรียน 2–3 ชั่วโมง

## การตัดสินใจสำคัญ

- ตัวต้านทานทุกตัวมี **ตัวเลือกหน่วย Ω / kΩ ต่อช่อง** (ตามที่อาจารย์กำหนด)
  แล้วแปลงเป็น Ω ก่อนคำนวณ — แสดงค่าที่แปลงแล้วให้ผู้ใช้ตรวจสอบ
- Route: `GET /` แสดงฟอร์ม, `POST /calculate` คำนวณและแสดงผล
- ข้อมูลผิด → HTTP 400 พร้อมข้อความภาษาไทย (หน้าไม่ล้ม)
- `VTH ≤ VBE` → รายงาน Cutoff (IC = 0, VCE = VCC) พร้อม Warning
- `VCE ≤ 0.2 V` → รายงาน Saturation + Warning ว่าแบบจำลองใช้ไม่ได้
- `0.2 V < VCE < 0.3 V` → เตือนว่าใกล้ Saturation

## โครงสร้าง

```
Browser (form)
   │ POST /calculate
   ▼
app.py ── parse/validate/unit conversion ──► dc_bias.py (สมการ)
   │                                              │
   └──────── render index.html ◄──────────────────┘
```

## การทดสอบ

- `tests/test_dc_bias.py` — ค่าอ้างอิงจากโจทย์, validation, cutoff, saturation
- `tests/test_web.py` — GET form, POST ผลลัพธ์จริง, การแปลงหน่วย,
  ผลไม่ hard-code, error 400, warning

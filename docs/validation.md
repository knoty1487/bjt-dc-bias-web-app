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

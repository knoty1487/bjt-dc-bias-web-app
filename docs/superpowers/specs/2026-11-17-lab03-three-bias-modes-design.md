# Lab 03 — สามโหมดไบอัสบนเว็บเดิม

## Intent
ต่อยอด Flask app จาก Lab 2 ให้เลือกโหมด Fixed / Emitter / Divider ได้ โดยไม่สร้างเว็บใหม่
และไม่เปลี่ยนผล Divider เดิม

## Goals
- แยกฟังก์ชันคำนวณ Fixed และ Emitter ใน `dc_bias.py` ใช้โครงสร้างผลร่วมกับ Divider
- `app.py` เลือกฟังก์ชันด้วย `if/elif` ตรวจเฉพาะฟิลด์ที่โหมดนั้นใช้ แปลง kΩ→Ω ที่เดียว
- ฟอร์มและผลระบุโหมด ช่องที่ไม่เกี่ยวข้องถูกdisabled ไม่โชว์ผลเก่าเมื่ออินพุตผิด
- ตรวจ A1–A5 ใน browser จริงด้วย OpenCode Browser (หรือแจ้ง NOT RUN หากใช้ไม่ได้)

## Non-goals / Anti-goals
- ไม่เขียน SPICE, AC/Transient, DC Load Line, ตัวเก็บประจุ Bypass
- ไม่ย้ายสมการเข้า HTML, ไม่สร้างโปรเจกต์ใหม่, ไม่ลบ tests เดิม
- ไม่เดาว่าโหมดไม่รู้จักคือ Divider

## Constraints
- ใช้ `.venv` เดิม, Flask เดิม, Python 3.15
- SI ภายใน `dc_bias.py`: V, A, Ω; แสดง IC เป็น mA
- ผล Divider เดิมต้องตรงกับ A1 baseline: IC = 1.229858 mA, VCE = 8.052155 V
- เกณฑ์ tolerance: |ΔIC| ≤ 0.01 mA, |ΔVCE| ≤ 0.02 V

## Approaches
1. **แก้โปรเจกต์เดิม (เลือก)** — ใช้ app.py/dc_bias.py/templates เดิม เพิ่มสาขาใหม่ เสี่ยงต่ำสุด
2. โปรเจกต์ใหม่แยก — ขัดกับใบงานและต้องย้าย tests/Config ซ้ำ
3. ย้ายสมการเข้า template — ขัดกับ AGENTS.md และตรวจสอบยาก

## Design
- `BiasResult` เพิ่ม `vth`/`rth` เป็น optional (ใช้เฉพาะ Divider) และ `mode`
- `calculate_fixed_bias(vcc, rb, rc, beta, vbe)`, `calculate_emitter_bias(vcc, rb, re, rc, beta, vbe)`
- ตรวจอย่างเดียวกัน: ค่าที่ต้องเป็นบวก ≤ 0 → InvalidInputError; numerator ≤ 0 → cutoff warning; VCE ≤ 0.2 → saturation warning
- ฟอร์มมี `<select name="mode">` + ปุ่ม "เปลี่ยนโหมด" (action=change_mode) และปุ่มคำนวณ
- ขึ้นอยู่กับโหมด: Fixed แสดง RB, Emitter แสดง RB+RE, Divider แสดง R1+R2+RE; RC/VCC/β/VBE แสดงทุกโหมด
- ผล: VTH/RTH แสดงเฉพาะ Divider; ตาราง resistor แสดงเฉพาะที่ใช้

## ค่าอ้างอิงอิสระ (คำนวณมือ)
| กรณี | IC | VCE |
|---|---|---|
| A1 Dividerเดิม | 1.22986 mA | 8.05216 V |
| A2 Fixed RB=1 MΩ | 1.13000 mA | 9.51400 V |
| A3 Emitter RB=1 MΩ, RE=1 kΩ | 1.02634 mA | 8.70545 V |
| A4 Emitter RE=2 kΩ | 0.94010 mA | 8.03277 V |

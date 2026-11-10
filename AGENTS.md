# AGENTS.md — AI Coding Conventions

แนวทางสำหรับ AI coding agent ที่ทำงานกับโปรเจกต์นี้ (ENG29 2121 Lab 02)

## กติกาหลัก

1. **แยกความรับผิดชอบของไฟล์**
   - `dc_bias.py` เก็บเฉพาะสมการ DC Bias — ห้าม import Flask, HTML หรือ HTTP
   - `app.py` จัดการ HTTP/validation/แปลงหน่วย แล้วเรียกฟังก์ชันใน `dc_bias.py`
   - `templates/index.html` ห้ามฝังสมการฟิสิกส์ — แสดงผลจาก context เท่านั้น
   - `static/style.css` ดูแลหน้าตาเท่านั้น (ไม่มี logic)

2. **หน่วย (Units)**
   - ภายใน `dc_bias.py` ใช้ SI เสมอ: โวลต์ (V), แอมแปร์ (A), โอห์ม (Ω)
   - การแปลง kΩ → Ω และการแสดง mA/µA ทำที่ชั้น `app.py`/template
   - ต้องแสดงหน่วยกำกับทุกค่าที่ผู้ใช้เห็น

3. **Validation & Warning**
   - ค่าผิด (≤ 0, ไม่ใช่ตัวเลข, ไม่ครบ) ต้องถูกปฏิเสธพร้อมข้อความที่อ่านเข้าใจ
   - สภาวะนอก Forward-Active ต้องมี Warning ชัดเจน ห้ามรายงานว่าแบบจำลองใช้ได้

4. **Tests**
   - ทุกการแก้สมการต้องมี/ปรับ unit test ใน `tests/test_dc_bias.py`
   - ทุกการแก้ route/template ต้องมี/ปรับ test ใน `tests/test_web.py`
   - รัน `python -m unittest discover -s tests -v` ให้ผ่านก่อน commit ทุกครั้ง

5. **ข้อห้าม**
   - ห้าม hard-code ผลลัพธ์ลง HTML
   - ห้าม commit `.venv/`, `.env`, API keys, credentials
   - ห้ามเพิ่มฟีเจอร์นอกขอบเขต (AC, Bode, Transient, SPICE) ใน Lab นี้

## Commit Message

ใช้รูปแบบสั้นชัดเจน เช่น:

```
Add DC bias calculation module with unit tests
Add Flask route and results template
Fix input validation message for missing fields
```

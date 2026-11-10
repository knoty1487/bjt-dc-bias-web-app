# Design — ปรับ UI ให้ใกล้ภาพตัวอย่างใน Handout (Lab 02)

วันที่: 2026-11-10
สถานะ: รออนุมัติ
ประเภทงาน: small change (ปรับ presentation layer เท่านั้น)

## ทำไม

อาจารย์เปรียบเทียบหน้าจอที่รันจริงกับภาพตัวอย่างใน handout (หน้า 01B) แล้วเห็นว่า
หน้าตาต่างกันมาก แม้ค่าที่คำนวณจะถูกต้องก็ตาม ตัวเลขในภาพตัวอย่างเป็น
"ค่าประกอบภาพ" ตามที่ handout ระบุไว้เอง (บรรทัด 14) จึงไม่แก้ตัวเลข
แก้เฉพาะหน้าตาให้สื่อ "Virtual Lab" แบบเดียวกับภาพ

## เป้าหมาย

- หน้าจอมีโครงเดียวกับภาพ: header bar → 3 คอลัมน์ (ค่าอุปกรณ์ | วงจร | ผลลัพธ์) → footer
- มีวงจร BJT วาดด้วย SVG และตัวเลขบนวงจรเปลี่ยนตามค่าที่ผู้ใช้พิมพ์
- มีแบนเนอร์สถานะการทำงานขนาดใหญ่ พร้อมเหตุผลเชิงตัวเลข
- ค่าที่คำนวณยังคงเป็นค่าที่ถูกต้อง (1.230 mA / 8.052 V / Active) ไม่แตะ `dc_bias.py`

## ไม่ใช่เป้าหมาย (Non-goals)

- ไม่เปลี่ยนตัวเลขให้ตรงกับภาพตัวอย่าง (ผิดหลักวงจร)
- ไม่เพิ่ม dropdown หน่วยแยกทีละช่อง — คง dropdown เดียวใช้ร่วมกัน 4 ตัวต้านทาน
  ตามที่ตกลงไว้ในดีไซน์เดิม
- ไม่เพิ่ม Fixed Bias / Emitter Bias / AC / Transient / Bode / SPICE
- ไม่เพิ่ม JavaScript framework — ใช้ vanilla JS ในไฟล์ `static/app.js` เท่านั้น
- ไม่แตะ validation, region thresholds, หรือ API shape ของ `/calculate`

## ข้อจำกัด

- ต้องรันได้โดยไม่ต้องมี JS (progressive enhancement): ค่าบนวงจรมีค่าเริ่มต้นจาก
  server-rendered form values ถ้า JS ถูกปิด วงจรยังแสดงค่าที่ถูกต้องของรอบก่อนหน้า
- ต้อง responsive: 3 คอลัมน์ ≥ 1100px, 2 คอลัมน์ 760–1100px, 1 คอลัมน์ < 760px
- ห้ามใช้ `|safe` หรือ bypass Jinja autoescaping
- เทสต์เดิม 24 ตัวต้องผ่านทั้งหมด

## ทางเลือกที่พิจารณา

| ทาง | ลักษณะ | ข้อดี | ข้อเสีย |
|---|---|---|---|
| A | 3 คอลัมน์ + วงจร + header + footer + dropdown หน่วยแยกช่อง | เหมือนภาพที่สุด | ขัดดีไซน์เดิมที่ตกลงว่าใช้หน่วยร่วม, ฟอร์มซับซ้อนขึ้น |
| **B (เลือก)** | 3 คอลัมน์ + วงจร + header + footer, คง dropdown หน่วยเดียว | ได้หน้าตาแบบภาพโดยไม่รื้อดีไซน์ | ยังต่างจากภาพตรงช่องหน่วย |
| C | ปรับแค่สี/ฟอนต์ | เร็ว | ยังไม่เหมือนภาพ |

เลือก B เพราะตอบโจทย์ "ใกล้ภาพ" โดยไม่ผิด decision เดิม และไม่เพิ่มความซับซ้อน
ของฟอร์มที่ผู้ใช้ต้องกรอก

## ดีไซน์

### โครงหน้า (`templates/index.html`)

```
<header class="site-header">
  ชื่อ + คำอธิบายวิชา            [badge: Computer Programming for EE]
</header>

<main class="layout">            grid: 360px | minmax(360px, 1fr) | 340px
  <form class="card">            ค่าอุปกรณ์ (เดิม + unit dropdown เดียว)
  <section class="card">         วงจร SVG + ค่า R ที่กำกับ
  <section class="card">         ผลลัพธ์ + region banner
</main>

<footer class="goal-strip">      Week 2 Goal + คำอธิบายสั้น
</footer>
```

### วงจร SVG

- `static/circuit.svg` ไม่ใช้ — ฝัง SVG inline ใน template เพื่อให้ JS อ่าน/เขียนได้
- องค์ประกอบ: ราง VCC ด้านบน, R1 (ซ้ายบน), R2 (ซ้ายล่าง → ground), RC (ขวาบน),
  ตัวทรานซิสเตอร์ NPN (กลาง), RE (ขวาล่าง → ground), ป้ายค่า `R1 = 100 kΩ` ฯลฯ
- ป้ายค่ามี `id`: `c-vcc`, `c-r1`, `c-r2`, `c-rc`, `c-re`, `c-beta`
- ค่าเริ่มต้น render จากฝั่ง server ด้วย `form.*` + `unit_label` (ทำงานได้แม้ไม่มี JS)

### Live update (`static/app.js`)

- ฟัง `input` บนช่อง VCC/R1/R2/RC/RE/β และ `change` บน dropdown หน่วย
- เขียนค่าลงป้าย `c-*` ตามรูปแบบ `${value} ${unit}` (ค่าว่าง → แสดง `—`)
- ไม่คำนวณ DC ใด ๆ ฝั่ง client — ตัวเลขผลลัพธ์ยังมาจาก Python เท่านั้น

### Region banner

แทน badge เดิมด้วยบล็อกใหญ่ `div.region-banner[data-region]`:

| region | ข้อความ | สี |
|---|---|---|
| active | `Active region approximation OK` + `VCE = 8.052 V > 1.0 V` | เขียว |
| near-saturation | `ใกล้ขอบอิ่มตัว` + `0.3 V < VCE = … < 1.0 V` | เหลือง |
| saturation | `Saturation` + `VCE = … ≤ 0.3 V` | แดง |
| cutoff | `Cutoff` + `VTH = … ≤ VBE = …` | แดง |

ข้อความเหตุผลสร้างจากค่าจริงที่คำนวณได้ (ไม่ hard-code) — ใส่ใน `dc_bias.py`
เป็น `region_reason` ใหม่ หรือประกอบใน template จาก `result` (เลือกอย่างหลัง
เพื่อไม่แตะ API ของ module วิศวกรรม)

### CSS (`static/style.css`)

- คงพาเลตต์เดิม (navy/blue/teal/paper) ซึ่งใกล้ภาพอยู่แล้ว
- เพิ่ม `.site-header`, `.goal-strip`, `.circuit`, `.region-banner`
- `td { overflow-wrap: anywhere; }` แก้ minor ที่ค้างจาก review

## สิ่งที่ตัดสินใจแล้ว (ของผม ไม่ใช่ของคุณ)

- วงจรอัปเดตตัวเลขตามที่พิมพ์ (ไม่ใช่ภาพนิ่ง)
- ไม่เพิ่มไลบรารี/ฟอนต์ภายนอก — ใช้ system font stack เดิม
- เก็บ `data-region` ไว้เป็น hook ของ CSS และเทสต์

## สิ่งที่เหลือให้ผู้สร้างตัดสิน

- ตำแหน่ง/ขนาดตัวอักษรของป้ายบน SVG ให้อ่านง่ายบนจอเล็ก
- จะย่อ SVG ด้วย `viewBox` เท่าไร

## ผลกระทบต่อเทสต์

- `test_page_links_stylesheet` ยังผ่าน
- `test_results_show_units_and_warning` ต้องอัปเดต: เดิมหา `class="region-badge"`
  → เปลี่ยนเป็น `class="region-banner"` (ยังมี `data-region`)
- เพิ่มเทสต์ใหม่: มี `<svg` ในหน้า, มีข้อความ `Active region approximation OK`,
  และป้าย `c-r1` มีค่าตามฟอร์ม

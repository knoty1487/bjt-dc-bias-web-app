"""Build B6814946_Lab3.docx on the Desktop from the verified Lab 03 results."""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "docs" / "evidence"
DESKTOP = Path(r"C:\Users\B6814946\Desktop")
OUT = DESKTOP / "B6814946_Lab3.docx"

GITHUB_URL = "https://github.com/knoty1487/bjt-dc-bias-web-app"
COMMIT_SHA = "ae6d37fb4379dd236f072fc76b934a7aa0dc0573"

doc = Document()

# ---- Thai-capable default font ----
style = doc.styles["Normal"]
style.font.name = "Tahoma"
style.font.size = Pt(11)
style._element.rPr.rFonts.set(qn("w:eastAsia"), "Tahoma")

for section in doc.sections:
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)


def heading(text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.name = "Tahoma"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "Tahoma")
    return h


def para(text, bold=False, size=11, color=None, align=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    r.font.size = Pt(size)
    r.font.name = "Tahoma"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "Tahoma")
    if color:
        r.font.color.rgb = RGBColor(*color)
    if align is not None:
        p.alignment = align
    return p


def bullet(text):
    p = doc.add_paragraph(text, style="List Bullet")
    for r in p.runs:
        r.font.name = "Tahoma"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Tahoma")
    return p


def code_block(lines):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    for i, line in enumerate(lines):
        if i:
            p.add_run("\n")
        r = p.add_run(line)
        r.font.name = "Consolas"
        r.font.size = Pt(9.5)
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Tahoma")
    return p


def make_table(headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        r = hdr[i].paragraphs[0].add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        r.font.name = "Tahoma"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Tahoma")
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(val))
            r.font.size = Pt(9)
            r.font.name = "Tahoma"
            r._element.rPr.rFonts.set(qn("w:eastAsia"), "Tahoma")
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Inches(w)
    return t


# ======================= COVER =======================
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title.add_run("รายงาน Lab 03")
r.bold = True
r.font.size = Pt(24)
r.font.name = "Tahoma"
r._element.rPr.rFonts.set(qn("w:eastAsia"), "Tahoma")

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = sub.add_run("BJT DC Bias Web App — สามโหมดไบอัสและการตรวจผลผ่าน Browser")
r.font.size = Pt(13)
r.font.name = "Tahoma"
r._element.rPr.rFonts.set(qn("w:eastAsia"), "Tahoma")

para("")

make_table(
    ["รายการ", "ข้อมูล"],
    [
        ["วิชา / รหัส", "ENG29 2121"],
        ["รหัสนักศึกษา", "B6814946"],
        ["ชื่อไฟล์รายงาน", "B6814946_Lab3.docx"],
        [" localhost URL", "http://127.0.0.1:5000/"],
        ["GitHub URL", GITHUB_URL],
        ["Commit SHA (Lab 03)", COMMIT_SHA],
        ["วิธีตรวจผลจริง", "OpenCode Browser (browser_* tools) — ไม่ใช่ Playwright MCP"],
        ["เกณฑ์ยอมรับ", "|ΔIC| ≤ 0.01 mA, |ΔVCE| ≤ 0.02 V เทียบค่าอ้างอิงที่ยังไม่ปัดเศษ"],
    ],
    widths=[1.7, 5.0],
)

para("")
para(
    "หมายเหตุ: โปรเจกต์นี้เป็นการต่อยอดเว็บ Flask จาก Lab 2 เดิม (ไม่ได้สร้างเว็บใหม่) "
    "ผล Divider เดิมยังคงตรงกับค่าอ้างอิงเดิมทุกประการ",
    size=10,
)

doc.add_page_break()

# ======================= 1. สรุปสิ่งที่ทำ =======================
heading("1. สรุปสิ่งที่ทำ", 1)
bullet("เพิ่ม 2 โหมดใหม่ใน dc_bias.py: Fixed Bias (calculate_fixed_bias) และ Emitter Bias (calculate_emitter_bias) พร้อมตรวจสอบอินพุต")
bullet("เพิ่มตัวเลือกโหมดในหน้าเว็บ และให้ฟอร์มแสดงเฉพาะช่องที่ใช้ตามโหมดที่เลือก (templates/index.html)")
bullet("เพิ่มการเลือกฟังก์ชันตามโหมดและการแปลงหน่วย kΩ/Ω ใน app.py")
bullet("รันทดสอบ A1–A5 ด้วย Browser จริง ทุกกรณี เก็บภาพหน้าจอใส่รายงานนี้")
bullet("พบและแก้บั๊กปุ่ม \"เปลี่ยนโหมด\" ที่ไม่ submit เพราะ required fields บล็อก — เติม formnovalidate และเขียน regression test")
bullet("รันชุดทดสอบอัตโนมัติ 31 รายการ ผ่านทั้งหมด และ Commit/Push ขึ้น origin/main แล้ว")

# ======================= 2. ตาราง A1–A5 =======================
heading("2. ผลตรวจ A1–A5 จาก Browser จริง", 1)
para(
    "วิธีตรวจ: เปิด http://127.0.0.1:5000/ → browser_snapshot อ่านช่อง → browser_select_option เลือกโหมด "
    "→ กด \"เปลี่ยนโหมด\" → snapshot ใหม่ → fill_form ตามหน่วยบนฟอร์ม → กด \"Calculate DC Bias\" "
    "→ browser_evaluate อ่านตารางผลจาก DOM → browser_take_screenshot เก็บหลักฐาน",
    size=10,
)
para("")

make_table(
    ["กรณี", "อินพุต (หน่วยตามฟอร์ม)", "ค่าคาดหมาย (อิสระ)", "ผลที่เห็นจริง", "วิธี", "สถานะ"],
    [
        [
            "A1 โหมดเดิม",
            "Divider · VCC 12 V, R1 100 kΩ, R2 22 kΩ, RC 2.2 kΩ, RE 1 kΩ, β 100, VBE 0.70 V",
            "IC 1.22986 mA\nVCE 8.05216 V",
            "IC 1.230 mA\nVCE 8.052 V\nForward Active",
            "OpenCode Browser",
            "PASS",
        ],
        [
            "A2 Fixed",
            "Fixed · RB 1000 kΩ (= 1 MΩ) · ไม่กรอก RE",
            "IC 1.13000 mA\nVCE 9.51400 V",
            "IC 1.130 mA\nVCE 9.514 V\nForward Active",
            "OpenCode Browser",
            "PASS",
        ],
        [
            "A3 Emitter",
            "Emitter · RB 1000 kΩ, RE 1 kΩ",
            "IC 1.026340 mA\nVCE 8.705450 V",
            "IC 1.026 mA\nVCE 8.705 V\nForward Active",
            "OpenCode Browser",
            "PASS",
        ],
        [
            "A4 เปลี่ยนค่าเดียว",
            "Emitter · เหมือน A3 แต่ RE = 2 kΩ (ตัวอื่นคงเดิม)",
            "IC ลดลงจาก A3\nIC 0.940100 mA\nVCE 8.032779 V",
            "IC 0.940 mA (ลดจาก 1.026)\nVCE 8.033 V\nForward Active",
            "OpenCode Browser",
            "PASS",
        ],
        [
            "A5 อินพุตผิด",
            "Fixed · RB = 0",
            "แจ้งแก้ RB, เว็บไม่ล่ม,\nไม่แสดงผลเดิมเป็นผลรอบนี้",
            "ข้อความ \"ข้อมูลไม่ถูกต้อง: RB ต้องมากกว่า 0 Ω\"\nไม่มีตารางผล (HTTP 400)",
            "OpenCode Browser",
            "PASS",
        ],
    ],
    widths=[0.9, 2.0, 1.3, 1.5, 1.0, 0.5],
)

para("")
para(
    "การเทียบผล: ทุกกรณีผลต่าง IC อยู่ในช่วง ±0.001 mA และ VCE อยู่ในช่วง ±0.001 V "
    "ซึ่งอยู่ภายใต้เกณฑ์ |ΔIC| ≤ 0.01 mA และ |ΔVCE| ≤ 0.02 V ทุกกรณี",
    size=10,
)
para(
    "A5: ข้อความที่เห็นมาจาก Flask (app.py จับ InvalidInputError แล้วส่งกลับมาพร้อม HTTP 400) "
    "ไม่ใช่การที่ browser บล็อกฟอร์ม — หลังเพิ่ม formnovalidate ฟอร์มส่ง RB=0 ถึง Flask จริงแล้วจึงได้ข้อความนี้ "
    "และหน้าไม่แสดงผลของรอบก่อน (ตารางผลหายไป)",
    size=10,
)

doc.add_page_break()

# ======================= 3. หลักฐานภาพหน้าจอ =======================
heading("3. หลักฐานจากหน้าเว็บ (Screenshot)", 1)
para(
    "ภาพด้านล่างเป็น full-page screenshot ที่ถ่ายจาก OpenCode Browser หลังส่งฟอร์มแต่ละกรณี "
    "(เก็บใน repository ที่ docs/evidence/)",
    size=10,
)
for case in ["A1", "A2", "A3", "A4", "A5"]:
    path = EVIDENCE / f"{case}-browser.png"
    heading(f"{case} — ผลจาก browser", 2)
    if path.exists():
        doc.add_picture(str(path), width=Inches(5.8))
        para(f"หลักฐาน: docs/evidence/{case}-browser.png", size=9)
    else:
        para(f"[ไม่พบไฟล์ {path}]", size=9)

doc.add_page_break()

# ======================= 4. ค่าอ้างอิงอิสระ =======================
heading("4. ค่าอ้างอิงอิสระ (คำนวณมือก่อนรัน)", 1)
para(
    "ใช้ร่วมทุกกรณี: VCC = 12 V, RC = 2.2 kΩ, β = 100, VBE = 0.70 V "
    "(แบบจำลอง Forward-Active: β และ VBE คงที่)",
    size=10,
)

heading("A1 · Voltage Divider (ค่าจาก Lab 2 เดิม)", 2)
code_block([
    "R1 = 100 kΩ, R2 = 22 kΩ, RE = 1 kΩ",
    "VTH = 12 × 22 / (100 + 22)          = 2.16393 V",
    "RTH = 100 × 22 / 122                = 18.03279 kΩ",
    "IB  = (2.16393 − 0.70) / (18032.79 + 101×1000) = 12.2986 µA",
    "IC  = 100 × 12.2986 µA              = 1.22986 mA",
    "IE  = 101 × 12.2986 µA              = 1.24216 mA",
    "VE  = 1.24216 mA × 1 kΩ             = 1.24216 V",
    "VC  = 12 − 1.22986 mA × 2.2 kΩ      = 9.29431 V",
    "VCE = 9.29431 − 1.24216             = 8.05216 V",
])

heading("A2 · Fixed Bias", 2)
code_block([
    "RB = 1 MΩ, emitter ต่อกราวด์ (VE = 0)",
    "IB  = (12 − 0.70) / 1e6             = 11.30 µA",
    "IC  = 100 × 11.30 µA                = 1.13000 mA",
    "VC  = 12 − 1.130 mA × 2.2 kΩ        = 9.514 V",
    "VCE = VC − VE = 9.514 − 0           = 9.514 V",
])

heading("A3 · Emitter Bias", 2)
code_block([
    "RB = 1 MΩ, RE = 1 kΩ",
    "IB  = (12 − 0.70) / (1e6 + 101×1e3) = 10.263397 µA",
    "IC  = 100 × IB                      = 1.026340 mA",
    "IE  = 101 × IB                      = 1.036603 mA",
    "VE  = IE × 1 kΩ                     = 1.036603 V",
    "VC  = 12 − IC × 2.2 kΩ              = 9.742053 V",
    "VCE = VC − VE                       = 8.705450 V",
])

heading("A4 · เปลี่ยน RE เป็น 2 kΩ", 2)
code_block([
    "RB = 1 MΩ, RE = 2 kΩ (ที่เหลือเท่า A3)",
    "IB  = (12 − 0.70) / (1e6 + 101×2e3) = 9.400998 µA",
    "IC  = 100 × IB                      = 0.940100 mA",
    "VE  = IE × 2 kΩ                     = 1.898902 V",
    "VCE = VC − VE                       = 8.032779 V",
])

doc.add_page_break()

# ======================= 5. คำตอบคำถาม =======================
heading("5. คำตอบคำถามในใบงาน", 1)

heading("5.1 A4 — ทำนายก่อนรันว่ IC จะเพิ่มหรือลด", 2)
para(
    "คำทำนาย: IC จะลดลงจาก A3",
    bold=True,
)
para(
    "เหตุผลสั้น ๆ: ใน Emitter Bias, IB = (VCC − VBE) / [RB + (β+1)·RE] เมื่อเพิ่ม RE จาก 1 kΩ เป็น 2 kΩ "
    "ตัวหารจะเพิ่มขึ้น (จาก 1.101 MΩ เป็น 1.202 MΩ) ทำให้ IB ลดลง และ IC = β·IB จึงลดลงตามด้วย "
    "เป็นผลของ negative feedback จาก RE (กระแส IE ไหลผ่าน RE ทำให้ VE สูงขึ้น ลดแรงดันตกกระจายบน RB "
    "และลด VBE ที่ขับฐาน)",
)
para(
    "ผลจริง: IC ลดจาก 1.026 mA (A3) เป็น 0.940 mA (A4) ตรงกับคำทำนาย และ VCE เปลี่ยนจาก 8.705 V เป็น 8.033 V",
)

heading("5.2 คำถามปิด Lab", 2)
para(
    "\"ถ้าตัวเลขคำนวณมือถูก แต่เปลี่ยน RE แล้วผลบนหน้าเว็บไม่เปลี่ยน "
    "คุณจะตรวจค่าที่ส่งจากฟอร์มและค่าที่เข้าไปในฟังก์ชันอย่างไร?\"",
    bold=True,
)
para("แนวทางตรวจทีละชั้น (ไล่ตามเส้นทางข้อมูล ไม่แก้สมequation ทันที):")
bullet("ดู snapshot หลังกดคำนวณ ว่าหน้าเปลี่ยนจริงหรือเป็นผลค้างจากรอบก่อน (ตรวจ title/โหมด/ตารางผล)")
bullet("ดู network log ว่ามี POST /calculate เกิดขึ้นไหม ถ้าไม่มี แปลว่าฟอร์มไม่ได้ส่ง — ตรวจปุ่ม/required/error ของ browser (กรณีนี้เจอปุ่มเปลี่ยนโหมดถูก required บล็อก)")
bullet("ตรวจ name ของช่อง RE ในฟอร์ม (name=\"re\") ว่าตรงกับสิ่งที่ Flask อ่านผ่าน request.form.get(\"re\") — ถ้าชื่อไม่ตรงค่า will เป็นว่าง")
bullet("ตรวจหน่วย: unit_re = kohm หรือ ohm แล้วดูการแปลงใน _read_resistance() ว่า value × _UNITS[unit] ได้ 1000 Ω หรือ 2000 Ω ตามที่กรอก")
bullet("ตรวจว่าค่า re ถูกเก็บลง resistors dict แล้วส่งเข้า calculate_emitter_bias(vcc, rb, re, rc, beta, vbe) — ไม่ใช่ส่ง Calculate_dc_bias ของ Divider")
bullet("พิมพ์/ดูค่า IB = (VCC − VBE)/[RB + (β+1)·RE] ภายในฟังก์ชัน ว่าตัวหารเปลี่ยนตาม RE หรือไม่")
bullet("รัน unit test ที่เปลี่ยน RE เท่านั้น (test_larger_emitter_resistor_reduces_ic) ถ้า test still ผ่านแต่ browser ไม่เปลี่ยน แสดงว่าปัญหาอยู่ที่ชั้นฟอร์ม/HTTP ไม่ใช่สมการ")
para(
    "หลักการ: ถ้าผลไม่เปลี่ยน ให้สงสัย \"ค่าส่งไม่ถึง\" หรือ \"ส่งแล้วแต่หน้าแสดงผลเก่า\" ก่อนสงสัยสมการ "
    "เพราะสมการคำนวณมือถูกอยู่แล้ว — แก้ทีละจุดแล้วรันกรณีที่เกี่ยวข้องซ้ำ",
    size=10,
)

heading("5.3 อธิบายบทบาท MCP", 2)
para(
    "ในรอบนี้ใช้ OpenCode Browser (เครื่องมือ browser_* ใน OpenCode Desktop) แทน Playwright MCP "
    "เพราะโปรเจกต์ไม่ได้ตั้งค่า Playwright MCP ไว้ (จึง 기록 Playwright MCP เป็น NOT RUN พร้อมเหตุผลนี้) "
    "การตรวจจริงประกอบด้วย browser_navigate เปิด URL, browser_snapshot อ่านโครงสร้างช่อง, "
    "browser_select_option/click เปลี่ยนโหมด, browser_fill_form กรอกค่า, browser_click กดคำนวณ, "
    "browser_evaluate อ่านผลจาก DOM และ browser_take_screenshot เก็บหลักฐาน",
)
bullet("MCP (Model Context Protocol) คือมาตรฐานที่ให้ AI เรียกเครื่องมือภายนอก เช่น Browser แทนการเดาโค้ด")
bullet("Skill browser-acceptance-check (ถ้ามี) เป็นเพียงคำสั่งบอกว่าต้องตรวจอะไรและรายงานหลักฐานอะไร — ไม่ได้เปิด browser เอง")
bullet("สถานะ \"connected\" ของ MCP อย่างเดียวไม่พอ ต้องเรียก tool แล้วได้ snapshot/ผลจากหน้าเว็บจริงจึงนับว่าผ่าน")
bullet("การอ่านโค้ดหรือส่ง curl แทน ไม่ถือเป็นการรัน browser case")

heading("5.4 สิ่งที่ AI สร้าง / นักศึกษาตรวจ", 2)
make_table(
    ["ส่วน", "ใครทำ", "รายละเอียด"],
    [
        ["โค้ด Fixed/Emitter bias ใน dc_bias.py", "AI เขียน", "นักศึกษาตรวจสมการ IB, IC, VCE เทียบค่าคำนวณมือ A2–A4"],
        ["mode dispatch + แปลงหน่วยใน app.py", "AI เขียน", "นักศึกษาตรวจชื่อฟิลด์/หน่วย/ฟังก์ชันที่ถูกเรียกตามโหมด"],
        ["ฟอร์มตามโหมดใน index.html", "AI เขียน", "นักศึกษาลองเลือกโหมดดูว่าช่องเปลี่ยนและผลเก่าหาย"],
        ["ค่าอ้างอิง A1–A5 ในตาราง", "นักศึกษากำหนด", "ใช้สมการวิชา Engineering Electronics คำนวณอิสระ ไม่เอาโค้ดมาเป็นคำตอบ"],
        ["รัน browser + อ่านผล + เก็บภาพ", "AI รันจริง", "นักศึกษาเปิดเว็บเองซ้ำอย่างน้อย 1 กรณีเพื่อทวนผล"],
        ["บั๊กปุ่มเปลี่ยนโหมด", "AI พบและแก้", "นักศึกษาทดสอบว่าปุ่มโหลดฟอร์มได้โดยไม่ต้องกรอกค่าก่อน"],
    ],
    widths=[2.2, 1.1, 3.4],
)

doc.add_page_break()

# ======================= 6. ตำแหน่งโค้ด =======================
heading("6. ตำแหน่งเลือกฟังก์ชันและแปลงหน่วยในโค้ด", 1)
para("ไฟล์ app.py — ตำแหน่งสำคัญ:", bold=True, size=10)
code_block([
    "_UNITS = {\"ohm\": 1.0, \"kohm\": 1000.0}          # บรรทัด 26",
    "_MODE_FIELDS = {                                # บรรทัด 27-31",
    "    MODE_DIVIDER: (\"r1\", \"r2\", \"re\"),",
    "    MODE_FIXED:   (\"rb\",),",
    "    MODE_EMITTER: (\"rb\", \"re\"),",
    "}",
    "def _read_resistance(form, field):              # บรรทัด 57-63",
    "    value = _read_number(form, field, label)",
    "    unit  = form.get(f\"unit_{field}\", \"ohm\")",
    "    return value * _UNITS[unit]                 # แปลง kΩ -> Ω ที่นี่",
    "",
    "# calculate() บรรทัด 128-137 — เลือกฟังก์ชันตามโหมด",
    "if   mode == MODE_DIVIDER: result = calculate_dc_bias(vcc, r1, r2, rc, re, beta, vbe)",
    "elif mode == MODE_FIXED:   result = calculate_fixed_bias(vcc, rb, rc, beta, vbe)",
    "else:                      result = calculate_emitter_bias(vcc, rb, re, rc, beta, vbe)",
])
para("ไฟล์ dc_bias.py — สมการหลัก:", bold=True, size=10)
code_block([
    "calculate_fixed_bias()   บรรทัด 186-198 : IB = (VCC − VBE) / RB, VE = 0",
    "calculate_emitter_bias() บรรทัด 201-214 : IB = (VCC − VBE) / [RB + (β+1)·RE]",
    "_operating_point()       บรรทัด 90-128  : IC = β·IB, VCE = VCC − IC·RC − IE·RE",
    "_validate_resistor()     บรรทัด 63-65   : ตรวจ R > 0 -> \"RB ต้องมากกว่า 0 Ω\"",
])

para("")
heading("7. วิธีรันและตรวจซ้ำ", 1)
code_block([
    "cd \"C:\\Users\\B6814946\\Documents\\GitHub\\BJT DC Bias Web App\"",
    ".venv\\Scripts\\python.exe -m flask --app app run --port 5000",
    "เปิด http://127.0.0.1:5000/",
    ".venv\\Scripts\\python.exe -m unittest discover -s tests -v   # 31 tests OK",
])
para(f"GitHub: {GITHUB_URL}", size=10)
para(f"Commit SHA: {COMMIT_SHA}", size=10)

para("")
para(
    "หมายเหตุการแก้ไขระหว่างรันจริง: ก่อนแก้ ปุ่ม \"เปลี่ยนโหมด\" เป็น type=submit แต่ช่องมี required "
    "ทำให้ browser ไม่ส่งฟอร์มเมื่อยังว่าง ผลคือโหมดไม่เปลี่ยน — แก้ด้วย formnovalidate ที่ปุ่ม "
    "และเพิ่ม regression test แล้วรัน A1–A5 ใหม่ผ่านทั้งหมด (ผลยังตรงเดิม)",
    size=10,
)

DESKTOP.mkdir(parents=True, exist_ok=True)
doc.save(OUT)
print(f"Saved: {OUT}")
print(f"Size: {OUT.stat().st_size} bytes")

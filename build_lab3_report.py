"""Build the Lab 03 report from the verified results in this repository."""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "docs" / "evidence" / "lab03"
DESKTOP = Path(r"C:\Users\B6814946\Desktop")
OUT = DESKTOP / "B6814946_Lab3.docx"
FALLBACK = DESKTOP / "B6814946_Lab3_updated.docx"

GITHUB_URL = "https://github.com/ottoponrod/BJT-DC-Bias-Web-App"
COMMIT_SHA = "24f157f079127c860e21d92818c164fdaf9b7762"

doc = Document()

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
        ["ชื่อไฟล์รายงาน", OUT.name],
        ["localhost URL", "http://127.0.0.1:5000/"],
        ["GitHub URL", GITHUB_URL],
        ["Commit SHA (Lab 03)", COMMIT_SHA],
        ["วิธีตรวจผลจริง", "OpenCode Browser (browser_* tools) — ไม่ใช่ Playwright MCP"],
        ["เกณฑ์ยอมรับ", "|ΔIC| ≤ 0.01 mA, |ΔVCE| ≤ 0.02 V เทียบค่าอ้างอิงที่ยังไม่ปัดเศษ"],
    ],
    widths=[1.7, 5.0],
)

para("")
para(
    "หมายเหตุ: โปรเจกต์นี้ต่อยอดเว็บ Flask จาก Lab 2 เดิม (ไม่ได้สร้างเว็บใหม่) "
    "โหมด Divider และค่าอ้างอิงเดิมยังคงอยู่ครบ และเพิ่มโหมด Fixed กับ Emitter "
    "เข้าไปในโครงสร้างเดิม",
    size=10,
)

doc.add_page_break()

# ======================= 1. สรุปสิ่งที่ทำ =======================
heading("1. สรุปสิ่งที่ทำ", 1)
bullet("เพิ่ม 2 โหมดใน dc_bias.py: calculate_fixed_bias() และ calculate_emitter_bias() พร้อม validation และ region detection")
bullet("เพิ่ม MODES/MODE_* และ tag โหมดลงใน BiasResult โดยโหมด Divider เดิมให้ผลเหมือนเดิม")
bullet("เพิ่ม dropdown เลือกโหมดใน templates/index.html และให้ฟอร์มแสดงเฉพาะช่องของโหมดนั้น")
bullet("เพิ่ม mode dispatch, การตรวจเฉพาะช่องที่จำเป็น และแปลงหน่วย kΩ/Ω ที่จุดเดียวใน app.py")
bullet("ปุ่ม \"เปลี่ยนโหมด\" ใช้ formnovalidate จึงสลับโหมดได้แม้ยังกรอกไม่ครบ (มี regression test)")
bullet("เขียนเทสต์ก่อนแก้โค้ด (TDD) และรันผ่านทั้งหมด 48 tests")
bullet("รัน A1–A5 ด้วย Browser จริง เก็บ screenshot และบันทึกค่าจริงเทียบค่าคำนวณมือ")
bullet("อัปเดต docs/validation.md และ README พร้อม GitHub URL และ Commit SHA")

# ======================= 2. ตาราง A1–A5 =======================
heading("2. ผลตรวจ A1–A5 จาก Browser จริง", 1)
para(
    "วิธีตรวจ: เปิด http://127.0.0.1:5000/ → อ่านช่องในฟอร์ม → เลือกโหมด → กด "
    "\"เปลี่ยนโหมด\" → กรอกค่าตามหน่วยบนฟอร์ม → กด \"Calculate DC Bias\" "
    "→ อ่านตารางผลจาก DOM → ถ่าย screenshot เก็บหลักฐาน",
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
            "ข้อความ \"RB ต้องมากกว่า 0 Ω\"\nไม่มีตารางผล/แบนเนอร์\nหน้าเว็บยังทำงานปกติ",
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
    "A5: ข้อความที่เห็นมาจาก Flask (dc_bias.py โยน ValidationError แล้ว app.py "
    "แสดงผลในหน้าเดิม) ไม่ใช่การที่ browser บล็อกฟอร์ม — ฟอร์มส่ง RB=0 ถึง Flask จริง "
    "และหน้าไม่แสดงตารางผลของรอบก่อนค้างอยู่",
    size=10,
)

doc.add_page_break()

# ======================= 3. หลักฐานภาพหน้าจอ =======================
heading("3. หลักฐานจากหน้าเว็บ (Screenshot)", 1)
para(
    "ภาพด้านล่างถ่ายจาก OpenCode Browser หลังส่งฟอร์มแต่ละกรณี "
    "(เก็บใน repository ที่ docs/evidence/lab03/)",
    size=10,
)
shots = [
    ("A1", "A1-divider.jpg", "Divider: IC 1.230 mA, VCE 8.052 V"),
    ("A2", "A2-fixed.jpg", "Fixed RB=1 MΩ: IC 1.130 mA, VCE 9.514 V"),
    ("A3", "A3-emitter-re1k.jpg", "Emitter RE=1 kΩ: IC 1.026 mA, VCE 8.705 V"),
    ("A4", "A4-emitter-re2k.jpg", "Emitter RE=2 kΩ: IC 0.940 mA, VCE 8.033 V"),
    ("A5", "A5-fixed-rb0-error.jpg", "Fixed RB=0: error RB ต้องมากกว่า 0 Ω"),
]
for case, filename, caption in shots:
    path = EVIDENCE / filename
    heading(f"{case} — {caption}", 2)
    if path.exists():
        doc.add_picture(str(path), width=Inches(5.9))
        para(f"หลักฐาน: docs/evidence/lab03/{filename}", size=9)
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
    "IB  = (12 − 0.70) / 1e6             = 11.3000 µA",
    "IC  = 100 × 11.3000 µA              = 1.13000 mA",
    "IE  = 101 × 11.3000 µA              = 1.14130 mA",
    "VC  = 12 − 1.130 mA × 2.2 kΩ        = 9.51400 V",
    "VCE = VC − VE = 9.514 − 0           = 9.51400 V",
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
    "IE  = 101 × IB                      = 0.949501 mA",
    "VE  = IE × 2 kΩ                     = 1.899002 V",
    "VC  = 12 − IC × 2.2 kΩ              = 9.931780 V",
    "VCE = VC − VE                       = 8.032779 V",
])

doc.add_page_break()

# ======================= 5. คำตอบคำถาม =======================
heading("5. คำตอบคำถามในใบงาน", 1)

heading("5.1 A4 — ทำนายก่อนรันว่า IC จะเพิ่มหรือลด", 2)
para("คำทำนาย: IC จะลดลงจาก A3", bold=True)
para(
    "เหตุผลสั้น ๆ: ใน Emitter Bias, IB = (VCC − VBE) / [RB + (β+1)·RE] "
    "เมื่อเพิ่ม RE จาก 1 kΩ เป็น 2 kΩ ตัวหารจะเพิ่มขึ้น (จาก 1.101 MΩ เป็น 1.202 MΩ) "
    "ทำให้ IB ลดลง และ IC = β·IB จึงลดลงตาม เป็นผลของ negative feedback จาก RE "
    "(กระแส IE ไหลผ่าน RE ทำให้ VE สูงขึ้น ลดแรงดันตกคร่อม RB และลด VBE ที่ขับฐาน)",
)
para(
    "ผลจริง: IC ลดจาก 1.026 mA (A3) เป็น 0.940 mA (A4) ตรงกับคำทำนาย "
    "และ VCE เปลี่ยนจาก 8.705 V เป็น 8.033 V",
)

heading("5.2 อธิบายบทบาท MCP / Browser", 2)
para(
    "ในรอบนี้ใช้ OpenCode Browser (เครื่องมือ browser_* ใน OpenCode Desktop) แทน Playwright MCP "
    "เพราะโปรเจกต์ไม่ได้ตั้งค่า Playwright MCP ไว้ (จึงบันทึก Playwright MCP เป็น NOT RUN พร้อมเหตุผลนี้) "
    "การตรวจจริงประกอบด้วยการเปิด URL, อ่านโครงสร้างช่อง, เลือกโหมด, กรอกค่า, กดคำนวณ, "
    "อ่านผลจาก DOM และถ่าย screenshot เก็บหลักฐาน",
)
bullet("MCP (Model Context Protocol) คือมาตรฐานที่ให้ AI เรียกเครื่องมือภายนอก เช่น Browser แทนการเดาโค้ด")
bullet("Skill browser-acceptance-check (ถ้ามี) เป็นเพียงคำสั่งบอกว่าต้องตรวจอะไรและรายงานหลักฐานอะไร — ไม่ได้เปิด browser เอง")
bullet("สถานะ \"connected\" ของ MCP อย่างเดียวไม่พอ ต้องเรียก tool แล้วได้ snapshot/ผลจากหน้าเว็บจริงจึงนับว่าผ่าน")
bullet("การอ่านโค้ดหรือส่ง curl แทน ไม่ถือเป็นการรัน browser case")

heading("5.3 สิ่งที่ AI สร้าง / นักศึกษาตรวจ", 2)
make_table(
    ["ส่วน", "ใครทำ", "รายละเอียด"],
    [
        ["โค้ด Fixed/Emitter bias ใน dc_bias.py", "AI เขียน", "นักศึกษาตรวจสมการ IB, IC, VCE เทียบค่าคำนวณมือ A2–A4"],
        ["mode dispatch + แปลงหน่วยใน app.py", "AI เขียน", "นักศึกษาตรวจชื่อฟิลด์/หน่วย/ฟังก์ชันที่ถูกเรียกตามโหมด"],
        ["ฟอร์มตามโหมดใน index.html", "AI เขียน", "นักศึกษาลองเลือกโหมดดูว่าช่องเปลี่ยนและผลเก่าหาย"],
        ["ค่าอ้างอิง A1–A5 ในตาราง", "นักศึกษากำหนด", "ใช้สมการวิชา Engineering Electronics คำนวณอิสระ ไม่เอาโค้ดมาเป็นคำตอบ"],
        ["รัน browser + อ่านผล + เก็บภาพ", "AI รันจริง", "นักศึกษาเปิดเว็บเองซ้ำอย่างน้อย 1 กรณีเพื่อทวนผล"],
        ["ปุ่มเปลี่ยนโหมด", "AI ใส่ formnovalidate", "นักศึกษาทดสอบว่าปุ่มโหลดฟอร์มได้โดยไม่ต้องกรอกค่าก่อน"],
    ],
    widths=[2.2, 1.1, 3.4],
)

doc.add_page_break()

# ======================= 6. ตำแหน่งโค้ด =======================
heading("6. ตำแหน่งเลือกฟังก์ชันและแปลงหน่วยในโค้ด", 1)
para("ไฟล์ app.py — ตำแหน่งสำคัญ:", bold=True, size=10)
code_block([
    "MODE_FIELDS = {                                # บรรทัด 42-46",
    "    MODE_DIVIDER: (\"r1\", \"r2\", \"rc\", \"re\"),",
    "    MODE_FIXED:   (\"rb\", \"rc\"),",
    "    MODE_EMITTER: (\"rb\", \"re\", \"rc\"),",
    "}",
    "def _collect_form(fallback)                     # บรรทัด 72 — อ่านฟอร์ม/คงค่าเดิม",
    "factor = 1000.0 if form[\"unit\"] == \"kilo\" else 1.0   # บรรทัด 120",
    "resistors = {field: values[field] * factor ...}       # แปลง kΩ -> Ω ที่นี่",
    "",
    "# calculate() บรรทัด 126-152 — เลือกฟังก์ชันตามโหมด",
    "if   mode == MODE_DIVIDER: result = calculate_dc_bias(BiasInputs(...))",
    "elif mode == MODE_FIXED:   result = calculate_fixed_bias(vcc, rb, rc, beta, vbe)",
    "else:                      result = calculate_emitter_bias(vcc, rb, re, rc, beta, vbe)",
])
para("ไฟล์ dc_bias.py — สมการหลัก:", bold=True, size=10)
code_block([
    "MODES = (MODE_DIVIDER, MODE_FIXED, MODE_EMITTER)      # บรรทัด 22",
    "calculate_dc_bias()      บรรทัด 153 : Divider เดิม (VTH, RTH)",
    "calculate_fixed_bias()   บรรทัด 189 : IB = (VCC − VBE) / RB, VE = 0",
    "calculate_emitter_bias() บรรทัด 208 : IB = (VCC − VBE) / [RB + (β+1)·RE]",
    "_operating_point()       บรรทัด 91  : IC = β·IB, IE, VE, VB, VC, VCE",
    "_validate_resistor()     บรรทัด 72  : R > 0 -> \"RB ต้องมากกว่า 0 Ω\"",
])

para("")
heading("7. วิธีรันและตรวจซ้ำ", 1)
code_block([
    "cd \"C:\\Users\\B6814946\\Documents\\GitHub\\BJT-DC-Bias-Web-App\"",
    ".venv\\Scripts\\python.exe -m flask --app app run --port 5000",
    "เปิด http://127.0.0.1:5000/",
    ".venv\\Scripts\\python.exe -m unittest discover -s tests -v   # 48 tests OK",
])
para(f"GitHub: {GITHUB_URL}", size=10)
para(f"Commit SHA: {COMMIT_SHA}", size=10)
para(
    "หมายเหตุ: commit ข้างต้นอยู่ในเครื่องแล้ว หาก push ไม่ได้ให้ตรวจสิทธิ์ของบัญชี "
    "GitHub ที่ใช้ (repo นี้ต้องใช้สิทธิ์ของเจ้าของ ottoponrod)",
    size=10,
)

DESKTOP.mkdir(parents=True, exist_ok=True)
try:
    doc.save(OUT)
    saved = OUT
except PermissionError:
    doc.save(FALLBACK)
    saved = FALLBACK
print(f"Saved: {saved}")
print(f"Size: {saved.stat().st_size} bytes")

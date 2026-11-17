# Lab 03 สามโหมดไบอัส Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** เพิ่ม Fixed/Emitter Bias ให้เว็บ Flask เดิมโดยคงผล Divider เดิม
**Architecture:** เพิ่มฟังก์ชันคำนวณใน `dc_bias.py`, เลือกสาขาใน `app.py`, ปรับ Jinja ให้เปลี่ยนช่องตามโหมด; ตรวจด้วย tests + browser
**Tech Stack:** Python 3.15, Flask 3.1.3, Jinja, unittest, OpenCode Browser
**Spec:** `docs/superpowers/specs/2026-11-17-lab03-three-bias-modes-design.md`

## Global Constraints
- ห้ามสร้างโปรเจกต์ใหม่ / ห้ามย้ายสมการเข้า HTML / ห้ามลบ tests เดิม
- SI ใน `dc_bias.py`; แปลง kΩ→Ω ที่ `app.py` เท่านั้น
- ผล A1 ต้องคงเดิม: IC = 1.229858 mA, VCE = 8.052155 V

## Review Focus
- RB = 0 ต้อง error และไม่แสดงผลเก่า → test_web A5
- โหมดไม่รู้จักต้อง error ไม่ใช่ fell back เป็น Divider → test_web
- Divider field หายต้องยัง error (ไม่ถูกโหมดอื่นกลืน) → test_web เดิม
- A4 เปลี่ยน RE ต้องเปลี่ยน IC → unit test + browser
- VCE ≤ 0.2 / numerator ≤ 0 ต้องเตือน → unit test

---

### Task 1: คำนวณ Fixed/Emitter ใน dc_bias.py
- Files: Modify `dc_bias.py`, Test `tests/test_dc_bias.py`
- Produces: `calculate_fixed_bias(vcc, rb, rc, beta, vbe)`, `calculate_emitter_bias(vcc, rb, re, rc, beta, vbe)` → `BiasResult`
- [ ] เขียน test A2/A3/A4 + validation ให้ fail (ImportError)
- [ ] รัน `.venv\Scripts\python.exe -m unittest tests.test_dc_bias -v` เห็น fail
- [ ] เพิ่มฟังก์ชัน + ปรับ `BiasResult` ให้ vth/rth/mode optional
- [ ] รัน tests ผ่าน

### Task 2: เลือกโหมดใน app.py
- Files: Modify `app.py`, Test `tests/test_web.py`
- Consumes: ฟังก์ชันจาก Task 1
- Produces: context `mode`, `mode_label`, `resistors`, `change_mode` action
- [ ] เขียน test POST mode=fixed/emitter/invalid/A5 และ action=change_mode ให้ fail
- [ ] รันเห็น fail
- [ ] แก้ `_form_context`, route `/calculate` ด้วย if/elif
- [ ] รัน tests ผ่าน

### Task 3: ปรับฟอร์มและผล
- Files: Modify `templates/index.html`, `static/style.css`
- [ ] ปรับให้ select mode + แสดงเฉพาะช่องที่ใช้ + ปุ่มเปลี่ยนโหมด
- [ ] ผลแสดง mode_label, VTH/RTH เฉพาะ Divider, ตาราง resistor ตามโหมด
- [ ] รันชุด tests ทั้งหมดผ่าน

### Task 4: ตรวจ Browser + เอกสาร + ส่งงาน
- [ ] รัน Flask ตรวจ A1–A5 ด้วย OpenCode Browser เก็บหลักฐาน
- [ ] อัปเดต README, docs/validation.md
- [ ] git diff/diff --staged, commit, push

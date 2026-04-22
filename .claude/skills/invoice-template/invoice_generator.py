"""Parameterized editable invoice PDF generator.

Generates a BLANK and SAMPLE PDF for any service niche from a single
config dict. See SKILL.md for how to build a config.

Usage:
    from invoice_generator import build_pair
    build_pair(CONFIG, out_prefix="hvac_invoice_template")
"""

from __future__ import annotations

import math
from typing import Any

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

NAVY = HexColor("#1F3A68")
DARK_TEXT = HexColor("#2B2B2B")
MUTED = HexColor("#6B7280")
ROW_BG = HexColor("#EEF2F8")
HEADER_BG = HexColor("#E4EAF3")
BORDER = HexColor("#C9D2E0")
FIELD_BG = HexColor("#F7F9FC")
PLACEHOLDER_BG = HexColor("#F2F4F8")

PAGE_W, PAGE_H = LETTER
MARGIN_L = 40
MARGIN_R = 40
MARGIN_T = 40
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R


_ASCII_REPLACEMENTS = str.maketrans({
    "—": "-",  # em dash
    "–": "-",  # en dash
    "‘": "'", "’": "'",  # curly single quotes
    "“": '"', "”": '"',  # curly double quotes
    "…": "...",  # ellipsis
    " ": " ",  # non-breaking space
})


def _ascii_safe(value):
    if not isinstance(value, str):
        return value
    return value.translate(_ASCII_REPLACEMENTS)


def _draw_gear(c, cx, cy, r_outer=14, r_inner=5, teeth=8):
    c.saveState()
    c.setFillColor(NAVY)
    c.setStrokeColor(NAVY)
    path = c.beginPath()
    step = math.pi / teeth
    for i in range(teeth * 2):
        radius = r_outer if i % 2 == 0 else r_outer - 4
        angle = i * step
        px = cx + radius * math.cos(angle)
        py = cy + radius * math.sin(angle)
        (path.moveTo if i == 0 else path.lineTo)(px, py)
    path.close()
    c.drawPath(path, stroke=0, fill=1)
    c.setFillColor(white)
    c.circle(cx, cy, r_inner, stroke=0, fill=1)
    c.restoreState()


def _section_title(c, text, x, y, size=10):
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", size)
    c.drawString(x, y, text)


def _box(c, x, y, w, h, fill=None, stroke=BORDER, stroke_w=0.6,
         dashed=False):
    if fill is not None:
        c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(stroke_w)
    if dashed:
        c.setDash(3, 2)
    c.rect(x, y, w, h, stroke=1, fill=1 if fill is not None else 0)
    if dashed:
        c.setDash()


def _text_field(c, name, x, y, w, h, value="", font_size=9,
                multiline=False, align="left"):
    c.acroForm.textfield(
        name=name,
        tooltip=name.replace("_", " ").title(),
        x=x + 1, y=y + 1, width=w - 2, height=h - 2,
        borderStyle="solid", borderWidth=0, borderColor=BORDER,
        fillColor=FIELD_BG, textColor=DARK_TEXT,
        forceBorder=False, fontSize=font_size,
        fieldFlags="multiline" if multiline else "",
        value=_ascii_safe(value), maxlen=10000 if multiline else 200,
        fontName="Helvetica",
    )


def _checkbox_field(c, name, x, y, size=10, checked=False):
    c.acroForm.checkbox(
        name=name, tooltip=name.replace("_", " ").title(),
        x=x, y=y, size=size, buttonStyle="check",
        borderColor=NAVY, fillColor=white, textColor=NAVY,
        forceBorder=True, checked=checked,
    )


def _draw_centered(c, text, x, y, w, font="Helvetica-Bold", size=8,
                   color=NAVY):
    c.setFillColor(color)
    c.setFont(font, size)
    tw = c.stringWidth(text, font, size)
    c.drawString(x + (w - tw) / 2, y, text)


def _draw_right(c, text, x, y, w, font="Helvetica-Bold", size=8,
                color=NAVY, right_pad=6):
    c.setFillColor(color)
    c.setFont(font, size)
    tw = c.stringWidth(text, font, size)
    c.drawString(x + w - tw - right_pad, y, text)


def _header(c, cfg, data, blank):
    if blank:
        logo_box_x = MARGIN_L
        logo_box_y = PAGE_H - MARGIN_T - 44
        logo_box_w = 60
        logo_box_h = 44
        _box(c, logo_box_x, logo_box_y, logo_box_w, logo_box_h,
             fill=PLACEHOLDER_BG, stroke=MUTED, dashed=True)
        _draw_centered(c, "YOUR LOGO", logo_box_x,
                       logo_box_y + logo_box_h / 2 + 2, logo_box_w,
                       color=MUTED, size=7)
        _draw_centered(c, "(replace in editor)", logo_box_x,
                       logo_box_y + logo_box_h / 2 - 8, logo_box_w,
                       font="Helvetica", size=6, color=MUTED)
        bn_x = logo_box_x + logo_box_w + 8
        bn_y = logo_box_y + 8
        bn_w = 180
        bn_h = 28
        _box(c, bn_x, bn_y, bn_w, bn_h, fill=FIELD_BG)
        _text_field(c, "business_name_field", bn_x, bn_y, bn_w, bn_h,
                    value="", font_size=12)
        c.setFillColor(MUTED)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(bn_x, bn_y + bn_h + 3, "BUSINESS NAME")
    else:
        business = cfg.get("sample_business_name", "Your Business")
        if cfg.get("logo_style", "gear") == "gear":
            _draw_gear(c, MARGIN_L + 16, PAGE_H - MARGIN_T - 24, r_outer=14)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 14)
        # Split business name into up to two lines at the first space
        lines = business.split(" ", 1) if " " in business else [business]
        for i, line in enumerate(lines[:2]):
            c.drawString(MARGIN_L + 38, PAGE_H - MARGIN_T - 18 - i * 14,
                         line)

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 26)
    title = cfg.get("title", "INVOICE")
    tw = c.stringWidth(title, "Helvetica-Bold", 26)
    c.drawString(PAGE_W - MARGIN_R - tw, PAGE_H - MARGIN_T - 18, title)
    c.setFillColor(DARK_TEXT)
    c.setFont("Helvetica", 11)
    sub = cfg.get("subtitle", "")
    if sub:
        sw = c.stringWidth(sub, "Helvetica", 11)
        c.drawString(PAGE_W - MARGIN_R - sw, PAGE_H - MARGIN_T - 34, sub)


def _labeled_field(c, name, x, y, w, value="", field_h=16,
                   label_text=None):
    if label_text:
        c.setFillColor(MUTED)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(x, y + field_h + 3, label_text.upper())
    _box(c, x, y, w, field_h, fill=FIELD_BG)
    _text_field(c, name, x, y, w, field_h, value=value, font_size=9)


def _top_right_block(c, left_x, top_y, data, total_w):
    gap = 10
    col_w = (total_w - gap) / 2
    row1_y = top_y - 36
    _labeled_field(c, "shop_name", left_x, row1_y, col_w,
                   value=data.get("shop_name", ""),
                   label_text="Shop Name")
    _labeled_field(c, "invoice_number", left_x + col_w + gap, row1_y,
                   col_w, value=data.get("invoice_number", ""),
                   label_text="Invoice #")
    row2_y = row1_y - 34
    _labeled_field(c, "invoicing_date", left_x, row2_y, col_w,
                   value=data.get("invoicing_date", ""),
                   label_text="Invoicing Date")
    _labeled_field(c, "service_date", left_x + col_w + gap, row2_y,
                   col_w, value=data.get("service_date", ""),
                   label_text="Service Date")
    return row2_y


def _domain_info(c, x, y, w, cfg, data):
    """Left-side niche-specific info block (was "VEHICLE INFORMATION")."""
    block = cfg["domain_info"]
    _section_title(c, block["section_title"], x, y)
    y -= 14
    col_w = w / 2
    row_h = 30
    header_h = 14
    fields = block["fields"]  # list of 4 dicts: {name,label}

    # Row 1
    _box(c, x, y - header_h, col_w, header_h, fill=HEADER_BG)
    _box(c, x + col_w, y - header_h, col_w, header_h, fill=HEADER_BG)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x + 5, y - header_h + 4, fields[0]["label"])
    c.drawString(x + col_w + 5, y - header_h + 4, fields[1]["label"])
    vy = y - header_h - row_h
    _box(c, x, vy, col_w, row_h, fill=FIELD_BG)
    _box(c, x + col_w, vy, col_w, row_h, fill=FIELD_BG)
    _text_field(c, fields[0]["name"], x, vy, col_w, row_h,
                value=data.get(fields[0]["name"], ""), font_size=9)
    _text_field(c, fields[1]["name"], x + col_w, vy, col_w, row_h,
                value=data.get(fields[1]["name"], ""), font_size=9)

    # Row 2
    hy2 = vy - header_h
    _box(c, x, hy2, col_w, header_h, fill=HEADER_BG)
    _box(c, x + col_w, hy2, col_w, header_h, fill=HEADER_BG)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x + 5, hy2 + 4, fields[2]["label"])
    c.drawString(x + col_w + 5, hy2 + 4, fields[3]["label"])
    vy2 = hy2 - row_h
    _box(c, x, vy2, col_w, row_h, fill=FIELD_BG)
    _box(c, x + col_w, vy2, col_w, row_h, fill=FIELD_BG)
    _text_field(c, fields[2]["name"], x, vy2, col_w, row_h,
                value=data.get(fields[2]["name"], ""), font_size=9)
    _text_field(c, fields[3]["name"], x + col_w, vy2, col_w, row_h,
                value=data.get(fields[3]["name"], ""), font_size=9)

    # Optional history block
    history = block.get("history")
    if history:
        sh_label_y = vy2 - 14
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x, sh_label_y, history["label"])
        sh_h = 36
        sh_y = sh_label_y - 4 - sh_h
        _box(c, x, sh_y, w, sh_h, fill=FIELD_BG)
        _text_field(c, history["name"], x, sh_y, w, sh_h,
                    value=data.get(history["name"], ""),
                    font_size=8, multiline=True)
        return sh_y
    return vy2


def _customer_information(c, x, y, w, data):
    _section_title(c, "CUSTOMER INFORMATION", x, y)
    y -= 14
    header_h = 14
    _box(c, x, y - header_h, w, header_h, fill=HEADER_BG)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x + 5, y - header_h + 4, "ADDRESS")
    row_h = 22
    vy = y - header_h - row_h
    _box(c, x, vy, w, row_h, fill=FIELD_BG)
    _text_field(c, "customer_address_left", x, vy, w, row_h,
                value=data.get("customer_address_left", ""), font_size=9)
    return vy


def _customer_contact(c, x, y, w, data):
    _section_title(c, "CUSTOMER CONTACT", x, y)
    y -= 14
    header_h = 14
    row_h = 22

    def head(cx, cw, txt, ty):
        _box(c, cx, ty, cw, header_h, fill=HEADER_BG)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(cx + 5, ty + 4, txt)

    head(x, w, "CUSTOMER NAME", y - header_h)
    cy = y - header_h - row_h
    _box(c, x, cy, w, row_h, fill=FIELD_BG)
    _text_field(c, "customer_name", x, cy, w, row_h,
                value=data.get("customer_name", ""), font_size=9)
    ay = cy - row_h
    _box(c, x, ay, w, row_h, fill=FIELD_BG)
    _text_field(c, "customer_address", x, ay, w, row_h,
                value=data.get("customer_address", ""), font_size=9)
    head(x, w, "PHONE", ay - header_h)
    py = ay - header_h - row_h
    _box(c, x, py, w, row_h, fill=FIELD_BG)
    _text_field(c, "customer_phone", x, py, w, row_h,
                value=data.get("customer_phone", ""), font_size=9)
    half = w / 2
    eh_y = py - header_h
    _box(c, x, eh_y, half, header_h, fill=HEADER_BG)
    _box(c, x + half, eh_y, half, header_h, fill=HEADER_BG)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x + 5, eh_y + 4, "EMAIL")
    c.drawString(x + half + 5, eh_y + 4, "EMAIL (ALT)")
    ey = eh_y - row_h
    _box(c, x, ey, half, row_h, fill=FIELD_BG)
    _box(c, x + half, ey, half, row_h, fill=FIELD_BG)
    _text_field(c, "customer_email_1", x, ey, half, row_h,
                value=data.get("customer_email_1", ""), font_size=9)
    _text_field(c, "customer_email_2", x + half, ey, half, row_h,
                value=data.get("customer_email_2", ""), font_size=9)
    return ey


def _services_table(c, x, y, w, cfg, data):
    table = cfg["services_table"]
    _section_title(c, table["section_title"], x, y)
    y -= 14
    parts_w = 75
    labor_w = 75
    total_w = 75
    desc_w = w - parts_w - labor_w - total_w
    header_h = 18
    hy = y - header_h
    _box(c, x, hy, desc_w, header_h, fill=HEADER_BG)
    _box(c, x + desc_w, hy, parts_w, header_h, fill=HEADER_BG)
    _box(c, x + desc_w + parts_w, hy, labor_w, header_h, fill=HEADER_BG)
    _box(c, x + desc_w + parts_w + labor_w, hy, total_w, header_h,
         fill=HEADER_BG)
    ty = hy + 6
    _draw_centered(c, table["columns"][0], x, ty, desc_w, size=7.5)
    _draw_right(c, table["columns"][1], x + desc_w, ty, parts_w, size=7.5)
    _draw_right(c, table["columns"][2], x + desc_w + parts_w, ty, labor_w,
                size=7.5)
    _draw_right(c, table["columns"][3], x + desc_w + parts_w + labor_w,
                ty, total_w, size=7.5)

    row_defs = [
        ("row1", 44),
        ("row2", 22),
        ("row3", 22),
        ("row4", 22),
        ("row5", 22),
        ("row6", 22),
    ]
    cur_y = hy
    for i, (prefix, rh) in enumerate(row_defs):
        row_bg = ROW_BG if i % 2 == 0 else white
        cur_y -= rh
        _box(c, x, cur_y, desc_w, rh, fill=row_bg)
        _box(c, x + desc_w, cur_y, parts_w, rh, fill=row_bg)
        _box(c, x + desc_w + parts_w, cur_y, labor_w, rh, fill=row_bg)
        _box(c, x + desc_w + parts_w + labor_w, cur_y, total_w, rh,
             fill=row_bg)
        _text_field(c, f"{prefix}_desc", x, cur_y, desc_w, rh,
                    value=data.get(f"{prefix}_desc", ""),
                    font_size=7.5, multiline=True)
        _text_field(c, f"{prefix}_parts", x + desc_w, cur_y, parts_w, rh,
                    value=data.get(f"{prefix}_parts", ""),
                    font_size=8, align="right")
        _text_field(c, f"{prefix}_labor", x + desc_w + parts_w, cur_y,
                    labor_w, rh, value=data.get(f"{prefix}_labor", ""),
                    font_size=8, align="right")
        _text_field(c, f"{prefix}_total",
                    x + desc_w + parts_w + labor_w, cur_y, total_w, rh,
                    value=data.get(f"{prefix}_total", ""),
                    font_size=8, align="right")

    totals = [
        ("Subtotal", "subtotal"),
        ("Tax", "tax"),
        ("Total", "total"),
        ("Amount Paid", "amount_paid"),
        ("Balance Due", "balance_due"),
    ]
    tot_h = 18
    tot_x_label = x + desc_w
    tot_x_val = x + desc_w + parts_w + labor_w
    for lbl, name in totals:
        cur_y -= tot_h
        c.setFillColor(DARK_TEXT)
        c.setFont("Helvetica-Bold", 8.5)
        lbl_w = parts_w + labor_w
        tw = c.stringWidth(lbl, "Helvetica-Bold", 8.5)
        c.drawString(tot_x_label + lbl_w - tw - 6, cur_y + 5, lbl)
        _box(c, tot_x_val, cur_y, total_w, tot_h, fill=white)
        _text_field(c, name, tot_x_val, cur_y, total_w, tot_h,
                    value=data.get(name, ""), font_size=8.5, align="right")
    return cur_y


def _payment_and_signature(c, x, y, w, data, checks):
    _section_title(c, "PAYMENT METHOD", x, y)
    y -= 14
    opts = [
        ("pm_cash", "Cash"),
        ("pm_card", "Credit / Debit"),
        ("pm_check", "Check"),
        ("pm_other", "Other"),
    ]
    left_w = w * 0.55
    right_w = w - left_w - 10
    row_h = 22
    _box(c, x, y - row_h, left_w, row_h, fill=FIELD_BG)
    cb_size = 10
    cb_label_gap = 5
    font = "Helvetica"
    font_size = 8.5
    slot = left_w / len(opts)
    cy = y - row_h + (row_h - cb_size) / 2
    text_y = cy + 2
    for i, (name, label) in enumerate(opts):
        label_w = c.stringWidth(label, font, font_size)
        group_w = cb_size + cb_label_gap + label_w
        cx = x + i * slot + (slot - group_w) / 2
        _checkbox_field(c, name, cx, cy, size=cb_size,
                        checked=checks.get(name, False))
        c.setFillColor(DARK_TEXT)
        c.setFont(font, font_size)
        c.drawString(cx + cb_size + cb_label_gap, text_y, label)

    sig_x = x + left_w + 10
    sig_w = right_w
    _box(c, sig_x, y - row_h, sig_w, row_h, fill=FIELD_BG)
    date_w = 90
    sig_only_w = sig_w - date_w
    _text_field(c, "signature", sig_x, y - row_h, sig_only_w, row_h,
                value=data.get("signature", ""), font_size=9)
    _text_field(c, "signed_date", sig_x + sig_only_w, y - row_h, date_w,
                row_h, value=data.get("signed_date", ""), font_size=9)
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(sig_x + 3, y - row_h - 8, "AUTHORIZED SIGNATURE")
    c.drawString(sig_x + sig_only_w + 3, y - row_h - 8, "DATE")
    return y - row_h - 12


def _notes_and_footer(c, x, y, w, cfg, data):
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x, y - 4, "NOTES")
    notes_h = 30
    ny = y - 8 - notes_h
    _box(c, x, ny, w, notes_h, fill=FIELD_BG)
    _text_field(c, "notes", x, ny, w, notes_h,
                value=data.get("notes", ""), font_size=8, multiline=True)

    footer_title = cfg.get("footer_section_title", "GENERAL CONDITION")
    gc_label_y = ny - 14
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, gc_label_y, footer_title)
    gc_h = 40
    gc_y = gc_label_y - 4 - gc_h
    _box(c, x, gc_y, w, gc_h, fill=FIELD_BG)
    _text_field(c, "footer_notes", x, gc_y, w, gc_h,
                value=data.get("footer_notes", ""),
                font_size=9, multiline=True)
    return gc_y


def _build_one(output_path: str, cfg: dict[str, Any], blank: bool):
    data = {} if blank else cfg.get("sample_data", {})
    checks = {} if blank else cfg.get("sample_checks", {})

    c = canvas.Canvas(output_path, pagesize=LETTER)
    c.setTitle(cfg.get("pdf_title", "Invoice Template"))
    c.setAuthor(cfg.get("pdf_author", "Editable Invoice Template"))

    _header(c, cfg, data, blank)

    top_y = PAGE_H - MARGIN_T - 60
    col_gap = 20
    left_w = (CONTENT_W - col_gap) * 0.55
    right_w = CONTENT_W - col_gap - left_w
    left_x = MARGIN_L
    right_x = MARGIN_L + left_w + col_gap

    top_right_bottom = _top_right_block(c, right_x, PAGE_H - MARGIN_T - 40,
                                        data, right_w)
    left_bottom = _domain_info(c, left_x, top_y, left_w, cfg, data)
    contact_bottom = _customer_contact(c, right_x, top_right_bottom - 16,
                                       right_w, data)
    cust_info_bottom = _customer_information(c, left_x, left_bottom - 16,
                                             left_w, data)
    table_top = min(cust_info_bottom, contact_bottom) - 18
    table_bottom = _services_table(c, MARGIN_L, table_top, CONTENT_W,
                                   cfg, data)
    pay_bottom = _payment_and_signature(c, MARGIN_L, table_bottom - 14,
                                        CONTENT_W, data, checks)
    _notes_and_footer(c, MARGIN_L, pay_bottom - 4, CONTENT_W, cfg, data)

    c.showPage()
    c.save()
    print(f"wrote {output_path}")


def build_pair(cfg: dict[str, Any], out_prefix: str) -> tuple[str, str]:
    """Build a BLANK and a SAMPLE PDF. Returns (blank_path, sample_path)."""
    blank = f"{out_prefix}_BLANK.pdf"
    sample = f"{out_prefix}_SAMPLE.pdf"
    _build_one(blank, cfg, blank=True)
    _build_one(sample, cfg, blank=False)
    return blank, sample

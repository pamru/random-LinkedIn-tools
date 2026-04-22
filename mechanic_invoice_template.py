"""Generate editable PDF templates for a mechanic invoice.

Produces two files:
  * mechanic_invoice_template_BLANK.pdf  - blank template for sale
  * mechanic_invoice_template_SAMPLE.pdf - filled with dummy data for listing

Every text area is an AcroForm field so buyers can fill it out in any PDF
reader (Acrobat, Preview, Foxit, most browsers).
"""

import math

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


SAMPLE_DATA = {
    "shop_name": "Precision Auto Repair",
    "invoice_number": "INV-10428",
    "invoicing_date": "03/12/2026",
    "service_date": "03/13/2026",
    "vin": "4T1BF1FK5JU074891",
    "license_plate": "TX-6422LM",
    "year_make_model": "2018 Toyota Camry",
    "mileage": "72,430",
    "service_history": (
        "Front brake pads worn below safety limit. Replaced pads and "
        "inspected rotors. Performed full synthetic oil change and replaced "
        "engine air filter. Vehicle test driven and operating normally."
    ),
    "customer_name": "Michael Torres",
    "customer_address": "2147 Willow Creek Dr, Austin, TX 78704",
    "customer_address_left": "2147 Willow Creek Dr, Austin, TX 78704",
    "customer_phone": "(555) 482-1197",
    "customer_email_1": "m.torres@email.com",
    "customer_email_2": "m.torres@email.com",
    "row1_desc": (
        "Front brake pads worn below safety limit. Replaced pads and "
        "inspected rotors."
    ),
    "row1_parts": "$120.00",
    "row1_labor": "$150.00",
    "row1_total": "$270.00",
    "row2_desc": "Brake Pad Replacement",
    "row2_parts": "$120.00",
    "row2_labor": "$130.00",
    "row2_total": "$250.00",
    "row3_desc": "Oil Change (Full Synthetic)",
    "row3_parts": "$45.00",
    "row3_labor": "$23.00",
    "row3_total": "$68.00",
    "row4_desc": "Air Filter Replacement",
    "row4_parts": "$25.00",
    "row4_labor": "$15.00",
    "row4_total": "$40.00",
    "row5_desc": "",
    "row5_parts": "",
    "row5_labor": "",
    "row5_total": "",
    "row6_desc": "Shop Fees",
    "row6_parts": "$10.00",
    "row6_labor": "",
    "row6_total": "$10.00",
    "subtotal": "$638.00",
    "tax": "$31.90",
    "total": "$669.90",
    "amount_paid": "$400.00",
    "balance_due": "$269.90",
    "notes": (
        "Customer approved all recommended services prior to work. "
        "Vehicle test driven post-repair and operating normally. "
        "Next recommended service: 77,500 miles or 6 months."
    ),
    "general_condition": (
        "Overall condition: Good. Tires at 6/32\". Battery tested healthy. "
        "Recommend tire rotation at next service."
    ),
    "signature": "Michael Torres",
    "signed_date": "03/13/2026",
    "business_name_field": "Precision Auto Repair",
}

SAMPLE_CHECKBOXES = {"pm_card": True}


def draw_gear(c, cx, cy, r_outer=14, r_inner=5, teeth=8):
    c.saveState()
    c.setFillColor(NAVY)
    c.setStrokeColor(NAVY)
    path = c.beginPath()
    step = math.pi / teeth
    for i in range(teeth * 2):
        radius = r_outer if i % 2 == 0 else r_outer - 4
        angle = i * step
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        if i == 0:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
    path.close()
    c.drawPath(path, stroke=0, fill=1)
    c.setFillColor(white)
    c.circle(cx, cy, r_inner, stroke=0, fill=1)
    c.restoreState()


def section_title(c, text, x, y, size=10):
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", size)
    c.drawString(x, y, text)


def box(c, x, y, w, h, fill=None, stroke=BORDER, stroke_w=0.6,
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


def text_field(c, name, x, y, w, h, value="", font_size=9, multiline=False,
               align="left"):
    form = c.acroForm
    form.textfield(
        name=name,
        tooltip=name.replace("_", " ").title(),
        x=x + 1,
        y=y + 1,
        width=w - 2,
        height=h - 2,
        borderStyle="solid",
        borderWidth=0,
        borderColor=BORDER,
        fillColor=FIELD_BG,
        textColor=DARK_TEXT,
        forceBorder=False,
        fontSize=font_size,
        fieldFlags="multiline" if multiline else "",
        value=value,
        maxlen=10000 if multiline else 200,
        fontName="Helvetica",
    )


def checkbox_field(c, name, x, y, size=10, checked=False):
    form = c.acroForm
    form.checkbox(
        name=name,
        tooltip=name.replace("_", " ").title(),
        x=x,
        y=y,
        size=size,
        buttonStyle="check",
        borderColor=NAVY,
        fillColor=white,
        textColor=NAVY,
        forceBorder=True,
        checked=checked,
    )


def draw_centered(c, text, x, y, w, font="Helvetica-Bold", size=8,
                  color=NAVY):
    c.setFillColor(color)
    c.setFont(font, size)
    tw = c.stringWidth(text, font, size)
    c.drawString(x + (w - tw) / 2, y, text)


def draw_right(c, text, x, y, w, font="Helvetica-Bold", size=8,
               color=NAVY, right_pad=6):
    c.setFillColor(color)
    c.setFont(font, size)
    tw = c.stringWidth(text, font, size)
    c.drawString(x + w - tw - right_pad, y, text)


def header(c, data, blank):
    if blank:
        # Logo placeholder box
        logo_box_x = MARGIN_L
        logo_box_y = PAGE_H - MARGIN_T - 44
        logo_box_w = 60
        logo_box_h = 44
        box(c, logo_box_x, logo_box_y, logo_box_w, logo_box_h,
            fill=PLACEHOLDER_BG, stroke=MUTED, dashed=True)
        c.setFillColor(MUTED)
        c.setFont("Helvetica-Bold", 7)
        draw_centered(c, "YOUR LOGO", logo_box_x,
                      logo_box_y + logo_box_h / 2 + 2, logo_box_w,
                      color=MUTED)
        draw_centered(c, "(replace in editor)", logo_box_x,
                      logo_box_y + logo_box_h / 2 - 8, logo_box_w,
                      font="Helvetica", size=6, color=MUTED)
        # Business name editable field next to logo
        bn_x = logo_box_x + logo_box_w + 8
        bn_y = logo_box_y + 8
        bn_w = 180
        bn_h = 28
        box(c, bn_x, bn_y, bn_w, bn_h, fill=FIELD_BG)
        text_field(c, "business_name_field", bn_x, bn_y, bn_w, bn_h,
                   value="", font_size=12)
        c.setFillColor(MUTED)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(bn_x, bn_y + bn_h + 3, "BUSINESS NAME")
    else:
        draw_gear(c, MARGIN_L + 16, PAGE_H - MARGIN_T - 24, r_outer=14)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(MARGIN_L + 38, PAGE_H - MARGIN_T - 18, "Precision")
        c.drawString(MARGIN_L + 38, PAGE_H - MARGIN_T - 32, "Auto Repair")

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 26)
    title = "INVOICE"
    tw = c.stringWidth(title, "Helvetica-Bold", 26)
    c.drawString(PAGE_W - MARGIN_R - tw, PAGE_H - MARGIN_T - 18, title)
    c.setFillColor(DARK_TEXT)
    c.setFont("Helvetica", 11)
    sub = "Vehicle Service Invoice"
    sw = c.stringWidth(sub, "Helvetica", 11)
    c.drawString(PAGE_W - MARGIN_R - sw, PAGE_H - MARGIN_T - 34, sub)


def draw_labeled_field(c, name, x, y, w, value="", field_h=16,
                       label_text=None, label_color=MUTED):
    if label_text:
        c.setFillColor(label_color)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(x, y + field_h + 3, label_text.upper())
    box(c, x, y, w, field_h, fill=FIELD_BG)
    text_field(c, name, x, y, w, field_h, value=value, font_size=9)


def top_right_block(c, left_x, top_y, data, total_w):
    gap = 10
    col_w = (total_w - gap) / 2
    row1_y = top_y - 36
    draw_labeled_field(c, "shop_name", left_x, row1_y, col_w,
                       value=data.get("shop_name", ""),
                       label_text="Shop Name")
    draw_labeled_field(c, "invoice_number", left_x + col_w + gap, row1_y,
                       col_w, value=data.get("invoice_number", ""),
                       label_text="Invoice #")
    row2_y = row1_y - 34
    draw_labeled_field(c, "invoicing_date", left_x, row2_y, col_w,
                       value=data.get("invoicing_date", ""),
                       label_text="Invoicing Date")
    draw_labeled_field(c, "service_date", left_x + col_w + gap, row2_y,
                       col_w, value=data.get("service_date", ""),
                       label_text="Service Date")
    return row2_y


def vehicle_information(c, x, y, w, data):
    section_title(c, "VEHICLE INFORMATION", x, y)
    y -= 14
    col_w = w / 2
    row_h = 30
    header_h = 14

    # Row 1 headers
    box(c, x, y - header_h, col_w, header_h, fill=HEADER_BG)
    box(c, x + col_w, y - header_h, col_w, header_h, fill=HEADER_BG)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x + 5, y - header_h + 4, "VIN")
    c.drawString(x + col_w + 5, y - header_h + 4, "LICENSE PLATE")
    vy = y - header_h - row_h
    box(c, x, vy, col_w, row_h, fill=FIELD_BG)
    box(c, x + col_w, vy, col_w, row_h, fill=FIELD_BG)
    text_field(c, "vin", x, vy, col_w, row_h,
               value=data.get("vin", ""), font_size=9)
    text_field(c, "license_plate", x + col_w, vy, col_w, row_h,
               value=data.get("license_plate", ""), font_size=9)

    # Row 2 headers
    hy2 = vy - header_h
    box(c, x, hy2, col_w, header_h, fill=HEADER_BG)
    box(c, x + col_w, hy2, col_w, header_h, fill=HEADER_BG)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x + 5, hy2 + 4, "YEAR / MAKE / MODEL")
    c.drawString(x + col_w + 5, hy2 + 4, "MILEAGE")
    vy2 = hy2 - row_h
    box(c, x, vy2, col_w, row_h, fill=FIELD_BG)
    box(c, x + col_w, vy2, col_w, row_h, fill=FIELD_BG)
    text_field(c, "year_make_model", x, vy2, col_w, row_h,
               value=data.get("year_make_model", ""), font_size=9)
    text_field(c, "mileage", x + col_w, vy2, col_w, row_h,
               value=data.get("mileage", ""), font_size=9)

    sh_label_y = vy2 - 14
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x, sh_label_y, "Service History")
    sh_h = 36
    sh_y = sh_label_y - 4 - sh_h
    box(c, x, sh_y, w, sh_h, fill=FIELD_BG)
    text_field(c, "service_history", x, sh_y, w, sh_h,
               value=data.get("service_history", ""),
               font_size=8, multiline=True)
    return sh_y


def customer_information(c, x, y, w, data):
    section_title(c, "CUSTOMER INFORMATION", x, y)
    y -= 14
    header_h = 14
    box(c, x, y - header_h, w, header_h, fill=HEADER_BG)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x + 5, y - header_h + 4, "ADDRESS")
    row_h = 22
    vy = y - header_h - row_h
    box(c, x, vy, w, row_h, fill=FIELD_BG)
    text_field(c, "customer_address_left", x, vy, w, row_h,
               value=data.get("customer_address_left", ""),
               font_size=9)
    return vy


def customer_contact(c, x, y, w, data):
    section_title(c, "CUSTOMER CONTACT", x, y)
    y -= 14
    header_h = 14
    row_h = 22

    def header_cell(cx, cw, txt, ty):
        box(c, cx, ty, cw, header_h, fill=HEADER_BG)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(cx + 5, ty + 4, txt)

    header_cell(x, w, "CUSTOMER NAME", y - header_h)
    cy = y - header_h - row_h
    box(c, x, cy, w, row_h, fill=FIELD_BG)
    text_field(c, "customer_name", x, cy, w, row_h,
               value=data.get("customer_name", ""), font_size=9)
    ay = cy - row_h
    box(c, x, ay, w, row_h, fill=FIELD_BG)
    text_field(c, "customer_address", x, ay, w, row_h,
               value=data.get("customer_address", ""), font_size=9)
    header_cell(x, w, "PHONE", ay - header_h)
    py = ay - header_h - row_h
    box(c, x, py, w, row_h, fill=FIELD_BG)
    text_field(c, "customer_phone", x, py, w, row_h,
               value=data.get("customer_phone", ""), font_size=9)
    half = w / 2
    eh_y = py - header_h
    box(c, x, eh_y, half, header_h, fill=HEADER_BG)
    box(c, x + half, eh_y, half, header_h, fill=HEADER_BG)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x + 5, eh_y + 4, "EMAIL")
    c.drawString(x + half + 5, eh_y + 4, "EMAIL (ALT)")
    ey = eh_y - row_h
    box(c, x, ey, half, row_h, fill=FIELD_BG)
    box(c, x + half, ey, half, row_h, fill=FIELD_BG)
    text_field(c, "customer_email_1", x, ey, half, row_h,
               value=data.get("customer_email_1", ""), font_size=9)
    text_field(c, "customer_email_2", x + half, ey, half, row_h,
               value=data.get("customer_email_2", ""), font_size=9)
    return ey


def repair_services_table(c, x, y, w, data):
    section_title(c, "REPAIR SERVICES", x, y)
    y -= 14
    parts_w = 75
    labor_w = 75
    total_w = 75
    desc_w = w - parts_w - labor_w - total_w
    header_h = 18

    # Centered header labels
    hy = y - header_h
    box(c, x, hy, desc_w, header_h, fill=HEADER_BG)
    box(c, x + desc_w, hy, parts_w, header_h, fill=HEADER_BG)
    box(c, x + desc_w + parts_w, hy, labor_w, header_h, fill=HEADER_BG)
    box(c, x + desc_w + parts_w + labor_w, hy, total_w, header_h,
        fill=HEADER_BG)
    ty = hy + 6
    draw_centered(c, "ITEM / SERVICE DESCRIPTION", x, ty, desc_w,
                  size=7.5)
    draw_right(c, "PARTS COST", x + desc_w, ty, parts_w, size=7.5)
    draw_right(c, "LABOR COST", x + desc_w + parts_w, ty, labor_w, size=7.5)
    draw_right(c, "TOTAL", x + desc_w + parts_w + labor_w, ty, total_w,
               size=7.5)

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
        box(c, x, cur_y, desc_w, rh, fill=row_bg)
        box(c, x + desc_w, cur_y, parts_w, rh, fill=row_bg)
        box(c, x + desc_w + parts_w, cur_y, labor_w, rh, fill=row_bg)
        box(c, x + desc_w + parts_w + labor_w, cur_y, total_w, rh,
            fill=row_bg)
        text_field(c, f"{prefix}_desc", x, cur_y, desc_w, rh,
                   value=data.get(f"{prefix}_desc", ""),
                   font_size=7.5, multiline=True)
        text_field(c, f"{prefix}_parts", x + desc_w, cur_y, parts_w, rh,
                   value=data.get(f"{prefix}_parts", ""),
                   font_size=8, align="right")
        text_field(c, f"{prefix}_labor", x + desc_w + parts_w, cur_y,
                   labor_w, rh, value=data.get(f"{prefix}_labor", ""),
                   font_size=8, align="right")
        text_field(c, f"{prefix}_total",
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
        box(c, tot_x_val, cur_y, total_w, tot_h, fill=white)
        text_field(c, name, tot_x_val, cur_y, total_w, tot_h,
                   value=data.get(name, ""), font_size=8.5, align="right")

    return cur_y


def payment_and_signature(c, x, y, w, data, checks):
    """Row with payment-method checkboxes on the left, signature on right."""
    section_title(c, "PAYMENT METHOD", x, y)
    y -= 14
    # Left block: checkboxes
    opts = [
        ("pm_cash", "Cash"),
        ("pm_card", "Credit / Debit"),
        ("pm_check", "Check"),
        ("pm_other", "Other"),
    ]
    left_w = w * 0.55
    right_w = w - left_w - 10
    row_h = 22
    box(c, x, y - row_h, left_w, row_h, fill=FIELD_BG)
    cb_size = 10
    cb_label_gap = 5
    font = "Helvetica"
    font_size = 8.5
    # Center each (checkbox + label) group within an equal slot.
    slot = left_w / len(opts)
    cy = y - row_h + (row_h - cb_size) / 2
    text_y = cy + 2
    for i, (name, label) in enumerate(opts):
        label_w = c.stringWidth(label, font, font_size)
        group_w = cb_size + cb_label_gap + label_w
        slot_left = x + i * slot
        cx = slot_left + (slot - group_w) / 2
        checkbox_field(c, name, cx, cy, size=cb_size,
                       checked=checks.get(name, False))
        c.setFillColor(DARK_TEXT)
        c.setFont(font, font_size)
        c.drawString(cx + cb_size + cb_label_gap, text_y, label)

    # Right block: signature + date
    sig_x = x + left_w + 10
    sig_w = right_w
    box(c, sig_x, y - row_h, sig_w, row_h, fill=FIELD_BG)
    # Split into signature (70%) and date (30%) with small labels
    date_w = 90
    sig_only_w = sig_w - date_w
    text_field(c, "signature", sig_x, y - row_h, sig_only_w, row_h,
               value=data.get("signature", ""), font_size=9)
    text_field(c, "signed_date", sig_x + sig_only_w, y - row_h, date_w,
               row_h, value=data.get("signed_date", ""), font_size=9)
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(sig_x + 3, y - row_h - 8, "AUTHORIZED SIGNATURE")
    c.drawString(sig_x + sig_only_w + 3, y - row_h - 8, "DATE")
    return y - row_h - 12


def notes_and_conditions(c, x, y, w, data):
    # Notes (smaller) + General Condition (bigger, prominent)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x, y - 4, "NOTES")
    notes_h = 30
    ny = y - 8 - notes_h
    box(c, x, ny, w, notes_h, fill=FIELD_BG)
    text_field(c, "notes", x, ny, w, notes_h,
               value=data.get("notes", ""), font_size=8, multiline=True)

    # General Condition — bigger block with prominent header
    gc_label_y = ny - 14
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, gc_label_y, "GENERAL CONDITION")
    gc_h = 40
    gc_y = gc_label_y - 4 - gc_h
    box(c, x, gc_y, w, gc_h, fill=FIELD_BG)
    text_field(c, "general_condition", x, gc_y, w, gc_h,
               value=data.get("general_condition", ""),
               font_size=9, multiline=True)
    return gc_y


def build(output_path, blank=False):
    data = {} if blank else SAMPLE_DATA
    checks = {} if blank else SAMPLE_CHECKBOXES

    c = canvas.Canvas(output_path, pagesize=LETTER)
    c.setTitle("Mechanic Invoice Template")
    c.setAuthor("Editable Invoice Template")

    header(c, data, blank)

    top_y = PAGE_H - MARGIN_T - 60
    col_gap = 20
    left_w = (CONTENT_W - col_gap) * 0.55
    right_w = CONTENT_W - col_gap - left_w
    left_x = MARGIN_L
    right_x = MARGIN_L + left_w + col_gap

    top_right_bottom = top_right_block(c, right_x,
                                       PAGE_H - MARGIN_T - 40, data,
                                       right_w)

    left_bottom = vehicle_information(c, left_x, top_y, left_w, data)
    contact_bottom = customer_contact(c, right_x, top_right_bottom - 16,
                                      right_w, data)
    cust_info_bottom = customer_information(c, left_x, left_bottom - 16,
                                            left_w, data)

    table_top = min(cust_info_bottom, contact_bottom) - 18
    table_bottom = repair_services_table(c, MARGIN_L, table_top,
                                         CONTENT_W, data)

    pay_bottom = payment_and_signature(c, MARGIN_L, table_bottom - 14,
                                       CONTENT_W, data, checks)
    notes_and_conditions(c, MARGIN_L, pay_bottom - 4, CONTENT_W, data)

    c.showPage()
    c.save()
    print(f"wrote {output_path}")


if __name__ == "__main__":
    build("mechanic_invoice_template_BLANK.pdf", blank=True)
    build("mechanic_invoice_template_SAMPLE.pdf", blank=False)

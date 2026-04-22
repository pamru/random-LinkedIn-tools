"""Generate an editable PDF template for a mechanic invoice.

Produces `mechanic_invoice_template.pdf` with AcroForm fields that can be
filled in by any standard PDF reader (Acrobat, Preview, Foxit, browsers).
"""

from reportlab.lib.colors import Color, HexColor, white, black
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

OUTPUT = "mechanic_invoice_template.pdf"

NAVY = HexColor("#1F3A68")
DARK_TEXT = HexColor("#2B2B2B")
MUTED = HexColor("#6B7280")
ROW_BG = HexColor("#EEF2F8")
HEADER_BG = HexColor("#E4EAF3")
BORDER = HexColor("#C9D2E0")
FIELD_BG = HexColor("#F7F9FC")

PAGE_W, PAGE_H = LETTER
MARGIN_L = 40
MARGIN_R = 40
MARGIN_T = 40
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R


def draw_gear(c, cx, cy, r_outer=14, r_inner=5, teeth=8):
    """Draw a simple gear-shaped logo."""
    import math

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
    # inner hole
    c.setFillColor(white)
    c.circle(cx, cy, r_inner, stroke=0, fill=1)
    c.restoreState()


def label(c, text, x, y, size=7.5, color=NAVY, bold=True):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.drawString(x, y, text)


def section_title(c, text, x, y, size=10):
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", size)
    c.drawString(x, y, text)


def box(c, x, y, w, h, fill=None, stroke=BORDER, stroke_w=0.6):
    if fill is not None:
        c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(stroke_w)
    c.rect(x, y, w, h, stroke=1, fill=1 if fill is not None else 0)


def text_field(c, name, x, y, w, h, value="", font_size=9, multiline=False,
               align="left"):
    """Add an AcroForm text field inside the given rect."""
    form = c.acroForm
    tf_align = {"left": "left", "center": "center", "right": "right"}[align]
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


def header(c):
    # Logo area
    draw_gear(c, MARGIN_L + 16, PAGE_H - MARGIN_T - 24, r_outer=14)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN_L + 38, PAGE_H - MARGIN_T - 18, "Precision")
    c.drawString(MARGIN_L + 38, PAGE_H - MARGIN_T - 32, "Auto Repair")

    # Title on the right
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 22)
    title = "MECHANIC INVOICE"
    tw = c.stringWidth(title, "Helvetica-Bold", 22)
    c.drawString(PAGE_W - MARGIN_R - tw, PAGE_H - MARGIN_T - 18, title)

    c.setFillColor(DARK_TEXT)
    c.setFont("Helvetica", 11)
    sub = "Vehicle Service Invoice"
    sw = c.stringWidth(sub, "Helvetica", 11)
    c.drawString(PAGE_W - MARGIN_R - sw, PAGE_H - MARGIN_T - 34, sub)


def draw_labeled_field(c, name, x, y, w, value="", field_h=16,
                       label_text=None, label_color=MUTED):
    """Draw a small label ABOVE a boxed text field, returning the field top y."""
    if label_text:
        c.setFillColor(label_color)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(x, y + field_h + 3, label_text.upper())
    box(c, x, y, w, field_h, fill=FIELD_BG)
    text_field(c, name, x, y, w, field_h, value=value, font_size=9)


def draw_table_cell_field(c, name, x, y, w, h, value="", align="left",
                          font_size=8, multiline=False):
    box(c, x, y, w, h, fill=None, stroke=BORDER)
    text_field(c, name, x, y, w, h, value=value, font_size=font_size,
               align=align, multiline=multiline)


def top_right_block(c, left_x, top_y):
    """Shop Name / Invoice #, then Invoicing Date / Service Date."""
    col_w = (CONTENT_W / 2 - 10) / 2
    gap = 10
    # Row 1: Shop Name | Invoice #
    row1_y = top_y - 36
    draw_labeled_field(c, "shop_name", left_x, row1_y, col_w,
                       value="Precision Auto Repair",
                       label_text="Shop Name")
    draw_labeled_field(c, "invoice_number", left_x + col_w + gap, row1_y,
                       col_w, value="INV-10428",
                       label_text="Invoice #")
    # Row 2: Invoicing Date | Service Date
    row2_y = row1_y - 34
    draw_labeled_field(c, "invoicing_date", left_x, row2_y, col_w,
                       value="03/12/2026",
                       label_text="Invoicing Date")
    draw_labeled_field(c, "service_date", left_x + col_w + gap, row2_y,
                       col_w, value="INV-1/3026",
                       label_text="Service Date")
    return row2_y


def vehicle_information(c, x, y, w):
    """Left-side VEHICLE INFORMATION block."""
    section_title(c, "VEHICLE INFORMATION", x, y)
    y -= 14
    # Two-column grid: VIN | LICENSE PLATE, YEAR/MAKE/MODEL | MILEAGE
    col_w = (w - 0) / 2
    row_h = 30
    # Header row
    header_h = 14
    box(c, x, y - header_h, col_w, header_h, fill=HEADER_BG)
    box(c, x + col_w, y - header_h, col_w, header_h, fill=HEADER_BG)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x + 5, y - header_h + 4, "VIN")
    c.drawString(x + col_w + 5, y - header_h + 4, "LICENSE PLATE")
    # Value row 1
    vy = y - header_h - row_h
    box(c, x, vy, col_w, row_h, fill=FIELD_BG)
    box(c, x + col_w, vy, col_w, row_h, fill=FIELD_BG)
    text_field(c, "vin", x, vy, col_w, row_h,
               value="415BFTKJUD74891", font_size=9)
    text_field(c, "license_plate", x + col_w, vy, col_w, row_h,
               value="TX-6422LM", font_size=9)
    # Header row 2
    hy2 = vy - header_h
    box(c, x, hy2, col_w, header_h, fill=HEADER_BG)
    box(c, x + col_w, hy2, col_w, header_h, fill=HEADER_BG)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x + 5, hy2 + 4, "YEAR / MAKE / MODEL")
    c.drawString(x + col_w + 5, hy2 + 4, "MILEAGE")
    # Value row 2
    vy2 = hy2 - row_h
    box(c, x, vy2, col_w, row_h, fill=FIELD_BG)
    box(c, x + col_w, vy2, col_w, row_h, fill=FIELD_BG)
    text_field(c, "year_make_model", x, vy2, col_w, row_h,
               value="2018 Toyota Camry", font_size=9)
    text_field(c, "mileage", x + col_w, vy2, col_w, row_h,
               value="72,430", font_size=9)
    # Service History
    sh_y_label = vy2 - 16
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x, sh_y_label, "Service History")
    sh_h = 48
    sh_y = sh_y_label - 4 - sh_h
    box(c, x, sh_y, w, sh_h, fill=FIELD_BG)
    text_field(
        c, "service_history", x, sh_y, w, sh_h,
        value=(
            "Front brake pads worn below safety limit. Replaced pads and "
            "inspected rotors. Performed full synthetic oil change and "
            "replaced engine air filter. Vehicle test driven and operating "
            "normally."
        ),
        font_size=8, multiline=True,
    )
    return sh_y  # bottom of this block


def customer_information(c, x, y, w):
    section_title(c, "CUSTOMER INFORMATION", x, y)
    y -= 14
    # ADDRESS header + field
    header_h = 14
    box(c, x, y - header_h, w, header_h, fill=HEADER_BG)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x + 5, y - header_h + 4, "ADDRESS")
    row_h = 22
    vy = y - header_h - row_h
    box(c, x, vy, w, row_h, fill=FIELD_BG)
    text_field(c, "customer_address_left", x, vy, w, row_h,
               value="2147 Willow Creek Dr, Austin, TX 78704",
               font_size=9)
    return vy


def customer_contact(c, x, y, w):
    section_title(c, "CUSTOMER CONTACT", x, y)
    y -= 14
    header_h = 14
    row_h = 22

    def header_cell(cx, cw, txt):
        box(c, cx, y - header_h, cw, header_h, fill=HEADER_BG)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(cx + 5, y - header_h + 4, txt)

    # CUSTOMER NAME
    header_cell(x, w, "CUSTOMER NAME")
    cy = y - header_h - row_h
    box(c, x, cy, w, row_h, fill=FIELD_BG)
    text_field(c, "customer_name", x, cy, w, row_h,
               value="Michael Torres", font_size=9)
    # Address row (full width, no header label per image)
    ay = cy - row_h
    box(c, x, ay, w, row_h, fill=FIELD_BG)
    text_field(c, "customer_address", x, ay, w, row_h,
               value="2147 Willow Creek Dr, Austin, TX 78704",
               font_size=9)
    # PHONE
    py_header = ay - header_h
    box(c, x, py_header, w, header_h, fill=HEADER_BG)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x + 5, py_header + 4, "PHONE")
    py = py_header - row_h
    box(c, x, py, w, row_h, fill=FIELD_BG)
    text_field(c, "customer_phone", x, py, w, row_h,
               value="(555) 482-1197", font_size=9)
    # EMAIL / EMAIL split
    eh_y = py - header_h
    half = w / 2
    box(c, x, eh_y, half, header_h, fill=HEADER_BG)
    box(c, x + half, eh_y, half, header_h, fill=HEADER_BG)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x + 5, eh_y + 4, "EMAIL")
    c.drawString(x + half + 5, eh_y + 4, "EMAIL")
    ey = eh_y - row_h
    box(c, x, ey, half, row_h, fill=FIELD_BG)
    box(c, x + half, ey, half, row_h, fill=FIELD_BG)
    text_field(c, "customer_email_1", x, ey, half, row_h,
               value="(555) 482-1197", font_size=9)
    text_field(c, "customer_email_2", x + half, ey, half, row_h,
               value="m.torres@email.com", font_size=9)
    return ey


def repair_services_table(c, x, y, w):
    section_title(c, "REPAIR SERVICES", x, y)
    y -= 14
    # Columns: ITEM (wide) | PARTS COST | LABOR COST | TOTAL
    parts_w = 75
    labor_w = 75
    total_w = 75
    desc_w = w - parts_w - labor_w - total_w
    header_h = 16
    # Header row
    box(c, x, y - header_h, desc_w, header_h, fill=HEADER_BG)
    box(c, x + desc_w, y - header_h, parts_w, header_h, fill=HEADER_BG)
    box(c, x + desc_w + parts_w, y - header_h, labor_w, header_h,
        fill=HEADER_BG)
    box(c, x + desc_w + parts_w + labor_w, y - header_h, total_w, header_h,
        fill=HEADER_BG)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x + 5, y - header_h + 5, "ITEM / SERVICE DESCRIPTION")
    c.drawString(x + desc_w + 10, y - header_h + 5, "PARTS COST")
    c.drawString(x + desc_w + parts_w + 10, y - header_h + 5, "LABOR COST")
    c.drawString(x + desc_w + parts_w + labor_w + 22, y - header_h + 5,
                 "TOTAL")

    # Prepopulated rows (matching the image)
    rows = [
        (
            "Front brake pads worn below safety limit. Replaced pads and "
            "inspected rotors. Replaced pads and inspected rotors. "
            "Performed full synthetic oil change and replaced engine air "
            "filter. Vehicle test driven and operating normally.",
            "$120.00", "$190.00", "$270.00", 46,
        ),
        ("Brake Pod Pod Replacement", "$120.00", "$130.00", "$190.00", 20),
        ("OK Change (Full Synthetic)", "$45.00", "$20.00", "$68.00", 20),
        ("Air Filter Replacement", "$25.00", "$15.00", "$40.00", 20),
        ("", "", "", "", 20),
        ("SHOP FEES", "$10.00", "", "$60.00", 20),
    ]

    cur_y = y - header_h
    for i, (desc, parts, labor, total, rh) in enumerate(rows):
        row_bg = ROW_BG if i % 2 == 0 else white
        cur_y -= rh
        # row backgrounds + borders
        box(c, x, cur_y, desc_w, rh, fill=row_bg)
        box(c, x + desc_w, cur_y, parts_w, rh, fill=row_bg)
        box(c, x + desc_w + parts_w, cur_y, labor_w, rh, fill=row_bg)
        box(c, x + desc_w + parts_w + labor_w, cur_y, total_w, rh,
            fill=row_bg)
        text_field(c, f"row{i+1}_desc", x, cur_y, desc_w, rh,
                   value=desc, font_size=7.5, multiline=True)
        text_field(c, f"row{i+1}_parts", x + desc_w, cur_y, parts_w, rh,
                   value=parts, font_size=8, align="right")
        text_field(c, f"row{i+1}_labor", x + desc_w + parts_w, cur_y,
                   labor_w, rh, value=labor, font_size=8, align="right")
        text_field(c, f"row{i+1}_total",
                   x + desc_w + parts_w + labor_w, cur_y, total_w, rh,
                   value=total, font_size=8, align="right")

    # Totals block to the right
    totals = [
        ("Subtotal", "subtotal", "$275.00"),
        ("Tax", "tax", "$31.50"),
        ("Total", "total", "$408.50"),
        ("Amount Paid", "amount_paid", "$200.00"),
        ("Balance Due", "balance_due", "$266.50"),
    ]
    tot_h = 18
    tot_x_label = x + desc_w  # right-aligned labels area spans parts col
    tot_x_val = x + desc_w + parts_w + labor_w
    for lbl, name, val in totals:
        cur_y -= tot_h
        # label cell (spans parts+labor columns, right aligned text)
        c.setFillColor(DARK_TEXT)
        c.setFont("Helvetica-Bold", 8.5)
        lbl_w = parts_w + labor_w
        tw = c.stringWidth(lbl, "Helvetica-Bold", 8.5)
        c.drawString(tot_x_label + lbl_w - tw - 6, cur_y + 5, lbl)
        # value cell
        box(c, tot_x_val, cur_y, total_w, tot_h, fill=white)
        text_field(c, name, tot_x_val, cur_y, total_w, tot_h,
                   value=val, font_size=8.5, align="right")

    return cur_y


def notes_and_conditions(c, x, y, w):
    # Free-form notes on the left, general condition on the right/full
    notes_h = 50
    y_notes = y - notes_h - 8
    box(c, x, y_notes, w, notes_h, fill=FIELD_BG)
    text_field(
        c, "notes", x, y_notes, w, notes_h,
        value=(
            "Front brake pads worn below safety limit. Replaced pads and "
            "inspected rotors.\n"
            "Front brake pads worn below safety limit. Replaced pads and "
            "inspected rotors.\n"
            "Performed full synthetic oil change and replaced engine air "
            "filter.\n"
            "Vehicle test driven and operating normally."
        ),
        font_size=8, multiline=True,
    )
    # General Condition
    gc_y = y_notes - 26
    box(c, x, gc_y, w, 20, fill=FIELD_BG)
    text_field(c, "general_condition", x, gc_y, w, 20,
               value="General Condition", font_size=9)
    return gc_y


def build():
    c = canvas.Canvas(OUTPUT, pagesize=LETTER)
    c.setTitle("Mechanic Invoice Template")
    c.setAuthor("Precision Auto Repair")

    # Page border (subtle)
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.8)
    c.rect(MARGIN_L - 10, MARGIN_T - 10,
           CONTENT_W + 20, PAGE_H - MARGIN_T - MARGIN_T + 20, stroke=1, fill=0)

    header(c)

    # Layout: two columns below the header
    top_y = PAGE_H - MARGIN_T - 60
    col_gap = 20
    left_w = (CONTENT_W - col_gap) * 0.55
    right_w = CONTENT_W - col_gap - left_w
    left_x = MARGIN_L
    right_x = MARGIN_L + left_w + col_gap

    # Right column top block: shop/invoice/dates
    top_right_bottom = top_right_block(c, right_x, PAGE_H - MARGIN_T - 40)

    # Left column: Vehicle Information
    left_bottom = vehicle_information(c, left_x, top_y, left_w)

    # Right column: Customer Contact (below the invoice meta fields)
    contact_bottom = customer_contact(
        c, right_x, top_right_bottom - 16, right_w
    )

    # Left column continues with Customer Information
    cust_info_bottom = customer_information(
        c, left_x, left_bottom - 16, left_w
    )

    # Repair services table full width
    table_top = min(cust_info_bottom, contact_bottom) - 18
    table_bottom = repair_services_table(c, MARGIN_L, table_top, CONTENT_W)

    # Notes + general condition
    notes_and_conditions(c, MARGIN_L, table_bottom, CONTENT_W)

    c.showPage()
    c.save()
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    build()

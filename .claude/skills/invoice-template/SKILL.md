---
name: invoice-template
description: Generate a pair of editable invoice PDFs (blank to sell, filled sample for listing thumbnails) for any service niche — HVAC, plumbing, pet grooming, auto, landscaping, cleaning, handyman, etc. Use when the user asks to create an invoice template, receipt template, or service form for sale on Etsy or similar. Also handles matching Etsy listing copy.
---

# Invoice Template Skill

This skill builds a **blank editable PDF** (the product to sell) plus a
**filled sample PDF** (for listing thumbnails) for any service niche,
using the same layout as the mechanic invoice in the repo root.

## What's in this skill

| File | Purpose |
| --- | --- |
| `invoice_generator.py` | Parameterized PDF engine. Never ask the user about this — just use it. |
| `example_configs.py` | Reference configs for MECHANIC, HVAC, and PET_GROOMING niches. Copy the closest one and edit. |

## How to use this skill

When the user says "make me an invoice template for X" (or similar):

### 1. Gather the niche details (one short round of questions)

Ask only what you don't already know. Aim for one concise message with
bullet points. You need:

- **Niche** (HVAC, plumbing, pet grooming, etc.)
- **Subtitle** (suggest one, e.g. "HVAC Service Invoice")
- **Sample business name** for the filled sample (suggest one if the
  user doesn't care — e.g. "ClearAir HVAC")
- **Domain info block** — the left-side section that replaces "VEHICLE
  INFORMATION". Pick 4 field labels relevant to the niche. Examples:
  - HVAC: Unit Type, Brand/Model, Serial #, Install Year
  - Plumbing: Property Type, Fixture, Water Source, Age
  - Pet grooming: Pet Name, Breed, Age/Weight, Temperament
  - Landscaping: Property Size, Service Area, Access Notes, Last Visit
- **Footer section title** — what replaces "GENERAL CONDITION". Could
  be "SYSTEM CONDITION", "PROPERTY NOTES", "PET CONDITION NOTES", etc.
- Whether to keep the **three money columns** (Parts / Labor / Total)
  as-is or rename them (e.g. "Service / Add-ons / Total" for grooming).

If the user is low-effort ("just pick for me"), don't re-ask — choose
sensible defaults and move on.

### 2. Build the config

Open `.claude/skills/invoice-template/example_configs.py` and copy the
closest existing config (MECHANIC, HVAC, or PET_GROOMING) as a
starting point. Edit:

- `title` — keep as `"INVOICE"` unless the user wants otherwise.
- `subtitle`
- `sample_business_name`
- `domain_info.section_title` and the 4 `fields` (each has `name` + `label`)
- `domain_info.history` — keep if there's a natural "history" concept
  for the niche, or set to `None` / omit the key
- `services_table.section_title` and `columns` (4 strings)
- `footer_section_title`
- `sample_data` — fill in realistic dummy values for EVERY field name
  referenced above (`vin`, `license_plate`, etc. are replaced by your
  new domain field names). Use realistic pricing so the Etsy thumbnail
  looks professional.
- `sample_checks` — usually `{"pm_card": True}` to show a checked box

Keep sample values realistic and specific (real-sounding addresses,
phone numbers, prices). Avoid placeholder-style text like "Customer
Name 1". Low-effort dummy data makes the listing photo look amateur.

### 3. Generate the PDFs

Write a tiny runner script in the project root (or run inline), e.g.:

```python
import sys
sys.path.insert(0, ".claude/skills/invoice-template")
from invoice_generator import build_pair
from example_configs import HVAC
build_pair(HVAC, out_prefix="hvac_invoice_template")
```

Or just `cd` into the skill directory and run:

```bash
python3 .claude/skills/invoice-template/example_configs.py
```
(which builds HVAC by default — edit the `__main__` block if needed.)

Output files land in the current working directory as:
- `{prefix}_BLANK.pdf` — the product
- `{prefix}_SAMPLE.pdf` — for thumbnails

### 4. Verify

After generating, render the sample to a PNG and Read it to confirm
the layout looks right (no overflow, field labels correct, numbers
align, checkboxes spaced evenly). Use pymupdf:

```python
import pymupdf
doc = pymupdf.open("hvac_invoice_template_SAMPLE.pdf")
doc[0].get_pixmap(dpi=150).save("/tmp/preview.png")
```

Then show the user where to download the files and offer to generate
matching Etsy listing copy (see `ETSY_LISTING_INSTRUCTIONS.md` in the
repo root for the template — swap "mechanic"/"vehicle" references for
the niche).

## Layout invariants (don't break these)

The engine keeps everything on a single US-Letter page. If you add or
remove sections, re-check for overflow by running:

```python
import pymupdf
doc = pymupdf.open("out_BLANK.pdf")
pg = doc[0]
overflow = [w.field_name for w in pg.widgets()
            if w.rect.y1 > pg.rect.y1 or w.rect.y0 < 0]
print(overflow or "ok")
```

## Dependencies

```bash
pip3 install reportlab pymupdf
```

## Common customizations

- **More/fewer line item rows**: edit `row_defs` in `_services_table`.
- **Different column widths**: edit `parts_w`, `labor_w`, `total_w` in
  `_services_table`.
- **No history block**: omit the `history` key from `domain_info`.
- **Different logo**: replace `_draw_gear` with another shape, or set
  `"logo_style": "none"` in the config (the sample header becomes
  business name only).

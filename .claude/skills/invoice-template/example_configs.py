"""Example configs for the invoice template generator.

Each CONFIG is a plain dict. Pass it to
`invoice_generator.build_pair(config, out_prefix="...")` to generate
BLANK + SAMPLE PDFs.
"""

# --- Mechanic / Auto Repair ----------------------------------------------
MECHANIC = {
    "title": "INVOICE",
    "subtitle": "Vehicle Service Invoice",
    "logo_style": "gear",
    "sample_business_name": "Precision Auto Repair",
    "pdf_title": "Mechanic Invoice Template",
    "footer_section_title": "GENERAL CONDITION",
    "domain_info": {
        "section_title": "VEHICLE INFORMATION",
        "fields": [
            {"name": "vin", "label": "VIN"},
            {"name": "license_plate", "label": "LICENSE PLATE"},
            {"name": "year_make_model", "label": "YEAR / MAKE / MODEL"},
            {"name": "mileage", "label": "MILEAGE"},
        ],
        "history": {"name": "service_history", "label": "Service History"},
    },
    "services_table": {
        "section_title": "REPAIR SERVICES",
        "columns": ["ITEM / SERVICE DESCRIPTION", "PARTS COST",
                    "LABOR COST", "TOTAL"],
    },
    "sample_data": {
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
            "inspected rotors. Performed full synthetic oil change and "
            "replaced engine air filter. Vehicle test driven and operating "
            "normally."
        ),
        "customer_name": "Michael Torres",
        "customer_address": "2147 Willow Creek Dr, Austin, TX 78704",
        "customer_address_left": "2147 Willow Creek Dr, Austin, TX 78704",
        "customer_phone": "(555) 482-1197",
        "customer_email_1": "m.torres@email.com",
        "customer_email_2": "m.torres@email.com",
        "row1_desc": "Front brake pads worn below safety limit. "
                     "Replaced pads and inspected rotors.",
        "row1_parts": "$120.00", "row1_labor": "$150.00",
        "row1_total": "$270.00",
        "row2_desc": "Brake Pad Replacement",
        "row2_parts": "$120.00", "row2_labor": "$130.00",
        "row2_total": "$250.00",
        "row3_desc": "Oil Change (Full Synthetic)",
        "row3_parts": "$45.00", "row3_labor": "$23.00",
        "row3_total": "$68.00",
        "row4_desc": "Air Filter Replacement",
        "row4_parts": "$25.00", "row4_labor": "$15.00",
        "row4_total": "$40.00",
        "row6_desc": "Shop Fees", "row6_parts": "$10.00",
        "row6_total": "$10.00",
        "subtotal": "$638.00", "tax": "$31.90", "total": "$669.90",
        "amount_paid": "$400.00", "balance_due": "$269.90",
        "notes": "Customer approved all recommended services prior to "
                 "work. Vehicle test driven post-repair and operating "
                 "normally. Next recommended service: 77,500 miles.",
        "footer_notes": "Overall condition: Good. Tires at 6/32\". "
                        "Battery tested healthy. Recommend tire rotation "
                        "at next service.",
        "signature": "Michael Torres", "signed_date": "03/13/2026",
    },
    "sample_checks": {"pm_card": True},
}


# --- HVAC Service Invoice ------------------------------------------------
HVAC = {
    "title": "INVOICE",
    "subtitle": "HVAC Service Invoice",
    "sample_business_name": "ClearAir HVAC",
    "pdf_title": "HVAC Invoice Template",
    "footer_section_title": "SYSTEM CONDITION",
    "domain_info": {
        "section_title": "SYSTEM INFORMATION",
        "fields": [
            {"name": "unit_type", "label": "UNIT TYPE"},
            {"name": "brand_model", "label": "BRAND / MODEL"},
            {"name": "serial_number", "label": "SERIAL #"},
            {"name": "install_year", "label": "INSTALL YEAR"},
        ],
        "history": {"name": "service_history",
                    "label": "Service History"},
    },
    "services_table": {
        "section_title": "SERVICES PERFORMED",
        "columns": ["SERVICE / PARTS DESCRIPTION", "PARTS COST",
                    "LABOR COST", "TOTAL"],
    },
    "sample_data": {
        "shop_name": "ClearAir HVAC",
        "invoice_number": "INV-8821",
        "invoicing_date": "04/18/2026",
        "service_date": "04/18/2026",
        "unit_type": "Central AC — 3 Ton",
        "brand_model": "Carrier 24ACC636",
        "serial_number": "2718X-HV-44921",
        "install_year": "2017",
        "service_history": (
            "Summer tune-up. Replaced capacitor, cleaned coils, topped "
            "refrigerant, and tested operating pressures. System cooling "
            "to spec."
        ),
        "customer_name": "Danielle Park",
        "customer_address": "8510 Riverbend Ln, Nashville, TN 37211",
        "customer_address_left": "8510 Riverbend Ln, Nashville, TN 37211",
        "customer_phone": "(615) 555-2047",
        "customer_email_1": "d.park@email.com",
        "row1_desc": "Diagnostic & full summer tune-up; pressures, "
                     "airflow, thermostat calibration.",
        "row1_parts": "$0.00", "row1_labor": "$120.00",
        "row1_total": "$120.00",
        "row2_desc": "Dual-Run Capacitor (45/5 MFD)",
        "row2_parts": "$58.00", "row2_labor": "$45.00",
        "row2_total": "$103.00",
        "row3_desc": "Coil Cleaning",
        "row3_parts": "$15.00", "row3_labor": "$60.00",
        "row3_total": "$75.00",
        "row4_desc": "R-410A Top-off (1 lb)",
        "row4_parts": "$42.00", "row4_labor": "$0.00",
        "row4_total": "$42.00",
        "row6_desc": "Trip Charge", "row6_parts": "$49.00",
        "row6_total": "$49.00",
        "subtotal": "$389.00", "tax": "$36.06", "total": "$425.06",
        "amount_paid": "$425.06", "balance_due": "$0.00",
        "notes": "System passed all functional checks. Recommend annual "
                 "spring tune-up and filter change every 90 days.",
        "footer_notes": "System condition: Good. Airflow within spec. "
                        "Minor surface rust on outdoor cabinet — not "
                        "affecting operation.",
        "signature": "Danielle Park", "signed_date": "04/18/2026",
    },
    "sample_checks": {"pm_card": True},
}


# --- Pet Grooming --------------------------------------------------------
PET_GROOMING = {
    "title": "INVOICE",
    "subtitle": "Pet Grooming Invoice",
    "sample_business_name": "Happy Tails",
    "pdf_title": "Pet Grooming Invoice Template",
    "footer_section_title": "PET CONDITION NOTES",
    "domain_info": {
        "section_title": "PET INFORMATION",
        "fields": [
            {"name": "pet_name", "label": "PET NAME"},
            {"name": "breed", "label": "BREED"},
            {"name": "age_weight", "label": "AGE / WEIGHT"},
            {"name": "temperament", "label": "TEMPERAMENT"},
        ],
        "history": {"name": "service_history",
                    "label": "Grooming History"},
    },
    "services_table": {
        "section_title": "GROOMING SERVICES",
        "columns": ["SERVICE DESCRIPTION", "SERVICE",
                    "ADD-ONS", "TOTAL"],
    },
    "sample_data": {
        "shop_name": "Happy Tails",
        "invoice_number": "HT-2044",
        "invoicing_date": "04/22/2026",
        "service_date": "04/22/2026",
        "pet_name": "Biscuit",
        "breed": "Goldendoodle",
        "age_weight": "4 yrs / 62 lb",
        "temperament": "Friendly",
        "service_history": (
            "Regular client since 2023. Prefers quiet dryer, gentle "
            "brushing. Last visit: 02/10/2026."
        ),
        "customer_name": "Ava Nguyen",
        "customer_address": "214 Cedar St, Portland, OR 97205",
        "customer_address_left": "214 Cedar St, Portland, OR 97205",
        "customer_phone": "(503) 555-9921",
        "customer_email_1": "ava.n@email.com",
        "row1_desc": "Full groom: bath, blow dry, breed cut, ear "
                     "cleaning, nail trim, sanitary trim.",
        "row1_parts": "$85.00", "row1_labor": "$10.00",
        "row1_total": "$95.00",
        "row2_desc": "De-Shedding Treatment",
        "row2_parts": "$25.00", "row2_total": "$25.00",
        "row3_desc": "Teeth Brushing",
        "row3_parts": "$10.00", "row3_total": "$10.00",
        "row4_desc": "Blueberry Facial",
        "row4_parts": "$8.00", "row4_total": "$8.00",
        "subtotal": "$138.00", "tax": "$0.00", "total": "$138.00",
        "amount_paid": "$138.00", "balance_due": "$0.00",
        "notes": "Biscuit was calm throughout. Recommend next "
                 "appointment in 6–8 weeks.",
        "footer_notes": "Coat and skin look healthy. Minor tartar on "
                        "rear molars — suggest vet cleaning soon.",
        "signature": "Ava Nguyen", "signed_date": "04/22/2026",
    },
    "sample_checks": {"pm_card": True},
}


if __name__ == "__main__":
    # Example: build the HVAC pair.
    from invoice_generator import build_pair
    build_pair(HVAC, out_prefix="hvac_invoice_template")

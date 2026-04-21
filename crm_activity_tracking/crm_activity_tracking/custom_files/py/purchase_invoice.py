import frappe

def update_item_buyer_details(doc, method=None):
    import frappe

    # Collect item updates first (avoid multiple saves)
    item_map = {}

    for row in doc.items:
        if not row.item_code:
            continue

        item_map[row.item_code] = {
            "supplier": doc.supplier,
            "rate": row.rate,
            "date": doc.posting_date
        }

    # Process each item only once
    for item_code, data in item_map.items():
        item_doc = frappe.get_doc("Item", item_code)

        # Remove existing rows for same supplier
        item_doc.custom_buyer_details = [
            d for d in item_doc.custom_buyer_details
            if d.buyer != data["supplier"]
        ]

        # Add new row
        item_doc.append("custom_buyer_details", {
            "buyer": data["supplier"],
            "purchase_rate": data["rate"],
            "date": data["date"]
        })

        # Save once per item
        item_doc.save(ignore_permissions=True)

    frappe.db.commit()
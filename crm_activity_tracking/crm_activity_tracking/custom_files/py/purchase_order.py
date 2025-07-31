import frappe
from frappe.utils import getdate

@frappe.whitelist()
def get_last_buying_rate(item_code, transaction_date, supplier):
    if not item_code or not transaction_date or not supplier:
        return None

    transaction_date = getdate(transaction_date)

    result = frappe.db.sql("""
        SELECT pii.rate
        FROM `tabPurchase Invoice Item` pii
        JOIN `tabPurchase Invoice` pi ON pii.parent = pi.name
        WHERE pi.supplier = %s
            AND pii.item_code = %s
            AND pi.docstatus != 2
            AND pi.posting_date <= %s
        ORDER BY pi.posting_date DESC, pi.modified DESC
        LIMIT 1
    """, (supplier, item_code, transaction_date), as_dict=True)

    if result:
        return result[0].rate

    return 0


def validate_supplier_lastprice(doc, event):
    """
    Triggered on save. Updates custom_last_supplier_buying_rate for each item.
    """
    if not doc.transaction_date or not doc.supplier:
        return

    for item in doc.items:
        if not item.item_code:
            continue

        last_rate = get_last_buying_rate(
            item_code=item.item_code,
            transaction_date=doc.transaction_date,
            supplier=doc.supplier
        )

        item.custom_last_supplier_buying_rate = last_rate

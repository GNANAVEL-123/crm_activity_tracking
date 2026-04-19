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


@frappe.whitelist()
def get_supplier_rate_details_single(item_code):

    import frappe
    from frappe.utils import formatdate

    # -----------------------------
    # GET DATA
    # -----------------------------
    data = frappe.db.sql("""
        SELECT 
            pi.supplier,
            pii.rate,
            pi.posting_date
        FROM `tabPurchase Invoice Item` pii
        INNER JOIN `tabPurchase Invoice` pi
            ON pi.name = pii.parent
        WHERE 
            pii.item_code = %s
            AND pi.docstatus = 1
        ORDER BY pi.posting_date DESC
    """, item_code, as_dict=True)

    if not data:
        return "<p style='padding:10px;'>No purchase history found</p>"

    # -----------------------------
    # UNIQUE SUPPLIER
    # -----------------------------
    supplier_map = {}
    for d in data:
        if d.supplier not in supplier_map:
            supplier_map[d.supplier] = d

    # -----------------------------
    # LOWEST RATE
    # -----------------------------
    min_rate = min([d.rate for d in supplier_map.values()])

    # -----------------------------
    # HTML + CSS (Enhanced)
    # -----------------------------
    html = """
    <style>
    body {
        background: linear-gradient(135deg, #f0f4f7, #e3f2fd);
    }

    .card {
        font-family: 'Segoe UI', Arial;
        border-radius: 12px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.15);
        padding: 15px;
        background: #ffffff;
    }

    .title {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 12px;
        color: #2c3e50;
    }

    .table {
        width: 100%;
        border-collapse: collapse;
        border-radius: 8px;
        overflow: hidden;
    }

    .table th {
        background: linear-gradient(45deg, #2196F3, #1565C0);
        color: white;
        padding: 10px;
        font-size: 13px;
        text-align: left;
    }

    .table td {
        padding: 10px;
        font-size: 13px;
        border-bottom: 1px solid #eee;
    }

    .table tr:hover {
        background-color: #f1f8ff;
        transition: 0.2s;
    }

    .best-rate {
        background: #e8f5e9 !important;
        font-weight: bold;
        color: #2e7d32;
    }

    .badge {
        background: #2e7d32;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        margin-left: 5px;
    }

    .footer {
        margin-top: 10px;
        font-size: 12px;
        color: #2e7d32;
    }
    </style>

    <div class="card">
        <div class="title">📊 Supplier-wise Latest Purchase Rate</div>

        <table class="table">
            <thead>
                <tr>
                    <th>Supplier</th>
                    <th style="text-align:right;">Last Rate</th>
                    <th>Last Purchase Date</th>
                </tr>
            </thead>
            <tbody>
    """

    # -----------------------------
    # TABLE ROWS
    # -----------------------------
    for s, d in supplier_map.items():

        is_best = d.rate == min_rate
        row_class = "best-rate" if is_best else ""
        badge = '<span class="badge">Best</span>' if is_best else ""

        # ✅ FORMAT DATE HERE
        formatted_date = formatdate(d.posting_date, "dd-MM-yyyy")

        html += f"""
            <tr class="{row_class}">
                <td>{s} {badge}</td>
                <td style="text-align:right;">₹ {float(d.rate):,.2f}</td>
                <td>{formatted_date}</td>
            </tr>
        """

    html += """
            </tbody>
        </table>

        <div class="footer">✔ Highlighted row indicates lowest supplier rate</div>
    </div>
    """

    return html
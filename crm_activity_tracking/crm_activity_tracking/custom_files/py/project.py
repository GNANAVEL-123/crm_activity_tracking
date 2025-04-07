import frappe
import json
from frappe.desk.reportview import get_filters_cond

def consumed_update(doc, action):
    if not doc.custom_item_consumption_details:
        return

    # Step 1: Build map of delivered_qty from Delivered Items table
    delivered_map = {}
    if doc.custom_project_item_details:
        for row in doc.custom_project_item_details:
            if row.item:
                delivered_map[row.item] = {
                    "delivered_qty": row.delivered_qty or 0,
                    "row_ref": row
                }

    # Step 2: Aggregate used_qty per item from Consumption table
    item_usage_map = {}
    for row in doc.custom_item_consumption_details:
        if row.item:
            item_usage_map[row.item] = item_usage_map.get(row.item, 0) + (row.used_qty or 0)

    # Step 3: Validate & update
    for item_code, used_qty in item_usage_map.items():
        if item_code not in delivered_map:
            frappe.throw(f"No delivered item found for <b>{item_code}</b>.")

        delivered_qty = delivered_map[item_code]["delivered_qty"]
        if used_qty > delivered_qty:
            frappe.throw(
                f"Used Qty ({used_qty}) for item <b>{item_code}</b> cannot be greater than Delivered Qty ({delivered_qty})."
            )

        # Update consumed_qty & balance_qty
        row = delivered_map[item_code]["row_ref"]
        row.consumed_qty = used_qty
        row.balance_qty = delivered_qty - used_qty



@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def item_list(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
    import json
    from frappe.desk.reportview import get_filters_cond

    if isinstance(filters, str):
        filters = json.loads(filters)
    
    project_name = filters.pop("doc", None)  # <-- remove 'doc' from filters to avoid SQL error

    if not project_name:
        return []
        
    conditions = []

    pro_doc = frappe.get_doc("Project", project_name)

    item_list = frappe.db.get_all(
        "Project Item Details",
        filters={"parenttype": "Project", "parent": pro_doc.name},
        pluck="item"
    )

    if not item_list:
        return []

    filters['name'] = item_list[0] if len(item_list) == 1 else ['in', item_list]

    meta = frappe.get_meta(doctype, cached=True)
    searchfields = meta.get_search_fields()

    columns = ""
    extra_searchfields = [field for field in searchfields if field != "name"]
    if extra_searchfields:
        columns += ", " + ", ".join(extra_searchfields)

    searchfields_cond = " or ".join([f"`tab{doctype}`.{field} like %(txt)s" for field in searchfields])

    return frappe.db.sql(
        f"""
        SELECT `tab{doctype}`.name {columns}
        FROM `tab{doctype}`
        WHERE 1=1 
            {get_filters_cond(doctype, filters, conditions).replace("%", "%%")}
            AND ({searchfields_cond})
        ORDER BY
            IF(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
            idx DESC,
            name
        LIMIT %(start)s, %(page_len)s
        """,
        {
            "txt": f"%%{txt}%%",
            "_txt": txt.replace("%", ""),
            "start": start,
            "page_len": page_len,
        },
        as_dict=as_dict,
    )


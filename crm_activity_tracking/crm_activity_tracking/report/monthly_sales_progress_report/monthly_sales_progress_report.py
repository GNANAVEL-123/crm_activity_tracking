import frappe
from frappe import _

def execute(filters=None):
    columns, data = [], []
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    columns = [
        {"label": _("DATE"), "fieldtype": "Date", "fieldname": "date", "width": 180},
        {"label": _("NO OF QUOTATION"), "fieldtype": "float", "fieldname": "no_quotation", "width": 180},
        {"label": _("NO OF QUOTATION VALUE"), "fieldtype": "float", "fieldname": "no_quotation_value", "width": 180},
        {"label": _("NO OF CRM QUOTATION FOLLOW"), "fieldtype": "float", "fieldname": "no_crm_quotation_follow", "width": 180},
        {"label": _("NO OF QUOTATION CONVERTING"), "fieldtype": "float", "fieldname": "no_quotation_converting", "width": 200},
        {"label": _("NO OF QUOTATION CANCEL"), "fieldtype": "Float", "fieldname": "no_quotation_cancel", "width": 180},
        {"label": _("NO OF NEW LEAD"), "fieldtype": "Float", "fieldname": "no_lead", "width": 200},
        {"label": _("NO OF LEAD FOLLOW"), "fieldtype": "Float", "fieldname": "no_lead_follow", "width": 180},
        {"label": _("NO OF REFILLING CERTIFICATE"), "fieldtype": "currency", "fieldname": "no_refilling", "width": 180},
        {"label": _("NO OF WARRANTY CERTIFICATE"), "fieldtype": "currency", "fieldname": "no_warranty", "width": 180},
    ]
    return columns

from datetime import timedelta, datetime

def get_data(filters):
    data = []

    # Ensure date filters exist
    if not filters.get("from_date") or not filters.get("to_date"):
        frappe.throw(_("Please specify both From Date and To Date"))

    # Parse the date range
    from_date = datetime.strptime(filters.get("from_date"), "%Y-%m-%d")
    to_date = datetime.strptime(filters.get("to_date"), "%Y-%m-%d")

    # Loop through each day in the date range
    current_date = from_date
    while current_date <= to_date:
        # Convert current date to string for filtering
        current_date_str = current_date.strftime("%Y-%m-%d")

        # Define filters for the specific day
        daily_filter = {
            "transaction_date": current_date_str,
        }
        lead_filter = {
            "creation": ["between", [f"{current_date_str} 00:00:00", f"{current_date_str} 23:59:59"]],
        }
        quo_follow_filter = {
            "custom_followup.date": ["between", [current_date_str, current_date_str]],
        }
        lead_follow_filter = {
            "custom_view_follow_up_details_copy.date": ["between", [current_date_str, current_date_str]],
        }

        # Add user filter if provided
        if filters.get("user"):
            daily_filter["custom_quotation_owner"] = filters.get("user")
            lead_filter["lead_owner"] = filters.get("user")
            quo_follow_filter["custom_followup.followed_by"] = filters.get("user")
            lead_follow_filter["custom_view_follow_up_details_copy.followed_by"] = filters.get("user")

        # Fetch daily counts and sums
        daily_data = {
            "date": current_date_str,
            "no_quotation": frappe.db.count("Quotation", filters=daily_filter),
            "no_quotation_value": get_sum("Quotation", "grand_total", daily_filter),
            "no_crm_quotation_follow": get_child_table_count(
                "Quotation", "custom_followup", "date", current_date_str, current_date_str, filters.get("user")
            ),
            "no_quotation_converting": frappe.db.count("Quotation", {"custom_order_convert_date": current_date_str}),
            "no_quotation_cancel": frappe.db.count("Quotation", {"custom_quotation_cancel_date": current_date_str}),
            "no_lead": frappe.db.count("Lead", filters=lead_filter),
            "no_lead_follow": get_child_table_count(
                "Lead", "custom_view_follow_up_details_copy", "date", current_date_str, current_date_str, filters.get("user")
            ),
            "no_refilling": frappe.db.count("Refilling Certificate", {"date": current_date_str, "employee": filters.get("user")}),
            "no_warranty": frappe.db.count("Warranty Certificate", {"date": current_date_str, "employee": filters.get("user")}),
        }

        # Append daily data to the result
        data.append(daily_data)

        # Move to the next day
        current_date += timedelta(days=1)

    return data

def get_child_table_count(parent_doctype, child_table_fieldname, date_field, from_date, to_date, user=None):
    """
    Fetch the count of child table records based on the parent doctype and date filters.

    Args:
        parent_doctype (str): Parent doctype name (e.g., "Quotation").
        child_table_fieldname (str): Child table fieldname in the parent doctype (e.g., "custom_followup").
        date_field (str): The date field in the child table to filter.
        from_date (str): Start date for filtering.
        to_date (str): End date for filtering.
        user (str): User filter (optional).

    Returns:
        int: Count of matching child table records.
    """
    additional_filter = f"AND child.followed_by = '{user}'" if user else ""

    child_table_count = frappe.db.sql(f"""
        SELECT COUNT(*) AS count
        FROM `tab{parent_doctype}` AS parent
        INNER JOIN `tabFollow-Up` AS child
        ON child.parent = parent.name
        WHERE child.parentfield = %s
        AND child.{date_field} BETWEEN %s AND %s
        {additional_filter}
    """, (child_table_fieldname, from_date, to_date), as_dict=True)

    return child_table_count[0].count if child_table_count else 0

def get_sum(doctype, fieldname, filters):
    """
    Get the sum of a specific field from a given doctype based on filters.

    Args:
        doctype (str): The name of the doctype.
        fieldname (str): The field to sum up.
        filters (dict): Filters to apply.

    Returns:
        float: The sum of the field values.
    """
    filter_conditions = " AND ".join([f"{key} {get_condition(value)}" for key, value in filters.items()])
    sql_query = f"""
        SELECT SUM(`{fieldname}`) AS total
        FROM `tab{doctype}`
        WHERE {filter_conditions}
    """
    result = frappe.db.sql(sql_query, as_dict=True)
    return result[0].total or 0

def get_condition(value):
    """
    Helper function to generate SQL condition based on filter type.

    Args:
        value: The filter value (could be a list or scalar).

    Returns:
        str: SQL condition string.
    """
    if isinstance(value, list) and value[0] == "between":
        return f"BETWEEN '{value[1][0]}' AND '{value[1][1]}'"
    elif isinstance(value, list):
        return f"IN {tuple(value)}"
    else:
        return f"= '{value}'"

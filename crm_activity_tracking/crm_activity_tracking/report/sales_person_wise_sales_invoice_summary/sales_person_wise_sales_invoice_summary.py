# Copyright (c) 2025, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from erpnext import get_company_currency


def execute(filters=None):
	filters = filters or {}

	columns = get_columns()
	data = get_data(filters)

	return columns, data



def get_columns():
	return [
		{
			"label": _("Sales Invoice"),
			"fieldname": "sales_invoice",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 150
		},
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 180
		},
		{
			"label": _("Sales Executive"),
			"fieldname": "custom_sales_executive",
			"fieldtype": "Link",
			"options": "User",
			"width": 180
		},
		{
			"label": _("Grand Total"),
			"fieldname": "grand_total",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Currency"),
			"fieldname": "currency",
			"fieldtype": "Link",
			"options": "Currency",
			"hidden": 1
		}
	]



def get_data(filters):
	conditions = []
	values = []

	if filters.get("company"):
		conditions.append("company = %s")
		values.append(filters["company"])

	if filters.get("customer"):
		conditions.append("customer = %s")
		values.append(filters["customer"])

	if filters.get("custom_sales_executive"):
		conditions.append("custom_sales_executive = %s")
		values.append(filters["custom_sales_executive"])

	if filters.get("from_date"):
		conditions.append("posting_date >= %s")
		values.append(filters["from_date"])

	if filters.get("to_date"):
		conditions.append("posting_date <= %s")
		values.append(filters["to_date"])

	condition_str = " AND ".join(conditions)
	if condition_str:
		condition_str = "AND " + condition_str

	data = frappe.db.sql(
		f"""
		SELECT
			name AS sales_invoice,
			posting_date,
			customer,
			custom_sales_executive,
			grand_total,
			currency
		FROM `tabSales Invoice`
		WHERE docstatus = 1
		{condition_str}
		ORDER BY posting_date DESC
		""",
		values,
		as_dict=True
	)

	return data

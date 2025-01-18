// Copyright (c) 2025, CRM and contributors
// For license information, please see license.txt

frappe.query_reports["Sales and Service Details Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd":1,
			"default": frappe.datetime.get_today(),
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd":1,
			"default": frappe.datetime.get_today(),
		},
		{
			"fieldname": "user",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options":"User",
			"width": "80"
		},
	]
};

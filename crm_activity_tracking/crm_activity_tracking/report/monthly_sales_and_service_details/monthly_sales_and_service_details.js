// Copyright (c) 2025, CRM and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly Sales and Service Details"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.get_today(),
		},
		{
			"fieldname": "region",
			"label": __("Region"),
			"fieldtype": "Link",
			"options":"Territory",
			"width": "80"
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

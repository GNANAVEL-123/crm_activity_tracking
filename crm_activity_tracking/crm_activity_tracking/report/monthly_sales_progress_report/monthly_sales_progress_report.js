// Copyright (c) 2025, CRM and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly Sales Progress Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd":1,
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd":1,
			"default": frappe.datetime.get_today(),
		},
	]
};

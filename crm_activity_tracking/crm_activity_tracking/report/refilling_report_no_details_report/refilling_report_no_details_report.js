// Copyright (c) 2024, CRM and contributors
// For license information, please see license.txt

frappe.query_reports["Refilling Report No Details Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80"
		},
		{
			"fieldname": "region",
			"label": __("Region"),
			"fieldtype": "Link",
			"options":"Territory",
			"width": "80"
		},
	]
};

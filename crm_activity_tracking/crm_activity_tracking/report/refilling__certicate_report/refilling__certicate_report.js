// Copyright (c) 2024, CRM and contributors
// For license information, please see license.txt

frappe.query_reports["Refilling  Certicate Report"] = {
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
		{
			"fieldname": "refilling_certificate",
			"label": __("Refilling Certificate"),
			"fieldtype": "Check",
			"width": "80",
			"default":1
		},
		{
			"fieldname": "warranty_certificate",
			"label": __("Warranty Certificate"),
			"fieldtype": "Check",
			"width": "80",
			"default":1
		},
		{
			"fieldname": "refilling_report_no",
			"label": __("Refilling Report No"),
			"fieldtype": "Check",
			"width": "80",
			"default":1
		},
		{
			"fieldname": "invoice_no_list",
			"label": __("Invoice No"),
			"fieldtype": "Select",
			"options":["", "Yes", "No"],
			"width": "80",
		},
	]
};

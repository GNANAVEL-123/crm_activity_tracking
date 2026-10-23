// Copyright (c) 2026, CRM and contributors
// For license information, please see license.txt

frappe.query_reports["AMC Refilling Details Report"] = {
	"filters": [
		{
			"fieldname": "customer_name",
			"label": __("Customer Name"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname": "amc",
			"label": __("AMC"),
			"fieldtype": "Link",
			"options": "AMC"
		},
		{
			"fieldname": "region",
			"label": __("Region"),
			"fieldtype": "Data"
		},
		{
			"fieldname": "location",
			"label": __("Location"),
			"fieldtype": "Link",
			"options": "AMC Location"
		},
		{
			"fieldname": "from_date",
			"label": __("Next Due From"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": __("Next Due To"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "month",
			"label": __("Next Due Month"),
			"fieldtype": "Select",
			"options": ["", "January", "February", "March", "April", "May", "June",
				"July", "August", "September", "October", "November", "December"]
		},
		{
			"fieldname": "year",
			"label": __("Next Due Year"),
			"fieldtype": "Select",
			"options": get_year_options()
		}
	]
};

function get_year_options() {
	const current_year = new Date().getFullYear();
	const years = [""];
	for (let year = current_year - 5; year <= current_year + 10; year++) {
		years.push(String(year));
	}
	return years;
}

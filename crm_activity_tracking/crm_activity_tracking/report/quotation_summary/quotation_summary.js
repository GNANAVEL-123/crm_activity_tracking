// Copyright (c) 2025, CRM and contributors
// For license information, please see license.txt

frappe.query_reports["Quotation Summary"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start()
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_end()
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: ["", "Draft", "Open", "Replied", "Partially Ordered", "Ordered", "Lost", "Cancelled", "Expired", "Order Cancelled"],
		},
		{
			fieldname: "allocated_to",
			label: __("Allocated To"),
			fieldtype: "Link",
			options:"User",
		},
		{
			fieldname: "customer",
			label: __("Company Name"),
			fieldtype: "Link",
			options:"Customer",
		},
		{
			fieldname: "region",
			label: __("Region"),
			fieldtype: "Link",
			options:"Territory",
		},
	],
};

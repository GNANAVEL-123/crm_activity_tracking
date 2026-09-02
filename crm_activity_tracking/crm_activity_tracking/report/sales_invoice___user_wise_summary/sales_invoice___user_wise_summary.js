// Copyright (c) 2026, CRM and contributors
// For license information, please see license.txt

frappe.query_reports["Sales Invoice - User Wise Summary"] = {
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
			default: frappe.datetime.get_today()
		},
		{
			fieldname: "docstatus_filter",
			label: __("Invoice Status"),
			fieldtype: "Select",
			options: [
				{ value: "Both", label: __("Both (Draft + Submitted)") },
				{ value: "Draft", label: __("Draft Only") },
				{ value: "Submitted", label: __("Submitted Only") }
			],
			default: "Both"
		},
		{
			fieldname: "owner",
			label: __("User"),
			fieldtype: "Link",
			options: "User"
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company")
		},
		{
			fieldname: "consolidated_view",
			label: __("Consolidated View (User Wise Total Only)"),
			fieldtype: "Check",
			default: 0
		}
	]
};
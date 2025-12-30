// Copyright (c) 2025, CRM and contributors
// For license information, please see license.txt

frappe.query_reports["Sales Person Wise Sales Invoice Summary"] = {
	filters: [
		{
			fieldname: "custom_sales_executive",
			label: __("Sales Executive"),
			fieldtype: "Link",
			options: "User"
		},
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer"
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: erpnext.utils.get_fiscal_year(
				frappe.datetime.get_today(),
				true
			)[1]
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today()
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1
		}
	]
};


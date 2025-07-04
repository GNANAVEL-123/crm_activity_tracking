// Copyright (c) 2025, CRM and contributors
// For license information, please see license.txt

frappe.query_reports["Tasks Summary"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "priority",
			label: __("Priority"),
			fieldtype: "Select",
			options: ["", "Low", "Medium", "High", "Urgent"],
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: ["", "Open", "Working", "Pending Review", "Overdue", "Completed"],
		},
		{
			fieldname: "allocated_to",
			label: __("Allocated To"),
			fieldtype: "Link",
			options: "User",
		},
	],
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.id == "delay") {
			if (data["delay"] > 0) {
				value = `<p style="color: red; font-weight: bold">${value}</p>`;
			} else {
				value = `<p style="color: green; font-weight: bold">${value}</p>`;
			}
		}
		return value;
	},
};

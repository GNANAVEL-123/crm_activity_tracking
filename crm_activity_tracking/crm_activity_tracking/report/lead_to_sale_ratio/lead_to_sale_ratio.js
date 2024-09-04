// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt

frappe.query_reports["Lead-to-Sale Ratio"] = {
	"filters": [
		{
			fieldname: 'from_date',
			label: 'From Date',
			fieldtype: 'Date',
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			reqd: 1
		},

		{
			fieldname: 'to_date',
			label: 'To Date',
			fieldtype: 'Date',
			default: 'Today',
			reqd: 1
		}

		// {
		// 	fieldname: 'type',
		// 	label: 'Type',
		// 	fieldtype: 'Select',
		// 	options: 'Lead\nQuotation',
		// 	reqd: 1,
		// 	default: "Lead"
		// },
	]
};

frappe.call({
    method: 'crm_activity_tracking.crm_activity_tracking.report.daily_tracking_status.daily_tracking_status.get_crm_settings',
    callback: function(r) {
        var showQuotationFilter = r.message.show_quotation_filter;
        if (showQuotationFilter) {
            frappe.query_reports["Lead-to-Sale Ratio"].filters.push({
				fieldname: 'type',
				label: 'Type',
				fieldtype: 'Select',
				options: 'Lead\nQuotation',
				reqd: 1,
				default: "Lead"
			},);
		
        }
		else{
			frappe.query_reports["Lead-to-Sale Ratio"].filters.push({
				fieldname: 'type',
				label: 'Type',
				fieldtype: 'Select',
				options: 'Lead',
				reqd: 1,
				default: "Lead"
			},);

		}
    }
});
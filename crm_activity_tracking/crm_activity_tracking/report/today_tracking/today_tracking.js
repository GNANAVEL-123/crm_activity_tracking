// Copyright (c) 2023, Thirvusoft and contributors
// For license information, please see license.txt

frappe.query_reports["Today Tracking"] = {
	"filters": [
		{
			fieldname: 'date',
			label: 'Date',
			fieldtype: 'Date',
			default: 'Today',
			reqd: 1
		},
		{
			fieldname: 'user',
			label: 'Monitored By',
			fieldtype: 'Link',
			options: "User",
			default:frappe.session.user,
			get_query: function () {
				return {
					query: "crm_activity_tracking.crm_activity_tracking.report.today_tracking.today_tracking.user_list",
					filters: { date: frappe.query_report.get_filter_value('date') },
				};
			},
		},
		{
			fieldname: 'lead',
			label: 'Lead',
			fieldtype: 'Check',
			default: 1
		},
	],

	// onload: function(report){

	// 	frappe.db.get_value("User", {"name": frappe.session.user}, "username", (r) => {
	// 		frappe.query_report.set_filter_value('user', r.username);
	// 	})

	// 	frappe.call({

	// 		method: "crm_activity_tracking.crm_activity_tracking.report.today_tracking.today_tracking.get_user_list",

	// 		args: {user: frappe.session.user},

	// 		callback(r){

	// 			if ((r.message).length < 2){
	// 				frappe.query_report.page.fields_dict.user.df.hidden = 1;
	// 			}
				
	// 			frappe.query_report.page.fields_dict.user.set_data(r.message);
	// 			frappe.query_report.page.fields_dict.user.refresh();
	// 		}
	// 	})

	// }
};
frappe.call({
    method: 'crm_activity_tracking.crm_activity_tracking.report.daily_tracking_status.daily_tracking_status.get_crm_settings',
    callback: function(r) {
        var showQuotationFilter = r.message.show_quotation_filter;
        if (showQuotationFilter) {
            frappe.query_reports["Today Tracking"].filters.push({
                fieldname: 'quotation',
                label: 'Quotation',
                fieldtype: 'Check',
                default: 1 // Assuming you want it checked by default
            });
        }
    }
});
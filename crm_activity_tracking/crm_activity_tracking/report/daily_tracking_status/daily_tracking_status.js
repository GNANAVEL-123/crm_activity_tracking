frappe.query_reports["Daily Tracking Status"] = {
    "filters": [
        {
            fieldname: 'from_date',
            label: 'From Date',
            fieldtype: 'Date',
            default: frappe.datetime.get_today(),
            reqd: 1
        },
        {
            fieldname: 'to_date',
            label: 'To Date',
            fieldtype: 'Date',
            default: frappe.datetime.get_today(),
            reqd: 1
        },
        {
            fieldname: 'user',
            label: 'Monitored By',
            fieldtype: 'Link',
            options: 'User'
        },
        {
            fieldname: 'lead',
            label: 'Lead',
            fieldtype: 'Check',
            default: 1
        },
    ]
};

frappe.call({
    method: 'crm_activity_tracking.crm_activity_tracking.report.daily_tracking_status.daily_tracking_status.get_crm_settings',
    callback: function(r) {
        var showQuotationFilter = r.message.show_quotation_filter;
        if (showQuotationFilter) {
            frappe.query_reports["Daily Tracking Status"].filters.push({
                fieldname: 'quotation',
                label: 'Quotation',
                fieldtype: 'Check',
                default: 1 // Assuming you want it checked by default
            });
        }
    }
});

// Copyright (c) 2025, CRM and contributors
// For license information, please see license.txt

frappe.ui.form.on("AMC Fire Alarm Tracking", {
	refresh(frm) {

	},
});
frappe.ui.form.on('AMC Fire Alaram Table', {
    remarks: function(frm, cdt, cdn){
        let row = locals[cdt][cdn];
        if(row.remarks){
            frappe.model.set_value(cdt, cdn, "enter_datetime",frappe.datetime.now_datetime());
            frm.refresh_field("refilling_schedule");
        }
    }
});

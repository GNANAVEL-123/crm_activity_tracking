// Copyright (c) 2025, CRM and contributors
// For license information, please see license.txt

frappe.ui.form.on("AMC Fire Hydrant Tracking", {
	refresh(frm) {

	},
});

frappe.ui.form.on('AMC Fire Hydrant Table', {
    remarks: function(frm, cdt, cdn){
        let row = locals[cdt][cdn];
        if(row.remarks){
            frappe.model.set_value(cdt, cdn, "enter_datetime",frappe.datetime.now_datetime());
            frm.refresh_field("landing_valve_table");
            frm.refresh_field("hose_box_and_rrl_hose");
            frm.refresh_field("pump_and_panel");
            frm.refresh_field("hose_reel_drum");
            frm.refresh_field("fire_brigade_inlet");
        }
    }
})
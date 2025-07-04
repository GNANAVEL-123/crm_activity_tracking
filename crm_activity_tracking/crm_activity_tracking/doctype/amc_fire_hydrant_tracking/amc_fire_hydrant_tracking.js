// Copyright (c) 2025, CRM and contributors
// For license information, please see license.txt

frappe.ui.form.on("AMC Fire Hydrant Tracking", {
	refresh(frm) {
        frm.set_query("company_address", function () {
			return {
				filters: {
					is_your_company_address: 1,
				},
			};
		});
        frm.set_query('customer_address',function(frm){
            return {
                filters:[
                     ["Dynamic Link","link_name","=",frm.customer_name],
                     ["Dynamic Link","link_doctype","=","Customer"]
                ]
            }
        })
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
// Copyright (c) 2024, CRM and contributors
// For license information, please see license.txt

frappe.ui.form.on("AMC", {
	refresh(frm) {

	},
});

frappe.ui.form.on('Refilling Schedule Table', {
    refilling_frequency: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.date_refilling && row.refilling_frequency) {
            let refillingDate = frappe.datetime.str_to_obj(row.date_refilling);
            let frequencyMonths = parseInt(row.refilling_frequency, 10);
            let dueDate = frappe.datetime.add_months(refillingDate, frequencyMonths);
            row.refilling_due_date = frappe.datetime.obj_to_str(dueDate);
            frm.refresh_field("refilling_schedule");
        }
    },

    year_frequency: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.year_of_mfg && row.year_frequency) {
            let yearOfMfg = parseInt(row.year_of_mfg, 10);
            let yearFrequency = parseInt(row.year_frequency, 10);
            row.expiry_life_due = yearOfMfg + yearFrequency;
            frm.refresh_field("refilling_schedule");
        }
    },

    date_refilling: function(frm, cdt, cdn){
        let row = locals[cdt][cdn];
        if(row.date_refilling){
            frappe.model.set_value(cdt, cdn, "enter_datetime",frappe.datetime.now_datetime());
            frm.refresh_field("refilling_schedule");
        }
    }
});

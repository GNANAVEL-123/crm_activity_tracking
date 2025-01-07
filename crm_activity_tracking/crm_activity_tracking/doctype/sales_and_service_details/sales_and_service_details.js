// Copyright (c) 2025, CRM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales and Service Details", {
    in: function(frm) {
        if (!frm.doc.in_time) {
            frm.set_value("in_time", frappe.datetime.now_datetime());
            frappe.msgprint(__('Check-in time has been updated!'));
        } else {
            frappe.msgprint(__('Check-in time is already updated!'));
        }  
    },
    out: function(frm) {
        if (!frm.doc.out_time) {
            frm.set_value("out_time", frappe.datetime.now_datetime());
            frappe.msgprint(__('Check-out time has been updated!'));
        } else {
            frappe.msgprint(__('Check-out time is already updated!'));
        }  
    },
});


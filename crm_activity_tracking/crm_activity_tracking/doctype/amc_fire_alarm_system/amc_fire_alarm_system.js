// Copyright (c) 2025, CRM and contributors
// For license information, please see license.txt

frappe.ui.form.on("AMC Fire Alarm System", {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__("Create AMC Fire Alaram Tracking"), function () {
                frappe.model.with_doctype('AMC Fire Alarm Tracking', function () {
                    let new_doc = frappe.model.get_new_doc('AMC Fire Alarm Tracking');
                    Object.assign(new_doc, {
                        // location: frm.doc.location,
                        customer_name: frm.doc.customer_name,
                        mail_id: frm.doc.mail_id,
                        vendor_number: frm.doc.vendor_number,
                        po_number: frm.doc.po_number,
                        amc_frequency: frm.doc.amc_frequency,
                        client_representative: frm.doc.client_representative,
                        contact_number: frm.doc.contact_number,
                        designation: frm.doc.designation,
                        service_by: frm.doc.service_by,
                        cr__contact_number: frm.doc.cr__contact_number,
                        // amc_template: frm.doc.name,
                    });
    
                    frappe.model.clear_table(new_doc, 'refilling_schedule');
                    frm.doc.refilling_schedule.forEach(row => {
                        let new_row = frappe.model.add_child(new_doc, 'refilling_schedule');
                        Object.assign(new_row, {
                            device_no: row.device_no,
                            zoneloop: row.zoneloop,
                            brand_name: row.brand_name,
                            location: row.location,
                        });
                    });
    
                    frappe.set_route('Form', 'AMC Fire Alarm Tracking', new_doc.name).then(() => {
                        new_doc.save().then(() => {
                            frappe.msgprint(__('AMC Fire Alarm Tracking has been successfully created.'));
                        });
                    });
                });
            }).addClass("btn-danger").css({
                'color': 'white',
                'background-color': '#944dff',
                'font-weight': 'bold',
            });
        }
    }
});

// Copyright (c) 2024, CRM and contributors
// For license information, please see license.txt

frappe.ui.form.on("AMC", {
    number_of_portable_fire_extinguisher(frm) {
        update_total_extinguisher(frm);
    },
    number_of_trolley_fireextinguisher(frm) {
        update_total_extinguisher(frm);
    },
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__("Create AMC Visitor Tracking"), function () {
                frappe.model.with_doctype('AMC Visitor Tracking', function () {
                    let new_doc = frappe.model.get_new_doc('AMC Visitor Tracking');
                    Object.assign(new_doc, {
                        location: frm.doc.location,
                        invoice_number: frm.doc.invoice_number,
                        amc_service_date: frm.doc.amc_service_date,
                        number_of_portable_fire_extinguisher: frm.doc.number_of_portable_fire_extinguisher,
                        job_sheet_no: frm.doc.job_sheet_no,
                        completion_report_no: frm.doc.completion_report_no,
                        customer_name: frm.doc.customer_name,
                        mail_id: frm.doc.mail_id,
                        service_by: frm.doc.service_by,
                        recommendations_quote_no: frm.doc.recommendations_quote_no,
                        product_delivery_date: frm.doc.product_delivery_date,
                        number_of_trolley_fireextinguisher: frm.doc.number_of_trolley_fireextinguisher,
                        concern_person: frm.doc.concern_person,
                        contact_number: frm.doc.contact_number,
                        vendor_number: frm.doc.vendor_number,
                        po_number: frm.doc.po_number,
                        frequency: frm.doc.amc_frequency,
                        amc_template: frm.doc.name,
                    });
    
                    frappe.model.clear_table(new_doc, 'refilling_schedule');
                    frm.doc.refilling_schedule.forEach(row => {
                        let new_row = frappe.model.add_child(new_doc, 'refilling_schedule');
                        Object.assign(new_row, {
                            location: row.location,
                            type: row.type,
                            cap: row.cap,
                            year_of_mfg: row.year_of_mfg,
                            year_frequency: row.year_frequency,
                            expiry_life_due: row.expiry_life_due,
                            full_weight: row.full_weight,
                            empty_weight: row.empty_weight,
                            actual_weight: row.actual_weight,
                            qr_code: row.qr_code,
                            qr_attach: row.qr_attach,
                        });
                    });
    
                    frappe.set_route('Form', 'AMC Visitor Tracking', new_doc.name).then(() => {
                        new_doc.save().then(() => {
                            frappe.msgprint(__('AMC Visitor Tracking has been successfully created.'));
                        });
                    });
                });
            }).addClass("btn-danger").css({
                'color': 'white',
                'background-color': '#944dff',
                'font-weight': 'bold',
            });
        }
        if (frm.doc.amc_master){
            console.log("MMMMMM")
            frm.set_query("location", 'refilling_schedule', function(frm, cdt, cdn){
                let row = locals[cdt][cdn];
                return {
                    query: "crm_activity_tracking.crm_activity_tracking.doctype.amc.amc.location_list",
                    filters: {
                        amc_master: frm.doc.amc_master,
                    }
                }
            })
        }
    },
    amc_master: function(frm) {
        if (frm.doc.amc_master) {
            console.log("MMMMMM");
            frm.fields_dict.refilling_schedule.grid.get_field("location").get_query = function(doc, cdt, cdn) {
                return {
                    query: "crm_activity_tracking.crm_activity_tracking.doctype.amc.amc.location_list",
                    filters: {
                        amc_master: doc.amc_master
                    }
                };
            };
        }
    },
    on_load: function(frm) {
        if (frm.doc.amc_master) {
            console.log("MMMMMM");
            frm.fields_dict.refilling_schedule.grid.get_field("location").get_query = function(doc, cdt, cdn) {
                return {
                    query: "crm_activity_tracking.crm_activity_tracking.doctype.amc.amc.location_list",
                    filters: {
                        amc_master: doc.amc_master
                    }
                };
            };
        }
    }
    
    
});

function update_total_extinguisher(frm) {
    frm.set_value(
        'total_extinguisher',
        (frm.doc.number_of_portable_fire_extinguisher || 0) + 
        (frm.doc.number_of_trolley_fireextinguisher || 0)
    );
}


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

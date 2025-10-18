// Copyright (c) 2025, CRM and contributors
// For license information, please see license.txt

frappe.ui.form.on("AMC Master", {
    generate_qr_code(frm) {
        frappe.call({
            method: "crm_activity_tracking.crm_activity_tracking.doctype.amc_master.amc_master.qrcode_creation",
            args: {
                docname: frm.doc.name
            },
            callback: function (r) {
                frappe.msgprint("QR Codes generated and updated.");
                frm.reload_doc(); // Refresh to show updated codes
            }
        });
    },
    number_of_portable_fire_extinguisher(frm) {
        update_total_extinguisher(frm);
    },
    number_of_trolley_fireextinguisher(frm) {
        update_total_extinguisher(frm);
    },
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
        if (!frm.is_new()) {
            frm.add_custom_button(__("Create AMC"), function () {
                frappe.model.with_doctype('AMC', function () {
                    let new_doc = frappe.model.get_new_doc('AMC');
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
                        amc_frequency: frm.doc.amc_frequency,
                        no_of_month: frm.doc.no_of_month,
                        amc_master: frm.doc.name,
                        customer_address: frm.doc.customer_address,
                        company_address: frm.doc.company_address
                    });
    
                    frappe.model.clear_table(new_doc, 'refilling_schedule');
                    frm.doc.refilling_schedule.forEach(row => {
                        let new_row = frappe.model.add_child(new_doc, 'refilling_schedule');
                        Object.assign(new_row, {
                            location: row.location,
                            year_of_mfg: row.year_of_mfg,
                            type: row.type,
                            year_frequency: row.year_frequency,
                            expiry_life_due: row.expiry_life_due,
                            cap: row.cap,
                            date_refilling: row.date_refilling,
                            full_weight: row.full_weight,
                            refilling_frequency: row.refilling_frequency,
                            refilling_due_date: row.refilling_due_date,
                            empty_weight: row.empty_weight,
                            actual_weight: row.actual_weight,
                            remarks: row.remarks,
                            qr_code: row.qr_code,
                            qr_attach: row.qr_attach,
                        });
                    });
    
                    frappe.set_route('Form', 'AMC', new_doc.name).then(() => {
                        new_doc.save().then(() => {
                            frappe.msgprint(__('AMC has been successfully created.'));
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

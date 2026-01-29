// Copyright (c) 2025, CRM and contributors
// For license information, please see license.txt

frappe.ui.form.on("AMC Fire Hydrant System", {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__("Create AMC Fire Hydrant Tracking"), function () {
                frappe.model.with_doctype('AMC Fire Hydrant Tracking', function () {
                    let new_doc = frappe.model.get_new_doc('AMC Fire Hydrant Tracking');
                    Object.assign(new_doc, {
                        region: frm.doc.region,
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
                        client_designation: frm.doc.client_designation,
                        employee_name:frm.doc.employee_name,
                        amc_fire_hydrant_template: frm.doc.name,
                        company:frm.doc.company,
                        company_address: frm.doc.company_address,
                        customer_address: frm.doc.customer_address,
                        invoice_no: frm.doc.invoice_no,
                        quotation_no: frm.doc.quotation_no,
                    });
    
                    frappe.model.clear_table(new_doc, 'landing_valve_table');
                    frm.doc.landing_valve_table.forEach(row => {
                        let new_row = frappe.model.add_child(new_doc, 'landing_valve_table');
                        Object.assign(new_row, {
                            point_no: row.point_no,
                            point_name: row.point_name,
                            location: row.location,
                        });
                    });

                    frappe.model.clear_table(new_doc, 'hose_box_and_rrl_hose');
                    frm.doc.hose_box_and_rrl_hose.forEach(row => {
                        let new_row = frappe.model.add_child(new_doc, 'hose_box_and_rrl_hose');
                        Object.assign(new_row, {
                            point_no: row.point_no,
                            point_name: row.point_name,
                            location: row.location,
                        });
                    });

                    frappe.model.clear_table(new_doc, 'pump_and_panel');
                    frm.doc.pump_and_panel.forEach(row => {
                        let new_row = frappe.model.add_child(new_doc, 'pump_and_panel');
                        Object.assign(new_row, {
                            point_no: row.point_no,
                            point_name: row.point_name,
                            location: row.location,
                        });
                    });

                    frappe.model.clear_table(new_doc, 'hose_reel_drum');
                    frm.doc.hose_reel_drum.forEach(row => {
                        let new_row = frappe.model.add_child(new_doc, 'hose_reel_drum');
                        Object.assign(new_row, {
                            point_no: row.point_no,
                            point_name: row.point_name,
                            location: row.location,
                        });
                    });
    
                    frappe.model.clear_table(new_doc, 'fire_brigade_inlet');
                    frm.doc.fire_brigade_inlet.forEach(row => {
                        let new_row = frappe.model.add_child(new_doc, 'fire_brigade_inlet');
                        Object.assign(new_row, {
                            point_no: row.point_no,
                            point_name: row.point_name,
                            location: row.location,
                        });
                    });
    
                    frappe.set_route('Form', 'AMC Fire Hydrant Tracking', new_doc.name).then(() => {
                        new_doc.save().then(() => {
                            frappe.msgprint(__('AMC Fire Hydrant Tracking has been successfully created.'));
                        });
                    });
                });
            }).addClass("btn-danger").css({
                'color': 'white',
                'background-color': '#944dff',
                'font-weight': 'bold',
            });
        }
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
    }
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
});

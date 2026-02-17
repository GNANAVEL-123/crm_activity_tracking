// Copyright (c) 2024, CRM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Refilling Report No", {
	refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__("Create Refilling Certificate"), function () {
                frappe.call({
                    method: "crm_activity_tracking.crm_activity_tracking.doctype.refilling_report_no.refilling_report_no.refilling_certificate",
                    args: {
                        rr_no:frm.doc.name
                    },
                    callback: function (response) {
                        if (response.message && response.message.length > 0) {
                            frappe.set_route("Form", "Refilling Certificate", response.message[0].name);
                        } else {
                            frappe.new_doc('Refilling Certificate', {
                                customer: frm.doc.customer,
                                region: frm.doc.region,
                                invoice_number: frm.doc.invoice_no,
                                refilling_report_no: frm.doc.name,
                            });
        
                            frappe.ui.form.on('Refilling Certificate', {
                                onload: function (newFrm) {
                                    newFrm.set_value("from_date", frm.doc.refilling_date);
                                    newFrm.set_value("to_date", frm.doc.refilling_due_date);
                                    newFrm.set_value("year", frm.doc.year);
                                    newFrm.set_value("refilling_report_date", frm.doc.refilling_date);
                                    newFrm.set_value("refilling_due_date", frm.doc.refilling_due_date);
        
                                    frappe.model.clear_table(newFrm.doc, 'table_wxkh');
        
                                    frm.doc.refilling_report_table.forEach(row => {
                                        let new_row = frappe.model.add_child(newFrm.doc, 'Refilling Certificate Table', 'table_wxkh');
                                        new_row.item = row.item_name;
                                        new_row.item_name = row.item_name;
                                        new_row.quantity = row.qty;
                                    });
        
                                    newFrm.refresh_fields();
                                }
                            });
                        }
                    }
                });
            }).addClass("btn-danger").css({
                'color': 'white',
                'background-color': '#bb6b93',
                'font-weight': 'bold'
            });
        }   
        if (!frm.is_new()) { 
            frm.add_custom_button("Send Whatsapp", () => {
                frm.events.open_whatsapp_dialog(frm);
            });    
            setTimeout(() => {
                $('button:contains("Send Whatsapp")')
                    .removeClass('btn-default')
                    .addClass('btn-success')
                    .css({
                        'background-color': '#423586ff',
                        'border-color': '#25D366',
                        'color': '#ffffff',
                        'font-weight': '600'
                    });
            }, 300);
        }
    },        
    year(frm) {
		if (frm.doc.refilling_date && frm.doc.year) {
			let refillingDate = frappe.datetime.str_to_obj(frm.doc.refilling_date); 
			let additionalYears = parseInt(frm.doc.year, 10); 
			let dueDate = frappe.datetime.add_months(refillingDate, additionalYears * 12); 
			let due_date = frappe.datetime.obj_to_str(dueDate); 
			frm.set_value("refilling_due_date", due_date);
		}
	},
    open_whatsapp_dialog(frm) {
        let default_mobile = "";
        if (frm.doc.mobile_no) {
            default_mobile = frm.doc.mobile_no;
            create_dialog(default_mobile);
        } else {
            create_dialog("");
        }

        function create_dialog(default_mobile_no) {
            let d = new frappe.ui.Dialog({
                title: "Send WhatsApp Message",
                fields: [
                    {
                        label: "Whatsapp Number",
                        fieldname: "mobile_no",
                        fieldtype: "Data",
                        reqd: 1,
                        default: default_mobile_no,   // 👈 Set default number here
                        description: "Enter WhatsApp number (only digits)"
                    }
                ],
                primary_action_label: "Send",
                primary_action(values) {

                    frm.call({
                        method: "crm_activity_tracking.crm_activity_tracking.custom_files.py.whatsapp.send_refilling_report_no",
                        args: {
                            rr_no: frm.doc.name,
                            mobile_no: values.mobile_no    // send dialog value
                        },
                        callback: function (response) {
                            if (response.message === "Success") {
                                frappe.show_alert({
                                    message: __("WhatsApp Message Sent Successfully"),
                                    indicator: "green",
                                });
                            } else {
                                frappe.show_alert({
                                    message: __("Failed to send WhatsApp Message"),
                                    indicator: "red",
                                });
                            }
                        }
                    });

                    d.hide();
                }
            });

            d.show();
        }
    },
});

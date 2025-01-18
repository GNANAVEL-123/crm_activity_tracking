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
});

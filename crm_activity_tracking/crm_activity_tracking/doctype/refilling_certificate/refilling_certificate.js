// Copyright (c) 2024, CRM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Refilling Certificate", {
	refresh(frm) {
        frm.set_query("address", function (frm) {
			return {
			  filters: [
				["Dynamic Link", "link_name", "=", frm.customer],
				["Dynamic Link", "link_doctype", "=", "Customer"],
			  ],
			};
		});
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
    address(frm){
        frm.set_query("address", function (frm) {
			return {
			  filters: [
				["Dynamic Link", "link_name", "=", frm.customer],
				["Dynamic Link", "link_doctype", "=", "Customer"],
			  ],
			};
		});
    },
	due_month_count(frm) {
        if (frm.doc.refilling_report_date) {
            let refillingDate = frappe.datetime.str_to_obj(frm.doc.refilling_report_date);
            let frequencyMonths = parseInt(frm.doc.due_month_count, 10);
            let dueDate = frappe.datetime.add_months(refillingDate, frequencyMonths);
            let due_date = frappe.datetime.obj_to_str(dueDate);
            frm.set_value("refilling_due_date", due_date);
        }
    },
	year(frm) {
		if (frm.doc.from_date && frm.doc.year) {
			let refillingDate = frappe.datetime.str_to_obj(frm.doc.from_date); 
			let additionalYears = parseInt(frm.doc.year, 10); 
			let dueDate = frappe.datetime.add_months(refillingDate, additionalYears * 12); 
			let due_date = frappe.datetime.obj_to_str(dueDate); 
			frm.set_value("to_date", due_date);
		}
	},
	open_whatsapp_dialog(frm) {
        let default_mobile = "";
		if (frm.doc.refilling_report_no) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Refilling Report No",
					filters: {
						name: frm.doc.refilling_report_no
					},
					fieldname: "mobile_no"
				},
				callback: function (r) {
					if (r.message && r.message.mobile_no) {
						default_mobile = r.message.mobile_no;
					}
					create_dialog(default_mobile);
				}
			});
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
                        method: "crm_activity_tracking.crm_activity_tracking.custom_files.py.whatsapp.send_refilling_certificate",
                        args: {
                            rc_no: frm.doc.name,
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

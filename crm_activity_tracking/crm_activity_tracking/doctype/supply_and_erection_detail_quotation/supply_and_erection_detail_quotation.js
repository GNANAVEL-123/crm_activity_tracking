// Copyright (c) 2026, CRM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Supply and Erection Detail Quotation", {

    refresh(frm) {
        if(!cur_frm.is_new())
			frm.add_custom_button("Send Whatsapp", () => {
				frm.events.open_whatsapp_dialog(frm);
			});
        // Filter company address
        frm.set_query("company_address", function () {
            return {
                filters: {
                    is_your_company_address: 1,
                },
            };
        });

        // Filter customer address
        frm.set_query("customer_address", function () {
            return {
                filters: [
                    ["Dynamic Link", "link_name", "=", frm.doc.customer],
                    ["Dynamic Link", "link_doctype", "=", "Customer"]
                ]
            };
        });
    },

    customer(frm) {
        if (frm.doc.customer) {
            frappe.call({
                method: "frappe.contacts.doctype.address.address.get_default_address",
                args: {
                    doctype: "Customer",
                    name: frm.doc.customer
                },
                callback: function (r) {
                    if (r.message) {
                        frm.set_value("customer_address", r.message.name);
                    }
                }
            });
        }
    },

    company(frm) {
        if (frm.doc.company) {
            frappe.call({
                method: "frappe.contacts.doctype.address.address.get_default_address",
                args: {
                    doctype: "Company",
                    name: frm.doc.company
                },
                callback: function (r) {
                    if (r.message) {
                        frm.set_value("company_address", r.message.name);
                    }
                }
            });
        }
    },
    open_whatsapp_dialog(frm) {
        let default_mobile = "";
        if (frm.doc.customer_address) {
            frappe.db.get_doc("Address", frm.doc.customer_address)
                .then(add_doc => {
                    if (add_doc.phone) {
                        default_mobile = add_doc.phone;
                    }

                    create_dialog(default_mobile);
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
                        method: "crm_activity_tracking.crm_activity_tracking.custom_files.py.whatsapp.send_quotation_supply_erection_whatsapp",
                        args: {
                            invoice: frm.doc.name,
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
frappe.ui.form.on("Supply and Erection Item Details", {
    qty: function(frm, cdt, cdn) {
        calculate_amounts(frm, cdt, cdn);
    },
    supply_rate: function(frm, cdt, cdn) {
        calculate_amounts(frm, cdt, cdn);
    },
    erection_rate: function(frm, cdt, cdn) {
        calculate_amounts(frm, cdt, cdn);
    }
});

function calculate_amounts(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    // Supply Amount
    row.supply_amount = (row.qty || 0) * (row.supply_rate || 0);

    // Erection Amount
    row.erection_amount = (row.qty || 0) * (row.erection_rate || 0);

    frm.refresh_field("items");
}
frappe.ui.form.on("Payment Entry", {
    refresh(frm) {
        if (
                frm.doc.docstatus === 1 &&
                (frm.doc.party_type === "Customer" || frm.doc.party_type === "Supplier")
            ) {
            // WhatsApp Button
            frm.add_custom_button("Send WhatsApp", () => {
                frm.events.open_whatsapp_dialog(frm);
            });
            // Email Button
            frm.add_custom_button("Send Email", () => {
                frm.events.open_email_dialog(frm);
            });
        }
    },

    open_whatsapp_dialog(frm) {
        let default_mobile = "";

        if (frm.doc.customer_address) {
            frappe.db.get_doc("Address", frm.doc.customer_address)
                .then(addr => {
                    if (addr.phone) default_mobile = addr.phone;
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
                        default: default_mobile_no,
                        description: "Enter WhatsApp number (digits only)"
                    }
                ],
                primary_action_label: "Send",
                primary_action(values) {

                    frm.call({
                        method: "crm_activity_tracking.crm_activity_tracking.custom_files.py.whatsapp.send_payment_entry_whatsapp",
                        args: {
                            payment_entry: frm.doc.name,
                            mobile_no: values.mobile_no
                        },
                        callback: function (r) {
                            if (r.message === "Success") {
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
    // EMAIL DIALOG
    open_email_dialog(frm) {
        let default_email = "";

        if (frm.doc.customer_address) {
           frappe.db.get_doc("Address", frm.doc.customer_address)
                .then(addr => {
                    if (addr.email_id) default_email = addr.email_id;
                    create_dialog(default_email);
                });
        } else {
            create_dialog("");
        }

        function create_dialog(default_email_id) {
            let d = new frappe.ui.Dialog({
                title: "Send Email",
                fields: [
                    {
                        label: "Email ID",
                        fieldname: "email_id",
                        fieldtype: "Data",
                        reqd: 1,
                        default: default_email_id,
                        options: "Email",
                        description: "Enter email address"
                    }
                ],
                primary_action_label: "Send",
                primary_action(values) {

                    frm.call({
                        method: "crm_activity_tracking.crm_activity_tracking.custom_files.py.payment_entry.send_payment_entry_email",
                        args: {
                            payment_entry: frm.doc.name,
                            email_id: values.email_id
                        },
                        callback: function (r) {
                            if (r.message === "Success") {
                                frappe.show_alert({
                                    message: __("Email Sent Successfully"),
                                    indicator: "green",
                                });
                            } else {
                                frappe.show_alert({
                                    message: __("Failed to send Email"),
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
    }
});

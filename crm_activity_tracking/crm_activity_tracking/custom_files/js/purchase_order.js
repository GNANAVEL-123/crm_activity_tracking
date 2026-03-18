frappe.ui.form.on('Purchase Order', {
    refresh: function(frm) {

        setTimeout(() => {

            frm.remove_custom_button("Product Bundle", "Get Items From");
            frm.remove_custom_button("Supplier Quotation", "Get Items From");
            frm.remove_custom_button("Material Request", "Get Items From");

            frm.remove_custom_button("Link to Material Request", "Tools");
            frm.remove_custom_button("Update Rate as per Last Purchase", "Tools");

            frm.remove_custom_button("Payment", "Create");
            frm.remove_custom_button("Payment Request", "Create");
            
            $("[data-doctype='Auto Repeat']").hide();
            $("[data-doctype='Project']").hide();
            $("[data-doctype='Supplier Quotation']").hide();

            $($("[data-doctype='Subcontracting Order']")[0].parentElement).hide();

		}, 500)
		if(!cur_frm.is_new())
		frm.add_custom_button("Send Whatsapp", () => {
				frm.events.open_whatsapp_dialog(frm);
		});
	},
	open_whatsapp_dialog(frm) {
        let default_mobile = "";
        if (frm.doc.supplier_address) {
            frappe.db.get_doc("Address", frm.doc.supplier_address)
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
                        method: "crm_activity_tracking.crm_activity_tracking.custom_files.py.whatsapp.send_purchase_order_whatsapp",
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
})



frappe.ui.form.on("Purchase Order Item", {
    item_code: function (frm, cdt, cdn) {
		const row = locals[cdt][cdn];

		if (!row.item_code || !frm.doc.transaction_date || !frm.doc.supplier) return;

		frappe.call({
			method: "crm_activity_tracking.crm_activity_tracking.custom_files.py.purchase_order.get_last_buying_rate",
			args: {
				item_code: row.item_code,
				transaction_date: frm.doc.transaction_date,
				supplier: frm.doc.supplier
			},
			callback: function (r) {
				if (r.message) {
					frappe.model.set_value(cdt, cdn, "custom_last_supplier_buying_rate", r.message);
					frappe.model.set_value(cdt, cdn, "rate", r.message);
				}
			}
		});
	},
})
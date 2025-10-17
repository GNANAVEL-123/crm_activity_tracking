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
    }
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
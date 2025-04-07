frappe.ui.form.on("Project", {
    refresh: function(frm){ 
        frm.set_query("item", "custom_item_consumption_details", function(frm, cdt, cdn) {
            let row = locals[cdt][cdn];
            return {
                query: "crm_activity_tracking.crm_activity_tracking.custom_files.py.project.item_list",
                filters: {
                    doc: cur_frm.doc.name,
                }
            };
        });
    }
});

frappe.ui.form.on("Project Item Details", {
    delivered_qty(frm, cdt, cdn) {
        update_balance_qty(cdt, cdn);
    },
    consumed_qty(frm, cdt, cdn) {
        update_balance_qty(cdt, cdn);
    }
});

function update_balance_qty(cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.delivered_qty != null) {
        let balance = row.delivered_qty - (row.consumed_qty || 0);
        frappe.model.set_value(cdt, cdn, 'balance_qty', balance);
    }
}

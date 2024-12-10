// Copyright (c) 2024, CRM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hydro Pressure Test", {
	refresh(frm) {
        frm.set_query("customer_address", function (frm) {
			return {
			  filters: [
				["Dynamic Link", "link_name", "=", frm.customer],
				["Dynamic Link", "link_doctype", "=", "Customer"],
			  ],
			};
		});
	},
    customer_address(frm){
        frm.set_query("customer_address", function (frm) {
			return {
			  filters: [
				["Dynamic Link", "link_name", "=", frm.customer],
				["Dynamic Link", "link_doctype", "=", "Customer"],
			  ],
			};
		});
    }
});

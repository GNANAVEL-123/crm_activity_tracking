// Copyright (c) 2024, CRM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Warranty Certificate", {
	refresh(frm) {
        frm.set_query("customer_address", function (frm) {
			return {
			  filters: [
				["Dynamic Link", "link_name", "=", frm.customer_name],
				["Dynamic Link", "link_doctype", "=", "Customer"],
			  ],
			};
		});
	},
    customer_address(frm){
        frm.set_query("customer_address", function (frm) {
			return {
			  filters: [
				["Dynamic Link", "link_name", "=", frm.customer_name],
				["Dynamic Link", "link_doctype", "=", "Customer"],
			  ],
			};
		});
    }
});

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
    }
});

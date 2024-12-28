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
    },
	due_month_count(frm) {
        if (frm.doc.refilling__report_date) {
            let refillingDate = frappe.datetime.str_to_obj(frm.doc.refilling__report_date);
            let frequencyMonths = parseInt(frm.doc.due_month_count, 10);
            let dueDate = frappe.datetime.add_months(refillingDate, frequencyMonths);
            let due_date = frappe.datetime.obj_to_str(dueDate);
            frm.set_value("refilling_due_date", due_date);
        }
    },
});

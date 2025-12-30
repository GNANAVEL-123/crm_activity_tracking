frappe.ui.form.on("Customer", {
    refresh: function (frm) {      
        frm.set_query("custom_sales_executive", function () {
			return {
				filters: {
					user_type_for_customer: "Sales Executive",
				},
			};
		});
        frm.set_query("custom_admin", function () {
			return {
				filters: {
					user_type_for_customer: "Admin",
				},
			};
		});
    }
})

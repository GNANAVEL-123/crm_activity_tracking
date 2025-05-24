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
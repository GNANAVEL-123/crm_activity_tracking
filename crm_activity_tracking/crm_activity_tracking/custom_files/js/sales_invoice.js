frappe.ui.form.on("Sales Invoice", {

    refresh: function(frm){

      setTimeout(() => {

        frm.remove_custom_button('Fetch Timesheet');

        frm.remove_custom_button('Maintenance Schedule', 'Create');
        frm.remove_custom_button('Quality Inspection(s)', 'Create');
        frm.remove_custom_button('Invoice Discounting', 'Create');
        frm.remove_custom_button('Dunning', 'Create');
        frm.remove_custom_button('UnReconcile', 'Actions');
        frm.remove_custom_button('Payment Request', 'Create');

        frm.remove_custom_button("Sales Order", "Get Items From");
        frm.remove_custom_button("Delivery Note", "Get Items From");
        frm.remove_custom_button("Quotation", "Get Items From");

        frm.remove_custom_button('Applicability Status', 'e-Waybill');

        $("[data-doctype='Invoice Discounting']").hide();
        $("[data-doctype='Dunning']").hide();
        $("[data-doctype='Timesheet']").hide();
        $("[data-doctype='Delivery Note']").hide();
        $("[data-doctype='POS Invoice']").hide();

        $($("[data-doctype='Auto Repeat']")[0].parentElement).hide();
        $($("[data-doctype='Purchase Invoice']")[0].parentElement).hide();

		}, 500)
    }
})
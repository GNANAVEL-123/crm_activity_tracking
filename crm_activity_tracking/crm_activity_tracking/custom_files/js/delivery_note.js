frappe.ui.form.on("Delivery Note", {

    refresh: function(frm){

        setTimeout(() => {
            frm.remove_custom_button('Update Items');

            frm.remove_custom_button('Delivery Trip', 'Create');
            frm.remove_custom_button('Installation Note', 'Create');
            frm.remove_custom_button('Shipment', 'Create');
            frm.remove_custom_button('Packing Slip', 'Create');
            frm.remove_custom_button('Quality Inspection(s)', 'Create');

            frm.remove_custom_button('Sales Order', "Get Items From");

            frm.remove_custom_button('Accounting Ledger', 'View');

            frm.remove_custom_button('Accounting Ledger', 'Preview');

            frm.remove_custom_button('Close', 'Status');

            frm.remove_custom_button('Applicability Status', 'e-Waybill');
            
            $("[data-doctype='Packing Slip']").hide();
            $("[data-doctype='Shipment']").hide();
            $("[data-doctype='Delivery Trip']").hide();
            $("[data-doctype='Quality Inspection']").hide();

            $($("[data-doctype='Auto Repeat']")[0].parentElement).hide();
            $($("[data-doctype='Material Request']")[0].parentElement).hide();
            $($("[data-doctype='Stock Entry']")[0].parentElement).hide();

		}, 500)

    }

})
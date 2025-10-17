frappe.ui.form.on('Purchase Receipt', {
    refresh: function(frm) {

        setTimeout(() => {

            frm.remove_custom_button('Asset', 'View');
            frm.remove_custom_button('Asset Movement', 'View');
            frm.remove_custom_button('Accounting Ledger', 'View');

            frm.remove_custom_button('Close', 'Status');
            

            frm.remove_custom_button('Make Stock Entry', 'Create');
            frm.remove_custom_button('Retention Stock Entry', 'Create');
            frm.remove_custom_button('Quality Inspection(s)', 'Create');

            frm.remove_custom_button("Purchase Invoice", "Get Items From");
            frm.remove_custom_button("Purchase Order", "Get Items From");

            frm.remove_custom_button("Link to Material Request", "Tools");
            
            $("[data-doctype='Stock Reservation Entry']").hide();
            $("[data-doctype='Asset']").hide();
            $("[data-doctype='Project']").hide();

            $($("[data-doctype='Auto Repeat']")[0].parentElement).hide();

		}, 500)
    }
})
frappe.ui.form.on("Sales Order", {

    refresh: function(frm){

        setTimeout(() => {

            frm.remove_custom_button('Pick List', 'Create');
            frm.remove_custom_button('Work Order', 'Create');
            frm.remove_custom_button('Material Request', 'Create');
            frm.remove_custom_button('Project', 'Create');
            frm.remove_custom_button('Request for Raw Materials', 'Create');
            frm.remove_custom_button('Purchase Order', 'Create');
            frm.remove_custom_button('Payment Request', 'Create');
            frm.remove_custom_button('Payment', 'Create');

            frm.remove_custom_button('Quotation', "Get Items From");
            frm.remove_custom_button('Close', 'Status');
            $("[data-doctype='Pick List']").hide();
            $("[data-doctype='Maintenance Visit']").hide();
            $($("[data-doctype='Auto Repeat']")).hide();
            $($("[data-doctype='Stock Reservation Entry']")).hide();
            $($("[data-doctype='Material Request']")[0].parentElement).hide();
            $($("[data-doctype='Payment Entry']")[0].parentElement).hide();
            $($("[data-doctype='Work Order']")[0].parentElement).hide();
            $($("[data-doctype='Project']")[0].parentElement).hide();

		}, 500)

    },
})
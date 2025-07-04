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
    if(!cur_frm.is_new())
      frm.add_custom_button("Send Whatsapp",function () {
          frm.trigger("send_whatsapp_message");
      
      })
    },
    send_whatsapp_message:function(frm){
      if(frm.doc.customer){
          frappe.call({
              method: "crm_activity_tracking.crm_activity_tracking.custom_files.py.whatsapp.send_sales_invoice_whatsapp",
              args: {
                  "invoice": frm.doc.name,
              },
              callback: function (response) {
                  if (response.message && response.message === "Success") {
                      frappe.show_alert({
                          message: __("Whatsapp Log Created successfully"),
                          indicator: "green",
                      });
                  } else {
                      frappe.show_alert({
                          message: __("Failed to create WhatsApp Log. Please try again."),
                          indicator: "red",
                      });
                  }
              }

          })
      }
    },
    customer: function (frm) {
      if (frm.doc.customer) {
        frappe.call({
          method: "crm_activity_tracking.crm_activity_tracking.custom_files.py.sales_invoice.get_customer_data",
          args: {
            customer: frm.doc.customer,
            company: frm.doc.company,
            freeze: true
          },
          callback: function (r) {
            if (r.message) {
              frm.doc.custom_total_unpaid = r.message["custom_total_unpaid"]
              frm.refresh_fields();
            }
          }
        });
      }
    },
    validate: function (frm) {
      if (frm.doc.customer) {
        frappe.call({
          method: "crm_activity_tracking.crm_activity_tracking.custom_files.py.sales_invoice.get_customer_data",
          args: {
            customer: frm.doc.customer,
            company: frm.doc.company,
            freeze: true
          },
          callback: function (r) {
            if (r.message) {
              frm.doc.custom_total_unpaid = r.message["custom_total_unpaid"]
              frm.refresh_fields();
            }
          }
        });
      }
    },

})
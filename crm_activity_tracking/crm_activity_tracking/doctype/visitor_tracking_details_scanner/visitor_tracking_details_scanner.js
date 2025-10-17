// Copyright (c) 2025, CRM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Visitor Tracking Details Scanner", {
    refresh(frm) {
        frm.add_custom_button("Clear", function () {
            // Clear QR field
            frm.set_value("qr_scanner", null);

            // Clear child table
            frm.clear_table("amc_visitor_tracking_details");

            frm.refresh_fields();
        });
    },

    qr_scanner(frm) {
        if (frm.doc.qr_scanner) {
            frappe.call({
                method: "crm_activity_tracking.crm_activity_tracking.doctype.visitor_tracking_details_scanner.visitor_tracking_details_scanner.get_qr_schedule_data",
                args: {
                    qr_code: frm.doc.qr_scanner
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        // Loop through and add all matching rows
                        r.message.forEach((data) => {
                            frm.add_child("amc_visitor_tracking_details", {
                                customer: data.customer_name,
                                amc_visitor_traking: data.amc_visitor_trcking,
                                amc_service_date: data.amc_service_date
                            });
                        });

                        frm.refresh_field("amc_visitor_tracking_details");
                    } else {
                        frappe.msgprint("No matching AMC Visitor Tracking found for this QR.");
                    }
                }
            });
        }
    }
});


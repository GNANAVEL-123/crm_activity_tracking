// Copyright (c) 2025, CRM and contributors
// For license information, please see license.txt

frappe.ui.form.on("AMC Master", {
    generate_qr_code(frm) {
        frappe.call({
            method: "crm_activity_tracking.crm_activity_tracking.doctype.amc_master.amc_master.qrcode_creation",
            args: {
                docname: frm.doc.name
            },
            callback: function (r) {
                frappe.msgprint("QR Codes generated and updated.");
                frm.reload_doc(); // Refresh to show updated codes
            }
        });
    }
});


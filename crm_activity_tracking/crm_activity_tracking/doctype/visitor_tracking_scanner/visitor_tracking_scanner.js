// Copyright (c) 2025, CRM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Visitor Tracking Scanner", {
    refresh(frm){
        frm.set_query("amc", function () {
			return {
				filters: {
					customer_name: frm.doc.customer,
				},
			};
		}); 
        frm.set_query("amc_visitor_tracking", function () {
			return {
				filters: {
					amc_template: frm.doc.amc,
				},
			};
		}); 
        frm.add_custom_button("Update Details to AMC Visitor Tracking", function () {
            if (!frm.doc.amc_visitor_tracking || !frm.doc.row_name) {
                frappe.msgprint("AMC Visitor Tracking required to update.");
                return;
            }

            frappe.call({
                method: "crm_activity_tracking.crm_activity_tracking.doctype.visitor_tracking_scanner.visitor_tracking_scanner.update_amc_row",
                args: {
                    parent: frm.doc.amc_visitor_tracking,
                    rowname: frm.doc.row_name,
                    values: {
                        location: frm.doc.location,
                        type: frm.doc.type,
                        cap: frm.doc.cap,
                        date_refilling: frm.doc.date_refilling,
                        refilling_due_date: frm.doc.refilling_due_date,
                        enter_datetime: frm.doc.enter_datetime,
                        refilling_frequency: frm.doc.refilling_frequency,
                        year_of_mfg: frm.doc.year_of_mfg,
                        year_frequency: frm.doc.year_frequency,
                        expiry_life_due: frm.doc.expiry_life_due,
                        full_weight: frm.doc.full_weight,
                        empty_weight: frm.doc.empty_weight,
                        actual_weight: frm.doc.actual_weight,
                        remarks: frm.doc.remarks
                    }
                },
                callback: function (r) {
                    if (r.message === "success") {
                        frappe.msgprint("AMC Visitor Tracking updated successfully.");

                        // ✅ Preserve these fields
                        const customer = frm.doc.customer;
                        const amc = frm.doc.amc;
                        const amc_visitor_tracking = frm.doc.amc_visitor_tracking;

                        // ✅ Manually clear the fields
                        frm.set_value("scan_qr_code", null);
                        frm.set_value("location", null);
                        frm.set_value("type", null);
                        frm.set_value("cap", null);
                        frm.set_value("date_refilling", null);
                        frm.set_value("refilling_frequency", null);
                        frm.set_value("refilling_due_date", null);
                        frm.set_value("enter_datetime", null);
                        frm.set_value("year_of_mfg", null);
                        frm.set_value("year_frequency", null);
                        frm.set_value("expiry_life_due", null);
                        frm.set_value("full_weight", null);
                        frm.set_value("empty_weight", null);
                        frm.set_value("actual_weight", null);
                        frm.set_value("remarks", null);
                        frm.set_value("qr_code", null);
                        frm.set_value("row_name", null);

                        frm.set_value("customer", customer);
                        frm.set_value("amc", amc);
                        frm.set_value("amc_visitor_tracking", amc_visitor_tracking);

                        frm.refresh_fields();
                    }
                }
            });
        });
    },
    amc(frm){
        frm.set_query("amc", function () {
            return {
                filters: {
                    customer_name: frm.doc.customer,
                },
            };
        }); 
        frm.set_query("amc_visitor_tracking", function () {
            return {
                filters: {
                    amc_template: frm.doc.amc,
                },
            };
        }); 
    },
    amc_visitor_tracking(frm){
        frm.set_query("amc", function () {
            return {
                filters: {
                    customer_name: frm.doc.customer,
                },
            };
        }); 
        frm.set_query("amc_visitor_tracking", function () {
            return {
                filters: {
                    amc_template: frm.doc.amc,
                },
            };
        }); 
    },
    after_save: function(frm) {
        frm.set_value("scan_qr_code", null);
        frm.set_value("location", null);
        frm.set_value("type", null);
        frm.set_value("cap", null);
        frm.set_value("date_refilling", null);
        frm.set_value("refilling_frequency", null);
        frm.set_value("refilling_due_date", null);  
        frm.set_value("enter_datetime", null);
        frm.set_value("year_of_mfg", null);
        frm.set_value("year_frequency", null);
        frm.set_value("expiry_life_due", null);
        frm.set_value("full_weight", null);
        frm.set_value("empty_weight", null);
        frm.set_value("actual_weight", null);
        frm.set_value("remarks", null);
        frm.set_value("qr_code", null);
        frm.set_value("row_name", null);

        frm.refresh_fields();
    },
    scan_qr_code(frm) {
        if (frm.doc.scan_qr_code && frm.doc.amc && frm.doc.customer) {
            frappe.call({
                method: "crm_activity_tracking.crm_activity_tracking.doctype.visitor_tracking_scanner.visitor_tracking_scanner.get_qr_schedule_data",
                args: {
                    qr_code: frm.doc.scan_qr_code,
                    amc: frm.doc.amc,
                    customer: frm.doc.customer
                },
                callback: function(r) {
                    if (r.message) {
                        const data = r.message;

                        frm.set_value("location", data.location);
                        frm.set_value("type", data.type);
                        frm.set_value("cap", data.cap);
                        frm.set_value("date_refilling", data.date_refilling);
                        frm.set_value("refilling_frequency", data.refilling_frequency);
                        frm.set_value("year_of_mfg", data.year_of_mfg);
                        frm.set_value("year_frequency", data.year_frequency);
                        frm.set_value("expiry_life_due", data.expiry_life_due);
                        frm.set_value("full_weight", data.full_weight);
                        frm.set_value("empty_weight", data.empty_weight);
                        frm.set_value("actual_weight", data.actual_weight);
                        frm.set_value("remarks", data.remarks);
                        frm.set_value("qr_code", data.qr_code);
                        frm.set_value("row_name", data.rowname);
                    } else {
                        frappe.msgprint("No matching QR Code found with given AMC and Customer.");
                    }
                }
            });
        } else if (frm.doc.scan_qr_code) {
            // only show if user is actively scanning something without required fields
            frappe.msgprint("AMC and Customer are required to scan.");
        }
    },
    refilling_frequency: function(frm) {
        frm.events.calculate_due_date(frm);
    },
    date_refilling: function(frm) {
        frm.events.calculate_due_date(frm);
        if (frm.doc.date_refilling) {
            frm.set_value("enter_datetime", frappe.datetime.now_datetime());
        }
    },
    calculate_due_date: function(frm) {
        if (frm.doc.date_refilling && frm.doc.refilling_frequency) {
            let refillingDate = frappe.datetime.str_to_obj(frm.doc.date_refilling); 
            let frequencyMonths = parseInt(frm.doc.refilling_frequency, 10);

            if (!isNaN(frequencyMonths)) {
                let dueDate = frappe.datetime.add_months(refillingDate, frequencyMonths);
                frm.set_value("refilling_due_date", frappe.datetime.obj_to_str(dueDate));
            }
        }
    }
});

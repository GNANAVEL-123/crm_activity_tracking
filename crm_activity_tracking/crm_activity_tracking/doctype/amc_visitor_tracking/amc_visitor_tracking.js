// Copyright (c) 2024, CRM and contributors
// For license information, please see license.txt

frappe.ui.form.on("AMC Visitor Tracking", {
    refresh: function (frm) {
        frappe.call({
            method: "crm_activity_tracking.crm_activity_tracking.doctype.amc_visitor_tracking.amc_visitor_tracking.description_list",
            args: {
                doc:frm.doc
            },
            callback: function (r) {
                if (r.message) {
                    r.message.forEach(feedback => {
                        let newRow = frm.add_child("feedback_table");
                        newRow.description = feedback;
                    });
                    frm.refresh_field("feedback_table");
                }
            }
        });
        frm.add_custom_button(__('Take Refilling Sheet Print'), function() {
            // Build print format URL
            let doctype = frm.doc.doctype;
            let docname = frm.doc.name;
            let print_format = "Refilling Sheet"; // your custom print format name
            let letterhead = 0; // 0 = with letterhead, 1 = without

            let url = `/printview?doctype=${encodeURIComponent(doctype)}`
                + `&name=${encodeURIComponent(docname)}`
                + `&format=${encodeURIComponent(print_format)}`
                + `&no_letterhead=${letterhead}`;

            // Open in new tab
            window.open(url, "_blank");
        });
        frm.add_custom_button(__('Take Remarks Details Print'), function() {
            // Build print format URL
            let doctype = frm.doc.doctype;
            let docname = frm.doc.name;
            let print_format = "AMC Remarks Details Print"; // your custom print format name
            let letterhead = 0; // 0 = with letterhead, 1 = without

            let url = `/printview?doctype=${encodeURIComponent(doctype)}`
                + `&name=${encodeURIComponent(docname)}`
                + `&format=${encodeURIComponent(print_format)}`
                + `&no_letterhead=${letterhead}`;

            // Open in new tab
            window.open(url, "_blank");
        });
        frm.add_custom_button(__('Create Quotation'), function() {
            create_quotation_from_amc(frm);
        });
        frm.set_query("company_address", function () {
			return {
				filters: {
					is_your_company_address: 1,
				},
			};
		});
        frm.set_query('customer_address',function(frm){
            return {
                filters:[
                     ["Dynamic Link","link_name","=",frm.customer_name],
                     ["Dynamic Link","link_doctype","=","Customer"]
                ]
            }
        })
    },    
    check_in(frm) {
        if (!frm.doc.in_time) { 
            frm.set_value('in_time', frappe.datetime.now_datetime());
            frappe.msgprint(__('Check-in time has been updated!'));
        } else {
            frappe.msgprint(__('Check-in time is already updated!'));
        }
    },
    check_out(frm) {
        if (!frm.doc.out_time) { 
            frm.set_value('out_time', frappe.datetime.now_datetime());
            frappe.msgprint(__('Check-out time has been updated!'));
        } else {
            frappe.msgprint(__('Check-out time is already updated!'));
        }
    },
    print_check(frm) {
        // value will be 1 if checked, 0 if unchecked
        let value = frm.doc.print_check ? 1 : 0;

        frm.doc.refilling_schedule.forEach(row => {
            row.refilling_print = value;
        });

        frm.refresh_field('refilling_schedule');
    },
    amc_frequency(frm) {
        if (frm.doc.amc_frequency && frm.doc.amc_service_date) {
            let serviceDate = new Date(frm.doc.amc_service_date);
            serviceDate.setMonth(serviceDate.getMonth() + parseInt(frm.doc.amc_frequency));
            let nextAMCServiceDueDate = serviceDate.toISOString().split('T')[0];
            frappe.model.set_value(frm.doc.doctype, frm.doc.name, 'next_amc_service_due_date', nextAMCServiceDueDate);
        }
    },
    amc_service_date(frm) {
        if (frm.doc.amc_frequency && frm.doc.amc_service_date) {
            let serviceDate = new Date(frm.doc.amc_service_date);
            serviceDate.setMonth(serviceDate.getMonth() + parseInt(frm.doc.amc_frequency));
            let nextAMCServiceDueDate = serviceDate.toISOString().split('T')[0];
            frappe.model.set_value(frm.doc.doctype, frm.doc.name, 'next_amc_service_due_date', nextAMCServiceDueDate);
        }
    },
    number_of_portable_fire_extinguisher(frm) {
        frm.set_value(
            'total_extinguisher',
            (frm.doc.number_of_portable_fire_extinguisher || 0) + 
            (frm.doc.number_of_trolley_fireextinguisher || 0)
        );
    },
    number_of_trolley_fireextinguisher(frm) {
        frm.set_value(
            'total_extinguisher',
            (frm.doc.number_of_portable_fire_extinguisher || 0) + 
            (frm.doc.number_of_trolley_fireextinguisher || 0)
        );
    },
    hours_add: function (frm) {
        if (frm.doc.hour > 0 && frm.doc.refilling_schedule) {
            frm.doc.refilling_schedule.forEach(row => {
                if (row.enter_datetime) {
                    let datetime = frappe.datetime.str_to_obj(row.enter_datetime);
                    let time_only = datetime.toTimeString().split(' ')[0];
                    datetime.setDate(datetime.getDate() + frm.doc.hour);
                    let updated_date = frappe.datetime.obj_to_str(datetime).split(' ')[0];
                    let final_date_time = `${updated_date} ${time_only}`;
                    frappe.model.set_value(row.doctype, row.name, 'enter_datetime', final_date_time);
                }
            });
            frm.refresh_field('refilling_schedule');
        }
    },    
    hours_deduct: function (frm) {
        if (frm.doc.hour > 0 && frm.doc.refilling_schedule) {
            frm.doc.refilling_schedule.forEach(row => {
                if (row.enter_datetime) {
                    let datetime = frappe.datetime.str_to_obj(row.enter_datetime);
                    let time_only = datetime.toTimeString().split(' ')[0];
                    datetime.setDate(datetime.getDate() - frm.doc.hour);
                    let updated_date = frappe.datetime.obj_to_str(datetime).split(' ')[0];
                    let final_date_time = `${updated_date} ${time_only}`;
                    frappe.model.set_value(row.doctype, row.name, 'enter_datetime', final_date_time);
                }
            });
            frm.refresh_field('refilling_schedule');
        }
    }
});

frappe.ui.form.on('Checkin Table', {
    checkin: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.in_time) {
            frappe.model.set_value(cdt, cdn, "in_time",frappe.datetime.now_datetime());
            frappe.msgprint(__('Check-in time has been updated!'));
            frm.refresh_field("checkin_details");
        } else {
            frappe.msgprint(__('Check-in time is already updated!'));
        }  
    },
    checkout: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.outtime) {
            frappe.model.set_value(cdt, cdn, "outtime",frappe.datetime.now_datetime());
            frappe.msgprint(__('Check-out time has been updated!'));
            frm.refresh_field("checkin_details");
        }else {
            frappe.msgprint(__('Check-out time is already updated!'));
        }
    },
});

frappe.ui.form.on('Refilling Schedule Table', {
    refilling_frequency: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.date_refilling && row.refilling_frequency) {
            console.log(row.date_refilling)
            console.log(row.refilling_frequency)
            let refillingDate = frappe.datetime.str_to_obj(row.date_refilling); 
            let frequencyMonths = parseInt(row.refilling_frequency, 10);
            let dueDate = frappe.datetime.add_months(refillingDate, frequencyMonths);
            row.refilling_due_date = frappe.datetime.obj_to_str(dueDate);
            frm.refresh_field("refilling_schedule");
        }
    },

    year_frequency: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.hpt && row.year_frequency) {
            let yearOfMfg = parseInt(row.hpt, 10); 
            let yearFrequency = parseInt(row.year_frequency, 10); 
            row.expiry_life_due = yearOfMfg + yearFrequency;
            frm.refresh_field("refilling_schedule");
        }
    },

    date_refilling: function(frm, cdt, cdn){
        let row = locals[cdt][cdn];
        if(row.date_refilling){
            frappe.model.set_value(cdt, cdn, "enter_datetime",frappe.datetime.now_datetime());
            frm.refresh_field("refilling_schedule");
        }
    },

    amc_remarks: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (!row.amc_remarks) {
            return;
        }

        let new_value = row.amc_remarks.trim();

        // Split existing remarks into a clean list, ignoring empty entries
        let existing_list = (row.remarks || "")
            .split(",")
            .map(v => v.trim())
            .filter(v => v.length > 0);

        // Check for duplicate (case-insensitive)
        let is_duplicate = existing_list.some(
            v => v.toLowerCase() === new_value.toLowerCase()
        );

        if (is_duplicate) {
            frappe.msgprint(__('"{0}" is already added in Remarks Details.', [new_value]));
        } else {
            existing_list.push(new_value);
            let updated_remarks = existing_list.join(", ");
            frappe.model.set_value(cdt, cdn, "remarks", updated_remarks);
        }

        // Always clear the link field after processing, whether duplicate or not
        frappe.model.set_value(cdt, cdn, "amc_remarks", "");
        frm.refresh_field("refilling_schedule");
    },

    clear_remarks: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (frm.doc.quotation) {
            frappe.msgprint(__('Cannot clear Remarks because a Quotation ({0}) is already linked.', [frm.doc.quotation]));
            return;
        }

        frappe.model.set_value(cdt, cdn, "remarks", "");
        frappe.model.set_value(cdt, cdn, "amc_remarks", "");
        frm.refresh_field("refilling_schedule");
    }
});


// ---------------------------------------------------------------
// Create Quotation from AMC Visitor Tracking
// ---------------------------------------------------------------

async function get_item_qty_map_from_remarks(frm) {
    // Collect every remark name across all refilling_schedule rows.
    // Duplicates are kept intentionally — repeat count = quantity.
    let remark_names = [];

    (frm.doc.refilling_schedule || []).forEach(row => {
        if (row.remarks) {
            row.remarks.split(",").forEach(r => {
                let v = r.trim();
                if (v) {
                    remark_names.push(v);
                }
            });
        }
    });

    if (!remark_names.length) {
        return {};
    }

    // Only fetch each unique remark's linked Item once (avoid duplicate DB calls)
    let unique_remarks = [...new Set(remark_names)];
    let remark_item_map = {};

    await Promise.all(
        unique_remarks.map(async (remark_name) => {
            try {
                let res = await frappe.db.get_value("AMC Remarks", remark_name, "item");
                remark_item_map[remark_name] = (res && res.message) ? res.message.item : null;
            } catch (e) {
                remark_item_map[remark_name] = null;
            }
        })
    );

    // Build final { item_code: qty } map.
    // If a remark has no linked item, it is skipped entirely (not added to quotation).
    let item_qty_map = {};

    remark_names.forEach(remark_name => {
        let item_code = remark_item_map[remark_name];
        if (item_code) {
            item_qty_map[item_code] = (item_qty_map[item_code] || 0) + 1;
        }
    });

    return item_qty_map;
}

async function create_quotation_from_amc(frm) {
    // If a Quotation is already linked, just open it — don't create another.
    // Check the local doc first, then fall back to a server check in case
    // the local cache is stale (e.g. after navigating back without a reload).
    let existing_quotation = frm.doc.quotation;

    if (!existing_quotation) {
        try {
            let res = await frappe.db.get_value(frm.doc.doctype, frm.doc.name, "quotation");
            existing_quotation = res && res.message ? res.message.quotation : null;
        } catch (e) {
            existing_quotation = null;
        }
    }

    if (existing_quotation) {
        frappe.set_route("Form", "Quotation", existing_quotation);
        return;
    }

    if (!frm.doc.customer_name) {
        frappe.msgprint(__('Customer is required before creating a Quotation.'));
        return;
    }

    frappe.dom.freeze(__('Preparing Quotation...'));

    let item_qty_map;
    try {
        item_qty_map = await get_item_qty_map_from_remarks(frm);
    } finally {
        frappe.dom.unfreeze();
    }

    let source = {
        customer: frm.doc.customer_name,
        location: frm.doc.location,
        customer_address: frm.doc.customer_address,
        company_address: frm.doc.company_address,
        company: frm.doc.company,
        custom_amc_tracking: frm.doc.name,
        amc_docname: frm.doc.name,
        amc_doctype: frm.doc.doctype
    };

    frappe.new_doc("Quotation");

    // The new Quotation form loads asynchronously — poll briefly until
    // cur_frm is actually pointing at the new (unsaved) Quotation.
    let attempts = 0;
    let max_attempts = 30; // ~4.5s total at 150ms interval

    let setup_quotation = async function () {
        attempts++;

        let ready = (
            cur_frm &&
            cur_frm.doc &&
            cur_frm.doc.doctype === "Quotation" &&
            cur_frm.doc.__islocal &&
            cur_frm.fields_dict &&
            cur_frm.fields_dict.party_name &&
            cur_frm.fields_dict.items
        );

        if (!ready) {
            if (attempts < max_attempts) {
                setTimeout(setup_quotation, 150);
            } else {
                frappe.msgprint(__('Quotation was created, but details could not be auto-filled. Please fill them manually.'));
            }
            return;
        }

        let q = cur_frm;

        try {
            // Set fields in dependency order — quotation_to change clears
            // party_name, and party_name change auto-fetches default addresses,
            // so later calls intentionally override those auto-fetched values.
            await q.set_value("quotation_to", "Customer");

            // Give quotation_to's own internal side effects (it clears
            // party_name asynchronously) time to fully settle before we
            // set party_name ourselves, otherwise it can get wiped out
            // by a race condition.
            await new Promise(resolve => setTimeout(resolve, 300));

            let party_attempts = 0;
            while (q.doc.party_name !== source.customer && party_attempts < 5) {
                await q.set_value("party_name", source.customer);
                await new Promise(resolve => setTimeout(resolve, 250));
                party_attempts++;
            }

            if (q.doc.party_name !== source.customer) {
                console.warn(
                    "create_quotation_from_amc: party_name did not stick after retries. Current value:",
                    q.doc.party_name
                );
            }

            await q.set_value("customer_address", source.customer_address);
            await q.set_value("company_address", source.company_address);
            await q.set_value("company", source.company);

            if (q.fields_dict.custom_region) {
                await q.set_value("custom_region", source.location);
            }

            if (q.fields_dict.custom_amc_tracking) {
                await q.set_value("custom_amc_tracking", source.custom_amc_tracking);
            }

            // Remove the blank default row Frappe adds to a new Quotation's
            // items table, so our items start at row 1 instead of row 2.
            q.clear_table("items");
            q.refresh_field("items");

            Object.keys(item_qty_map).forEach(item_code => {
                let child = q.add_child("items");
                frappe.model.set_value(child.doctype, child.name, "item_code", item_code);
                frappe.model.set_value(child.doctype, child.name, "qty", item_qty_map[item_code]);
            });
            q.refresh_field("items");

            if (!Object.keys(item_qty_map).length) {
                frappe.msgprint(__('No items were added — none of the Remarks had a linked Item in AMC Remarks.'));
            }

            if (q.doc.party_name !== source.customer) {
                frappe.msgprint(
                    __('Warning: Customer (Party Name) could not be set automatically. Please select it manually before saving.')
                );
            }
        } catch (setup_error) {
            console.error("create_quotation_from_amc: field setup failed", setup_error);
            frappe.msgprint(
                __('Something went wrong while filling the Quotation: {0}. Please check the browser console for details.', [setup_error.message || setup_error])
            );
            return;
        }

        // Auto-save as Draft, then link the new Quotation's name back
        // into the AMC Visitor Tracking record's "quotation" field.
        try {
            await q.save();

            await frappe.call({
                method: "crm_activity_tracking.crm_activity_tracking.doctype.amc_visitor_tracking.amc_visitor_tracking.update_quotation_link",
                args: {
                    amc_name: source.amc_docname,
                    quotation_name: q.doc.name
                }
            });

            // Also update the local client-side cache for that document,
            // so if the user navigates back without a full reload, the
            // "quotation" field shows the new value immediately instead
            // of a stale cached empty value.
            if (locals[source.amc_doctype] && locals[source.amc_doctype][source.amc_docname]) {
                locals[source.amc_doctype][source.amc_docname].quotation = q.doc.name;
            }

            frappe.show_alert({
                message: __('Quotation {0} created and linked back to {1}.', [q.doc.name, source.amc_docname]),
                indicator: 'green'
            });
        } catch (save_error) {
            console.error("create_quotation_from_amc: save/link failed", save_error);
            frappe.msgprint(
                __('Quotation was filled in but could not be saved automatically (some required field may still be missing). Please complete and save it manually — the link back to AMC Visitor Tracking will not happen until then.')
            );
        }
    };

    setTimeout(setup_quotation, 150);
}
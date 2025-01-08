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
        if (row.year_of_mfg && row.year_frequency) {
            let yearOfMfg = parseInt(row.year_of_mfg, 10); 
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
    }
});

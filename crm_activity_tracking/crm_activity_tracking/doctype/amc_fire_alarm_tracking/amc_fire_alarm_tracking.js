// Copyright (c) 2025, CRM and contributors
// For license information, please see license.txt

frappe.ui.form.on("AMC Fire Alarm Tracking", {
	refresh(frm) {
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
frappe.ui.form.on('AMC Fire Alaram Table', {
    remarks: function(frm, cdt, cdn){
        let row = locals[cdt][cdn];
        if(row.remarks){
            frappe.model.set_value(cdt, cdn, "enter_datetime",frappe.datetime.now_datetime());
            frm.refresh_field("refilling_schedule");
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

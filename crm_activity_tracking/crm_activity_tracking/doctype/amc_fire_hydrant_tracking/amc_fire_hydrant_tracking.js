// Copyright (c) 2025, CRM and contributors
// For license information, please see license.txt

frappe.ui.form.on("AMC Fire Hydrant Tracking", {
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
    hour_add: function (frm) {
        if (frm.doc.hour > 0 && frm.doc.landing_valve_table) {
            frm.doc.landing_valve_table.forEach(row => {
                if (row.enter_datetime) {
                    let datetime = frappe.datetime.str_to_obj(row.enter_datetime);
                    let time_only = datetime.toTimeString().split(' ')[0];
                    datetime.setDate(datetime.getDate() + frm.doc.hour);
                    let updated_date = frappe.datetime.obj_to_str(datetime).split(' ')[0];
                    let final_date_time = `${updated_date} ${time_only}`;
                    frappe.model.set_value(row.doctype, row.name, 'enter_datetime', final_date_time);
                }
            });
            frm.refresh_field('landing_valve_table');
        }
    },    
    hours_deduct: function (frm) {
        if (frm.doc.hour > 0 && frm.doc.landing_valve_table) {
            frm.doc.landing_valve_table.forEach(row => {
                if (row.enter_datetime) {
                    let datetime = frappe.datetime.str_to_obj(row.enter_datetime);
                    let time_only = datetime.toTimeString().split(' ')[0];
                    datetime.setDate(datetime.getDate() - frm.doc.hour);
                    let updated_date = frappe.datetime.obj_to_str(datetime).split(' ')[0];
                    let final_date_time = `${updated_date} ${time_only}`;
                    frappe.model.set_value(row.doctype, row.name, 'enter_datetime', final_date_time);
                }
            });
            frm.refresh_field('landing_valve_table');
        }
    },
    hour_add1: function (frm) {
        if (frm.doc.hour1 > 0 && frm.doc.hose_box_and_rrl_hose) {
            frm.doc.hose_box_and_rrl_hose.forEach(row => {
                if (row.enter_datetime) {
                    let datetime = frappe.datetime.str_to_obj(row.enter_datetime);
                    let time_only = datetime.toTimeString().split(' ')[0];
                    datetime.setDate(datetime.getDate() + frm.doc.hour1);
                    let updated_date = frappe.datetime.obj_to_str(datetime).split(' ')[0];
                    let final_date_time = `${updated_date} ${time_only}`;
                    frappe.model.set_value(row.doctype, row.name, 'enter_datetime', final_date_time);
                }
            });
            frm.refresh_field('hose_box_and_rrl_hose');
        }
    },    
    hours_deduct1: function (frm) {
        if (frm.doc.hour1 > 0 && frm.doc.hose_box_and_rrl_hose) {
            frm.doc.hose_box_and_rrl_hose.forEach(row => {
                if (row.enter_datetime) {
                    let datetime = frappe.datetime.str_to_obj(row.enter_datetime);
                    let time_only = datetime.toTimeString().split(' ')[0];
                    datetime.setDate(datetime.getDate() - frm.doc.hour1);
                    let updated_date = frappe.datetime.obj_to_str(datetime).split(' ')[0];
                    let final_date_time = `${updated_date} ${time_only}`;
                    frappe.model.set_value(row.doctype, row.name, 'enter_datetime', final_date_time);
                }
            });
            frm.refresh_field('hose_box_and_rrl_hose');
        }
    },
    hour_add2: function (frm) {
        if (frm.doc.hour2 > 0 && frm.doc.pump_and_panel) {
            frm.doc.pump_and_panel.forEach(row => {
                if (row.enter_datetime) {
                    let datetime = frappe.datetime.str_to_obj(row.enter_datetime);
                    let time_only = datetime.toTimeString().split(' ')[0];
                    datetime.setDate(datetime.getDate() + frm.doc.hour2);
                    let updated_date = frappe.datetime.obj_to_str(datetime).split(' ')[0];
                    let final_date_time = `${updated_date} ${time_only}`;
                    frappe.model.set_value(row.doctype, row.name, 'enter_datetime', final_date_time);
                }
            });
            frm.refresh_field('pump_and_panel');
        }
    },    
    hours_deduct2: function (frm) {
        if (frm.doc.hour2 > 0 && frm.doc.pump_and_panel) {
            frm.doc.pump_and_panel.forEach(row => {
                if (row.enter_datetime) {
                    let datetime = frappe.datetime.str_to_obj(row.enter_datetime);
                    let time_only = datetime.toTimeString().split(' ')[0];
                    datetime.setDate(datetime.getDate() - frm.doc.hour2);
                    let updated_date = frappe.datetime.obj_to_str(datetime).split(' ')[0];
                    let final_date_time = `${updated_date} ${time_only}`;
                    frappe.model.set_value(row.doctype, row.name, 'enter_datetime', final_date_time);
                }
            });
            frm.refresh_field('pump_and_panel');
        }
    },
    hour_add3: function (frm) {
        if (frm.doc.hour3 > 0 && frm.doc.hose_reel_drum) {
            frm.doc.hose_reel_drum.forEach(row => {
                if (row.enter_datetime) {
                    let datetime = frappe.datetime.str_to_obj(row.enter_datetime);
                    let time_only = datetime.toTimeString().split(' ')[0];
                    datetime.setDate(datetime.getDate() + frm.doc.hour3);
                    let updated_date = frappe.datetime.obj_to_str(datetime).split(' ')[0];
                    let final_date_time = `${updated_date} ${time_only}`;
                    frappe.model.set_value(row.doctype, row.name, 'enter_datetime', final_date_time);
                }
            });
            frm.refresh_field('hose_reel_drum');
        }
    },    
    hours_deduct3: function (frm) {
        if (frm.doc.hour3 > 0 && frm.doc.hose_reel_drum) {
            frm.doc.hose_reel_drum.forEach(row => {
                if (row.enter_datetime) {
                    let datetime = frappe.datetime.str_to_obj(row.enter_datetime);
                    let time_only = datetime.toTimeString().split(' ')[0];
                    datetime.setDate(datetime.getDate() - frm.doc.hour3);
                    let updated_date = frappe.datetime.obj_to_str(datetime).split(' ')[0];
                    let final_date_time = `${updated_date} ${time_only}`;
                    frappe.model.set_value(row.doctype, row.name, 'enter_datetime', final_date_time);
                }
            });
            frm.refresh_field('hose_reel_drum');
        }
    },
    hour_add4: function (frm) {
        if (frm.doc.hour4 > 0 && frm.doc.fire_brigade_inlet) {
            frm.doc.fire_brigade_inlet.forEach(row => {
                if (row.enter_datetime) {
                    let datetime = frappe.datetime.str_to_obj(row.enter_datetime);
                    let time_only = datetime.toTimeString().split(' ')[0];
                    datetime.setDate(datetime.getDate() + frm.doc.hour4);
                    let updated_date = frappe.datetime.obj_to_str(datetime).split(' ')[0];
                    let final_date_time = `${updated_date} ${time_only}`;
                    frappe.model.set_value(row.doctype, row.name, 'enter_datetime', final_date_time);
                }
            });
            frm.refresh_field('fire_brigade_inlet');
        }
    },    
    hours_deduct4: function (frm) {
        if (frm.doc.hour4 > 0 && frm.doc.fire_brigade_inlet) {
            frm.doc.fire_brigade_inlet.forEach(row => {
                if (row.enter_datetime) {
                    let datetime = frappe.datetime.str_to_obj(row.enter_datetime);
                    let time_only = datetime.toTimeString().split(' ')[0];
                    datetime.setDate(datetime.getDate() - frm.doc.hour4);
                    let updated_date = frappe.datetime.obj_to_str(datetime).split(' ')[0];
                    let final_date_time = `${updated_date} ${time_only}`;
                    frappe.model.set_value(row.doctype, row.name, 'enter_datetime', final_date_time);
                }
            });
            frm.refresh_field('fire_brigade_inlet');
        }
    }
});

frappe.ui.form.on('AMC Fire Hydrant Table', {
    remarks: function(frm, cdt, cdn){
        let row = locals[cdt][cdn];
        if(row.remarks){
            frappe.model.set_value(cdt, cdn, "enter_datetime",frappe.datetime.now_datetime());
            frm.refresh_field("landing_valve_table");
            frm.refresh_field("hose_box_and_rrl_hose");
            frm.refresh_field("pump_and_panel");
            frm.refresh_field("hose_reel_drum");
            frm.refresh_field("fire_brigade_inlet");
        }
    }
})

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
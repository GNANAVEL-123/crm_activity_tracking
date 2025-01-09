frappe.ui.form.on("Quotation", {
	
	onload: function(frm){

		
	},
    refresh: function(frm){


        frappe.call({
            method: 'crm_activity_tracking.crm_activity_tracking.report.daily_tracking_status.daily_tracking_status.get_crm_settings',
            callback: function(r) {
				console.log(r.message)
                if (r.message && r.message.show_quotation_filter === 1) {
					frm.set_value('show_followup', 1);
                } else {
                    frm.set_value('show_followup', 0);
                }
            }
        });

		if (frm.doc.docstatus == 1 && ["Open", "Expired"].includes(frm.doc.status)) {
			frm.add_custom_button(__("Converted"), function() {
                frappe.call({
                    method: "crm_activity_tracking.crm_activity_tracking.custom_files.py.quotation.sales_order_making",
                    args: {
                        doc: frm.doc,
                    },
                    callback: function (r) {
                        if (r.message) {
							frm.set_value("status", "Ordered")
                            frappe.show_alert({
                                message: __("Sales Order Making Successfully"),
                                indicator: "green",
                            });
                        }
                    }
    
                })
                
            }, );
		}

		if(frm.doc.docstatus == 1 && frm.doc.status !== "Order Cancelled"){
			frm.add_custom_button(__("Order Cancelled"), function() {
					frm.set_value("status", "Order Cancelled")
					frm.set_value("custom_quotation_cancel_date", frappe.datetime.now_date())
					frappe.show_alert({
						message: __("Order Cancelled Successfully"),
						indicator: "red",
					});
                }, 
			);
		}

		frappe.db.get_value('User', {'name': frappe.session.user}, 'role_profile_name', (r) => {
			if (r.role_profile_name == 'Admin') {
			 cur_frm.fields_dict.items.grid.update_docfield_property('rate','read_only',1)
			} else {
			 cur_frm.fields_dict.items.grid.update_docfield_property('rate','read_only',0)
			}
		   });
		if(['Ordered','Lost'].includes(frm.doc.status)){
			frm.set_df_property('custom_followup', 'read_only', 1);
		}
		else{
			frm.set_df_property('custom_followup', 'read_only',0);
		}
		setTimeout(() => {
			frm.remove_custom_button("Set as Lost");
			frm.remove_custom_button('Sales Order',"Create");
			frm.remove_custom_button("Opportunity", "Get Items From");
		}, 100)

		frm.set_query("custom_quotation_owner", function () {
			return {
				filters: {
					enabled: 1,
				},
			};
		});

		frm.set_query("custom_project_location", function () {
			return {
				filters: {
					is_group: 0,
				},
			};
		});

		frm.set_query('custom_item_group',function(frm){
			return {
				filters:{
					'is_group':0,
				}
			}
		});
		if(frm.doc.docstatus == 1 && frm.doc.status == "Open"){
			frm.add_custom_button(__("Converted"), function() {
                frappe.call({
                    method: "crm_activity_tracking.crm_activity_tracking.custom_files.py.quotation.sales_order_making",
                    args: {
                        doc: frm.doc,
                    },
                    callback: function (r) {
                        if (r.message) {
							frm.set_value("status", "Ordered")
                            frappe.show_alert({
                                message: __("Sales Order Making Successfully"),
                                indicator: "green",
                            });
                        }
                    }
    
                })
                
            }, );
		}
		if(frm.doc.docstatus == 1){
			frm.add_custom_button(__("Create Refilling Certificate"), function () {
                // Create a new document for Refilling Certificate
                frappe.new_doc('Refilling Certificate', {
                    customer: frm.doc.party_name,
                    address: frm.doc.customer_address,
					region: frm.doc.custom_region
                });
        
                frappe.ui.form.on('Refilling Certificate', 'onload', function (newFrm) {
					newFrm.set_value("from_date", frm.doc.transaction_date);
                    newFrm.set_value("refilling_report_date", frm.doc.transaction_date);
                    if (newFrm.doc.table_wxkh === undefined) {
                        newFrm.doc.table_wxkh = [];
                    }
					frappe.model.clear_table(newFrm.doc, 'table_wxkh');
                    frm.doc.items.forEach(row => {
                        let new_row = frappe.model.add_child(newFrm.doc, 'Refilling Certificate Table', 'table_wxkh');
                        new_row.item = row.item_code;
                        new_row.item_name = row.item_name;
                        new_row.quantity = row.qty;
                        new_row.rate = row.rate;
                        new_row.uom = row.uom;
                    });
        
                    newFrm.refresh_field('table_wxkh');
                });
            }).addClass("btn-danger").css({
                'color': 'white',
                'background-color': '#bb6b93',
                'font-weight': 'bold'
            });
		}
		if(frm.doc.docstatus == 1){
			frm.add_custom_button(__("Create Warranty Certificate"), function () {
                // Create a new document for Refilling Certificate
                frappe.new_doc('Warranty Certificate', {
                    customer_name: frm.doc.party_name,
                    customer_address: frm.doc.customer_address,
					region: frm.doc.custom_region
                });
        
                frappe.ui.form.on('Warranty Certificate', 'onload', function (newFrm) {
					newFrm.set_value("refilling__report_date", frm.doc.transaction_date);
                    if (newFrm.doc.table_nrxp === undefined) {
                        newFrm.doc.table_nrxp = [];
                    }
					frappe.model.clear_table(newFrm.doc, 'table_nrxp');
                    frm.doc.items.forEach(row => {
                        let new_row = frappe.model.add_child(newFrm.doc, 'Warranty Certificate Table', 'table_nrxp');
                        new_row.item = row.item_code;
                        new_row.item_name = row.item_name;
                        new_row.quantity = row.qty;
                        new_row.rate = row.rate;
                        new_row.uom = row.uom;
                    });
        
                    newFrm.refresh_field('table_nrxp');
                });
            }).addClass("btn-danger").css({
                'color': 'white',
                'background-color': '#53a098',
                'font-weight': 'bold'
            });
		}
		// frm.set_query('item_code',"items", function(doc){
		// 	if (frm.doc.custom_item_group){
		// 		return {
		// 			query:"global_safety_enterprises.global_safety_enterprises.utils.py.quotation.item_query",
		// 			filters:{
		// 				'parent_item_group':frm.doc.custom_item_group,
		// 			}
		// 		}
		// 	}
		// })
    },

	custom_margin_: function(frm){

		if (frm.doc.custom_margin_ >= 0){

			for (var i = 0; i < (frm.doc.items).length; i++){

				frappe.model.set_value(frm.doc.items[i].doctype, frm.doc.items[i].name, "custom_ts_margin", frm.doc.custom_margin_)

			}
		}
		else{

			frm.set_value("custom_margin_", 0)

			frappe.show_alert({message: "Margin (%) Must Be Postive Number.", indicator: 'red'});
		}
	},
	custom_ts_status:function(frm){
		cur_frm.set_value('status',frm.doc.custom_ts_status)
		cur_frm.set_value('custom_status_updated',1)
		
	},
})

frappe.ui.form.on("Quotation Item", {

	custom_ts_margin: function(frm, cdt, cdn){

		var data = locals[cdt][cdn]

		if (data.custom_ts_margin >= 0){

			frappe.model.set_value(cdt, cdn, "discount_amount", 0)
			frappe.model.set_value(cdt, cdn, "margin_type", "Percentage")
			frappe.model.set_value(cdt, cdn, "margin_rate_or_amount", data.custom_ts_margin)
		}
		else{

			frappe.model.set_value(cdt, cdn, "custom_ts_margin", 0)

			frappe.show_alert({message: "Margin (%) Must Be Postive Number, In Row <b>" + data.idx + "</b>.", indicator: 'red'});
		}

	},

	item_code: function(frm, cdt, cdn){

		setTimeout(() => {

			frappe.model.set_value(cdt, cdn, "custom_ts_margin", frm.doc.custom_margin_)

		}, 200);
	},

	rate: function(frm, cdt, cdn){

		var data = locals[cdt][cdn]

		if (data.rate < 0){

			frappe.model.set_value(cdt, cdn, "rate", data.price_list_rate)

			frappe.show_alert({message: "Rate Must Be Postive Number, In Row <b>" + data.idx + "</b>, So Default Purchase Rate Is Set.", indicator: 'red'});
		}

	}
})

frappe.ui.form.on("Follow-Up", {
	date:function(frm,cdt,cdn){
		let row = locals[cdt][cdn]
		if(row.date){
		for (var i in cur_frm.doc.custom_followup) {
			var value = cur_frm.doc.custom_followup[i]
			if (row.idx == value.idx){
				break
			}
			if(row.date < value.date){
				frappe.show_alert({message:`Row - ${row.idx} Date (<span style='color:red'>${moment(row.date).format('DD-MM-YYYY')}</span>) should not be earlier than Row - ${value.idx} Date (<span style='color:red'>${moment(value.date).format('DD-MM-YYYY')}</span>)`, indicator:'red'})
				row.date = ''
				break
			}
		}
	}

	},
	next_follow_up_date:function(frm,cdt,cdn){
		let row = locals[cdt][cdn]
		if(row.next_follow_up_date < row.date){
			frappe.show_alert({message:`Follow Up Date - <span style='color:red'>${moment(row.next_follow_up_date).format('DD-MM-YYYY')}</span> should not be earlier than Date -<span style='color:red'> ${moment(row.date).format('DD-MM-YYYY')}</span>`,indicator:'red'})
			row.next_follow_up_date = ''
		}
	},
	status:function(frm,cdt,cdn){
		let row = locals[cdt][cdn]
		if(row.status == 'Do Not Disturb'){
			cur_frm.set_value('custom_status_updated',0)
		}
		else{
			cur_frm.set_value('custom_status_updated',1)
		}
	}
})
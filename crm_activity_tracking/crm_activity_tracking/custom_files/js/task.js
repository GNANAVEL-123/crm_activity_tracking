frappe.ui.form.on("Task", {
	refresh: function(frm){
		if(!cur_frm.is_new())
			frm.add_custom_button("Send Whatsapp",function () {
				frm.trigger("send_whatsapp_message");
			})
	},
	send_whatsapp_message:function(frm){
		if(frm.doc.custom_allocated_to){
			frappe.call({
				method: "crm_activity_tracking.crm_activity_tracking.custom_files.py.whatsapp.send_task_message",
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
})

frappe.ui.form.on("Follow-Up", {
	date: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn]
		if (row.date) {
			for (var i in cur_frm.doc.custom_view_follow_up_details_copy) {
				var value = cur_frm.doc.custom_view_follow_up_details_copy[i]
				if (row.idx == value.idx) {
					break
				}
				if (row.date < value.date) {
					frappe.show_alert({ message: `Row - ${row.idx} Date (<span style='color:red'>${moment(row.date).format('DD-MM-YYYY')}</span>) should not be earlier than Row - ${value.idx} Date (<span style='color:red'>${moment(value.date).format('DD-MM-YYYY')}</span>)`, indicator: 'red' })
					row.date = ''
					break
				}
			}
		}
	},
	next_follow_up_date: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn]
		if (row.next_follow_up_date < row.date) {
			frappe.show_alert({ message: `Tracking Date - <span style='color:red'>${moment(row.next_follow_up_date).format('DD-MM-YYYY')}</span> should not be earlier than Date -<span style='color:red'> ${moment(row.date).format('DD-MM-YYYY')}</span>`, indicator: 'red' })
			row.next_follow_up_date = ''
		}
	}
})
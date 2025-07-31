{% include "india_compliance/gst_india/client_scripts/party.js" %}

frappe.ui.form.on("Lead", {
	refresh: async function (frm) {

		// india_compliance.set_state_options(frm);

		setTimeout(() => {

			frm.remove_custom_button("Opportunity", "Create");
			frm.remove_custom_button("Prospect", "Create");
			frm.remove_custom_button("Add to Prospect", "Action");

			$("[data-doctype='Prospect']").hide();

		}, 100)

		frm.set_query("lead_owner", function () {
			return {
				filters: {
					enabled: 1,
				},
			};
		});

		if (!frm.doc.__islocal) {

			if (['Open', "Replied"].includes(frm.doc.status)) {
				frm.add_custom_button(__('<p style="color: #171717; padding-top:8px;padding-left:10px;padding-right:10px;"><b>Create Opportunity</b></p>'), () => {

					frappe.model.open_mapped_doc({
						method: "erpnext.crm.doctype.lead.lead.make_opportunity",
						frm: frm
					});

				});
			}
			if (['Quotation Created', 'Replied', 'Opportunity Open', 'Opportunity Closed', 'Do Not Disturb'].includes(frm.doc.status)) {
				frm.add_custom_button(__('<b style="color:#fc6126">Reopen Lead</b>'), () => {
					frm.set_value('custom_reopen', 1)
					frm.set_value('status', 'Open')
					frm.save()

				});
			}
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
	},
	followed_by: function(frm, cdt, cdn){
        let row = locals[cdt][cdn];
        if(row.followed_by){
            frappe.model.set_value(cdt, cdn, "enter_datetime",frappe.datetime.now_datetime());
            frm.refresh_field("custom_view_follow_up_details_copy");
        }
    }
})

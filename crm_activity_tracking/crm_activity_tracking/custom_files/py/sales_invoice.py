import frappe
from erpnext.accounts.party import  get_dashboard_info

@frappe.whitelist()
def get_customer_data(customer,company):
	if customer:
		doc = frappe.get_doc("Customer",customer)
		data_points = get_dashboard_info(doc.doctype, doc.name, doc.loyalty_program)
		res = {
			'custom_total_unpaid': 0,
		}
		for data_point in data_points:
			if data_point['total_unpaid']:
				res['custom_total_unpaid'] += data_point['total_unpaid']
		return res
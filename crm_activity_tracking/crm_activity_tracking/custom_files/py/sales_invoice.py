import frappe
from erpnext.accounts.party import  get_dashboard_info
from crm_activity_tracking.crm_activity_tracking.custom_files.py.quotation import get_last_selling_rate

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

def validate_customer_lastprice(doc, event):
    if not doc.posting_date or not doc.customer:
        return

    for item in doc.items:
        if not item.item_code:
            continue

        last_rate = get_last_selling_rate(
            item_code=item.item_code,
            transaction_date=doc.posting_date,
            customer=doc.customer
        )

        item.custom_last_customer_selling_rate = last_rate
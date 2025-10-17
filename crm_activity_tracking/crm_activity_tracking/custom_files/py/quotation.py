import frappe
import json
from frappe.utils import getdate, nowdate
from frappe.desk.reportview import get_filters_cond, get_match_cond
from frappe.permissions import (
	add_user_permission,
	get_doc_permissions,
	has_permission,
	remove_user_permission,
)
from erpnext.selling.doctype.quotation.quotation import make_sales_order

def on_trash(doc,event):
    
    for i in frappe.get_all('User Permission',['user'],{'allow':'Quotation','for_value':doc.name}):
        remove_user_permission("Quotation", doc.name, i.user)

def on_update_after_submit(doc,event):
    create_user_permission(doc)
    # sales_order_making(doc, event)
    
def validate(doc,event):
    if not doc.get('__islocal'):
        create_user_permission(doc)
    if doc.custom_visit_count and doc.items:
        tot_visit_amt = 0
        for amt in doc.items:
            if amt.rate and amt.amount:
                amt.custom_visit_count_amount = (doc.custom_visit_count or 0) * (amt.amount or 0)
                tot_visit_amt += amt.custom_visit_count_amount
        doc.custom_total_visit_amount = tot_visit_amt
    if doc.custom_tracking_email_id:
        frappe.utils.validate_email_address(doc.custom_tracking_email_id, throw=True)
    validate_customer_lastprice(doc, event)

def after_insert(doc,event):
    create_user_permission(doc)

# def sales_order_making(doc, event):
#     if doc.docstatus == 1 and doc.status == "Ordered":
#         so = make_sales_order(doc.name)
#         so.delivery_date = nowdate()
#         so.save()
#         so.submit()

@frappe.whitelist()
def sales_order_making(doc):
    # Parse the incoming document JSON
    doc = json.loads(doc)
    
    # Ensure the document is submitted (docstatus = 1)
    if doc.get('docstatus') == 1:
        # Create a new Sales Order from the document
        so = make_sales_order(doc['name'])
        so.transaction_date = doc.get('transaction_date')
        so.delivery_date = doc.get('transaction_date')
        so.save()
        so.submit()

        # Fetch and return the Sales Order document as a dictionary
        if so:
            so_doc = frappe.get_doc("Sales Order", so.name) 
            if so_doc:
                frappe.set_value("Quotation", doc['name'], 'custom_order_convert_date', nowdate())
                return so_doc.as_dict()
            else:
                return None


def create_user_permission(doc):
    
    if doc.custom_quotation_owner and not frappe.db.exists('User Permission',{'user':doc.custom_quotation_owner,'allow':'Quotation','for_value':doc.name}):
        role_profile = frappe.get_value('User',doc.custom_quotation_owner,'role_profile_name')
        if role_profile not in ['Admin', 'CRM Admin', 'Super Admin']:
            add_user_permission("Quotation", doc.name, doc.custom_quotation_owner,ignore_permissions=True,is_default=0)
    
    if doc.custom_assigned_to and not frappe.db.exists('User Permission',{'user':doc.custom_assigned_to,'allow':'Quotation','for_value':doc.name}):
        role_profile = frappe.get_value('User',doc.custom_assigned_to,'role_profile_name')
        if role_profile not in ['Admin', 'CRM Admin', 'Super Admin']:
            add_user_permission("Quotation", doc.name, doc.custom_assigned_to,ignore_permissions=True,is_default=0)

    for i in frappe.get_all('User Permission',['user'],{'user':['not in',[doc.custom_quotation_owner,doc.custom_assigned_to]],'allow':'Quotation','for_value':doc.name}):
        remove_user_permission("Quotation", doc.name, i.user)

def tax_details(doc):

    sgst_list = []
    cgst_list = []
    igst_list = []

    for tax in doc.taxes:

        if "SGST" in tax.account_head and tax.tax_amount != 0:
            tax_details = json.loads(tax.item_wise_tax_detail)
            values = list(tax_details.values())

            for value in values:

                if sgst_list:

                    matched = False

                    for i in range (0, len(sgst_list), 1):

                        if value[0] != 0:

                            if sgst_list[i].get(f"SGST@ {value[0]} %"):
                                sgst_list[i][f"SGST@ {value[0]} %"] += value[1]
                                break

                            if len(sgst_list) == i + 1 and not matched:
                                sgst_list.append({f"SGST@ {value[0]} %": value[1]})
                else:
                    if value[0] != 0:
                        sgst_list.append({f"SGST@ {value[0]} %": value[1]})

        if "CGST" in tax.account_head and tax.tax_amount != 0:
            tax_details = json.loads(tax.item_wise_tax_detail)
            values = list(tax_details.values())

            for value in values:

                if cgst_list:

                    matched = False

                    for i in range (0, len(cgst_list), 1):

                        if value[0] != 0:

                            if cgst_list[i].get(f"CGST@ {value[0]} %"):
                                cgst_list[i][f"CGST@ {value[0]} %"] += value[1]
                                break

                            if len(cgst_list) == i + 1 and not matched:
                                cgst_list.append({f"CGST@ {value[0]} %": value[1]})
                else:
                    if value[0] != 0:
                        cgst_list.append({f"CGST@ {value[0]} %": value[1]})

        if "IGST" in tax.account_head and tax.tax_amount != 0:
            tax_details = json.loads(tax.item_wise_tax_detail)
            values = list(tax_details.values())

            for value in values:

                if igst_list:

                    matched = False

                    for i in range (0, len(igst_list), 1):

                        if value[0] != 0:

                            if igst_list[i].get(f"IGST@ {value[0]} %"):
                                igst_list[i][f"IGST@ {value[0]} %"] += value[1]
                                break

                            if len(igst_list) == i + 1 and not matched:
                                igst_list.append({f"IGST@ {value[0]} %": value[1]})
                else:
                    if value[0] != 0:
                        igst_list.append({f"IGST@ {value[0]} %": value[1]})

    key = []
    value = []

    if cgst_list and sgst_list:

        key.append("Taxable Value")
        value.append(f'{round(doc.net_total, 2): .2f}')

        for i in range(0, len(sgst_list), 1):
            key.append(list(sgst_list[i].keys())[0])
            
            final_value = f'{round(list(sgst_list[i].values())[0], 2): .2f}'
            value.append(final_value)


            key.append(list(cgst_list[i].keys())[0])

            final_value = f'{round(list(cgst_list[i].values())[0], 2): .2f}'
            value.append(final_value)

    elif igst_list:

        key.append("Taxable Value")
        value.append(f'{round(doc.net_total, 2): .2f}')

        for igst in igst_list:
            key.append(list(igst.keys())[0])

            final_value = f'{round(list(igst.values())[0], 2): .2f}'
            value.append(final_value)

    return key, value


@frappe.whitelist()
def get_last_selling_rate(item_code, transaction_date, customer):
    if not item_code or not transaction_date or not customer:
        return None

    transaction_date = getdate(transaction_date)

    result = frappe.db.sql("""
        SELECT sii.rate
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON sii.parent = si.name
        WHERE si.customer = %s
            AND sii.item_code = %s
            AND si.docstatus != 2
            AND si.posting_date <= %s
        ORDER BY si.posting_date DESC, si.modified DESC
        LIMIT 1
    """, (customer, item_code, transaction_date), as_dict=True)

    if result:
        return result[0].rate

    return 0

def validate_customer_lastprice(doc, event):
    """
    This will be triggered when saving Quotation.
    It will update each item's `custom_last_customer_selling_rate` field.
    """
    if not doc.transaction_date or not doc.party_name:
        return

    for item in doc.items:
        if not item.item_code:
            continue

        last_rate = get_last_selling_rate(
            item_code=item.item_code,
            transaction_date=doc.transaction_date,
            customer=doc.party_name
        )

        item.custom_last_customer_selling_rate = last_rate

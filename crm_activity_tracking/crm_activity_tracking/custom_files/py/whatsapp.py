import frappe
import os
import requests
from urllib.parse import quote

@frappe.whitelist()
def send_sales_invoice_whatsapp(invoice):
    if(isinstance(invoice, str)):
        doc = frappe.get_doc("Sales Invoice", invoice)
    pdf_options={
        "page-size":"A4"
    }
    fcontent = frappe.get_print(doc=doc, print_format="Sales Invoice", as_pdf=1, no_letterhead=1,pdf_options=pdf_options)
    pdf_file_name = "{0}.pdf".format(doc.name)

    _file = frappe.get_doc(
        {
            "doctype": "File",
            "file_name": pdf_file_name,
            "content": fcontent,
        }
    )
    _file.insert()
    file_path = os.path.join(frappe.get_site_path("public", "files"), _file.file_name)
    message = (
        f"*Sales Invoice* 📄\n"
        f"Customer: *{doc.customer}*\n"
        f"Invoice No: *{doc.name}*\n"
        f"Date: {doc.posting_date}\n"
        f"Amount: ₹{frappe.utils.fmt_money(doc.rounded_total or doc.grand_total)}\n\n"
        f"Thank you for your business!"
    )
    frappe.enqueue(
                send_whatsapp,
                media_url=frappe.utils.get_url()+_file.file_url,
                doc=doc,
                message=message,
                invoice=doc.name
            )
    return 'Success'
	
def send_whatsapp(media_url, message, doc, invoice=None):
    response=""
    url_message = ""
    instance_id = frappe.db.get_single_value("Harshini Whatsapp Settings",'instance_id')
    # access = frappe.db.get_single_value("Whatsapp Settings",'access_token')
    url = frappe.db.get_single_value("Harshini Whatsapp Settings",'url')
    customer_mobile_no = ""
    if doc.customer_address:
        add_doc = frappe.get_doc("Address", doc.customer_address)
        if add_doc.phone:
            customer_mobile_no = add_doc.phone
        else:
            frappe.throw("Customer phone number not found in the linked Address.")
    else:
        frappe.throw("No customer address linked to this document.")
    # customer_mobile_no='8838077682'
    if customer_mobile_no:
            encoded_message = quote(message)
            log_doc = frappe.new_doc('Whatsapp Log')
            log_doc.mobile_no = customer_mobile_no
            log_doc.status = 'Not Sent'
            log_doc.reference_doctype = 'Sales Invoice'
            log_doc.reference_document = doc.name
            url_message = f"{url}FileWithCaption?token={instance_id}&phone=91{customer_mobile_no}&link={media_url}&message={encoded_message}"
            log_doc.request_url = url_message
            log_doc.save()
            try:
                payload={}
                headers = {}
                response = requests.request("GET", url_message, headers=headers, data=payload)
                frappe.log_error(title="Whatsapp Invoice Success", message=f""" {media_url}\n{response}\n{url_message}\n""")
                frappe.db.set_value('Whatsapp Log',log_doc.name,'status','Success')
                frappe.db.set_value('Whatsapp Log',log_doc.name,'response',str(response.json()))
            except Exception as e:
                frappe.log_error(title="Whatsapp Invoice Failure", message=f""" {media_url}\n{response}\n{url_message}\n""")
                frappe.db.set_value('Whatsapp Log',log_doc.name,'status','Failure')
                frappe.db.set_value('Whatsapp Log',log_doc.name,'response',str(response.json()))

@frappe.whitelist()
def send_task_message(invoice):
    response = ""
    url_message = ""

    # Fetch WhatsApp settings
    instance_id = frappe.db.get_single_value("Harshini Whatsapp Settings", 'instance_id')
    url = frappe.db.get_single_value("Harshini Whatsapp Settings", 'url')

    # Get the Task document
    task_doc = frappe.get_doc("Task", invoice)
    customer_mobile_no = ""

    # Check and fetch assigned user's mobile number
    if task_doc and task_doc.custom_allocated_to:
        user_mobile = frappe.db.get_value("User", task_doc.custom_allocated_to, "mobile_no")

        if user_mobile:
            customer_mobile_no = user_mobile
        else:
            frappe.throw(f"Mobile number not found for user: {task_doc.custom_allocated_to}")

        # Prepare message and WhatsApp URL
        site_url = f"https://erp.srihariharantraders.com/app/task/{task_doc.name}"
        message = (
            f"*Task Assigned* 📋\n"
            f"Task ID: *{task_doc.name}*\n"
            f"Subject: *{task_doc.subject or 'No Subject'}*\n"
            f"🔗 View Task: {site_url}\n\n"
            f"This task has been assigned to you. Please review and take action."
        )
        encoded_message = quote(message)
        # Create Whatsapp Log
        log_doc = frappe.new_doc('Whatsapp Log')
        log_doc.mobile_no = customer_mobile_no
        log_doc.status = 'Not Sent'
        log_doc.reference_doctype = 'Task'
        log_doc.reference_document = task_doc.name
        url_message = f"{url}Text?token={instance_id}&phone=91{customer_mobile_no}&message={encoded_message}"
        log_doc.request_url = url_message
        log_doc.save()

        try:
            payload = {}
            headers = {}
            response = requests.get(url_message, headers=headers, data=payload)
            
            frappe.db.set_value('Whatsapp Log', log_doc.name, 'status', 'Success')
            frappe.db.set_value('Whatsapp Log', log_doc.name, 'response', str(response.json()))
            frappe.log_error(title="Whatsapp Task Success", message=f"{response.text}\n{url_message}")
            return "Success"

        except Exception as e:
            frappe.db.set_value('Whatsapp Log', log_doc.name, 'status', 'Failure')
            frappe.db.set_value('Whatsapp Log', log_doc.name, 'response', str(e))
            frappe.log_error(title="Whatsapp Task Failure", message=f"{str(e)}\n{url_message}")
            return "Failure"

    else:
        frappe.throw("No user assigned in the 'Allocated To' field of the Task.")

@frappe.whitelist()
def send_quotation_whatsapp(invoice):
    if(isinstance(invoice, str)):
        doc = frappe.get_doc("Quotation", invoice)
    pdf_options={
        "page-size":"A4"
    }
    fcontent = frappe.get_print(doc=doc, print_format="Quotation With Logo", as_pdf=1, no_letterhead=1,pdf_options=pdf_options)
    pdf_file_name = "{0}.pdf".format(doc.name)

    _file = frappe.get_doc(
        {
            "doctype": "File",
            "file_name": pdf_file_name,
            "content": fcontent,
        }
    )
    _file.insert()
    file_path = os.path.join(frappe.get_site_path("public", "files"), _file.file_name)
    message = (
        f"*Quotation* 📄\n"
        f"Customer: *{doc.party_name}*\n"
        f"Quotation No: *{doc.name}*\n"
        f"Date: {doc.transaction_date}\n"
        f"Amount: ₹{frappe.utils.fmt_money(doc.rounded_total or doc.grand_total)}\n\n"
        f"Thank you for your interest!"
    )
    frappe.enqueue(
                send_whatsapp_quotation,
                media_url=frappe.utils.get_url()+_file.file_url,
                doc=doc,
                message=message,
                invoice=doc.name
            )
    return 'Success'
	
def send_whatsapp_quotation(media_url, message, doc, invoice=None):
    response=""
    url_message = ""
    instance_id = frappe.db.get_single_value("Harshini Whatsapp Settings",'instance_id')
    # access = frappe.db.get_single_value("Whatsapp Settings",'access_token')
    url = frappe.db.get_single_value("Harshini Whatsapp Settings",'url')
    customer_mobile_no = ""
    if doc.customer_address:
        add_doc = frappe.get_doc("Address", doc.customer_address)
        if add_doc.phone:
            customer_mobile_no = add_doc.phone
        else:
            frappe.throw("Customer phone number not found in the linked Address.")
    else:
        frappe.throw("No customer address linked to this document.")
    # customer_mobile_no='8838077682'
    if customer_mobile_no:
            encoded_message = quote(message)
            log_doc = frappe.new_doc('Whatsapp Log')
            log_doc.mobile_no = customer_mobile_no
            log_doc.status = 'Not Sent'
            log_doc.reference_doctype = 'Quotation'
            log_doc.reference_document = doc.name
            url_message = f"{url}FileWithCaption?token={instance_id}&phone=91{customer_mobile_no}&link={media_url}&message={encoded_message}"
            log_doc.request_url = url_message
            log_doc.save()
            try:
                payload={}
                headers = {}
                response = requests.request("GET", url_message, headers=headers, data=payload)
                frappe.log_error(title="Whatsapp Invoice Success", message=f""" {media_url}\n{response}\n{url_message}\n""")
                frappe.db.set_value('Whatsapp Log',log_doc.name,'status','Success')
                frappe.db.set_value('Whatsapp Log',log_doc.name,'response',str(response.json()))
            except Exception as e:
                frappe.log_error(title="Whatsapp Invoice Failure", message=f""" {media_url}\n{response}\n{url_message}\n""")
                frappe.db.set_value('Whatsapp Log',log_doc.name,'status','Failure')
                frappe.db.set_value('Whatsapp Log',log_doc.name,'response',str(response.json()))
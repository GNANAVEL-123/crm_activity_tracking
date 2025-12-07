import frappe
import os
import requests
from urllib.parse import quote

@frappe.whitelist()
def send_sales_invoice_whatsapp(invoice, mobile_no=None):
    if not mobile_no:
        frappe.throw("Mobile number is required.")

    if isinstance(invoice, str):
        doc = frappe.get_doc("Sales Invoice", invoice)

    mobile_no = str(mobile_no).replace(" ", "").replace("+91", "").replace("-", "")

    pdf_options = {"page-size": "A4"}
    fcontent = frappe.get_print(
        doc=doc,
        print_format="Sales Invoice",
        as_pdf=1,
        no_letterhead=1,
        pdf_options=pdf_options
    )

    file_name = f"{doc.name}.pdf"

    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "content": fcontent,
    })
    file_doc.insert()

    message = (
        f"*Sales Invoice* 📄\n"
        f"Customer: *{doc.customer}*\n"
        f"Invoice No: *{doc.name}*\n"
        f"Date: {doc.posting_date}\n"
        f"Amount: ₹{frappe.utils.fmt_money(doc.rounded_total or doc.grand_total)}\n\n"
        f"Thank you for your business!"
    )
    frappe.enqueue(
        send_whatsapp_sales_invoice,
        media_url=frappe.utils.get_url() + file_doc.file_url,
        message=message,
        doc=doc,
        mobile_no=mobile_no
    )

    return "Success"
	
def send_whatsapp_sales_invoice(media_url, message, doc, mobile_no=None):
    if not mobile_no:
        frappe.throw("Mobile number is required to send WhatsApp message.")

    instance_id = frappe.db.get_single_value("Harshini Whatsapp Settings", "instance_id")
    url = frappe.db.get_single_value("Harshini Whatsapp Settings", "url")

    encoded_message = quote(message)

    # Create WhatsApp Log
    log_doc = frappe.new_doc("Whatsapp Log")
    log_doc.mobile_no = mobile_no
    log_doc.status = "Not Sent"
    log_doc.reference_doctype = "Sales Invoice"
    log_doc.reference_document = doc.name

    url_message = (
        f"{url}FileWithCaption?token={instance_id}"
        f"&phone=91{mobile_no}&link={media_url}&message={encoded_message}"
    )

    log_doc.request_url = url_message
    log_doc.save()

    try:
        response = requests.get(url_message)

        # Log success
        frappe.log_error(
            title="WhatsApp Quotation Success",
            message=f"URL: {url_message}\nResponse: {response.text}"
        )

        frappe.db.set_value("Whatsapp Log", log_doc.name, "status", "Success")
        frappe.db.set_value("Whatsapp Log", log_doc.name, "response", str(response.json()))

    except Exception as e:

        # Log failure
        frappe.log_error(
            title="WhatsApp Quotation Failure",
            message=f"URL: {url_message}\nError: {str(e)}"
        )

        frappe.db.set_value("Whatsapp Log", log_doc.name, "status", "Failure")
        frappe.db.set_value("Whatsapp Log", log_doc.name, "response", str(e))

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
        site_url = f"{frappe.utils.get_url()}/app/task/{task_doc.name}"
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
def send_quotation_whatsapp(invoice, mobile_no=None):
    if not mobile_no:
        frappe.throw("Mobile number is required.")

    if isinstance(invoice, str):
        doc = frappe.get_doc("Quotation", invoice)

    # Clean number
    mobile_no = str(mobile_no).replace(" ", "").replace("+91", "").replace("-", "")

    pdf_options = {"page-size": "A4"}
    fcontent = frappe.get_print(
        doc=doc, print_format="Quotation With Logo", as_pdf=1, no_letterhead=1, pdf_options=pdf_options
    )

    pdf_file_name = f"{doc.name}.pdf"
    _file = frappe.get_doc({
        "doctype": "File",
        "file_name": pdf_file_name,
        "content": fcontent,
    })
    _file.insert()

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
        media_url=frappe.utils.get_url() + _file.file_url,
        doc=doc,
        message=message,
        mobile_no=mobile_no
    )

    return "Success"
	
def send_whatsapp_quotation(media_url, message, doc, mobile_no=None, invoice=None):
    response = ""
    url_message = ""

    if not mobile_no:
        frappe.throw("Mobile number is required.")

    # Clean the mobile number
    mobile_no = str(mobile_no).replace(" ", "").replace("+91", "").replace("-", "")

    instance_id = frappe.db.get_single_value("Harshini Whatsapp Settings", 'instance_id')
    url = frappe.db.get_single_value("Harshini Whatsapp Settings", 'url')

    encoded_message = quote(message)

    # Create WhatsApp Log
    log_doc = frappe.new_doc('Whatsapp Log')
    log_doc.mobile_no = mobile_no
    log_doc.status = 'Not Sent'
    log_doc.reference_doctype = 'Quotation'
    log_doc.reference_document = doc.name

    url_message = (
        f"{url}FileWithCaption?token={instance_id}"
        f"&phone=91{mobile_no}&link={media_url}&message={encoded_message}"
    )

    log_doc.request_url = url_message
    log_doc.save()

    try:
        response = requests.get(url_message)
        frappe.log_error(
            title="Whatsapp Invoice Success",
            message=f"""{media_url}\n{response}\n{url_message}\n"""
        )
        frappe.db.set_value('Whatsapp Log', log_doc.name, 'status', 'Success')
        frappe.db.set_value('Whatsapp Log', log_doc.name, 'response', str(response.json()))

    except Exception as e:
        frappe.log_error(
            title="Whatsapp Invoice Failure",
            message=f"""{media_url}\n{response}\n{url_message}\n"""
        )
        frappe.db.set_value('Whatsapp Log', log_doc.name, 'status', 'Failure')
        frappe.db.set_value('Whatsapp Log', log_doc.name, 'response', str(e))


@frappe.whitelist()
def send_payment_entry_whatsapp(payment_entry, mobile_no=None):
    if not mobile_no:
        frappe.throw("Mobile number is required.")

    if isinstance(payment_entry, str):
        doc = frappe.get_doc("Payment Entry", payment_entry)

    if doc.party_type != "Customer":
        frappe.throw("WhatsApp sending allowed only for Customer payments.")

    # Clean number
    mobile_no = str(mobile_no).replace(" ", "").replace("+91", "").replace("-", "")

    # WhatsApp text message only — No file
    message = (
        f"*Payment Confirmation* 📄\n"
        f"Customer: *{doc.party}*\n"
        f"Payment Entry: *{doc.name}*\n"
        f"Date: {doc.get_formatted('posting_date')}\n"
        f"Amount: ₹{frappe.utils.fmt_money(doc.paid_amount)}\n\n"
        f"Thank you for your payment!"
    )

    # Encode message
    encoded_message = quote(message)

    # Fetch credentials
    instance_id = frappe.db.get_single_value("Harshini Whatsapp Settings", "instance_id")
    url = frappe.db.get_single_value("Harshini Whatsapp Settings", "url")

    # WhatsApp message URL (text only)
    url_message = f"{url}Text?token={instance_id}&phone=91{mobile_no}&message={encoded_message}"

    # Create log record
    log_doc = frappe.new_doc("Whatsapp Log")
    log_doc.mobile_no = mobile_no
    log_doc.status = "Not Sent"
    log_doc.reference_doctype = "Payment Entry"
    log_doc.reference_document = doc.name
    log_doc.request_url = url_message
    log_doc.save()

    try:
        response = requests.get(url_message)
        frappe.db.set_value("Whatsapp Log", log_doc.name, "status", "Success")
        frappe.db.set_value("Whatsapp Log", log_doc.name, "response", str(response.text))

    except Exception as e:
        frappe.db.set_value("Whatsapp Log", log_doc.name, "status", "Failure")
        frappe.db.set_value("Whatsapp Log", log_doc.name, "response", str(e))

    return "Success"

# Copyright (c) 2025, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, add_days


class HarshiniWhatsappSettings(Document):
	pass

def inactive_customer_email_send():
    email_settings = frappe.get_single("Harshini Whatsapp Settings")

    if not email_settings.send_email_for_inactive_customers:
        return

    inactive_days = email_settings.inactive_days or 0
    if inactive_days <= 0:
        return

    last_sent = email_settings.last_email_send_date
    fre_days = email_settings.frequency_of_days or 0

    if last_sent:
        next_due_date = add_days(last_sent, fre_days)
        if today() != next_due_date:
            return

    customers = get_inactive_customers(inactive_days)

    for cust in customers:

        customer_doc = frappe.get_doc("Customer", cust[0])

        if not customer_doc.custom_send_email_to_nonactive:
            continue

        email_id = get_customer_email_from_address(customer_doc.name)
        if not email_id:
            continue

        subject = "🌟 We Value You – It's Been a While!"

        message = f"""
            <p>Dear <b>{cust[1]}</b>,</p>
            <p>It has been <b>{cust[8]} days</b> since your last purchase 🛒.</p>
            <p>We miss serving you and hope to see you soon 😊.</p>
            <p>Please feel free to visit us again.</p>
            <p>Warm Regards,<br><b>Harshini Fire Protection Equipments And Service</b></p>
        """

        frappe.sendmail(
            recipients=email_id,
            subject=subject,
            message=message,
            reference_doctype="Customer",
            reference_name=customer_doc.name,
            send_priority=1,
            sender="admin@harshinifire.com",
        )

    email_settings.last_email_send_date = today()
    email_settings.save(ignore_permissions=True)
    frappe.db.commit()

def get_inactive_customers(inactive_days):
    return frappe.db.sql(
        f"""
        SELECT
            cust.name,
            cust.customer_name,
            cust.territory,
            cust.customer_group,
            COUNT(so.name) as num_orders,
            SUM(so.base_net_total),
            SUM(so.base_net_total) as total_order_considered,
            MAX(so.posting_date) as last_order_date,
            DATEDIFF(CURRENT_DATE, MAX(so.posting_date)) as days_since_last_order
        FROM
            `tabCustomer` cust
        JOIN
            `tabSales Invoice` so
        ON
            cust.name = so.customer AND so.docstatus = 1
        GROUP BY cust.name
        HAVING days_since_last_order >= {inactive_days}
        """,
        as_list=1,
    )


def get_customer_email_from_address(customer):
    email = frappe.db.sql(
        """
        SELECT addr.email_id
        FROM `tabAddress` addr
        JOIN `tabDynamic Link` dl ON dl.parent = addr.name
        WHERE dl.link_doctype = 'Customer'
          AND dl.link_name = %s
        ORDER BY addr.creation DESC
        LIMIT 1
        """,
        (customer,),
    )
    return email[0][0] if email else None


def payment_remainder_email_send():
    email_settings = frappe.get_single("Harshini Whatsapp Settings")

    if not email_settings.send_email_for_payment_remainder:
        return

    freq_days = email_settings.frequency_of_payment_remainder_days or 0
    last_sent = email_settings.last_payment_send_date

    if last_sent:
        next_due = add_days(last_sent, freq_days)
        if today() != next_due:
            return 

    overdue_customers = get_overdue_customers()

    for cust in overdue_customers:

        customer_name = cust["customer"]
        customer_doc = frappe.get_doc("Customer", customer_name)

        email_id = get_customer_email_from_address(customer_name)
        if not email_id:
            continue

        invoice_list = ", ".join(cust["invoice_list"])
        total_amount = cust["total_overdue"]

        subject = "⏰ Payment Reminder – Overdue Invoice Alert"

        message = f"""
            <p>Dear <b>{customer_doc.customer_name}</b>,</p>
            <p>This is a gentle reminder that your following invoices are overdue:</p>
            <p><b>Invoices:</b> {invoice_list}</p>
            <p><b>Total Outstanding Amount:</b> ₹ {total_amount}</p>
            <p>Kindly make the payment at the earliest to avoid further reminders.</p>
            <p>Warm Regards,<br><b>Harshini Fire Protection Equipments And Service</b></p>
        """
        if cust["customer"] == "Developer Testing":
            frappe.sendmail(
                recipients=email_id,
                subject=subject,
                message=message,
                reference_doctype="Customer",
                reference_name=customer_name,
                send_priority=1,
                sender="admin@harshinifire.com",
            )

    email_settings.last_payment_send_date = today()
    email_settings.save(ignore_permissions=True)
    frappe.db.commit()

def get_overdue_customers():
    rows = frappe.db.sql(
        """
        SELECT
            si.customer,
            si.name AS invoice,
            si.grand_total,
            si.outstanding_amount
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1
          AND si.outstanding_amount > 0
          AND si.due_date < CURDATE()
        ORDER BY si.customer, si.due_date
        """,
        as_dict=True,
    )

    customer_map = {}

    for r in rows:
        cust = r.customer

        if cust not in customer_map:
            customer_map[cust] = {
                "customer": cust,
                "invoice_list": [],
                "total_overdue": 0
            }

        customer_map[cust]["invoice_list"].append(r.invoice)
        customer_map[cust]["total_overdue"] += r.outstanding_amount

    return list(customer_map.values())

def get_customer_email_from_address(customer):
    email = frappe.db.sql(
        """
        SELECT addr.email_id
        FROM `tabAddress` addr
        JOIN `tabDynamic Link` dl ON dl.parent = addr.name
        WHERE dl.link_doctype = 'Customer'
          AND dl.link_name = %s
        ORDER BY addr.creation DESC
        LIMIT 1
        """,
        (customer,),
    )
    return email[0][0] if email else None
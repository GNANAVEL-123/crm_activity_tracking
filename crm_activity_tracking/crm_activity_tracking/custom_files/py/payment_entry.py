import frappe
@frappe.whitelist()
def send_payment_entry_email(payment_entry, email_id=None):
    if not email_id:
        frappe.throw("Email ID is required.")

    if isinstance(payment_entry, str):
        doc = frappe.get_doc("Payment Entry", payment_entry)

    # One template for both Customer & Supplier
    template_doc = frappe.get_doc("Email Template", "Payment Confirmation Email Template")

    html_template = template_doc.response_html or template_doc.message

    # Render with Jinja
    message = frappe.render_template(html_template, {"doc": doc})

    # Dynamic subject
    if doc.party_type == "Customer":
        subject = f"Payment Confirmation - {doc.name}"
    else:
        subject = f"Payment Advice - {doc.name}"

    try:
        frappe.sendmail(
            recipients=[email_id],
            subject=subject,
            message=message,
            reference_doctype="Payment Entry",
            reference_name=doc.name,
            send_priority=1,
            sender="admin@harshinifire.com",
        )
        return "Success"

    except Exception as e:
        frappe.log_error("Payment Entry Email Error", str(e))
        return "Failed"

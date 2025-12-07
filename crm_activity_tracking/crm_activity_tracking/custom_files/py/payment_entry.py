import frappe
@frappe.whitelist()
def send_payment_entry_email(payment_entry, email_id=None):
    if not email_id:
        frappe.throw("Email ID is required.")

    if isinstance(payment_entry, str):
        doc = frappe.get_doc("Payment Entry", payment_entry)

    if doc.party_type != "Customer":
        frappe.throw("Email sending allowed only for Customer payments.")

    subject = f"Payment Confirmation - {doc.name}"

    message = f"""
        <b>Payment Confirmation</b><br><br>
        <b>Customer:</b> {doc.party}<br>
        <b>Payment Entry:</b> {doc.name}<br>
        <b>Date:</b> {doc.get_formatted('posting_date')}<br>
        <b>Amount:</b> ₹{frappe.utils.fmt_money(doc.paid_amount)}<br><br>
        Thank you for your payment!
    """

    try:
        frappe.sendmail(
            recipients=[email_id],
            subject=subject,
            message=message,
            sender="admin@harshinifire.com",
        )
        return "Success"

    except Exception as e:
        frappe.log_error("Payment Entry Email Error", str(e))
        return "Failed"

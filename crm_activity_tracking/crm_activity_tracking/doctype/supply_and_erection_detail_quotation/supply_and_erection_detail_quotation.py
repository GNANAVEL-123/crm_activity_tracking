# Copyright (c) 2026, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, flt


class SupplyandErectionDetailQuotation(Document):
	def validate(self):
		total_supply_amount = 0
		total_erection_amount = 0

		for row in self.items:
			# Row calculations
			row.supply_amount = (row.qty or 0) * (row.supply_rate or 0)
			row.erection_amount = (row.qty or 0) * (row.erection_rate or 0)

			# Add to totals
			total_supply_amount += row.supply_amount
			total_erection_amount += row.erection_amount

		# Set totals in parent
		self.total_supply_amount = total_supply_amount
		self.total_erection_amount = total_erection_amount

		# Optional: Grand Total
		self.total_amount = total_supply_amount + total_erection_amount

	def before_insert(self):
		if not self.terms_and_conditions:  # only if empty

			terms_list = [
				"Materials storage, water, electrical provision, scaffolding and other service clearance shall be your scope.",
				"All civil works shall be your scope.",
				"All site clearance shall be your scope.",
				"This offer is valid only for 30 days.",
				"Taxes applicable additionally.",
				"Goods once sold cannot be taken back in any circumstances.",
				"Warranty shall be applicable as per the manufacturers terms.",
				"Authorized personnel should be deputed for clearances when and wherever required by us.",
				"Quantities quoted are only tentative and shall be billed only on actual running length/quantities.",
				"This quote shall only be applicable for 15 days from the date of receipt of quotation.",
				"Erection amount quoted above is only for fixing the materials supplied by us.",
				"Provision of location for safe storage of materials brought inside company shall be your scope.",
				"Housekeeping shall be your scope.",
				"Onus of approval for items/materials required additionally rests with you.",
				"Provision of diesel for commissioning and water for testing shall be your scope.",
				"Structural stability responsibility rests with you.",
				"Required NDT test on commissioning shall be your scope.",
				"Provision of electricity supply shall be your scope.",
				"Provision of earth pit shall be your scope.",
				"Periodic maintenance responsibility rests with you.",
				"Warranty as per manufacturer wording.",
				"Payment terms: 80% advance, 10% on delivery, balance on commissioning.",
				"Erection charges apply only for supplied materials.",
				"Water tank interlinking and slab provision is client scope.",
				"Other terms applicable as per discussion."
			]

			for term in terms_list:
				row = self.append("terms_and_conditions", {})
				row.terms = term  # 🔁 change fieldname if different



import frappe

@frappe.whitelist()
def send_quotation_supply_erection_email(invoice, email=None):
    if not email:
        frappe.throw("Email ID is required.")

    doc = frappe.get_doc("Supply and Erection Detail Quotation", invoice)

    pdf = frappe.get_print(
        doc=doc,
        print_format="Supply and Erection Detail Quotation",
        as_pdf=1,
        no_letterhead=1,
        pdf_options={"page-size": "A4"},
    )

    subject = f"Quotation - {doc.name}"

    message = f"""
    <p>Dear {doc.customer_name},</p>

    <p>Please find the attached quotation.</p>

    <table cellpadding="5">
        <tr>
            <td><b>Quotation No</b></td>
            <td>{doc.name}</td>
        </tr>
        <tr>
            <td><b>Date</b></td>
            <td>{doc.date}</td>
        </tr>
        <tr>
            <td><b>Amount</b></td>
            <td>{frappe.utils.fmt_money(doc.total_amount)}</td>
        </tr>
    </table>

    <br>

    <p>Thank you for your interest.</p>

    <p>Regards,<br>{doc.company}</p>
    """

    frappe.sendmail(
        recipients=[email],
        subject=subject,
        message=message,
        attachments=[
            {
                "fname": f"{doc.name}.pdf",
                "fcontent": pdf
            }
        ],
		sender="admin@harshinifire.com",
        reference_doctype=doc.doctype,
        reference_name=doc.name,
        now=False      # Uses Email Queue
    )

    return "Success"

@frappe.whitelist()
def get_lowest_buyer_rate(item):
    item = frappe.get_doc("Item", item)

    lowest_rate = None
    lowest_buyer = None
    purchase_date = None

    for row in item.custom_buyer_details:
        rate = flt(row.purchase_rate)
        if rate <= 0:
            continue

        if lowest_rate is None or rate < lowest_rate:
            lowest_rate = rate
            lowest_buyer = row.buyer
            purchase_date = row.date  # make sure this fieldname is correct

    if lowest_rate is not None:
        return {
            "buyer": lowest_buyer,
            "rate": lowest_rate,
            "date": purchase_date
        }

    return None

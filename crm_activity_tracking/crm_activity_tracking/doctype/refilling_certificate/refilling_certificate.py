# Copyright (c) 2024, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RefillingCertificate(Document):
	def validate(self):
		if self.refilling_report_no:
			rc_doc_list = frappe.get_list(
				"Refilling Certificate",
				filters={
					"refilling_report_no": self.refilling_report_no,
					"name": ["!=", self.name]
				},
				fields=["name"]
			)
			if rc_doc_list:
				rc_doc_name = rc_doc_list[0].name
				frappe.throw(f"Refilling Report No {self.refilling_report_no} already exists in Refilling Certificate {rc_doc_name}.")

	def on_update(self):
		if self.refilling_report_no:
			try:
				rr_report_doc = frappe.get_doc("Refilling Report No", self.refilling_report_no)
				if not rr_report_doc.out_date:
					frappe.db.set_value("Refilling Report No", rr_report_doc.name, "out_date", self.refilling_report_date)
				if not rr_report_doc.invoice_no:
					frappe.db.set_value("Refilling Report No", rr_report_doc.name, "invoice_no", self.invoice_number)
			except frappe.DoesNotExistError:
				# If the document doesn't exist, just continue without doing anything
				pass

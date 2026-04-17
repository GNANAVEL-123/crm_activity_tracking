# Copyright (c) 2026, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


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

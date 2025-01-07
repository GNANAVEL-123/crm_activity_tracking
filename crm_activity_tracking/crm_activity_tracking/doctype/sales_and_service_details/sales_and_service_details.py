import frappe
from frappe.model.document import Document


class SalesandServiceDetails(Document):
    def validate(self):
        # Calculate totals
        self.total_value = (self.ppe_value or 0) + (self.extinguisher_value or 0) + (self.refilling_value or 0)
        self.total_nos = (self.to_fe_nos or 0) + (self.total_fa_nos or 0) + (self.total_hydrant or 0)

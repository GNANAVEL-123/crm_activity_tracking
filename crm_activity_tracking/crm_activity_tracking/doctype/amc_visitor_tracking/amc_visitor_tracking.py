# Copyright (c) 2024, CRM and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime
from frappe.model.document import Document


class AMCVisitorTracking(Document):
	def validate(self):
		if self.checkin_details:
			seen_dates = {}
			for row in self.checkin_details:
				row_date = row.in_time.split(" ")[0]
				if row_date in seen_dates:
					frappe.throw(
						f"Duplicate date found: {row_date} in rows {seen_dates[row_date]} and {row.idx}. Each date must be unique."
					)
				else:
					seen_dates[row_date] = row.idx
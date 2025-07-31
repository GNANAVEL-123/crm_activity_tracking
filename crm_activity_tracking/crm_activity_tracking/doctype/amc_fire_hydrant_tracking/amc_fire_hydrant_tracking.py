# Copyright (c) 2025, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class AMCFireHydrantTracking(Document):
	def validate(self):
		if self.amc_frequency and self.amc_service_date and not self.is_new():
			service_date = datetime.strptime(self.amc_service_date, "%Y-%m-%d")
			next_amc_service_date = service_date + relativedelta(months=self.amc_frequency)
			self.next_amc_service_due_date = next_amc_service_date.strftime("%Y-%m-%d")
		if self.checkin_details:
			for che in self.checkin_details:
				if che.in_time and che.outtime:
					if not self.feedback_table or any(not row.description or not row.marks for row in self.feedback_table):
						frappe.throw("Please ensure all rows in Feedback Table have both 'Description' and 'Marks' filled before Update Checkout.")

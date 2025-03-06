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

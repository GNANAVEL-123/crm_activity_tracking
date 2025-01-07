# Copyright (c) 2025, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, add_months, nowdate
from datetime import timedelta, date
from frappe.model.document import Document


class AMCFireAlarmSystem(Document):
	def validate(self):
		if self.amc_service_date and self.amc_frequency and not self.amc_frequency_list:
			self.amc_frequency_list = []
			start_date = getdate(self.amc_service_date)
			for _ in range(self.amc_frequency):
				end_date = add_months(start_date, self.amc_frequency) - timedelta(days=1)
				self.append("amc_frequency_list", {
					"from_date": start_date.strftime('%Y-%m-%d'),
					"to_date": end_date.strftime('%Y-%m-%d') 
				})
				start_date = end_date + timedelta(days=1)

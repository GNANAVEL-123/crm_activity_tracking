# Copyright (c) 2025, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, add_months, nowdate
from datetime import timedelta, date
from frappe.model.document import Document


class AMCFireAlarmSystem(Document):
	def validate(self):
		if self.amc_service_date and self.amc_frequency and not self.amc_frequency_list and self.no_of_month:
			self.amc_frequency_list = []
			start_date = getdate(self.amc_service_date)
			for i in range(self.no_of_month):
				end_date = add_months(start_date, self.amc_frequency) - timedelta(days=1)
				self.append("amc_frequency_list", {
					"from_date": start_date.strftime('%Y-%m-%d'),
					"to_date": end_date.strftime('%Y-%m-%d') 
				})
				start_date = add_months(start_date, self.amc_frequency)
				if i + 1 >= self.no_of_month:
					break

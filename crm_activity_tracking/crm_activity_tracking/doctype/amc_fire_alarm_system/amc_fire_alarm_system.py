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

def amc_fire_alarm_tracker():
	amc_list = frappe.db.get_all("AMC Fire Alarm System", fields=["name"])
	if amc_list:
		for amc in amc_list:
			if amc.name:
				amc_doc = frappe.get_doc("AMC Fire Alarm System", amc.name)
				if amc_doc and amc_doc.amc_frequency_list:
					for amc_fre in amc_doc.amc_frequency_list:
						avt = frappe.db.get_list(
							"AMC Fire Alarm Tracking",
							filters={"amc_service_date": amc_fre.from_date, "amc_template": amc_doc.name},
							fields=["name"]
						)
						if getdate(amc_fre.from_date) == getdate(nowdate()) and not avt:
							next_date = ""
							if amc_fre.from_date and amc_doc.amc_frequency:
								from_date = getdate(amc_fre.from_date)
								frequency_months = amc_doc.amc_frequency
								next_date = from_date + relativedelta(months=frequency_months)
							amc_tracker_doc = frappe.new_doc("AMC Fire Alarm Tracking")
							amc_tracker_doc.amc_fire_alarm_template = amc_doc.name
							amc_tracker_doc.customer_name = amc_doc.customer_name
							amc_tracker_doc.contact_number = amc_doc.contact_number
							amc_tracker_doc.mail_id = amc_doc.mail_id
							amc_tracker_doc.region = amc_doc.location
							amc_tracker_doc.client_representative = amc_doc.client_representative
							amc_tracker_doc.client_designation = amc_doc.client_designation
							amc_tracker_doc.employee_name = amc_doc.employee_name
							amc_tracker_doc.service_by = amc_doc.service_by
							amc_tracker_doc.amc_service_date = amc_fre.from_date
							amc_tracker_doc.amc_frequency = amc_doc.amc_frequency
							amc_tracker_doc.designation = amc_doc.designation                         
							amc_tracker_doc.cr__contact_number = amc_doc.cr__contact_number
							amc_tracker_doc.vendor_number = amc_doc.vendor_number
							amc_tracker_doc.po_number = amc_doc.po_number
							if amc_doc.refilling_schedule:
								for refilling_entry in amc_doc.refilling_schedule:
									refilling_child = amc_tracker_doc.append("refilling_schedule", {})
									refilling_child.location = refilling_entry.location
									refilling_child.device_no = refilling_entry.device_no
									refilling_child.zoneloop = refilling_entry.zoneloop
							amc_tracker_doc.save(ignore_permissions=True)

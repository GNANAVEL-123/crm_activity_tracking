# Copyright (c) 2024, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json

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
		if self.amc_frequency and self.amc_service_date:
			service_date = datetime.strptime(self.amc_service_date, "%Y-%m-%d")
			next_amc_service_date = service_date + relativedelta(months=self.amc_frequency)
			self.next_amc_service_due_date = next_amc_service_date.strftime("%Y-%m-%d")

@frappe.whitelist()
def description_list(doc):
    if doc:
        doc = json.loads(doc)
        given_des = []
        if doc.get("feedback_table"):
            for des in doc.get("feedback_table"):
                if des.get("description"):
                    given_des.append(des["description"])
        desc_list = frappe.db.get_all("Feedback Description", fields=["name"])
        desc_list = [desc["name"] for desc in desc_list]
        return_list = [desc for desc in desc_list if desc not in given_des]
        return return_list

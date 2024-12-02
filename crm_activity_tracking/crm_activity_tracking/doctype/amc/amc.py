# Copyright (c) 2024, CRM and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AMC(Document):
	from datetime import timedelta, datetime

def validate(self):
    if self.amc_service_date and self.amc_frequency and not self.amc_frequency_list:
        # Clear existing entries in amc_frequency_list
        self.amc_frequency_list = []

        # Convert service date to datetime object
        start_date = datetime.strptime(str(self.amc_service_date), '%d-%m-%Y')

        # Generate entries for the given frequency
        for i in range(self.amc_frequency):
            from_date = start_date
            to_date = start_date + timedelta(days=90)  # Approximation for 3 months
            self.append("amc_frequency_list", {
                "from_date": from_date.strftime('%d-%m-%Y'),
                "to_date": to_date.strftime('%d-%m-%Y')
            })
            # Update start_date for the next iteration
            start_date = to_date + timedelta(days=1)

        # Log for debugging
        frappe.errprint(self.amc_frequency_list)




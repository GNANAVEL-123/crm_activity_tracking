# Copyright (c) 2024, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_months, nowdate
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
import calendar

class AMC(Document):

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
        if self.number_of_portable_fire_extinguisher or self.number_of_trolley_fireextinguisher:
            self.total_extinguisher = ((self.number_of_portable_fire_extinguisher or 0) + (self.number_of_trolley_fireextinguisher or 0))
        



def amc_visitor_tracker():
    amc_list = frappe.db.get_all("AMC", fields=["name"])
    if amc_list:
        for amc in amc_list:
            if amc.name:
                amc_doc = frappe.get_doc("AMC", amc.name)
                if amc_doc and amc_doc.amc_frequency_list:
                    for amc_fre in amc_doc.amc_frequency_list:
                        if getdate(amc_fre.from_date) == getdate(nowdate()):
                            next_date = ""
                            if amc_fre.from_date and amc_doc.amc_frequency:
                                from_date = getdate(amc_fre.from_date)
                                frequency_months = amc_doc.amc_frequency
                                next_date = from_date + relativedelta(months=frequency_months)
                            amc_tracker_doc = frappe.new_doc("AMC Visitor Tracking")
                            amc_tracker_doc.amc_template = amc_doc.name
                            amc_tracker_doc.customer_name = amc_doc.customer_name
                            amc_tracker_doc.contact_number = amc_doc.contact_number
                            amc_tracker_doc.mail_id = amc_doc.mail_id
                            amc_tracker_doc.location = amc_doc.location
                            amc_tracker_doc.concern_person = amc_doc.concern_person
                            amc_tracker_doc.service_by = amc_doc.service_by
                            amc_tracker_doc.amc_service_date = amc_fre.from_date
                            amc_tracker_doc.next_amc_service_due_date = next_date
                            amc_tracker_doc.amc_frequency = amc_doc.amc_frequency
                            amc_tracker_doc.invoice_number = amc_doc.invoice_number
                            amc_tracker_doc.total_extinguisher = amc_doc.total_extinguisher
                            amc_tracker_doc.number_of_portable_fire_extinguisher = amc_doc.number_of_portable_fire_extinguisher
                            amc_tracker_doc.number_of_trolley_fireextinguisher = amc_doc.number_of_trolley_fireextinguisher
                            amc_tracker_doc.recommendations_quote_no = amc_doc.recommendations_quote_no
                            amc_tracker_doc.vendor_number = amc_doc.vendor_number
                            amc_tracker_doc.po_number = amc_doc.po_number
                            if amc_doc.refilling_schedule:
                                for refilling_entry in amc_doc.refilling_schedule:
                                    refilling_child = amc_tracker_doc.append("refilling_schedule", {})
                                    refilling_child.location = refilling_entry.location
                                    refilling_child.type = refilling_entry.type
                                    refilling_child.cap = refilling_entry.cap
                                    refilling_child.full_weight = refilling_entry.full_weight
                                    refilling_child.actual_weight = refilling_entry.actual_weight
                                    refilling_child.empty_weight = refilling_entry.empty_weight
                                    refilling_child.year_of_mfg = refilling_entry.year_of_mfg
                                    refilling_child.year_frequency = refilling_entry.year_frequency
                                    refilling_child.expiry_life_due = refilling_entry.expiry_life_due
                            amc_tracker_doc.save(ignore_permissions=True)

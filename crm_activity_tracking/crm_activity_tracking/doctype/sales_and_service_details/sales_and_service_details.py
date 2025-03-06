import frappe
from frappe.model.document import Document
from frappe.permissions import (
	add_user_permission,
	get_doc_permissions,
	has_permission,
	remove_user_permission,
)

class SalesandServiceDetails(Document):
    def validate(self):
        # Calculate totals
        self.total_value = (self.ppe_value or 0) + (self.extinguisher_value or 0) + (self.refilling_value or 0)
        self.total_nos = (self.to_fe_nos or 0) + (self.total_fa_nos or 0) + (self.total_hydrant or 0)
        # in time validate
        if not self.in_time:
            frappe.throw("Update In-time then only It Save")
        if not self.get('__islocal'):
            self.manage_user_permission()
        # serivce and sales validation
        if self.sales_purpose == "Meeting" and not self.remarks:
            frappe.throw("Please fill Remarks.")

        if self.service_purpose == "General Visit" and not self.remarks:
            frappe.throw("Please fill Remarks.")

        if self.service_purpose == "AMC Service":
            if not (self.fire_extinguisher or self.fire_alarm or self.hydrant):
                frappe.throw("Please fill in at least one of the AMC Service details (Fire Extinguisher, Fire Alarm, or Hydrant).")

        if self.service_purpose == "Delivery":
            if not (self.invoice_no and self.invoice_date and self.invoice_value):
                frappe.throw("Please fill in all Delivery Details (Invoice Number and Invoice Date).")

        if self.service_purpose == "Payments":
            if not self.payment_status:
                frappe.throw("Please fill Payment Status.")
            if self.payment_status == "Unpaid" and not self.remarks:
                frappe.throw("Enter Remarks of Unpaid Reason.")
            if self.payment_status == "Paid":
                if not (self.payment_type and self.amount):
                    frappe.throw("Please fill in both Payment Type and Amount.")

        if self.sales_purpose == "Payments":
            if not self.payment_status:
                frappe.throw("Please fill Payment Status.")
            if self.payment_status == "Unpaid" and not self.remarks:
                frappe.throw("Enter Remarks of Unpaid Reason.")
            if self.payment_status == "Paid":
                if not (self.payment_type and self.amount):
                    frappe.throw("Please fill in both Payment Type and Amount.")


        if self.sales_purpose in ["New Visit Follow", "Existing Visit Follow", "Quotation Follow", "PO Follow", "New Enquiry"]:
            if not (self.ppe or self.new_fire_extinguisher or self.refilling):
                frappe.throw("Please fill in at least one of PPE, New Fire Extinguisher, or Refilling details.")

        if self.service_purpose == "Repair" and not self.remarks:
            frappe.throw("Enter Remarks of Repair Reason.")
        if self.service_purpose == "Refilling" and not self.remarks:
            frappe.throw("Enter Remarks of Refilling Reason.")

        if self.service_purpose != "Lunch" or self.sales_purpose != "Lunch":
            if not self.customer_contact_no and not self.customer_name:
                frappe.throw("Enter Customer Name and Contact No.")
    def after_insert(self):  
        self.manage_user_permission()

    def manage_user_permission(self):
        if self.employee and not frappe.db.exists('User Permission',{'user':self.employee,'allow':'Sales and Service Details','for_value':self.name}):
            role_profile = frappe.get_value('User',self.employee,'role_profile_name')
            if role_profile not in ['Admin', 'CRM Admin', 'Regional Admin']:
                add_user_permission("Sales and Service Details", self.name, self.employee, ignore_permissions=True, is_default=0)
        
        for i in frappe.get_all('User Permission',['user'],{'user':["!=", self.employee],'allow':'Sales and Service Details','for_value':self.name}):
            remove_user_permission("Sales and Service Details", self.name, i.user)

    def on_trash(self):
        for i in frappe.get_all('User Permission',['user'],{'allow':'Sales and Service Details','for_value':self.name}):
            remove_user_permission("Sales and Service Details", self.name, i.user)

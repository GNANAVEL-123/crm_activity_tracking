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

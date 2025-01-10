# Copyright (c) 2024, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.permissions import (
	add_user_permission,
	get_doc_permissions,
	has_permission,
	remove_user_permission,
)

class RefillingReportNo(Document):
	def validate(self):
		if not self.get('__islocal'):
			self.manage_user_permission()

	def after_insert(self):  
		self.manage_user_permission()

	def manage_user_permission(self):
		if self.employee and not frappe.db.exists('User Permission',{'user':self.employee,'allow':'Refilling Report No','for_value':self.name}):
			role_profile = frappe.get_value('User',self.employee,'role_profile_name')
			if role_profile not in ['Admin', 'CRM Admin', 'Regional Admin']:
				add_user_permission("Refilling Report No", self.name, self.employee, ignore_permissions=True, is_default=0)
		
		for i in frappe.get_all('User Permission',['user'],{'user':["!=", self.employee],'allow':'Refilling Report No','for_value':self.name}):
			remove_user_permission("Refilling Report No", self.name, i.user)

	def on_trash(self):
		for i in frappe.get_all('User Permission',['user'],{'allow':'Refilling Report No','for_value':self.name}):
			remove_user_permission("Refilling Report No", self.name, i.user)
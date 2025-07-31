import frappe
from frappe.permissions import (
	add_user_permission,
	get_doc_permissions,
	has_permission,
	remove_user_permission,
)

def validate(doc, method):
    if not doc.get('__islocal'):
        manage_user_permission(doc)

def after_insert(doc, method):  
    manage_user_permission(doc)

def manage_user_permission(doc):
    if doc.custom_allocated_to and not frappe.db.exists('User Permission',{'user':doc.custom_allocated_to,'allow':'Task','for_value':doc.name}):
        role_profile = frappe.get_value('User',doc.custom_allocated_to,'role_profile_name')
        if role_profile not in ['Admin', 'Super Admin']:
            add_user_permission("Task", doc.name, doc.custom_allocated_to, ignore_permissions=True, is_default=0)
    
    for i in frappe.get_all('User Permission',['user'],{'user':["!=", doc.custom_allocated_to],'allow':'Task','for_value':doc.name}):
        remove_user_permission("Task", doc.name, i.user)

def on_trash(doc, action):
    for i in frappe.get_all('User Permission',['user'],{'allow':'Task','for_value':doc.name}):
        remove_user_permission("Task", doc.name, i.user)
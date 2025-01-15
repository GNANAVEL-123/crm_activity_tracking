import frappe
from frappe.utils import cstr
from frappe import _
from erpnext.crm.doctype.lead.lead import Lead
from frappe.utils import getdate
import re
from frappe.permissions import (
	add_user_permission,
	get_doc_permissions,
	has_permission,
	remove_user_permission,
)

def after_insert(doc,event):
    create_user_permission(doc)

def validate(doc, method):
    if doc.custom_view_follow_up_details_copy:
        last_followup = doc.custom_view_follow_up_details_copy[-1] 
        # if last_followup.status:
        #     doc.status = last_followup.status
    if doc.mobile_no:
        validate_phone_number(phone_number=(doc.mobile_no or ""))
    if not doc.get('__islocal'):
        create_user_permission(doc)

def create_user_permission(doc):
    
    if doc.lead_owner and not frappe.db.exists('User Permission',{'user':doc.lead_owner,'allow':'Lead','for_value':doc.name}):
        role_profile = frappe.get_value('User',doc.lead_owner,'role_profile_name')
        if role_profile not in ['Admin', 'CRM Admin', 'Super Admin']:
            add_user_permission("Lead", doc.name, doc.lead_owner,ignore_permissions=True,is_default=0)
    
    if doc.custom_assigned_to and not frappe.db.exists('User Permission',{'user':doc.custom_assigned_to,'allow':'Lead','for_value':doc.name}):
        role_profile = frappe.get_value('User',doc.custom_assigned_to,'role_profile_name')
        if role_profile not in ['Admin', 'CRM Admin', 'Super Admin']:
            add_user_permission("Lead", doc.name, doc.custom_assigned_to,ignore_permissions=True,is_default=0)

    if doc.custom_allocated_to_manager and not frappe.db.exists('User Permission',{'user':doc.custom_allocated_to_manager,'allow':'Lead','for_value':doc.name}):
        role_profile = frappe.get_value('User',doc.custom_allocated_to_manager,'role_profile_name')
        if role_profile not in ['Admin', 'CRM Admin', 'Super Admin']:
            add_user_permission("Lead", doc.name, doc.custom_allocated_to_manager,ignore_permissions=True,is_default=0)
    
    for i in frappe.get_all('User Permission',['user'],{'user':['not in',[doc.lead_owner,doc.custom_assigned_to, doc.custom_allocated_to_manager]],'allow':'Lead','for_value':doc.name}):
        remove_user_permission("Lead", doc.name, i.user)

class CustomLead(Lead):
    def before_insert(self):
        self.contact_doc = None
        if frappe.db.get_single_value("CRM Settings", "auto_creation_of_contact"):
            self.contact_doc = self.create_contact()
        if frappe.db.get_single_value("CRM Settings", "custom_auto_creation_of_address"):
            if self.custom_address_line_1 and self.city and self.state:
                self.address_doc = self.create_address()

    def validate(self):
        self.set_full_name()
        self.set_lead_name()
        self.set_title()
        # self.set_status()
        self.check_email_id_is_unique()
        self.validate_email_id()

    def create_address(self):

        if not self.lead_name:
            self.set_full_name()
            self.set_lead_name()

        address = frappe.new_doc("Address")
        address.update(
            {   
                'address_title': self.custom_address_title or self.first_name or self.lead_name,
                "address_line1": self.custom_address_line_1,
                "city": self.city,
                "state": self.state,
                "email_id": self.email_id,
                "phone": self.mobile_no,
                'gstin':self.custom_gstin,
                'gst_category':self.custom_gst_category,
                'pincode':self.custom_pincode,
                'address_type':self.custom_address_type,
                'address_line2':self.custom_address_line_2
            }
        )

        
        address.insert(ignore_permissions=True,ignore_mandatory= True)
        # contact.reload()  # load changes by hooks on contact

        return address

    def after_insert(self):
        self.link_to_contact()
        self.link_to_address()
    
    def link_to_address(self):
        if frappe.db.get_single_value("CRM Settings", "custom_auto_creation_of_address"):
            if self.custom_address_line_1 and self.city and self.state:
                # update contact links
                if self.address_doc:
                    self.address_doc.append(
                        "links", {"link_doctype": "Lead", "link_name": self.name, "link_title": self.lead_name}
                    )
                    self.address_doc.save()
                if self.contact_doc:
                    self.contact_doc.address = self.address_doc.name
                    self.contact_doc.save()
            
    def create_contact(self):
        if not self.lead_name:
            self.set_full_name()
            self.set_lead_name()

        contact = frappe.new_doc("Contact")
        contact.update(
            {
                "first_name": self.first_name or self.lead_name,
                "last_name": self.last_name,
                "salutation": self.salutation,
                "gender": self.gender,
                'middle_name':self.middle_name,
                "company_name": self.company_name,
            }
        )

        if self.email_id:
            contact.append("email_ids", {"email_id": self.email_id, "is_primary": 1})

        if self.phone:
            contact.append("phone_nos", {"phone": self.phone, "is_primary_phone": 1})

        if self.mobile_no:
            contact.append("phone_nos", {"phone": self.mobile_no, "is_primary_mobile_no": 1})

        contact.insert(ignore_permissions=True)
        contact.reload()  # load changes by hooks on contact

        return contact


def validate_phone_number(phone_number):
    
    pattern = re.compile(r"^\+?1?\d{10,10}$")
    
    if not pattern.match(phone_number):
        
        frappe.msgprint(f'Invalid Mobile Number.', title = 'Warning', indicator = "orange", raise_exception = 1)


def on_trash(doc,event):
    
    for i in frappe.get_all('User Permission',['user'],{'allow':'Lead','for_value':doc.name}):
        remove_user_permission("Lead", doc.name, i.user)


# lead_user_permission_update_script
def user_permission():
	lead_list = frappe.db.get_all("Lead", fields=["name"])
	print(lead_list)
	if lead_list:
		for i in lead_list:
			if i.name:
				lead_doc = frappe.get_doc("Lead", i.name)
				print(lead_doc)
				if lead_doc.lead_owner and not frappe.db.exists('User Permission',{'user':lead_doc.lead_owner,'allow':'Lead','for_value':lead_doc.name}):
					role_profile = frappe.get_value('User',lead_doc.lead_owner,'role_profile_name')
					if role_profile not in ['Admin', 'CRM Admin', 'Super Admin']:
						add_user_permission("Lead", lead_doc.name, lead_doc.lead_owner,ignore_permissions=True,is_default=0)
		
				if lead_doc.custom_assigned_to and not frappe.db.exists('User Permission',{'user':lead_doc.custom_assigned_to,'allow':'Lead','for_value':lead_doc.name}):
					role_profile = frappe.get_value('User',lead_doc.custom_assigned_to,'role_profile_name')
					if role_profile not in ['Admin', 'CRM Admin', 'Super Admin']:
						add_user_permission("Lead", lead_doc.name, lead_doc.custom_assigned_to,ignore_permissions=True,is_default=0)

				if lead_doc.custom_allocated_to_manager and not frappe.db.exists('User Permission',{'user':lead_doc.custom_allocated_to_manager,'allow':'Lead','for_value':lead_doc.name}):
					role_profile = frappe.get_value('User',lead_doc.custom_allocated_to_manager,'role_profile_name')
					if role_profile not in ['Admin', 'CRM Admin', 'Super Admin']:
						add_user_permission("Lead", lead_doc.name, lead_doc.custom_allocated_to_manager,ignore_permissions=True,is_default=0)

def user_permission_quotation():
	lead_list = frappe.db.get_all("Quotation", filters={'docstatus':["in", [0, 1]]}, fields=["name"])
	print(lead_list)
	if lead_list:
		for i in lead_list:
			if i.name:
				lead_doc = frappe.get_doc("Quotation", i.name)
				print(lead_doc)
				if lead_doc.custom_quotation_owner and not frappe.db.exists('User Permission',{'user':lead_doc.custom_quotation_owner,'allow':'Quotation','for_value':lead_doc.name}):
					role_profile = frappe.get_value('User',lead_doc.custom_quotation_owner,'role_profile_name')
					if role_profile not in ['Admin','CRM Admin']:
						add_user_permission("Quotation", lead_doc.name, lead_doc.custom_quotation_owner,ignore_permissions=True,is_default=0)
		
				if lead_doc.custom_assigned_to and not frappe.db.exists('User Permission',{'user':lead_doc.custom_assigned_to,'allow':'Quotation','for_value':lead_doc.name}):
					role_profile = frappe.get_value('User',lead_doc.custom_assigned_to,'role_profile_name')
					if role_profile not in ['Admin','CRM Admin']:
						add_user_permission("Quotation", lead_doc.name, lead_doc.custom_assigned_to,ignore_permissions=True,is_default=0)
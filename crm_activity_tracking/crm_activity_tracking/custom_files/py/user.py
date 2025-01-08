import frappe
def create_user_permission(doc,event):
    if not doc.get('__islocal') or event == 'after_insert':
        if doc.role_profile_name not in ['Regional Admin', 'Admin', 'CRM Admin']:
            if not frappe.db.exists('User Permission',{'allow':'Quotation','user':doc.name,'for_value':''}):
                new_doc = frappe.new_doc("User Permission")

                new_doc.user = doc.name
                new_doc.allow = 'Quotation'
                new_doc.for_value = ''

                new_doc.flags.ignore_mandatory = True
                new_doc.save()
            if not frappe.db.exists('User Permission',{'allow':'Lead','user':doc.name,'for_value':''}):
                new_doc = frappe.new_doc("User Permission")

                new_doc.user = doc.name
                new_doc.allow = 'Lead'
                new_doc.for_value = ''

                new_doc.flags.ignore_mandatory = True
                new_doc.save()
            if not frappe.db.exists('User Permission',{'allow':'Sales and Service Details','user':doc.name,'for_value':''}):
                new_doc = frappe.new_doc("User Permission")

                new_doc.user = doc.name
                new_doc.allow = 'Sales and Service Details'
                new_doc.for_value = ''

                new_doc.flags.ignore_mandatory = True
                new_doc.save()
            if not frappe.db.exists('User Permission',{'allow':'Refilling Report No','user':doc.name,'for_value':''}):
                new_doc = frappe.new_doc("User Permission")

                new_doc.user = doc.name
                new_doc.allow = 'Refilling Report No'
                new_doc.for_value = ''

                new_doc.flags.ignore_mandatory = True
                new_doc.save()
        else:
            exists = frappe.get_all("User Permission", filters = {"user": doc.name, "allow": 'Quotation'}, fields = ["name"], pluck = "name")
            for exist in exists:
                if frappe.db.exists("User Permission", exist):
                    frappe.delete_doc("User Permission", exist, delete_permanently = True)
            exists_lead = frappe.get_all("User Permission", filters = {"user": doc.name, "allow": 'Lead'}, fields = ["name"], pluck = "name")
            for exist_l in exists_lead:
                if frappe.db.exists("User Permission", exist_l):
                    frappe.delete_doc("User Permission", exist_l, delete_permanently = True)
            exists_salesservice = frappe.get_all("User Permission", filters = {"user": doc.name, "allow": 'Sales and Service Details'}, fields = ["name"], pluck = "name")
            for exist_ss in exists_salesservice:
                if frappe.db.exists("User Permission", exist_ss):
                    frappe.delete_doc("User Permission", exist_ss, delete_permanently = True)
            exists_refillingreport = frappe.get_all("User Permission", filters = {"user": doc.name, "allow": 'Refilling Report No'}, fields = ["name"], pluck = "name")
            for exist_rr in exists_refillingreport:
                if frappe.db.exists("User Permission", exist_ss):
                    frappe.delete_doc("User Permission", exist_ss, delete_permanently = True)

# def user_lead_permission():
#     crmprofile = frappe.db.get_all("User", filters={"role_profile_name": ["not in", ['Regional Admin', 'Admin', 'CRM Admin']]}, fields=["name"])
#     if crmprofile:
#         for crm in crmprofile:
#             if not frappe.db.exists('User Permission',{'allow':'Refilling Report No','user':crm.name,'for_value':''}):
#                 new_doc = frappe.new_doc("User Permission")

#                 new_doc.user = crm.name
#                 new_doc.allow = 'Refilling Report No'
#                 new_doc.for_value = ''

#                 new_doc.flags.ignore_mandatory = True
#                 new_doc.save()
#             if not frappe.db.exists('User Permission',{'allow':'Sales and Service Details','user':crm.name,'for_value':''}):
#                 new_doc = frappe.new_doc("User Permission")

#                 new_doc.user = crm.name
#                 new_doc.allow = 'Sales and Service Details'
#                 new_doc.for_value = ''

#                 new_doc.flags.ignore_mandatory = True
#                 new_doc.save()

# from crm_activity_tracking.crm_activity_tracking.custom_files.py.user import user_lead_permission           

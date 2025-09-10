import frappe

def manage_user_permissions(doc, event):
    # Skip if the document is new or on the 'after_insert' event
    if not doc.get('__islocal') or event == 'after_insert':
        # Define role restrictions
        restricted_roles = ['Admin', 'CRM Admin', 'Super Admin']
        regional_admin_only = ['Regional Admin']
        extended_restricted_roles = restricted_roles + regional_admin_only

        def create_user_permission(user, doctype):
            """Helper to create a new User Permission."""
            if not frappe.db.exists('User Permission', {'allow': doctype, 'user': user, 'for_value': ''}):
                new_doc = frappe.new_doc("User Permission")
                new_doc.user = user
                new_doc.allow = doctype
                new_doc.for_value = ''
                new_doc.flags.ignore_mandatory = True
                new_doc.save()

        def delete_user_permissions(user, doctype):
            """Helper to delete existing User Permissions."""
            existing_permissions = frappe.get_all(
                "User Permission",
                filters={"user": user, "allow": doctype},
                fields=["name"],
                pluck="name"
            )
            for permission in existing_permissions:
                frappe.delete_doc("User Permission", permission, delete_permanently=True)

        # Manage permissions for Quotation and Lead
        if doc.role_profile_name not in restricted_roles:
            create_user_permission(doc.name, 'Quotation')
            create_user_permission(doc.name, 'Lead')
            create_user_permission(doc.name, 'Project')
        else:
            delete_user_permissions(doc.name, 'Quotation')
            delete_user_permissions(doc.name, 'Lead')
            delete_user_permissions(doc.name, 'Project')

        # Manage permissions for Refilling Report No and Sales and Service Details
        if doc.role_profile_name not in extended_restricted_roles:
            create_user_permission(doc.name, 'Sales and Service Details')
            create_user_permission(doc.name, 'Refilling Report No')
        else:
            delete_user_permissions(doc.name, 'Sales and Service Details')
            delete_user_permissions(doc.name, 'Refilling Report No')

        # Task User Permision
        if doc.role_profile_name not in ['Admin', 'Super Admin', 'Regional Admin']:
            create_user_permission(doc.name, "Task")
        else:
            delete_user_permissions(doc.name, 'Task')



def user_lead_permission():
    crmprofile = frappe.db.get_all("User", filters={"role_profile_name": ["not in", ['Admin', 'CRM Admin', 'Super Admin']]}, fields=["name"])
    if crmprofile:
        for crm in crmprofile:
            if not frappe.db.exists('User Permission', {'allow': 'Refilling Report No', 'user': crm.name, 'for_value': ''}):
                new_doc = frappe.new_doc("User Permission")
                new_doc.user = crm.name
                new_doc.allow = 'Refilling Report No'
                new_doc.for_value = ''
                new_doc.flags.ignore_mandatory = True
                new_doc.save()

            if not frappe.db.exists('User Permission', {'allow': 'Sales and Service Details', 'user': crm.name, 'for_value': ''}):
                new_doc = frappe.new_doc("User Permission")
                new_doc.user = crm.name
                new_doc.allow = 'Sales and Service Details'
                new_doc.for_value = ''
                new_doc.flags.ignore_mandatory = True
                new_doc.save()

            if not frappe.db.exists('User Permission', {'allow': 'Quotation', 'user': crm.name, 'for_value': ''}):
                new_doc = frappe.new_doc("User Permission")
                new_doc.user = crm.name
                new_doc.allow = 'Quotation'
                new_doc.for_value = ''
                new_doc.flags.ignore_mandatory = True
                new_doc.save()

            if not frappe.db.exists('User Permission', {'allow': 'Lead', 'user': crm.name, 'for_value': ''}):
                new_doc = frappe.new_doc("User Permission")
                new_doc.user = crm.name
                new_doc.allow = 'Lead'
                new_doc.for_value = ''
                new_doc.flags.ignore_mandatory = True
                new_doc.save()

def user_project_permission():
    crmprofile = frappe.db.get_all("User", filters={"role_profile_name": ["not in", ['Admin', 'CRM Admin', 'Super Admin']]}, fields=["name"])
    if crmprofile:
        for crm in crmprofile:
            if not frappe.db.exists('User Permission', {'allow': 'Project', 'user': crm.name, 'for_value': ''}):
                new_doc = frappe.new_doc("User Permission")
                new_doc.user = crm.name
                new_doc.allow = 'Project'
                new_doc.for_value = ''
                new_doc.flags.ignore_mandatory = True
                new_doc.save()

def user_task_permission():
    crmprofile = frappe.db.get_all("User", filters={"role_profile_name": ["not in", ['Admin', 'Super Admin']]}, fields=["name"])
    if crmprofile:
        for crm in crmprofile:
            if not frappe.db.exists('User Permission', {'allow': 'Task', 'user': crm.name, 'for_value': ''}):
                new_doc = frappe.new_doc("User Permission")
                new_doc.user = crm.name
                new_doc.allow = 'Task'
                new_doc.for_value = ''
                new_doc.flags.ignore_mandatory = True
                new_doc.save()
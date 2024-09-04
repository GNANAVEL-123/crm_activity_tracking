# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

def execute(filters = None):

    columns = get_columns(filters)

    data = get_data(filters)

    return columns, data

def get_columns(filters):

    columns = [

        {
            'fieldname': 'lead_quotation_id',
            'fieldtype': 'Data',
            'label': 'ID',
            'width': 200
        },

        {
            'fieldname': 'lead_name',
            'fieldtype': 'Data',
            'label': 'Name',
            'width': 200
        },
  
        {
            'fieldname': 'organization_name',
            'fieldtype': 'Data',
            'label': 'Organization Name',
            'width': 200
        },

        {
            'fieldname': 'lead_owner',
            'fieldtype': 'Data',
            'label': 'Owner',
            'width': 200
        },

        {
            'fieldname': 'territory',
            'fieldtype': 'Link',
            'label': 'Territory',
            'options': 'Territory',
            'width': 182,
            'hidden': 1
        },

        {
            'fieldname': 'status',
            'fieldtype': 'Data',
            'label': 'Status',
            'width': 182
        },

        {
            'fieldname': 'contact_number',
            'fieldtype': 'Data',
            'label': 'Contact Number',
            'width': 182
        },

        {
            'fieldname': 'remarks',
            'fieldtype': 'Data',
            'label': 'Remarks',
            'width': 400
        },

        {
            'fieldname':'description',
            'fieldtype':'Small Text',
            'label':'Description',
            'width':400
        },

        {
            'fieldname': 'for_number_card',
            'fieldtype': 'Int',
            'label': 'For Number Card',
            'hidden': 1,
        },
    ]

    return columns

def get_data(filters):

    if filters.get('user'):

        filter_user = filters.get('user')

        filters["user"] = frappe.get_value("User", {"username": filter_user}, "name")

    follow_condition = ""

    data1 = []
    data2 = []

    if filters.get('lead'):

        if filters.get('user'):

            follow_condition = f"""AND (
                SELECT follow.next_follow_up_by
                FROM `tabFollow-Up` AS follow
                WHERE follow.parent = lead.name
                ORDER BY follow.idx DESC
                LIMIT 1
            ) = '{filters.get('user')}'"""

        data1 += frappe.db.sql(f'''
        SELECT
            1 as for_number_card,
            lead.name AS lead_quotation_id,
            lead.lead_name AS lead_name,
            lead.lead_owner AS lead_owner,
            lead.status AS status,
            lead.custom_remarks AS remarks,
            lead.company_name AS organization_name,
            (
                SELECT follow.description
                FROM `tabFollow-Up` AS follow
                WHERE follow.parent = lead.name
                ORDER BY follow.idx DESC
                LIMIT 1
            ) AS description,
            (
                SELECT contact.mobile_no
                FROM `tabContact` AS contact
                INNER JOIN `tabDynamic Link` AS dynamiclink ON contact.name = dynamiclink.parent
                WHERE dynamiclink.link_name = lead.name
                AND dynamiclink.link_doctype = 'Lead'
                ORDER BY contact.creation DESC
                LIMIT 1
            ) AS contact_number
        FROM `tabLead` AS lead
        WHERE lead.status NOT IN ("Quotation Created", "Do Not Disturb")
            AND (
                SELECT MAX(follow.next_follow_up_date)
                FROM `tabFollow-Up` AS follow
                WHERE follow.parent = lead.name
            ) <= '{filters.get("date")}'
            {follow_condition}
        ''', as_dict = 1)
        for i in data1:
            i['lead_owner'] = frappe.get_value("User", {"name": i['lead_owner']}, "username")
            i['lead_quotation_id'] = f'''
            <a href="#" style="text-decoration: underline; color: #007bff; font-size: 13px;" onclick='frappe.set_route("Form", "Lead", "{i["lead_quotation_id"]}")'>
                {i["lead_quotation_id"]}
            </a>
            '''

        

    if filters.get('quotation'):

        if filters.get('user'):

            follow_condition = f"""AND (
                SELECT follow.next_follow_up_by
                FROM `tabFollow-Up` AS follow
                WHERE follow.parent = quotation.name
                ORDER BY follow.idx DESC
                LIMIT 1
            ) = '{filters.get('user')}'"""

        data2 = frappe.db.sql(f'''
        SELECT
            1 as for_number_card,
            quotation.name AS lead_quotation_id,
            quotation.customer_name AS lead_name,
            quotation.custom_quotation_owner AS lead_owner,
            REPLACE(quotation.custom_ts_contact_number, '-', '')  as contact_number,
            quotation.status AS status,
            (
                SELECT follow.description
                FROM `tabFollow-Up` AS follow
                WHERE follow.parent = quotation.name
                ORDER BY follow.idx DESC
                LIMIT 1
            ) AS description
        FROM `tabQuotation` AS quotation
        WHERE quotation.status NOT IN ("Ordered", "Lost", "Cancelled") 
            AND (
                SELECT MAX(follow.next_follow_up_date)
                FROM `tabFollow-Up` AS follow
                WHERE follow.parent = quotation.name
            ) <= '{filters.get("date")}'
            {follow_condition}
        ''', as_dict = 1)
        for i in data2:
            i['lead_owner'] = frappe.get_value("User", {"name": i['lead_owner']}, "username")
            i['lead_quotation_id'] = f'''
            <a href="#" style="text-decoration: underline; color: #007bff; font-size: 13px;" onclick='frappe.set_route("Form", "Quotation", "{i["lead_quotation_id"]}")'>
                {i["lead_quotation_id"]}
            </a>
            '''

    data=data1+data2
    return data

@frappe.whitelist()
def get_user_list(user):
    user_list = frappe.get_list("User", {"enabled": 1}, ["username"], pluck = "username")

    return user_list
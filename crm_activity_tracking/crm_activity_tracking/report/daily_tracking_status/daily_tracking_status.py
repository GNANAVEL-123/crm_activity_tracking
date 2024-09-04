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
            'fieldname': 'name',
            'fieldtype': 'Data',
            'label': 'ID',
            'width': 195
        },
        
        {
            'fieldname': 'date',
            'fieldtype': 'Date',
            'label': 'Date',
            'width': 120
        },

        {
            'fieldname': 'lead_name',
            'fieldtype': 'Data',
            'label': 'Name',
            'width': 195
        },

        {
            'fieldname': 'lead_owner',
            'fieldtype': 'Data',
            'label': 'Owner',
            'width': 195
        },
        
        {
            'fieldname': 'organization_name',
            'fieldtype': 'Data',
            'label': 'Organization Name',
            'width': 200
        },

        # {
        # 	'fieldname': 'territory',
        # 	'fieldtype': 'Link',
        # 	'label': 'Territory',
        # 	'options': 'Territory',
        # 	'width': 182
        # },

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
        
        {
            'fieldname': 'map',
            'fieldtype': 'Data',
            'label': 'View Map'
        },
    ]

    return columns

def get_data(filters):
    data=[]
    if (filters.get('lead')):
        follow_up_filter = {}
        lead_filter = {'status':['not in', ['Do Not Contact']]}
        if(filters.get('from_date')) and (filters.get('to_date')) :
            follow_up_filter['date'] = ["between", [ filters.get('from_date'), filters.get('to_date')]]
        if (filters.get('user')):
            follow_up_filter['followed_by'] = filters.get('user')

        all_leads = frappe.db.get_all('Follow-Up', filters=follow_up_filter, fields=['idx', 'parent','followed_by','description', "longitude", "latitude", "date"])
        all_leads1=[]
        for i in all_leads:
            follow_up_filter['parent'] = i['parent']
            
            if(max(frappe.db.get_all('Follow-Up', filters={'parent':i['parent']}, pluck='idx')) == i['idx']):
                if(not i.get("followed_by")):
                    all_leads1.append(i)
                elif(not filters.get("user")):
                    all_leads1.append(i)
                elif(filters.get("user") and i.get("followed_by")==filters.get("user")):
                    all_leads1.append(i)
        desc={i['parent']:[i['description'],i.get("followed_by")  or "",i.get("longitude"),i.get("latitude"), i.get('date')] for i in all_leads1}

        leads = [i['parent'] for i in all_leads1]
        site_lead=leads
        lead_filter['name'] = ['in', site_lead]

        leads = frappe.db.get_all('Lead', filters=lead_filter, fields=['name', 'lead_name', 'lead_owner','status', 'custom_remarks as remarks', 'company_name as organization_name'])

        for i in leads:
            i["for_number_card"] = 1
            i['description']=desc[i["name"]][0]
            i['next_followup_by']=desc[i["name"]][1]
            i['date'] = desc[i["name"]][4]
            
            long = desc[i["name"]][2]
            lat = desc[i["name"]][3]
            
            if long and lat:
                i['map'] = f'''<button style=" font-size: 13px;  background-color: #000000;color: #ffffff;border-radius: 5px; height: 24px;" onclick='window.open(`https://www.google.com/maps/search/?api=1&query={lat},{long}`)'>
                View Map
                </button>'''
                
            else:
                i['map'] = f'''<button style=" font-size: 13px;  background-color: #000000;color: #ffffff;border-radius: 5px; height: 24px;">
                No Record
                </button>'''
            
            contact=frappe.get_all(
                "Contact",
                    filters=[
                    ["Dynamic Link", "link_doctype", "=", 'Lead'],
                    ["Dynamic Link", "link_name", "=", i['name']],
                    ["Contact Phone", 'is_primary_mobile_no', "=", 1]

                    ],
                    fields=['`tabContact Phone`.phone'],
                    order_by='`tabContact`.creation desc'
                )
            if contact:
                i['contact_number']=contact[0]['phone']
                            
            i["name"] = f'''
            <a href="#" style="text-decoration: underline; color: #007bff; font-size: 13px;" onclick="frappe.set_route('Form', 'Lead', '{i["name"]}')">
                {i["name"]}
            </a>
            '''


            
            i['lead_owner'] = frappe.get_value("User", {"name": i['lead_owner']}, "username")
        
        data+=leads
        
    if (filters.get('quotation')):
        follow_up_filter = {}
        lead_filter={}
        lead_filter = {'docstatus':['not in', [2]]}
        if(filters.get('from_date')) and (filters.get('to_date')) :
            follow_up_filter['date'] = ["between", [ filters.get('from_date'), filters.get('to_date')]]
        if (filters.get('user')):
            follow_up_filter['followed_by'] = filters.get('user')

        all_leads = frappe.db.get_all('Follow-Up', filters=follow_up_filter, fields=['idx', 'parent','followed_by','description', "longitude", "latitude", "date"])
        all_leads1=[]
        for i in all_leads:
            follow_up_filter['parent'] = i['parent']
            
            if(max(frappe.db.get_all('Follow-Up', filters={'parent':i['parent']}, pluck='idx')) == i['idx']):
                if(not i.get("followed_by")):
                    all_leads1.append(i)
                elif(not filters.get("user")):
                    all_leads1.append(i)
                elif(filters.get("user") and i.get("followed_by")==filters.get("user")):
                    all_leads1.append(i)
        desc={i['parent']:[i['description'],i.get("followed_by") or "",i.get("longitude"),i.get("latitude"), i.get('date')] for i in all_leads1}


        leads = [i['parent'] for i in all_leads1]
        site_lead=leads
        lead_filter['name'] = ['in', site_lead]

        leads = frappe.db.get_all('Quotation', filters=lead_filter, fields=['name', 'customer_name as lead_name', 'custom_quotation_owner as lead_owner','status','custom_ts_contact_number as contact_number'])

        for i in leads:
            i["for_number_card"] = 1
            i['description']=desc[i["name"]][0]
            i['next_followup_by']=desc[i["name"]][1]
            i['date'] = desc[i["name"]][4]
            
            long = desc[i["name"]][2]
            lat = desc[i["name"]][3]
            
            if long and lat:
                    i['map'] = f'''<button style=" font-size: 13px;  background-color: #000000;color: #ffffff;border-radius: 5px; height: 24px;" onclick='window.open(`https://www.google.com/maps/search/?api=1&query={lat},{long}`)'>
                    View Map
                    </button>'''
                    
            else:
                i['map'] = f'''<button style=" font-size: 13px;  background-color: #000000;color: #ffffff;border-radius: 5px; height: 24px;">
                No Record
                </button>'''

            contact=frappe.get_all(
                "Contact",
                    filters=[
                    ["Dynamic Link", "link_doctype", "=", 'Quotation'],
                    ["Dynamic Link", "link_name", "=", i['name']],
                    ["Contact Phone", 'is_primary_mobile_no', "=", 1]

                    ],
                    fields=['`tabContact Phone`.phone'],
                    order_by='`tabContact`.creation desc'
                )
            if contact:
                i['contact_number']=contact[0]['phone']
                
            i['name'] = f'''
            <a href="#" style="text-decoration: underline; color: #007bff; font-size: 13px;" onclick='frappe.set_route("Form", "Quotation", "{i["name"]}")'>
                {i["name"]}
            </a>
            '''

            
            i['lead_owner'] = frappe.get_value("User", {"name": i['lead_owner']}, "username")
            
        data+=leads
    
    return data
    
    
import frappe
from frappe import _

@frappe.whitelist()
def get_crm_settings():
    crm_settings = frappe.get_single('CRM Settings')
    return {
        'show_quotation_filter': crm_settings.quotation_followup
    }
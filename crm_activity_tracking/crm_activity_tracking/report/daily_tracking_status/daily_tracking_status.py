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
			'fieldname':'custom_enter_datetime',
			'fieldtype':'Datetime',
			'label':'Description Entertime',
			'width':200
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
        follow_up_filter['parenttype'] = 'Lead'
        if(filters.get('from_date')) and (filters.get('to_date')) :
            follow_up_filter['date'] = ["between", [ filters.get('from_date'), filters.get('to_date')]]
        if (filters.get('user')):
            follow_up_filter['followed_by'] = filters.get('user')

        all_leads = frappe.db.get_all('Follow-Up', filters=follow_up_filter, fields=['idx', 'parent','followed_by','description', "longitude", "latitude", "date", "custom_enter_datetime"])
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
        desc={i['parent']:[i['description'],i.get("followed_by")  or "",i.get("longitude"),i.get("latitude"), i.get('date'),  i.get('custom_enter_datetime') ] for i in all_leads1}

        leads = [i['parent'] for i in all_leads1]
        site_lead=leads
        lead_filter['name'] = ['in', site_lead]

        leads = frappe.db.get_all('Lead', filters=lead_filter, fields=['name', 'lead_name', 'lead_owner','status', 'custom_remarks as remarks', 'company_name as organization_name'])

        for i in leads:
            i["for_number_card"] = 1
            i['description']=desc[i["name"]][0]
            i['next_followup_by']=desc[i["name"]][1]
            i['date'] = desc[i["name"]][4]
            i['custom_enter_datetime'] = desc[i["name"]][5]
            
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
        lead_filter = {'docstatus': ['not in', [2]]}

        # ✅ Mandatory filter
        follow_up_filter['parenttype'] = 'Quotation'

        # ✅ Date filter (correct place)
        if filters.get('from_date') and filters.get('to_date'):
            follow_up_filter['date'] = ["between", [filters.get('from_date'), filters.get('to_date')]]

        # ✅ User filter
        if filters.get('user'):
            follow_up_filter['followed_by'] = filters.get('user')

        # ✅ Get all followups (sorted)
        all_leads = frappe.db.get_all(
            'Follow-Up',
            filters=follow_up_filter,
            fields=[
                'parent', 'followed_by', 'description',
                'longitude', 'latitude', 'date', 'custom_enter_datetime'
            ],
            order_by="parent asc, custom_enter_datetime desc, date desc"
        )

        # ✅ STEP 1: Group by parent
        grouped = {}
        for i in all_leads:
            grouped.setdefault(i['parent'], []).append(i)

        # ✅ STEP 2: Pick best row per parent
        all_leads1 = []

        for parent, rows in grouped.items():
            best_row = None

            for row in rows:
                current_time = row.get('custom_enter_datetime') or row.get('date')

                if not current_time:
                    continue

                if isinstance(current_time, str):
                    current_time = frappe.utils.get_datetime(current_time)

                if not best_row:
                    best_row = row
                    continue

                best_time = best_row.get('custom_enter_datetime') or best_row.get('date')

                if isinstance(best_time, str):
                    best_time = frappe.utils.get_datetime(best_time)

                # ✅ PRIORITY 1: Prefer description
                if row.get("description") and not best_row.get("description"):
                    best_row = row

                # ✅ PRIORITY 2: Both have description → latest
                elif row.get("description") and best_row.get("description"):
                    if current_time > best_time:
                        best_row = row

                # ✅ PRIORITY 3: Both empty → latest
                elif not row.get("description") and not best_row.get("description"):
                    if current_time > best_time:
                        best_row = row

            if best_row:
                all_leads1.append(best_row)

        # ✅ STEP 3: Prepare desc map
        desc = {
            i['parent']: [
                i.get('description') or "",
                i.get("followed_by") or "",
                i.get("longitude"),
                i.get("latitude"),
                i.get('date'),
                i.get('custom_enter_datetime')
            ]
            for i in all_leads1
        }

        # ✅ STEP 4: Get quotations
        leads = [i['parent'] for i in all_leads1]

        if not leads:
            return data

        lead_filter['name'] = ['in', leads]

        leads = frappe.db.get_all(
            'Quotation',
            filters=lead_filter,
            fields=[
                'name',
                'customer_name as lead_name',
                'custom_quotation_owner as lead_owner',
                'status',
                'custom_ts_contact_number as contact_number'
            ]
        )

        # ✅ STEP 5: Final data preparation
        for i in leads:

            if i["name"] not in desc:
                continue

            i["for_number_card"] = 1
            i['description'] = desc[i["name"]][0]
            i['next_followup_by'] = desc[i["name"]][1]
            i['date'] = desc[i["name"]][4]
            i['custom_enter_datetime'] = desc[i["name"]][5]

            long = desc[i["name"]][2]
            lat = desc[i["name"]][3]

            # ✅ Map button
            if long and lat:
                i['map'] = f'''
                <button style="font-size:13px;background:#000;color:#fff;border-radius:5px;height:24px;"
                onclick='window.open(`https://www.google.com/maps/search/?api=1&query={lat},{long}`)'>
                View Map
                </button>
                '''
            else:
                i['map'] = '''
                <button style="font-size:13px;background:#000;color:#fff;border-radius:5px;height:24px;">
                No Record
                </button>
                '''

            # ✅ Contact fetch
            contact = frappe.get_all(
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
                i['contact_number'] = contact[0]['phone']

            # ✅ Link formatting
            i['name'] = f'''
            <a href="#" style="text-decoration:underline;color:#007bff;font-size:13px;"
            onclick='frappe.set_route("Form","Quotation","{i["name"]}")'>
            {i["name"]}
            </a>
            '''

            # ✅ Owner name
            i['lead_owner'] = frappe.get_value("User", i['lead_owner'], "username")

        data += leads
    
    return data
    
    
import frappe
from frappe import _

@frappe.whitelist()
def get_crm_settings():
    crm_settings = frappe.get_single('CRM Settings')
    return {
        'show_quotation_filter': crm_settings.quotation_followup
    }
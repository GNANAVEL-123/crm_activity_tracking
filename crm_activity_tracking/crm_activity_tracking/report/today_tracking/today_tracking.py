# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe.desk.reportview import get_filters_cond, get_match_cond
from frappe.utils.data import nowdate, getdate

def execute(filters = None):

	columns = get_columns(filters)

	data = get_data(filters)

	return columns, data

def get_columns(filters):

	columns = [
		{
			'fieldname': 'company_name',
			'fieldtype': 'Data',
			'label': 'Company Name',
			'width': 195,
			'hidden':0
		},
		{
			'fieldname': 'lead_name',
			'fieldtype': 'Data',
			'label': 'Name',
			'width': 195
		},

		{
			'fieldname': 'name',
			'fieldtype': 'Data',
			'label': 'ID',
			'width': 195
		},

		
		

		{
			'fieldname': 'lead_owner',
			'fieldtype': 'Data',
			'label': 'Owner',
			'width': 195,
			'hidden':1
		},
		{
			'fieldname': 'contact_name',
			'fieldtype': 'Data',
			'label': 'Contact Name',
			'width': 182
		},

		{
			'fieldname': 'contact_number',
			'fieldtype': 'Data',
			'label': 'Contact Number',
			'width': 182
		},
		{
			'fieldname': 'customer_mail',
			'fieldtype': 'Data',
			'label': 'Customer Mail',
			'width': 195
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
			'width': 182,
			'hidden': 1
		},
		
		{
			'fieldname': 'mode_of_communication',
			'fieldtype': 'Data',
			'label': 'Mode of Communication',
			'width': 195,
			'hidden':1
		},
		{
			'fieldname':'description',
			'fieldtype':'Small Text',
			'label':'Description',
			'width':400
		},

		{
			'fieldname': 'remarks',
			'fieldtype': 'Data',
			'label': 'Remarks',
			'width': 400
		},
	]

	return columns

def get_data(filters):
	# if filters.get('user'):

	# 	filter_user = filters.get('user')

	# 	filters["user"] = frappe.get_value("User", {"username": filter_user}, "name")

	data=[]
	if (filters.get('lead')):
		follow_up_filter = {}
		lead_filter = {'status':['not in', ['Do Not Contact', 'Quotation', 'Converted']]}
		if(filters.get('date')):
			follow_up_filter['next_follow_up_date'] = filters.get('date')
		if (filters.get('user')):
			follow_up_filter['next_follow_up_by'] = filters.get('user')

		all_leads = frappe.db.get_all('Follow-Up', filters=follow_up_filter, fields=['idx', 'parent','next_follow_up_by','description', 'mode_of_communication'])
		all_leads1=[]
		for i in all_leads:
			follow_up_filter['parent'] = i['parent']			
			if(max(frappe.db.get_all('Follow-Up', filters={'parent':i['parent']}, pluck='idx')) == i['idx']):
				if(not i.get("next_follow_up_by")):
					all_leads1.append(i)
				elif(not filters.get("user")):
					all_leads1.append(i)
				elif(filters.get("user") and i.get("next_follow_up_by")==filters.get("user")):
					all_leads1.append(i)
		desc={i['parent']:[i['description'],i.get("next_follow_up_by") or "", i.get("mode_of_communication") or ""] for i in all_leads1}


		leads = [i['parent'] for i in all_leads1]
		site_lead=leads
		lead_filter['name'] = ['in', site_lead]
		leads = frappe.db.get_list('Lead', filters=lead_filter, fields=['name', 'lead_name', 'lead_owner','status', 'custom_remarks as remarks', 'customer as company_name'])

		for i in leads:
			i['description']=desc[i["name"]][0]
			i['next_followup_by']=desc[i["name"]][1]
			i['mode_of_communication']=desc[i["name"]][2]

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
			address_email=frappe.get_all(
				"Address",
					filters=[
					["Dynamic Link", "link_doctype", "=", 'Lead'],
					["Dynamic Link", "link_name", "=", i['name']],
					],
					fields=['email_id'],
					order_by='`tabAddress`.creation desc'
				)
			if address_email:
				i['customer_mail']=address_email[0]['email_id']
			i['name'] = f'''
			<a href="#" style="text-decoration: underline; color: #007bff; font-size: 13px;" onclick='frappe.set_route("Form", "Lead", "{i["name"]}")'>
				{i["name"]}
			</a>
			'''

   
		data+=leads
		
	if (filters.get('quotation')):
		follow_up_filter = {}
		lead_filter={'docstatus':['not in', [2]], 'status':['not in', ['Ordered', 'Lost', 'Cancelled', 'Order Cancelled']]}

		if(filters.get('date')):
			follow_up_filter['next_follow_up_date'] = filters.get('date')
		if (filters.get('user')):
			follow_up_filter['next_follow_up_by'] = filters.get('user')

		all_leads = frappe.db.get_all('Follow-Up', filters=follow_up_filter, fields=['idx', 'parent','next_follow_up_by','description','mode_of_communication'])
		all_leads1=[]
		for i in all_leads:
			follow_up_filter['parent'] = i['parent']
			
			if(max(frappe.db.get_all('Follow-Up', filters={'parent':i['parent']}, pluck='idx')) == i['idx']):
				if(not i.get("next_follow_up_by")):
					all_leads1.append(i)
				elif(not filters.get("user")):
					all_leads1.append(i)
				elif(filters.get("user") and i.get("next_follow_up_by")==filters.get("user")):
					all_leads1.append(i)
		desc={i['parent']:[i['description'],i.get("next_follow_up_by") or "",i.get("mode_of_communication") or ""] for i in all_leads1}


		leads = [i['parent'] for i in all_leads1]
		site_lead=leads
		lead_filter['name'] = ['in', site_lead]

		leads = frappe.db.get_list('Quotation', filters=lead_filter, fields=['name', 'customer_name as lead_name', 'custom_quotation_owner as lead_owner','status', 'custom_phone as contact_number', 'custom_kind_attn as contact_name', 'company_name', 'customer_address'])

		for i in leads:
			i['description']=desc[i["name"]][0]
			i['next_followup_by']=desc[i["name"]][1]
			i['mode_of_communication']=desc[i["name"]][2]
			
			if i.customer_address:
				address_email=frappe.db.get_all(
					"Address",
						filters={"name":i.customer_address},
						fields=['email_id'],
						order_by='`tabAddress`.creation desc'
					)
				if address_email:
					i['customer_mail']=address_email[0]['email_id']
			# contact=frappe.get_all(
			# 	"Contact",
			# 		filters=[
			# 		["Dynamic Link", "link_doctype", "=", 'Quotation'],
			# 		["Dynamic Link", "link_name", "=", i['name']],
			# 		["Contact Phone", 'is_primary_mobile_no', "=", 1]

			# 		],
			# 		fields=['`tabContact Phone`.phone'],
			# 		order_by='`tabContact`.creation desc'
			# 	)
			# if contact:
			# 	i['contact_number']=contact[0]['phone']

			i['name'] = f'''
			<a href="#" style="text-decoration: underline; color: #007bff; font-size: 13px;" onclick='frappe.set_route("Form", "Quotation", "{i["name"]}")'>
				{i["name"]}
			</a>
			'''

   
		data+=leads

	return data
	
@frappe.whitelist()
def get_user_list(user):
	user_list = frappe.get_list("User", {"enabled": 1}, ["username"], pluck = "username")

	return user_list

# @frappe.whitelist()
# def get_users_list(user, date):
#     user_list = set()
#     if date:
#         all_quotation = frappe.db.get_all(
#             'Follow-Up',
#             filters={'parenttype': "Quotation", 'next_follow_up_date': date},
#             fields=['next_follow_up_by']
#         )
#         all_lead = frappe.db.get_all(
#             'Follow-Up',
#             filters={'parenttype': "Lead", 'next_follow_up_date': date},
#             fields=['next_follow_up_by']
#         )
#         user_list.update(entry['next_follow_up_by'] for entry in all_quotation if entry['next_follow_up_by'])
#         user_list.update(entry['next_follow_up_by'] for entry in all_lead if entry['next_follow_up_by'])
#     return list(user_list)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def user_list(doctype, txt, searchfield, start, page_len, filters, as_dict=False):

	if isinstance(filters, str):
		filters = json.loads(filters)
		
	conditions = []
	date = filters.pop("date")
	user_list = set()
	all_quotation = frappe.db.get_all(
		'Follow-Up',
		filters={'parenttype': "Quotation", 'next_follow_up_date': date},
		fields=['next_follow_up_by']
	)
	all_lead = frappe.db.get_all(
		'Follow-Up',
		filters={'parenttype': "Lead", 'next_follow_up_date': date},
		fields=['next_follow_up_by']
	)
	user_list.update(entry['next_follow_up_by'] for entry in all_quotation if entry['next_follow_up_by'])
	user_list.update(entry['next_follow_up_by'] for entry in all_lead if entry['next_follow_up_by'])
	if len(list(user_list)) == 1:
	    filters['name'] = list(user_list)[0]
	elif len(list(user_list)) > 1:
	    filters['name'] = ['in', list(user_list)]
	else:
	    return [] 
	meta = frappe.get_meta(doctype, cached=True)
	searchfields = meta.get_search_fields()

	columns = ""
	extra_searchfields = [field for field in searchfields if field != "name"]

	if extra_searchfields:
		columns += ", " + ", ".join(extra_searchfields)

	searchfields_cond = " or ".join([f"`tab{doctype}`.{field} like %(txt)s" for field in searchfields])
	return frappe.db.sql(
		f"""
		select `tab{doctype}`.name {columns}
		from `tab{doctype}`
		where 1=1 
			{get_filters_cond(doctype, filters, conditions).replace("%", "%%")}
			and ({searchfields_cond})
		order by
			if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
			idx desc,
			name
		limit %(start)s, %(page_len)s
		""",
		{
			"txt": f"%%{txt}%%",
			"_txt": txt.replace("%", ""),
			"start": start,
			"page_len": page_len,
		},
		as_dict=as_dict,
	)

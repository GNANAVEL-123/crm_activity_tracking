# Copyright (c) 2025, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import date_diff, nowdate


def execute(filters=None):
	columns, data = [], []
	data = get_data(filters)
	columns = get_columns()
	charts = get_chart_data(data)
	return columns, data, None, charts


def get_data(filters):
	conditions = get_conditions(filters)
	tasks = frappe.get_all(
		"Task",
		filters=conditions,
		fields=[
			"name",
			"subject",
			"exp_start_date",
			"exp_end_date",
			"status",
			"priority",
			"completed_on",
			"progress",
			"custom_customer",
			"custom_contact_no",
			"custom_region"
		],
		order_by="creation",
	)
	for task in tasks:
		if task.exp_end_date:
			if task.completed_on:
				task.delay = date_diff(task.completed_on, task.exp_end_date)
			elif task.status == "Completed":
				# task is completed but completed on is not set (for older tasks)
				task.delay = 0
			else:
				# task not completed
				task.delay = date_diff(nowdate(), task.exp_end_date)
		else:
			# task has no end date, hence no delay
			task.delay = 0

		task.status = _(task.status)
		task.priority = _(task.priority)

	# Sort by descending order of delay
	tasks.sort(key=lambda x: x["delay"], reverse=True)
	return tasks


def get_conditions(filters):
	conditions = frappe._dict()
	keys = ["priority", "status"]
	for key in keys:
		if filters.get(key):
			conditions[key] = filters.get(key)
	if filters.get("from_date"):
		conditions.exp_end_date = [">=", filters.get("from_date")]
	if filters.get("to_date"):
		conditions.exp_start_date = ["<=", filters.get("to_date")]
	return conditions


def get_chart_data(data):
    status_counts = {}

    for entry in data:
        status = entry.get("status", "Unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    charts = {
        "data": {
            "labels": list(status_counts.keys()),  # Task statuses as labels
            "datasets": [{"name": _("Task Count"), "values": list(status_counts.values())}],
        },
        "type": "bar",  # You can change this to "pie" or "percentage" if needed
        "colors": ["#1E90FF", "#28A745", "#DC3545", "#FFC107", "#17A2B8"],  # Adjust colors as needed
    }

    return charts



def get_columns():
	columns = [
		{"fieldname": "name", "fieldtype": "Link", "label": _("Task"), "options": "Task", "width": 150},
		{"fieldname": "subject", "fieldtype": "Data", "label": _("Subject"), "width": 200},
		{"fieldname": "status", "fieldtype": "Data", "label": _("Status"), "width": 100},
		{"fieldname": "priority", "fieldtype": "Data", "label": _("Priority"), "width": 80},
		{
			"fieldname": "exp_start_date",
			"fieldtype": "Date",
			"label": _("Expected Start Date"),
			"width": 150,
		},
		{
			"fieldname": "exp_end_date",
			"fieldtype": "Date",
			"label": _("Expected End Date"),
			"width": 150,
		},
		{"fieldname": "custom_customer", "fieldtype": "Link", "label": _("Company"), "options":"Customer","width": 100},
		{"fieldname": "custom_contact_no", "fieldtype": "Data", "label": _("Contact No"), "width": 100},
		{"fieldname": "custom_region", "fieldtype": "Link", "label": _("Region"), "options":"Territory","width": 100},
	]
	return columns

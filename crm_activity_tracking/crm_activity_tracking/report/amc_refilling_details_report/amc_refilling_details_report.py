# Copyright (c) 2026, CRM and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder.functions import Extract, Trim
from pypika.enums import DatePart

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def execute(filters=None):
	filters = filters or {}
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{"label": _("AMC"), "fieldname": "amc", "fieldtype": "Link", "options": "AMC", "width": 140},
		{"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Link", "options": "Customer", "width": 200},
		{"label": _("Location"), "fieldname": "location", "fieldtype": "Link", "options": "AMC Location", "width": 160},
		{"label": _("Cap"), "fieldname": "cap", "fieldtype": "Data", "width": 100},
		{"label": _("Type"), "fieldname": "type", "fieldtype": "Link", "options": "AMC Type", "width": 140},
		{"label": _("Date of Refilling"), "fieldname": "date_refilling", "fieldtype": "Date", "width": 130},
		{"label": _("Frequency"), "fieldname": "refilling_frequency", "fieldtype": "Float", "width": 100},
		{"label": _("Next Due Date"), "fieldname": "refilling_due_date", "fieldtype": "Date", "width": 130},
		{"label": _("Concern Person"), "fieldname": "concern_person", "fieldtype": "Data", "width": 150},
		{"label": _("Region"), "fieldname": "region", "fieldtype": "Data", "width": 140},
	]


def get_data(filters):
	amc = frappe.qb.DocType("AMC")
	rs = frappe.qb.DocType("Refilling Schedule Table")

	query = (
		frappe.qb.from_(amc)
		.inner_join(rs)
		.on((rs.parent == amc.name) & (rs.parenttype == "AMC") & (rs.parentfield == "refilling_schedule"))
		.select(
			amc.name.as_("amc"),
			amc.customer_name,
			amc.concern_person,
			amc.location.as_("region"),
			rs.location,
			rs.cap,
			rs.type,
			rs.date_refilling,
			rs.refilling_frequency,
			rs.refilling_due_date,
		)
		.where(amc.docstatus < 2)
		.orderby(amc.name)
		.orderby(rs.idx)
	)

	if filters.get("amc"):
		query = query.where(amc.name == filters.amc)
	if filters.get("customer_name"):
		query = query.where(amc.customer_name == filters.customer_name)
	if filters.get("region"):
		query = query.where(Trim(amc.location).like(f"%{filters.region.strip()}%"))
	if filters.get("location"):
		query = query.where(rs.location == filters.location)
	if filters.get("from_date"):
		query = query.where(rs.refilling_due_date >= filters.from_date)
	if filters.get("to_date"):
		query = query.where(rs.refilling_due_date <= filters.to_date)
	if filters.get("year"):
		query = query.where(Extract(DatePart.year, rs.refilling_due_date) == int(filters.year))
	if filters.get("month"):
		query = query.where(Extract(DatePart.month, rs.refilling_due_date) == MONTHS.index(filters.month) + 1)

	return query.run(as_dict=True)

"""Mobile app v2 setup. Safe to re-run; never changes existing records.

* Indexes for the follow-up calendar / missed queries.
* Mobile App Settings defaults, only where a value was never saved.
* A few starter note templates when none exist.
"""

import frappe
from frappe.utils import nowdate

SETTINGS = "Mobile App Settings"

DEFAULTS = {
	"max_reminder_times": 5,
	"new_lead_days": 3,
	# Follow-ups still open from before go-live are history, not "Missed".
	"missed_cutoff_date": nowdate(),
}

TEMPLATES = [
	("Interested", "Interested — call back after 2 days"),
	("Needs quotation", "Needs quotation — share price list"),
	("Site visit", "Site visit required — fix a date"),
	("Not reachable", "Not reachable — try again in the evening"),
	("Budget approved", "Budget approved — send final quotation"),
]


def execute():
	add_indexes()
	set_default_settings()
	add_templates()


def add_indexes():
	frappe.db.add_index("Follow-Up", ["parenttype", "parent", "followed", "next_follow_up_date"], "mobile_open_followups")
	frappe.db.add_index("Follow-Up", ["next_follow_up_by", "next_follow_up_date"], "mobile_assignee_date")


def set_default_settings():
	for field, value in DEFAULTS.items():
		stored = frappe.db.sql(
			"SELECT value FROM `tabSingles` WHERE doctype = %s AND field = %s",
			(SETTINGS, field),
		)
		if stored and stored[0][0] not in (None, ""):
			continue
		frappe.db.set_single_value(SETTINGS, field, value)


def add_templates():
	if not frappe.db.table_exists("Mobile Note Template") or frappe.db.count("Mobile Note Template"):
		return
	for title, text in TEMPLATES:
		frappe.get_doc({
			"doctype": "Mobile Note Template",
			"title": title,
			"text": text,
			"applies_to": "Both",
			"enabled": 1,
		}).insert(ignore_permissions=True)

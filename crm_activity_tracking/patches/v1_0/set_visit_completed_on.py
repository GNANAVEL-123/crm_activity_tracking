"""Backfill AMC Visitor Tracking.completed_on / service_completed_on for
visits completed before these fields existed, using the visit's last
modified time (the closest record of when it was completed). Safe to re-run.
"""

import frappe

DOCTYPE = "AMC Visitor Tracking"


def execute():
	for status_field, stamp_field in (("status", "completed_on"), ("service_status", "service_completed_on")):
		if not frappe.db.has_column(DOCTYPE, stamp_field):
			continue
		frappe.db.sql(
			f"""UPDATE `tab{DOCTYPE}` SET `{stamp_field}` = `modified`
			WHERE `{status_field}` = 'Completed' AND `{stamp_field}` IS NULL"""
		)
	frappe.db.commit()

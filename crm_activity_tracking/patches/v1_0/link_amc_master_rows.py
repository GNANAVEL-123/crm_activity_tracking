"""Backfill Refilling Schedule Table.amc_master_row on AMC rows.

For every AMC linked to an AMC Master, each AMC row without a valid link is
matched to an AMC Master row by QR code, else by location + type + cap.
A match is used only when exactly one unclaimed master row fits, so
duplicate extinguishers are never guessed. Safe to re-run.
"""

import frappe

CHILD = "Refilling Schedule Table"


def execute():
	if not frappe.db.has_column(CHILD, "amc_master_row"):
		return

	linked = unmatched = 0
	for amc in frappe.get_all("AMC", filters={"amc_master": ["is", "set"]}, fields=["name", "amc_master"]):
		master_rows = frappe.get_all(
			CHILD,
			filters={"parent": amc.amc_master, "parenttype": "AMC Master", "parentfield": "refilling_schedule"},
			fields=["name", "qr_code", "location", "type", "cap"],
		)
		master_names = {r.name for r in master_rows}
		amc_rows = frappe.get_all(
			CHILD,
			filters={"parent": amc.name, "parenttype": "AMC", "parentfield": "refilling_schedule"},
			fields=["name", "qr_code", "location", "type", "cap", "amc_master_row"],
			order_by="idx asc",
		)
		claimed = {r.amc_master_row for r in amc_rows if r.amc_master_row in master_names}

		for row in amc_rows:
			if row.amc_master_row in master_names:
				continue
			free = [m for m in master_rows if m.name not in claimed]
			match = None
			if row.qr_code:
				hits = [m for m in free if m.qr_code == row.qr_code]
				match = hits[0] if len(hits) == 1 else None
			if not match and row.location:
				hits = [m for m in free if (m.location, m.type, m.cap) == (row.location, row.type, row.cap)]
				match = hits[0] if len(hits) == 1 else None
			if not match:
				unmatched += 1
				continue
			frappe.db.set_value(CHILD, row.name, "amc_master_row", match.name, update_modified=False)
			claimed.add(match.name)
			linked += 1

	frappe.db.commit()
	print(f"amc_master_row: linked {linked} AMC rows, {unmatched} left unmatched")

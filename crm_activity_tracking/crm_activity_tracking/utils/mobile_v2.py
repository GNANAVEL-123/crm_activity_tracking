"""Mobile app v2 endpoints (lists with counts, follow-up calendar, reminders).

URL: /api/method/crm_activity_tracking.crm_activity_tracking.utils.mobile_v2.<method>
utils/api.py is left unchanged; the released app keeps calling it.

Rules (see the ERPNext plan):
* Backward compatible: the released app (v1.0.11) keeps working. Only new
  parameters change behaviour; response keys are only ever added.
* Lists are scoped with frappe.get_list, so User Permissions apply.
* Reminder actions change one Follow-Up row in place. They do not re-save the
  whole Lead, so old leads with legacy phone formats can still be followed up.
"""

import json
import re

import frappe
from frappe import _
from frappe.utils import add_days, cint, get_datetime, getdate, now_datetime, nowdate

LEAD_TABLE = "custom_view_follow_up_details_copy"
QUOTATION_TABLE = "custom_followup"
CHILD_TABLE = {"Lead": LEAD_TABLE, "Quotation": QUOTATION_TABLE}

CLOSED_LEAD_STATUSES = ("Converted", "Lost Quotation", "Do Not Contact")
LOST_LEAD_STATUSES = ("Lost Quotation", "Do Not Contact")
CLOSED_QUOTATION_STATUSES = ("Ordered", "Lost", "Cancelled")


# --------------------------------------------------------------------- helpers


def _setting(field, default):
	"""Raw Mobile App Settings value; `default` when never saved or blank.
	(get_single_value casts unsaved Int/Check fields to 0.)"""
	row = frappe.db.sql(
		"SELECT value FROM `tabSingles` WHERE doctype = %s AND field = %s",
		("Mobile App Settings", field),
	)
	if not row or row[0][0] in (None, ""):
		return default
	return row[0][0]


def _missed_cutoff():
	value = _setting("missed_cutoff_date", None)
	return getdate(value) if value else None


def _max_times():
	return max(cint(_setting("max_reminder_times", 5)), 1)


def _time_str(value):
	"""DB Time values arrive as timedelta; return 'HH:MM:SS' or None."""
	if value in (None, ""):
		return None
	if hasattr(value, "total_seconds"):
		total = int(value.total_seconds())
		return f"{total // 3600:02d}:{(total % 3600) // 60:02d}:{total % 60:02d}"
	text = str(value)
	return text if re.match(r"^\d{1,2}:\d{2}(:\d{2})?$", text) else None


def _normalise_time(value):
	"""Accepts 'H:MM', 'HH:MM' or 'HH:MM:SS'; returns 'HH:MM:SS'."""
	text = str(value or "").strip()
	m = re.match(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$", text)
	if not m or int(m.group(1)) > 23 or int(m.group(2)) > 59:
		frappe.throw(_("Invalid time {0}. Use HH:MM.").format(text))
	return f"{int(m.group(1)):02d}:{m.group(2)}:{m.group(3) or '00'}"


def _parse_list(value):
	if value in (None, ""):
		return []
	if isinstance(value, str):
		value = frappe.parse_json(value)
	return value if isinstance(value, list) else [value]


def _digits(value):
	return re.sub(r"\D", "", str(value or ""))


def _open_followups(doctype, parents, cutoff=None):
	"""Open (followed=0) dated rows per parent: {parent: [(date, time, desc)]}."""
	if not parents:
		return {}
	conditions = ""
	values = {"pt": doctype, "parents": list(parents)}
	if cutoff:
		conditions = " AND next_follow_up_date >= %(cutoff)s"
		values["cutoff"] = cutoff
	rows = frappe.db.sql(
		f"""
		SELECT parent, next_follow_up_date, next_follow_up_time
		FROM `tabFollow-Up`
		WHERE parenttype = %(pt)s AND parent IN %(parents)s
		  AND IFNULL(followed, 0) = 0 AND next_follow_up_date IS NOT NULL{conditions}
		ORDER BY next_follow_up_date, next_follow_up_time
		""",
		values,
		as_dict=True,
	)
	result = {}
	for r in rows:
		result.setdefault(r.parent, []).append((getdate(r.next_follow_up_date), _time_str(r.next_follow_up_time)))
	return result


def _future_open(doctype, parents):
	"""Earliest open follow-up dated today or later (released-app meaning)."""
	if not parents:
		return {}
	rows = frappe.db.sql(
		"""
		SELECT parent, MIN(next_follow_up_date) AS d
		FROM `tabFollow-Up`
		WHERE parenttype = %(pt)s AND parent IN %(parents)s
		  AND IFNULL(followed, 0) = 0 AND next_follow_up_date >= %(today)s
		GROUP BY parent
		""",
		{"pt": doctype, "parents": list(parents), "today": nowdate()},
		as_dict=True,
	)
	return {r.parent: r.d for r in rows}


def _latest_notes(doctype, parents):
	if not parents:
		return {}
	rows = frappe.db.sql(
		"""
		SELECT fu.parent, fu.description
		FROM `tabFollow-Up` fu
		JOIN (
			SELECT parent, MAX(creation) AS c FROM `tabFollow-Up`
			WHERE parenttype = %(pt)s AND parent IN %(parents)s
			  AND IFNULL(description, '') != ''
			GROUP BY parent
		) latest ON latest.parent = fu.parent AND latest.c = fu.creation
		WHERE fu.parenttype = %(pt)s
		""",
		{"pt": doctype, "parents": list(parents)},
		as_dict=True,
	)
	return {r.parent: r.description for r in rows}


def _contains(haystack, needle):
	return needle in str(haystack or "").lower()


# ------------------------------------------------------------------ lead list


@frappe.whitelist(allow_guest=False)
def get_leads(limit_start=0, limit=20, name=None, type=None, status=None, source=None,
				 search=None, owner=None, follow_filter=None, status_group=None):
	limit_start = cint(limit_start)
	limit = cint(limit) or 20
	today = getdate(nowdate())
	cutoff = _missed_cutoff()
	new_days = cint(_setting("new_lead_days", 3)) or 3
	new_since = add_days(now_datetime(), -new_days)

	meta = frappe.get_meta("Lead")
	filters = {}
	if type:
		filters["lead_type" if meta.has_field("lead_type") else "type"] = type
	if status:
		filters["status"] = status
	if source:
		filters["source"] = source

	leads = frappe.get_list(
		"Lead",
		filters=filters,
		fields=["name", "image", "first_name", "lead_name", "company_name", "status", "source",
				"creation", "lead_owner", "custom_assigned_to", "mobile_no", "phone", "custom_remarks"],
		order_by="creation desc",
		limit_page_length=0,
	)

	if owner:
		leads = [l for l in leads if owner in (l.lead_owner, l.custom_assigned_to)]

	if search:
		q = str(search).strip().lower()
		q_digits = _digits(q)
		def match(l):
			if any(_contains(l.get(f), q) for f in ("first_name", "lead_name", "company_name", "custom_remarks", "name")):
				return True
			return len(q_digits) >= 4 and any(q_digits in _digits(l.get(f)) for f in ("mobile_no", "phone"))
		leads = [l for l in leads if match(l)]
	elif name:
		# Released app: first-name search.
		q = str(name).strip().lower()
		leads = [l for l in leads if _contains(l.first_name, q)]

	names = [l.name for l in leads]
	open_rows = _open_followups("Lead", names, cutoff)

	def has_today(l):
		return any(d == today for d, _t in open_rows.get(l.name, []))

	def has_missed(l):
		return l.status not in CLOSED_LEAD_STATUSES and any(d < today for d, _t in open_rows.get(l.name, []))

	def is_new(l):
		return bool(l.creation and get_datetime(l.creation) >= new_since)

	counts = {
		"all": len(leads),
		"today": sum(1 for l in leads if has_today(l)),
		"missed": sum(1 for l in leads if has_missed(l)),
		"new": sum(1 for l in leads if is_new(l)),
		"converted": sum(1 for l in leads if l.status == "Converted"),
		"lost": sum(1 for l in leads if l.status in LOST_LEAD_STATUSES),
	}

	selected = leads
	if follow_filter == "today":
		selected = [l for l in leads if has_today(l)]
	elif follow_filter == "missed":
		selected = [l for l in leads if has_missed(l)]
	elif follow_filter == "upcoming":
		selected = [l for l in leads if any(d > today for d, _t in open_rows.get(l.name, []))]
	elif follow_filter == "none":
		selected = [l for l in leads if not open_rows.get(l.name)]

	if status_group == "new":
		selected = [l for l in selected if is_new(l)]
	elif status_group == "lost":
		selected = [l for l in selected if l.status in LOST_LEAD_STATUSES]
	elif status_group == "converted":
		selected = [l for l in selected if l.status == "Converted"]

	if follow_filter in ("today", "missed", "upcoming"):
		selected.sort(key=lambda l: open_rows.get(l.name, [(today, None)])[0])

	page = selected[limit_start:limit_start + limit]
	page_names = [l.name for l in page]
	future = _future_open("Lead", page_names)
	notes = _latest_notes("Lead", page_names)
	site_url = frappe.utils.get_url()

	rows = []
	for l in page:
		first = (open_rows.get(l.name) or [None])[0]
		rows.append({
			"image": (site_url + l.image) if l.image else None,
			"name": l.name,
			"first_name": l.first_name or l.lead_name,
			"status": l.status,
			"source": l.source,
			"creation": l.creation,
			# Released app: next follow-up today or later only.
			"next_follow_up": future.get(l.name),
			# New app: earliest open follow-up, missed included.
			"next_open_follow_up": first[0] if first else None,
			"next_follow_time": first[1] if first else None,
			"is_new": is_new(l),
			"mobile": l.mobile_no or l.phone,
			"last_note": notes.get(l.name) or l.custom_remarks,
			"owner": l.custom_assigned_to or l.lead_owner,
		})

	return {
		"leads": rows,
		"total": len(selected),
		"status": meta.get_field("status").options.split("\n"),
		"source": frappe.get_all("Lead Source", pluck="name"),
		"counts": counts,
	}


# ------------------------------------------------------------- quotation list


@frappe.whitelist(allow_guest=False)
def get_quotations(limit_start=0, limit=20, name=None, status=None, territory=None,
					  search=None, quotation_to=None, owner=None, status_group=None, party_name=None):
	limit_start = cint(limit_start)
	limit = cint(limit) or 20
	cutoff = _missed_cutoff()

	filters = {"docstatus": ["<", 2]}
	if status:
		filters["status"] = status
	if territory:
		filters["territory"] = territory
	if quotation_to:
		filters["quotation_to"] = quotation_to
	if party_name:
		filters["party_name"] = party_name

	quotes = frappe.get_list(
		"Quotation",
		filters=filters,
		or_filters={"name": ["like", f"%{name}%"]} if name and not search else None,
		fields=["name", "quotation_to", "customer_name", "party_name", "status", "transaction_date",
				"valid_till", "grand_total", "territory", "docstatus", "owner", "custom_quotation_owner"],
		order_by="creation desc",
		limit_page_length=0,
	)

	if owner:
		quotes = [q for q in quotes if owner in (q.custom_quotation_owner, q.owner)]
	if search:
		s = str(search).strip().lower()
		quotes = [q for q in quotes if any(_contains(q.get(f), s) for f in ("name", "customer_name", "party_name"))]

	counts = {
		"all": len(quotes),
		"draft": sum(1 for q in quotes if q.docstatus == 0),
		"submitted": sum(1 for q in quotes if q.docstatus == 1),
	}

	selected = quotes
	if status_group == "draft":
		selected = [q for q in quotes if q.docstatus == 0]
	elif status_group == "submitted":
		selected = [q for q in quotes if q.docstatus == 1]

	page = selected[limit_start:limit_start + limit]
	open_rows = _open_followups("Quotation", [q.name for q in page], cutoff)
	site_url = frappe.utils.get_url()

	rows = []
	for q in page:
		first = (open_rows.get(q.name) or [None])[0]
		image = None
		if q.quotation_to == "Customer" and q.party_name and frappe.has_permission("Customer", "read", doc=q.party_name):
			img = frappe.db.get_value("Customer", q.party_name, "image")
			image = site_url + img if img else None
		rows.append({
			"name": q.name,
			"quotation_to": q.quotation_to,
			"customer_name": q.customer_name,
			"party_name": q.party_name,
			"status": q.status,
			"transaction_date": q.transaction_date,
			"valid_till": q.valid_till,
			"grand_total": q.grand_total,
			"territory": q.territory,
			"customer_image": image,
			"docstatus": q.docstatus,
			"next_follow_up": first[0] if first else None,
			"next_follow_time": first[1] if first else None,
		})

	return {
		"quotations": rows,
		"total": len(selected),
		"status": frappe.get_meta("Quotation").get_field("status").options.split("\n"),
		"territory": frappe.get_all("Territory", pluck="name"),
		"counts": counts,
	}


# ------------------------------------------------------------- follow-up calendar


@frappe.whitelist(allow_guest=False)
def get_followups(from_date, to_date, doctype="Lead", status=None, source=None, owner=None,
				  quotation_to=None, include_done=0):
	"""Follow-ups between two dates for the calendar / agenda.

	Scope: parents the user may read (User Permissions), and by default rows
	assigned to the user (next_follow_up_by, else followed_by). owner="all"
	shows every row on permitted parents; owner=<user> shows that user's rows.
	"""
	if doctype not in CHILD_TABLE:
		frappe.throw(_("Follow-ups are available for Lead or Quotation only."))
	from_date, to_date = getdate(from_date), getdate(to_date)
	if (to_date - from_date).days > 62:
		frappe.throw(_("Choose a range of two months or less."))

	today = getdate(nowdate())
	cutoff = _missed_cutoff()

	parent_filters = {}
	if doctype == "Lead":
		if status:
			parent_filters["status"] = status
		if source:
			parent_filters["source"] = source
		parent_fields = ["name", "lead_name", "first_name", "status", "source", "mobile_no", "phone"]
	else:
		parent_filters["docstatus"] = ["<", 2]
		if status:
			parent_filters["status"] = status
		if quotation_to:
			parent_filters["quotation_to"] = quotation_to
		parent_fields = ["name", "customer_name", "party_name", "status", "quotation_to", "grand_total", "custom_phone"]

	parents = {p.name: p for p in frappe.get_list(doctype, filters=parent_filters, fields=parent_fields, limit_page_length=0)}
	if not parents:
		return {"success": True, "counts_by_date": {}, "items": []}

	conditions = ["parenttype = %(pt)s", "parent IN %(parents)s",
				  "next_follow_up_date BETWEEN %(from)s AND %(to)s"]
	values = {"pt": doctype, "parents": list(parents), "from": from_date, "to": to_date}
	if not cint(include_done):
		conditions.append("IFNULL(followed, 0) = 0")
	if cutoff:
		conditions.append("next_follow_up_date >= %(cutoff)s")
		values["cutoff"] = cutoff
	if owner != "all":
		conditions.append("IFNULL(NULLIF(next_follow_up_by, ''), followed_by) = %(user)s")
		values["user"] = owner or frappe.session.user

	rows = frappe.db.sql(
		f"""
		SELECT name, parent, next_follow_up_date, next_follow_up_time, description, status,
			   followed, next_follow_up_by, followed_by
		FROM `tabFollow-Up`
		WHERE {' AND '.join(conditions)}
		ORDER BY next_follow_up_date, next_follow_up_time
		""",
		values,
		as_dict=True,
	)

	closed = CLOSED_LEAD_STATUSES if doctype == "Lead" else CLOSED_QUOTATION_STATUSES
	items, counts = [], {}
	for r in rows:
		p = parents[r.parent]
		date = getdate(r.next_follow_up_date)
		followed = cint(r.followed)
		missed = not followed and date < today
		# Past reminders on closed leads/quotations are not actionable.
		if missed and p.status in closed:
			continue
		key = str(date)
		bucket = counts.setdefault(key, {"open": 0, "missed": 0})
		bucket["missed" if missed else "open"] += 0 if followed else 1
		item = {
			"name": r.name,
			"parenttype": doctype,
			"parent": r.parent,
			"date": key,
			"time": _time_str(r.next_follow_up_time),
			"note": r.description,
			"row_status": r.status,
			"assigned_to": r.next_follow_up_by or r.followed_by,
			"followed": followed,
			"is_missed": missed,
		}
		if doctype == "Lead":
			item.update({
				"party_name": p.lead_name or p.first_name or p.name,
				"mobile": p.mobile_no or p.phone,
				"lead_status": p.status,
				"source": p.source,
			})
		else:
			item.update({
				"party_name": p.customer_name or p.party_name,
				"mobile": p.custom_phone,
				"status": p.status,
				"quotation_to": p.quotation_to,
				"grand_total": p.grand_total,
			})
		items.append(item)

	return {"success": True, "counts_by_date": counts, "items": items}


# ------------------------------------------------------------------ duplicates


@frappe.whitelist(allow_guest=False)
def check_duplicate_lead(mobile):
	"""Finds a lead with the same mobile (last 10 digits, mobile_no or phone)
	among the leads this user is permitted to read."""
	ten = _digits(mobile)[-10:]
	if len(ten) < 10:
		return {"exists": False}
	rows = frappe.get_list(
		"Lead",
		or_filters={"mobile_no": ["like", f"%{ten}"], "phone": ["like", f"%{ten}"]},
		fields=["name", "lead_name", "status", "lead_owner", "custom_assigned_to"],
		order_by="creation desc",
		limit_page_length=1,
	)
	if not rows:
		return {"exists": False}
	match = rows[0]
	return {
		"exists": True,
		"lead": match.name,
		"lead_name": match.lead_name,
		"status": match.status,
		"owner": match.custom_assigned_to or match.lead_owner,
	}


# ------------------------------------------------------------------ templates


@frappe.whitelist(allow_guest=False)
def get_note_templates(applies_to="Lead"):
	return frappe.get_list(
		"Mobile Note Template",
		filters={"enabled": 1, "applies_to": ["in", ["Both", applies_to]]},
		fields=["title", "text"],
		order_by="title asc",
	)


@frappe.whitelist(allow_guest=False)
def get_lead_statuses():
	options = frappe.get_meta("Lead").get_field("status").options or ""
	return [o for o in options.split("\n") if o.strip()]


# ------------------------------------------------------------------ reminders


def _check_parent(doctype, name, ptype="write"):
	if doctype not in CHILD_TABLE:
		frappe.throw(_("Reminders are available for Lead or Quotation only."))
	if not frappe.db.exists(doctype, name):
		frappe.throw(_("{0} {1} not found").format(_(doctype), name), frappe.DoesNotExistError)
	if not frappe.has_permission(doctype, ptype, doc=name):
		frappe.throw(_("You are not allowed to update this {0}.").format(_(doctype)), frappe.PermissionError)
	if doctype == "Quotation" and cint(frappe.db.get_value("Quotation", name, "docstatus")) == 2:
		frappe.throw(_("This quotation is cancelled."))


def _row(name):
	row = frappe.db.get_value(
		"Follow-Up", name, ["name", "parent", "parenttype", "parentfield", "followed"], as_dict=True
	)
	if not row or row.parenttype not in CHILD_TABLE:
		frappe.throw(_("Reminder not found."), frappe.DoesNotExistError)
	_check_parent(row.parenttype, row.parent)
	return row


def _touch(doctype, name):
	frappe.db.set_value(doctype, name, "modified", now_datetime(), update_modified=False)


def _validate_times_for_day(doctype, name, date, new_count, exclude_row=None):
	max_times = _max_times()
	existing = frappe.db.sql(
		"""
		SELECT COUNT(*) FROM `tabFollow-Up`
		WHERE parenttype = %s AND parent = %s AND next_follow_up_date = %s
		  AND IFNULL(followed, 0) = 0 AND name != %s
		""",
		(doctype, name, date, exclude_row or ""),
	)[0][0]
	if cint(existing) + new_count > max_times:
		frappe.throw(_("You can set at most {0} reminder times for one day.").format(max_times))


def insert_followup_rows(doctype, name, date, times, note, status=None, assigned_to=None):
	"""Adds one open Follow-Up row per time (or one all-day row). Returns names."""
	date = getdate(date)
	times = [_normalise_time(t) for t in times] if times else [None]
	if len(set(times)) != len(times):
		frappe.throw(_("The same time is selected twice."))
	_validate_times_for_day(doctype, name, date, len(times))

	parentfield = CHILD_TABLE[doctype]
	idx = cint(frappe.db.sql(
		"SELECT MAX(idx) FROM `tabFollow-Up` WHERE parenttype = %s AND parent = %s", (doctype, name)
	)[0][0])
	user = frappe.session.user
	created = []
	for t in times:
		idx += 1
		row = frappe.get_doc({
			"doctype": "Follow-Up",
			"parent": name,
			"parenttype": doctype,
			"parentfield": parentfield,
			"idx": idx,
			"date": nowdate(),
			"followed_by": user,
			"next_follow_up_by": assigned_to or user,
			"next_follow_up_date": date,
			"next_follow_up_time": t,
			"description": note,
			"status": status,
			"followed": 0,
		})
		if frappe.get_meta("Follow-Up").has_field("custom_enter_datetime"):
			row.custom_enter_datetime = now_datetime()
		row.db_insert()
		created.append(row.name)
	return created


@frappe.whitelist(allow_guest=False)
def add_reminder(reference_doctype, reference_name, date, times=None, note=None, status=None):
	"""Adds reminder(s) without closing the other open reminders.
	`times`: list of 'HH:MM' (max per day from Mobile App Settings); empty = all day."""
	_check_parent(reference_doctype, reference_name)
	if getdate(date) < getdate(nowdate()):
		frappe.throw(_("Reminder date cannot be in the past."))
	if not (note or "").strip():
		frappe.throw(_("Please add a note for the reminder."))

	assigned_to = None
	if reference_doctype == "Lead":
		assigned_to = frappe.db.get_value("Lead", reference_name, "custom_assigned_to")
		if status:
			options = (frappe.get_meta("Lead").get_field("status").options or "").split("\n")
			if status not in options:
				frappe.throw(_("Invalid status {0}").format(status))
			frappe.db.set_value("Lead", reference_name, "status", status)
	row_status = status or (frappe.db.get_value("Lead", reference_name, "status") if reference_doctype == "Lead" else None)

	created = insert_followup_rows(
		reference_doctype, reference_name, date, _parse_list(times), note.strip(),
		status=row_status, assigned_to=assigned_to,
	)
	_touch(reference_doctype, reference_name)
	return {"success": True, "rows": created}


@frappe.whitelist(allow_guest=False)
def complete_followup(name, note=None):
	row = _row(name)
	values = {"followed": 1, "completed_on": now_datetime()}
	if note:
		values["description"] = note
	frappe.db.set_value("Follow-Up", row.name, values)
	_touch(row.parenttype, row.parent)
	return {"success": True, "name": row.name}


@frappe.whitelist(allow_guest=False)
def reschedule_followup(name, date, time=None):
	row = _row(name)
	if getdate(date) < getdate(nowdate()):
		frappe.throw(_("Reminder date cannot be in the past."))
	_validate_times_for_day(row.parenttype, row.parent, getdate(date), 1, exclude_row=row.name)
	frappe.db.set_value("Follow-Up", row.name, {
		"next_follow_up_date": getdate(date),
		"next_follow_up_time": _normalise_time(time) if time else None,
		"followed": 0,
		"completed_on": None,
	})
	_touch(row.parenttype, row.parent)
	return {"success": True, "name": row.name}


@frappe.whitelist(allow_guest=False)
def delete_followup(name):
	row = _row(name)
	frappe.db.delete("Follow-Up", {"name": row.name})
	_touch(row.parenttype, row.parent)
	return {"success": True}


# ------------------------------------------------------------- lead creation


@frappe.whitelist(allow_guest=False)
def create_lead():
	"""Same body as api.create_lead_with_followup, plus
	`reminders: [{"date": "2026-10-20", "times": ["10:30", "16:00"], "note": "..."}]`.
	The lead is created by the existing endpoint (same hooks and behaviour);
	reminder rows are added afterwards, one per time."""
	from crm_activity_tracking.crm_activity_tracking.utils.api import create_lead_with_followup

	data = frappe.request.get_json() or {}
	reminders = _parse_list(data.get("reminders"))
	today = getdate(nowdate())
	max_times = _max_times()
	for r in reminders:
		if not r.get("date"):
			frappe.throw(_("Reminder date is required."))
		if getdate(r["date"]) < today:
			frappe.throw(_("Reminder date cannot be in the past."))
		times = _parse_list(r.get("times"))
		if len(times) > max_times:
			frappe.throw(_("You can set at most {0} reminder times for one day.").format(max_times))
		for t in times:
			_normalise_time(t)

	result = create_lead_with_followup()
	lead = (result or {}).get("lead")
	if not lead:
		return result

	if reminders:
		_check_parent("Lead", lead)
	status = data.get("status") or "Lead"
	for r in reminders:
		insert_followup_rows(
			"Lead", lead, r["date"], _parse_list(r.get("times")),
			(r.get("note") or data.get("notes") or "").strip(),
			status=status, assigned_to=data.get("assigned_to"),
		)
	return {"success": True, "lead": lead}


# ----------------------------------------------------------- AMC / service


def _employee():
	from crm_activity_tracking.crm_activity_tracking.utils.api import get_current_employee

	return get_current_employee()


def _check_visit(doc, ptype="read"):
	"""Only visits the user has been granted (role + User Permissions)."""
	if not frappe.has_permission("AMC Visitor Tracking", ptype, doc=doc):
		frappe.throw(_("You are not permitted to access this visit."), frappe.PermissionError)


def _add_progress(visitors, service=False):
	"""total_rows / done_rows (refilling_complete) per visit. Service visits
	count only rows marked refilling_print, as the app shows."""
	names = [v["name"] for v in visitors]
	if not names:
		return
	condition = " AND refilling_print = 1" if service else ""
	rows = frappe.db.sql(
		f"""
		SELECT parent, COUNT(*) AS total_rows, SUM(IFNULL(refilling_complete, 0) = 1) AS done_rows
		FROM `tabRefilling Schedule Table`
		WHERE parenttype = 'AMC Visitor Tracking' AND parent IN %(names)s{condition}
		GROUP BY parent
		""",
		{"names": names},
		as_dict=True,
	)
	progress = {r.parent: r for r in rows}
	for v in visitors:
		r = progress.get(v["name"])
		v["total_rows"] = cint(r.total_rows) if r else 0
		v["done_rows"] = cint(r.done_rows) if r else 0


def _visits(service):
	today = nowdate()
	date_field = "service_visit_date" if service else "amc_service_date"
	status_field = "service_status" if service else "status"
	visitors = frappe.get_list(
		"AMC Visitor Tracking",
		filters={
			date_field: ["<=", today],
			"assign_service_employee" if service else "assign_employee": _employee(),
			# Completed visits drop off; started (Working) ones stay resumable.
			status_field: ["in", ["Open", "Working"] if service else ["Assigned", "Working"]],
		},
		fields=["name", "customer_name", date_field, "next_amc_service_due_date", "contact_number",
				"concern_person", "location", status_field,
				"assign_service_employee" if service else "assign_employee"],
		order_by=f"{date_field} asc, creation desc",
		limit_page_length=0,
	)
	for v in visitors:
		due = v.get(date_field)
		v["is_missed"] = bool(due and str(due) < today)
	_add_progress(visitors, service=service)
	return visitors


@frappe.whitelist(allow_guest=False)
def get_amc_visits():
	"""AMC visits due today or missed, not completed, with progress."""
	return _visits(service=False)


@frappe.whitelist(allow_guest=False)
def get_service_visits():
	"""Service visits due today or missed (Open or Working), with progress."""
	return _visits(service=True)


@frappe.whitelist(allow_guest=False)
def get_visit_detail(name, is_service=0):
	"""AMC Visitor Tracking with refilling rows; frequency, dates and the print
	flag come from the linked AMC row when amc_refilling_row is set."""
	doc = frappe.get_doc("AMC Visitor Tracking", name)
	_check_visit(doc)
	data = doc.as_dict()
	field = frappe.get_meta("AMC").get_field("refilling_schedule")
	child = field.options if field else None
	# Linked AMC row details only when the user may read that AMC.
	if doc.amc_template and not frappe.has_permission("AMC", "read", doc=doc.amc_template):
		child = None
	for row in data.get("refilling_schedule") or []:
		linked = row.get("amc_refilling_row")
		if not linked or not child:
			continue
		values = frappe.db.get_value(
			child, linked,
			["refilling_frequency", "date_refilling", "refilling_due_date", "refilling_print"],
			as_dict=True,
		)
		if values:
			row.update(values)
	return data


EDITABLE_ROW_FIELDS = ("actual_weight", "remarks", "refilling_complete", "enter_datetime")


@frappe.whitelist(allow_guest=False)
def update_refilling_row(name, row_name, data, is_service=0):
	"""Updates one extinguisher row and marks the visit (or its service part)
	Working. Only actual_weight, remarks, refilling_complete, enter_datetime change."""
	if isinstance(data, str):
		data = json.loads(data)
	if isinstance(data.get("remarks"), list):
		data["remarks"] = ", ".join(str(x).strip() for x in data["remarks"] if str(x or "").strip())

	is_service = cint(is_service)
	doc = frappe.get_doc("AMC Visitor Tracking", name)
	_check_visit(doc, "write")
	status_field = "service_status" if is_service else "status"
	if doc.get(status_field) == "Completed":
		frappe.throw(_("This visit is already completed."))

	row = next((r for r in doc.refilling_schedule if r.name == row_name or r.qr_code == row_name), None)
	if not row:
		frappe.throw(_("Extinguisher row not found in this visit."), frappe.DoesNotExistError)

	updates = {k: v for k, v in data.items() if k in EDITABLE_ROW_FIELDS}
	if "refilling_complete" in updates:
		updates["refilling_complete"] = 1 if updates["refilling_complete"] in (1, True, "1", "true") else 0
	if updates:
		frappe.db.set_value(row.doctype, row.name, updates)

	if doc.get(status_field) not in ("Working", "Completed"):
		frappe.db.set_value("AMC Visitor Tracking", name, status_field, "Working")
	return {"status": "success", "message": "Row updated"}


@frappe.whitelist(allow_guest=False)
def complete_visit(name, is_service=0):
	"""Completes an AMC visit, or its service part. Started visits are accepted."""
	is_service = cint(is_service)
	doc = frappe.get_doc("AMC Visitor Tracking", name)
	_check_visit(doc, "write")
	status_field = "service_status" if is_service else "status"
	status = doc.get(status_field)
	if status == "Completed":
		return {"status": "already_completed", "message": "Visit is already completed"}
	if status not in (("Open", "Working") if is_service else ("Assigned", "Working")):
		frappe.throw(_("This visit is not assigned yet, so it cannot be completed."))
	frappe.db.set_value("AMC Visitor Tracking", name, status_field, "Completed")
	return {"status": "success", "message": "Visit completed"}

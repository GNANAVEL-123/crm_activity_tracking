from frappe import _


def get_data():
	return {
		"fieldname": "amc_template",
		"transactions": [
			{"label": _("Visits"), "items": ["AMC Visitor Tracking"]},
		],
	}

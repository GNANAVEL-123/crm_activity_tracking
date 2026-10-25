from frappe import _


def get_data():
	return {
		"fieldname": "amc_master",
		"transactions": [
			{"label": _("AMC"), "items": ["AMC"]},
		],
	}

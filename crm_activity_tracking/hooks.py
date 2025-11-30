app_name = "crm_activity_tracking"
app_title = "Crm Activity Tracking"
app_publisher = "CRM"
app_description = "CRM Activity Tracking"
app_email = "crm@gmail.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/crm_activity_tracking/css/crm_activity_tracking.css"
# app_include_js = "/assets/crm_activity_tracking/js/crm_activity_tracking.js"

# include js, css files in header of web template
# web_include_css = "/assets/crm_activity_tracking/css/crm_activity_tracking.css"
# web_include_js = "/assets/crm_activity_tracking/js/crm_activity_tracking.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "crm_activity_tracking/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Lead" : "crm_activity_tracking/custom_files/js/lead.js",
			"Quotation" : "crm_activity_tracking/custom_files/js/quotation.js",
			"Task" :"crm_activity_tracking/custom_files/js/task.js",
			"Project": "crm_activity_tracking/custom_files/js/project.js",
			"Purchase Order": "crm_activity_tracking/custom_files/js/purchase_order.js",
			"Purchase Receipt": "crm_activity_tracking/custom_files/js/purchase_receipt.js",
			"Purchase Invoice": "crm_activity_tracking/custom_files/js/purchase_invoice.js",
			"Sales Order": "crm_activity_tracking/custom_files/js/sales_order.js",
			"Delivery Note": "crm_activity_tracking/custom_files/js/delivery_note.js",
			"Sales Invoice": "crm_activity_tracking/custom_files/js/sales_invoice.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "crm_activity_tracking/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
jinja = {
    "methods" : [
		"frappe.utils.data.money_in_words",
		"crm_activity_tracking.crm_activity_tracking.custom_files.py.quotation.tax_details",
		"crm_activity_tracking.crm_activity_tracking.custom_files.py.print_format.get_invoice_item_and_tax_details",
    ]
}
# Installation
# ------------

# before_install = "crm_activity_tracking.install.before_install"
# after_install = "crm_activity_tracking.install.after_install"

# Uninstallation
# ------------
after_migrate = "crm_activity_tracking.migrate.after_migrate"

# before_uninstall = "crm_activity_tracking.uninstall.before_uninstall"
# after_uninstall = "crm_activity_tracking.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "crm_activity_tracking.utils.before_app_install"
# after_app_install = "crm_activity_tracking.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "crm_activity_tracking.utils.before_app_uninstall"
# after_app_uninstall = "crm_activity_tracking.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "crm_activity_tracking.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Lead": "crm_activity_tracking.crm_activity_tracking.custom_files.py.lead.CustomLead",
}

# Document Events
# ---------------
# Hook on document methods and events


doc_events = {
	"Lead": {
		"validate": "crm_activity_tracking.crm_activity_tracking.custom_files.py.lead.validate",
		"after_insert": "crm_activity_tracking.crm_activity_tracking.custom_files.py.lead.after_insert",
		"on_trash": "crm_activity_tracking.crm_activity_tracking.custom_files.py.lead.on_trash"
	},
  "Quotation": {
		"validate": "crm_activity_tracking.crm_activity_tracking.custom_files.py.quotation.validate",
		"after_insert": "crm_activity_tracking.crm_activity_tracking.custom_files.py.quotation.after_insert",
		"on_update_after_submit":"crm_activity_tracking.crm_activity_tracking.custom_files.py.quotation.after_insert",
		"on_trash": "crm_activity_tracking.crm_activity_tracking.custom_files.py.quotation.on_trash"
	},
	'User':{
		'after_insert':"crm_activity_tracking.crm_activity_tracking.custom_files.py.user.manage_user_permissions",
		'validate':"crm_activity_tracking.crm_activity_tracking.custom_files.py.user.manage_user_permissions"

	},
	"Project" : {
		"validate":"crm_activity_tracking.crm_activity_tracking.custom_files.py.project.validate",
		"after_insert":"crm_activity_tracking.crm_activity_tracking.custom_files.py.project.after_insert",
		"on_trash":"crm_activity_tracking.crm_activity_tracking.custom_files.py.project.on_trash"
	},
	"Sales Invoice" : {
		"autoname":"crm_activity_tracking.crm_activity_tracking.custom_files.py.auto_name.sales_inv_naming",
		"on_trash":"crm_activity_tracking.crm_activity_tracking.custom_files.py.auto_name.si_delete",
		"validate":"crm_activity_tracking.crm_activity_tracking.custom_files.py.sales_invoice.validate_customer_lastprice",
	},
	"Delivery Note" : {
		"autoname":"crm_activity_tracking.crm_activity_tracking.custom_files.py.auto_name.dn_naming",
		"on_trash":"crm_activity_tracking.crm_activity_tracking.custom_files.py.auto_name.dn_delete",
	},
	"Purchase Order" : {
		"autoname":"crm_activity_tracking.crm_activity_tracking.custom_files.py.auto_name.po_naming",
		"on_trash":"crm_activity_tracking.crm_activity_tracking.custom_files.py.auto_name.po_delete",
		"validate":"crm_activity_tracking.crm_activity_tracking.custom_files.py.purchase_order.validate_supplier_lastprice"
	},
	"Task" : {
		"validate": "crm_activity_tracking.crm_activity_tracking.custom_files.py.task.validate",
		"after_insert": "crm_activity_tracking.crm_activity_tracking.custom_files.py.task.after_insert",
		"on_trash": "crm_activity_tracking.crm_activity_tracking.custom_files.py.task.on_trash"
	}
}
# Scheduled Taskss
# ---------------

scheduler_events = {
# 	"all": [
# 		"crm_activity_tracking.tasks.all"
# 	],
# 	"daily": [
# 		"crm_activity_tracking.tasks.daily"
# 	],
# 	"hourly": [
# 		"crm_activity_tracking.tasks.hourly"
# 	],
# 	"weekly": [
# 		"crm_activity_tracking.tasks.weekly"
# 	],
# 	"monthly": [
# 		"crm_activity_tracking.tasks.monthly"
# 	],
	"cron":{
		'0 2 * * *': [
			"crm_activity_tracking.crm_activity_tracking.doctype.amc.amc.amc_visitor_tracker",
			"crm_activity_tracking.crm_activity_tracking.doctype.amc_fire_alarm_system.amc_fire_alarm_system.amc_fire_alarm_tracker",
			"crm_activity_tracking.crm_activity_tracking.doctype.amc_fire_hydrant_system.amc_fire_hydrant_system.amc_fire_hydrant_tracker",
			"crm_activity_tracking.crm_activity_tracking.custom_files.py.cron.leave_allocation"
		],
		'* * * * *': [
			"crm_activity_tracking.crm_activity_tracking.custom_files.py.cron.schedule_whatsapp_message",
		],
		'0 8 * * *': [
			"crm_activity_tracking.crm_activity_tracking.custom_files.py.cron.quotation_tracking_email_send",
			"crm_activity_tracking.crm_activity_tracking.custom_files.py.cron.task_tracking_email_send",
			"crm_activity_tracking.crm_activity_tracking.custom_files.py.cron.inactive_email_cron",
			"crm_activity_tracking.crm_activity_tracking.custom_files.py.cron.payment_remainder_email_send_cron",
		],
    }
}

# Testing
# -------

# before_tests = "crm_activity_tracking.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "crm_activity_tracking.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "crm_activity_tracking.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["crm_activity_tracking.utils.before_request"]
# after_request = ["crm_activity_tracking.utils.after_request"]

# Job Events
# ----------
# before_job = ["crm_activity_tracking.utils.before_job"]
# after_job = ["crm_activity_tracking.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"crm_activity_tracking.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }


import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from frappe.utils import nowdate
def after_install():
    custom_fields = {
        'User': [
            dict(
                fieldname= "mobile_app_default",
                fieldtype= "Tab Break",
                label= "Mobile App Defaults",
                insert_after= "connections_tab",
            ),
            dict(
                fieldname= "allow_mobile_login",
                fieldtype= "Check",
                label= "Allow Mobile Login",
                insert_after= "mobile_app_default"
            ),
            dict(
                fieldname= "mobile_app_profile",
                fieldtype= "Link",
                options = "Mobile App Profile",
                label= "Mobile App Profile",
                insert_after= "allow_mobile_login"
            ),
            dict(
                fieldname="track_location_on",
                fieldtype="Select",
                label="Track Location On",
                options="\nCheck In and Check Out\nNo Tracking",
                default="Check In and Check Out",
                insert_after="mobile_app_profile"
            ),
            dict(
                fieldname= "current_device_info",
                fieldtype= "Column Break",
                label= "",
                insert_after= "track_location_on",
            ),
            dict(
                fieldname= "otp",
                fieldtype= "Data",
                label= "Otp For Login",
                insert_after= "current_device_info"
            ),
            dict(
                fieldname= "device_info",
                fieldtype= "Data",
                label= "Device Info",
                insert_after= "otp"
            ),
            dict(
                fieldname= "device_info",
                fieldtype= "Data",
                label= "Device Info",
                insert_after= "otp"
            ),
            dict(
                fieldname= "remove_device",
                fieldtype= "Button",
                label= "Remove Device",
                insert_after= "device_info"
            ),
            dict(
                fieldname= "last_sync_date_time",
                fieldtype= "Datetime",
                label= "Last Sync Date Time",
                insert_after= "remove_device"
            ),
        ]
    }

    create_custom_fields(custom_fields)



@frappe.whitelist()
def get_location_timeline(employee,date):

    logs = frappe.get_all(
        "Employee Location Log Detail",
        filters={
            "parenttype": "Employee Location Log",
            "parent": [
                "in",
                frappe.get_all(
                    "Employee Location Log",
                    filters={
                        "employee": employee,
                        "date": date
                    },
                    pluck="name"
                )
            ]
        },
        fields=["latitude", "longitude", "time"],
        order_by="time asc"
    )

    return logs
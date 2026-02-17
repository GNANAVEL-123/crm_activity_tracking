import json
import random
import string
import frappe
from frappe import _
from frappe.utils import flt
from frappe.utils import cint
from frappe.utils.file_manager import save_file
from frappe.utils import now_datetime, today,nowdate

@frappe.whitelist(allow_guest=True)
def login():
    try:
        data = frappe.request.get_json() or {}

        usr = data.get("username")
        pwd = data.get("password")
        otp = data.get("otp")

        if not usr or not pwd:
            return {
                "success": False,
                "message": "Username or Password missing"
            }

        if not otp:
            return {
                "success": False,
                "message": "OTP missing"
            }

        if not frappe.db.exists("User", usr):
            return {
                "success": False,
                "message": "Invalid Username"
            }

        user = frappe.get_doc("User", usr)

        if not cint(user.enabled):
            return {
                "success": False,
                "message": "User account is disabled"
            }

        if not user.allow_mobile_login:
            return {
                "success": False,
                "message": "Mobile App Access Denied"
            }

        if not user.mobile_app_profile:
            return {
                "success": False,
                "message": "Mobile App Profile is Not Set"
            }

        stored_otp = user.otp

        if not stored_otp or otp != stored_otp:
            return {
                "success": False,
                "message": "Invalid OTP"
            }

        try:
            login_manager = frappe.auth.LoginManager()
            login_manager.authenticate(usr, pwd)
            login_manager.post_login()
        except Exception:
            frappe.log_error("Login Error", frappe.get_traceback())
            return {
                "success": False,
                "message": "Invalid Password"
            }

        api_keys = generate_keys(frappe.session.user)

        device_info = generate_unique_device_info()
        frappe.db.set_value("User", usr, "device_info", device_info)

        frappe.db.commit()

        return {
            "success": True,
            "message": "Logged In",
            "user": frappe.session.user,
            "full_name": user.full_name,
            "api_key": api_keys.get("api_key"),
            "api_secret": api_keys.get("api_secret"),
            "device_info": device_info
        }

    except Exception:
        frappe.log_error("Unhandled Mobile Login Error", frappe.get_traceback())
        return {
            "success": False,
            "message": "Server error. Please try again."
        }


def generate_unique_device_info():
    while True:
        random_device_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        
        existing = frappe.db.exists("User", {"device_info": random_device_id})
        if not existing:
            return random_device_id


def generate_keys(user: str):

    user_details: User = frappe.get_doc("User", user)

    api_secret = frappe.generate_hash(length=15)
    
    if not user_details.api_key:
        
        api_key = frappe.generate_hash(length=15)
        
        user_details.api_key = api_key
    else:
        
        api_key = user_details.api_key

    user_details.api_secret = api_secret

    user_details.save(ignore_permissions = True)

    return {"api_secret": api_secret,"api_key": api_key}

@frappe.whitelist(allow_guest = False)
def get_session_user_details():
    user = frappe.session.user
    user_doc = frappe.get_doc("User", user)
    
    data = user_doc.as_dict()

    sensitive_fields = [
        "password", "new_password", "otp", "last_reset_password_key",
        "reset_password_key", "api_secret", "email_verification_token",
        "two_factor_secret", "two_factor_qr_image",
        "login_before_password_reset", "unsubscribed", "salt",
        "last_passwords", "login_after"
    ]

    for field in sensitive_fields:
        if field in data:
            data.pop(field)

    return data


@frappe.whitelist(allow_guest=False)
def mobile_is_session_active():
    try:
        user = frappe.session.user

        if user in ["Guest", None]:
            return {"active": False}

        user_doc = frappe.get_doc("User", user)

        if not getattr(user_doc, "allow_mobile_login", False):
            return {"active": False}

        return {"active": True}

    except Exception as e:
        return {"active": False}

@frappe.whitelist(allow_guest = False)
def fetch_profile():
    try:
        user = frappe.session.user

        if user in ["Guest", None]:
            return {"success": False, "message": "Invalid session"}

        user_doc = frappe.get_doc("User", user)

        if user_doc.allow_mobile_login:
            if user_doc.mobile_app_profile:
                profile = frappe.get_doc('Mobile App Profile',user_doc.mobile_app_profile)
                profile = {
                    "allow_mobile_login": user_doc.get("allow_mobile_login", 0),
                    "profile": user_doc.mobile_app_profile,
                    "allow_lead_creation": profile.allow_lead_creation,
                    "allow_quotation_creation": profile.allow_quotation_creation,
                    "default_company": frappe.db.get_single_value('Mobile App Settings','default_company'),
                    "is_default_company_set": True if frappe.db.get_single_value('Mobile App Settings','default_company') else False,
                    
                    "default_tax_category": frappe.db.get_single_value('Mobile App Settings','default_tax_category'),
                    "is_default_tax_category_set": True if frappe.db.get_single_value('Mobile App Settings','default_tax_category') else False,

                    "default_sales_taxes_and_charges_template": frappe.db.get_single_value('Mobile App Settings','default_sales_taxes_and_charges_template'),
                    "is_default_sales_taxes_and_charges_template_set": True if frappe.db.get_single_value('Mobile App Settings','default_sales_taxes_and_charges_template') else False,

                    "default_price_list": frappe.db.get_single_value('Mobile App Settings','default_price_list'),
                    "is_default_price_list_set": True if frappe.db.get_single_value('Mobile App Settings','default_price_list') else False,
                }
                
                return {"success": True, "data": profile}

            else:
                return {"success": False, "message": "Mobile app Profile Not Set"}

        else:
            return {"success": False, "message": "Mobile Login Denied"}


    except Exception:
        return {"success": False, "message": "Something went wrong"}


@frappe.whitelist(allow_guest=False)
def todays_followup():
    frappe.throw('Test')
    date = frappe.utils.nowdate()

    query = """
        SELECT 
            fu.name AS follow_up_id,
            fu.parenttype,
            fu.parent,
            fu.next_follow_up_date,
            IF(fu.parenttype = 'Lead', l.lead_name, q.customer_name) AS party_name,
            IF(fu.parenttype = 'Lead', l.status, q.status) AS party_status
        FROM `tabFollow-Up` fu
        LEFT JOIN `tabLead` l 
            ON fu.parenttype = 'Lead' 
            AND fu.parent = l.name
        LEFT JOIN `tabQuotation` q 
            ON fu.parenttype = 'Quotation'
            AND fu.parent = q.name
        WHERE fu.next_follow_up_date = %s
            AND (fu.parenttype = 'Lead' OR fu.parenttype = 'Quotation')
            AND fu.followed = 0
    """

    data = frappe.db.sql(query, (date,), as_dict=True)
    return {"success": True, "data": data}

@frappe.whitelist(allow_guest=False)
def get_today_checkin_status(employee=None):
    user = frappe.session.user

    if not employee:
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")

    if not employee:
        return {"success": False, "message": "Employee not found"}

    today = frappe.utils.today()

    last_log = frappe.db.get_value(
        "Employee Checkin",
        {"employee": employee},
        ["log_type", "time"],
        order_by="time desc",
        as_dict=True
    )

    if not last_log:
        return {"success": True, "status": "NONE"}

    last_date = str(last_log.time.date())

    if last_date != today:
        return {"success": True, "status": "NONE"}

    if last_log.log_type == "IN":
        return {"success": True, "status": "IN"}
    else:
        return {"success": True, "status": "OUT"}


@frappe.whitelist(allow_guest=False)
def get_leads(limit_start=0, limit=20, name=None, type=None, status=None, source=None):
    limit_start = int(limit_start)
    limit = int(limit)

    status_list = frappe.get_meta("Lead").get_field("status").options.split("\n")
    source_list = frappe.get_all('Lead Source',pluck = 'name')

    conditions = ""
    site_url = frappe.utils.get_url()
    filters = {"site_url": site_url}

    if name:
        conditions += " AND l.first_name LIKE %(name)s"
        filters["name"] = f"%{name}%"

    if type:
        conditions += " AND l.lead_type = %(type)s"
        filters["type"] = type

    if status:
        conditions += " AND l.status = %(status)s"
        filters["status"] = status

    if source:
        conditions += " AND l.source = %(source)s"
        filters["source"] = source

    query = f"""
        SELECT
            l.image,
            l.name,
            l.first_name,
            l.status,
            l.source,
            (
                SELECT MIN(f.next_follow_up_date)
                FROM `tabFollow-Up` f
                WHERE f.parent = l.name
                  AND f.next_follow_up_date >= CURDATE()
                  AND f.followed = 0
            ) AS next_follow_up
        FROM `tabLead` l
        WHERE 1=1 {conditions}
        ORDER BY creation DESC
        LIMIT {limit_start}, {limit}
    """

    data = frappe.db.sql(query, filters, as_dict=True)

    for row in data:
        if row["image"]:
            row["image"] = site_url + row["image"]
        else:
            row["image"] = None

    total_count = frappe.db.sql(f"""
        SELECT COUNT(*)
        FROM `tabLead` l
        WHERE 1=1 {conditions}
    """, filters)[0][0]

    return {
        "leads": data,
        "total": total_count,
        "status": status_list,
        "source": source_list,
    }
    
@frappe.whitelist(allow_guest=False)
def get_quotations(limit_start=0, limit=20, name=None, status=None, territory=None):
    limit_start = int(limit_start)
    limit = int(limit)

    site_url = frappe.utils.get_url()

    status_list = frappe.get_meta("Quotation").get_field("status").options.split("\n")

    territory_list = frappe.get_all("Territory", pluck="name")

    conditions = ""
    filters = {}

    if name:
        conditions += " AND q.name LIKE %(name)s"
        filters["name"] = f"%{name}%"

    if status:
        conditions += " AND q.status = %(status)s"
        filters["status"] = status

    if territory:
        conditions += " AND q.territory = %(territory)s"
        filters["territory"] = territory

    query = f"""
        SELECT
            q.name,
            q.quotation_to,
            q.customer_name,
            q.party_name,
            q.status,
            q.transaction_date,
            q.valid_till,
            q.grand_total,
            q.territory,
            c.image AS customer_image
        FROM `tabQuotation` q
        LEFT JOIN `tabCustomer` c
            ON q.quotation_to = 'Customer'
           AND c.name = q.party_name
        WHERE q.docstatus < 2
        {conditions}
        ORDER BY q.creation DESC
        LIMIT {limit_start}, {limit}
    """

    data = frappe.db.sql(query, filters, as_dict=True)

    for row in data:
        if row.get("customer_image"):
            row["customer_image"] = site_url + row["customer_image"]
        else:
            row["customer_image"] = None

    total_count = frappe.db.sql(f"""
        SELECT COUNT(*)
        FROM `tabQuotation` q
        WHERE q.docstatus < 2
        {conditions}
    """, filters)[0][0]

    return {
        "quotations": data,
        "total": total_count,
        "status": status_list,
        "territory": territory_list
    }


@frappe.whitelist(allow_guest = False)
def get_lead_detail(name):
    lead = frappe.get_doc("Lead", name)

    attachments = frappe.get_all(
        "File",
        filters={
            "attached_to_doctype": "Lead",
            "attached_to_name": name,
            "is_folder": 0
        },
        fields=[
            "name",
            "file_name",
            "file_url",
            "file_type",
            "is_private",
            "creation"
        ],
        order_by="creation desc"
    )

    data = lead.as_dict()
    data["attachments"] = attachments
    return data

@frappe.whitelist(allow_guest = False)
def get_metadata():
    lead_meta = frappe.get_meta('Lead').get_field("status").options.split("\n")
    indutries = frappe.get_all('Industry Type',pluck = 'name')
    itemlist = frappe.get_all('Item',pluck = 'name')
    customer = frappe.get_all('Customer',pluck = 'name')
    
    companies = frappe.get_all('Company',pluck = 'name')
    lead_source = frappe.get_all('Lead Source',pluck = 'name')
    territory = frappe.get_all('Territory',pluck = 'name')
    users = frappe.get_all('User',filters = {'enabled': 1},pluck = 'name')
    return {'lead_meta': lead_meta,
            'customer':customer,
            'industry': indutries,
            'itemlist': itemlist,
            'companies':companies,
            'lead_source':lead_source,
            'territory':territory,
            'user': users}

@frappe.whitelist(allow_guest = False)
def create_checkin(latitude=None, longitude=None, address=None,device_token = None):
    user = frappe.session.user

    frequency = frappe.db.get_single_value("Mobile App Settings","location_update_interval")
    track_location_on = frappe.db.get_value("User",user,"track_location_on")
    allow_tracking = 0
    if track_location_on == "Check In and Check Out":
        allow_tracking = 1

    if not latitude or not longitude:
        return {"success": False, "message": "Missing GPS data"}

    doc = frappe.new_doc("Employee Checkin")
    doc.employee = get_employee_from_user(user)
    doc.log_type = "IN"
    doc.device_id = frappe.request.headers.get("User-Agent")
    doc.latitude = latitude
    doc.longitude = longitude
    doc.device_id = device_token
    # doc.address = address
    doc.save(ignore_permissions=True)

    return {
        "success": True,
        "allow_tracking": allow_tracking,
        "frequency": frequency,
        "message": "Check-In created successfully",
        "checkin_id": doc.name
    }


@frappe.whitelist(allow_guest = False)
def get_leave_metadata():
    employee_id = frappe.db.get_value(
        "Employee",
        {"user_id": frappe.session.user},
        "name"
    )

    if not employee_id:
        frappe.throw("Employee not linked to user")

    employee_name, leave_approver = frappe.db.get_value(
        "Employee",
        employee_id,
        ["employee_name", "leave_approver"]
    )

    return {
        "employee_id": employee_id,
        "employee_name": employee_name,
        "leave_approver": leave_approver,
        "leave_types": frappe.get_all(
            "Leave Type",
            pluck="name"
        ),
        "from_date_required": 1,
        "to_date_required": 1,
        "half_day_allowed": 1,
        "default_half_day": 0,
        "reason_required": 1
    }

@frappe.whitelist(allow_guest = False)
def create_leave_application(data):
    """
    data = {
        employee_id,
        leave_type,
        from_date,
        to_date,
        total_days,
        half_day,
        session,
        reason,
        half_day_date
    }
    """

    data = frappe.parse_json(data)

    employee = data.get("employee_id")
    leave_type = data.get("leave_type")

    if not employee or not leave_type:
        frappe.throw("Employee and Leave Type are required")

    from_date = data.get("from_date")
    to_date = data.get("to_date")

    existing_leave = frappe.db.exists(
        "Leave Application",
        {
            "employee": employee,
            "docstatus": ["!=", 2],
            "status": ["in", ["Open", "Pending Approval"]],
            "from_date": ["<=", to_date],
            "to_date": [">=", from_date],
        },
    )

    if existing_leave:
        frappe.throw("You already have a Leave Application that is Pending or in Draft for the selected date range.")


    doc = frappe.new_doc("Leave Application")
    doc.employee = employee
    doc.leave_type = leave_type
    doc.from_date = from_date
    doc.to_date = to_date
    doc.description = data.get("reason")

    if data.get("half_day"):
        doc.half_day = 1
        doc.half_day_date = data.get("half_day_date")
        doc.half_day_session = data.get("session")

    doc.insert(ignore_permissions=True)

    return {
        "success": True,
        "leave_application": doc.name
    }

@frappe.whitelist(allow_guest = False)
def create_checkout(latitude=None, longitude=None, address=None,device_token = None):
    user = frappe.session.user

    if not latitude or not longitude:
        return {"success": False, "message": "Missing GPS data"}

    doc = frappe.new_doc("Employee Checkin")
    doc.employee = get_employee_from_user(user)
    doc.log_type = "OUT"
    doc.device_id = frappe.request.headers.get("User-Agent")
    doc.latitude = latitude
    doc.longitude = longitude
    doc.device_id = device_token
    # doc.address = address
    doc.save(ignore_permissions=True)

    return {
        "success": True,
        "message": "Check-Out created successfully",
        "checkout_id": doc.name
    }


def get_employee_from_user(user):
    emp = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if not emp:
        frappe.throw(_("Employee not linked with user"))
    return emp


@frappe.whitelist(allow_guest = False)
def create_lead_with_followup():
    """
    data: dict containing lead fields and optional followups
    """
    data = frappe.request.get_json()

    raw_followups = data.get("follow_ups") or "[]"
    followups = json.loads(raw_followups) if isinstance(raw_followups, str) else raw_followups

    raw_items = data.get("items") or "[]"
    items = json.loads(raw_items) if isinstance(raw_items, str) else raw_items

    lead = frappe.get_doc({
        "doctype": "Lead",
        "source": data.get("lead_source"),
        "custom_allocated_to_manager": data.get("allocated_to_manager"),
        "territory": data.get("territory"),
        "status": data.get("status", "Lead"),

        "customer": data.get("customer"),
        "lead_name": data.get("lead_name"),
        "mobile_no": data.get("whatsapp_no"),
        "phone": data.get("phone"),

        "lead_owner": frappe.session.user,
        "custom_assigned_to": data.get("assigned_to"),
        "custom_remarks": data.get("notes"),

        "industry": data.get("industry"),
        "company": frappe.db.get_single_value('Mobile App Settings','default_company') or data.get("company_name"),

        "email_id": data.get("email"),
        "address": data.get("address"),
        "annual_revenue": data.get("annual_revenue"),
        "number_of_employees": data.get("no_of_employees"),
        "first_name": data.get("lead_name"),
        "custom_view_follow_up_details_copy": []
    })

    if data.get("items"):
        item_list = data.get("items")
        for item in item_list:
            lead.append("custom_item_request_type",{
                'item': item
            })

    for f in followups:
        lead.append("custom_view_follow_up_details_copy", {
            "description": f.get("description"),
            "date": today(),
            "custom_enter_datetime": now_datetime(),
            "next_follow_up_date": f.get("next_follow_up_date"),
            "followed_by": f.get("followed_by", frappe.session.user),
            "status": f.get("status", "Lead")
        })

    lead.insert()
    frappe.db.commit()
    return {
        'success': True,
        'lead':lead.name
    }

@frappe.whitelist(allow_guest = False)
def log_employee_location(data):
    if isinstance(data, str):
        data = json.loads(data)

    latitude = data.get("lat")
    longitude = data.get("lng")
    log_time = data.get("time")

    if not latitude or not longitude:
        frappe.throw("Latitude/Longitude missing")

    user = frappe.session.user

    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if not employee:
        frappe.throw("Employee not linked to this user")

    today = nowdate()

    doc_name = frappe.db.get_value(
        "Employee Location Log",
        {"employee": employee, "date": today},
        "name"
    )

    if doc_name:
        doc = frappe.get_doc("Employee Location Log", doc_name)
    else:
        doc = frappe.get_doc({
            "doctype": "Employee Location Log",
            "employee": employee,
            "date": today,
            "total_updates": 0
        })

    doc.append("location", {
        "latitude": latitude,
        "longitude": longitude,
        "time": log_time
    })

    doc.total_updates = len(doc.location)

    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "status": "success",
        "employee": employee,
        "date": today,
        "updates": doc.total_updates
    }

@frappe.whitelist(allow_guest=False)
def add_followup():
    try:
        data = frappe.request.get_json()

        reference_doctype = data.get("reference_doctype")
        reference_name = data.get("reference_name")
        next_follow_up_date = data.get("next_follow_up_date")
        remarks = data.get("remarks")
        status = data.get("status")

        if not reference_doctype or not reference_name:
            frappe.throw("Reference is required")

        if not status:
            if not next_follow_up_date or not remarks:
                frappe.throw(
                    "Next follow-up date and remarks are required if status is not provided"
                )

        parent_doc = frappe.get_doc(reference_doctype, reference_name)

        for row in parent_doc.get("custom_view_follow_up_details_copy") or []:
            row.followed = 1
        if reference_doctype == 'Lead':
            follow_up = parent_doc.append("custom_view_follow_up_details_copy", {})
        elif reference_doctype == 'Quotation':
            follow_up = parent_doc.append("custom_followup", {})
            
        follow_up.followed_by = frappe.session.user
        follow_up.date = frappe.utils.nowdate()

        if next_follow_up_date:
            follow_up.next_follow_up_date = next_follow_up_date

        if remarks:
            follow_up.description = remarks

        if status:
            parent_doc.status = status

        parent_doc.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "success": True,
            "message": "Follow-up added successfully",
            "name": follow_up.name,
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Add Follow Up Error")
        return {
            "success": False,
            "error": str(e),
        }


@frappe.whitelist(allow_guest = False)
def get_field_options(doctype, fieldname):
    meta = frappe.get_meta(doctype)
    field = meta.get_field(fieldname)

    if not field:
        return []

    options = field.options or ""
    return [opt.strip() for opt in options.split("\n") if opt.strip()]


@frappe.whitelist(allow_guest=False)
def upload_attachment():
    try:
        doctype = frappe.form_dict.get("doctype")
        docname = frappe.form_dict.get("docname")
        file = frappe.request.files.get("file")

        if not doctype or not docname:
            return {
                "success": False,
                "message": "Missing doctype or docname"
            }

        if not file:
            return {
                "success": False,
                "message": "No file received"
            }

        if not frappe.db.exists(doctype, docname):
            return {
                "success": False,
                "message": "Document not found"
            }

        saved_file = save_file(
            fname=file.filename,
            content=file.stream.read(),
            dt=doctype,
            dn=docname,
            is_private=0
        )

        return {
            "success": True,
            "message": "File uploaded successfully",
            "file_url": saved_file.file_url,
            "file_name": saved_file.file_name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Upload Attachment Error")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist(allow_guest = False)
def update_followup_remarks(row_name, remarks):
    if not row_name:
        frappe.throw("Row name is required")

    row = frappe.db.get_value(
        "Follow-Up",
        row_name,
        ["name"],
        as_dict=True
    )

    if not row:
        frappe.throw("Follow-up not found")

    frappe.db.set_value(
        "Follow-Up",
        row_name,
        "description",
        remarks
    )

    frappe.db.commit()

    return "success"

@frappe.whitelist(allow_guest = False)
def update_lead():
    data = frappe.request.get_json()
    lead = frappe.get_doc("Lead", data.get("lead_id"))

    lead.lead_name = data.get("lead_name")
    lead.lead_owner = data.get("lead_owner")
    lead.status = data.get("status")

    lead.custom_assigned_to = data.get("assigned_to")
    lead.custom_allocated_to_manager = data.get("allocated_to_manager")

    lead.company = data.get("company_name")
    lead.source = data.get("lead_source")
    lead.customer = data.get("customer")
    lead.territory = data.get("territory")
    lead.industry = data.get("industry")

    lead.email_id = data.get("email")
    lead.mobile_no = data.get("phone")
    lead.phone = data.get("whatsapp_no")

    lead.address = data.get("address")
    lead.annual_revenue = data.get("annual_revenue")
    lead.number_of_employees = data.get("no_of_employees")
    lead.custom_remarks = data.get("notes")

    lead.save(ignore_permissions=True)
    frappe.db.commit()

    return {"success": True}


@frappe.whitelist(allow_guest=False)
def update_lead_with_followup():
    data = frappe.request.get_json()
    lead_id = data.get("lead_id")

    if not lead_id:
        frappe.throw("Lead ID is required")

    lead = frappe.get_doc("Lead", lead_id)

    lead.source = data.get("lead_source")
    lead.custom_allocated_to_manager = data.get("allocated_to_manager")
    lead.territory = data.get("territory")
    lead.status = data.get("status", lead.status)

    lead.customer = data.get("customer")
    lead.lead_name = data.get("lead_name")
    lead.mobile_no = data.get("phone")
    lead.phone = data.get("whatsapp_no")

    lead.lead_owner = data.get("lead_owner")
    lead.custom_assigned_to = data.get("assigned_to")
    lead.custom_remarks = data.get("notes")

    lead.industry = data.get("industry")
    lead.company = data.get("company_name")

    lead.email_id = data.get("email")
    lead.address = data.get("address")
    lead.annual_revenue = data.get("annual_revenue")
    lead.number_of_employees = data.get("no_of_employees")

    lead.set("custom_item_request_type", [])

    raw_items = data.get("items") or []
    items = json.loads(raw_items) if isinstance(raw_items, str) else raw_items

    for item in items:
        lead.append("custom_item_request_type", {
            "item": item
        })

    raw_followups = data.get("follow_ups") or "[]"
    followups = json.loads(raw_followups) if isinstance(raw_followups, str) else raw_followups

    for f in followups:
        lead.append("custom_view_follow_up_details_copy", {
            "description": f.get("description"),
            "date": today(),
            "custom_enter_datetime": now_datetime(),
            "next_follow_up_date": f.get("next_follow_up_date"),
            "followed_by": frappe.session.user,
            "status": lead.status
        })

    lead.save()
    frappe.db.commit()

    return {
        "success": True,
        "lead": lead.name
    }

@frappe.whitelist(allow_guest = False)
def get_quotation_metadata():
    companies = frappe.get_all(
        "Company",
        fields=["name", "default_gst_rate"]
    )

    items = frappe.get_all(
        "Item",
        filters={"disabled": 0},
        fields=[
            "name as item_code",
            "item_name",
            "stock_uom",
            "standard_rate",
        ]
    )

    territory = frappe.get_all('Territory',pluck = 'name')

    user = frappe.get_all('User',filters = {'enabled': 1},pluck = 'name')

    for item in items:
        item["tax_rate"] = 0

        if item.get("item_tax_template"):
            tax = frappe.get_all(
                "Item Tax",
                filters={"parent": item["item_tax_template"]},
                fields=["tax_rate"],
                limit=1
            )
            if tax:
                item["tax_rate"] = tax[0]["tax_rate"]

    customers = frappe.get_all(
        "Customer",
        filters={"disabled": 0},
        fields=["name", "customer_name", "territory","tax_category"]
    )

    leads = frappe.get_all(
        "Lead",
        filters={"status": ["!=", "Converted"]},
        fields=["name", "lead_name", "company_name"]
    )

    tax_categories = frappe.get_all(
        "Tax Category",
        filters={"disabled": 0},
        pluck="name"
    )

    sales_tax_templates = frappe.get_all(
        "Sales Taxes and Charges Template",
        filters={
            "disabled": 0
        },
        fields=["name", "title","company","tax_category"]
    )

    price_lists = frappe.get_all(
        "Price List",
        filters={
            "selling": 1,
            "enabled": 1
        },
        pluck="name"
    )

    taxes = frappe.get_all(
        "Sales Taxes and Charges Template",
        filters={"disabled": 0},
        fields=["name", "title","company","tax_category"]
    )

    quotation_types = [
        "FIRE EXTINGUISHER",
        "FIRE ALARM",
        "HYDRANT",
        "FIRE FLOODING",
        "FIRE EXTINGUISHER & FIRE ALARM",
        "FIRE HYDRANT & FIRE ALARM",
        "FIRE EXTINGUISHER & FIRE HYDRANT",
        "FIRE EXTINGUISHER & FIRE ALARM, FIRE HYDRANT"
    ]

    return {
        "items": items,
        "customers": customers,
        "leads": leads,
        "territory": territory,
        "tax_categories": tax_categories,
        "sales_tax_templates": sales_tax_templates,
        "price_lists": price_lists,
        "users": user,
        "taxes": taxes,
        "companies": companies,
        "quotation_types": quotation_types
    }

@frappe.whitelist(allow_guest = False)
def get_tax_template_details(template_name):
    return frappe.get_all(
        "Sales Taxes and Charges",
        filters={"parent": template_name},
        fields=[
            "charge_type",
            "account_head",
            "rate",
            "description"
        ],
        order_by="idx"
    )

@frappe.whitelist(allow_guest = False)
def get_item_price(item_code, price_list="Standard Selling"):
    price = frappe.db.get_value(
        "Item Price",
        {
            "item_code": item_code,
            "price_list": price_list,
            "selling": 1
        },
        "price_list_rate"
    )

    return {
        "rate": price or 0
    }

@frappe.whitelist(allow_guest=False)
def validate_quotation(data):
    data = frappe.parse_json(data)
    errors = []
    warnings = []

    if not data.get("party_name"):
        errors.append("Party Name is required")

    items = data.get("items", [])
    if not items:
        errors.append("At least one item is required")

    total = 0

    for item in items:
        qty = flt(item.get("qty"))
        rate = flt(item.get("rate"))
        discount = flt(item.get("discount_amount"))

        if qty <= 0:
            errors.append(f"Invalid qty for {item.get('item_code')}")

        amount = (qty * rate) - discount
        item["amount"] = flt(amount, 2)

        total += amount

    discount_amount = flt(data.get("discount_amount"))
    discount_on = data.get("discount_on")

    total_tax = 0
    taxes = []

    def calculate_tax(taxable_amount):
        nonlocal total_tax, taxes
        total_tax = 0
        taxes = []

        tax_rules = frappe.get_all(
            "Sales Taxes and Charges",
            filters={"parent": data.get("tax_category")},
            fields=["rate", "account_head"]
        )

        for tax in tax_rules:
            tax_amount = taxable_amount * flt(tax.rate) / 100
            total_tax += tax_amount

            taxes.append({
                "account_head": tax.account_head,
                "rate": tax.rate,
                "tax_amount": flt(tax_amount, 2)
            })

    if discount_on == "net_total":
        net_total = total - discount_amount
        calculate_tax(net_total)
        grand_total = net_total + total_tax

    else:
        calculate_tax(total)
        net_total = total
        grand_total = (total + total_tax) - discount_amount

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "totals": {
            "total": flt(total, 2),
            "net_total": flt(net_total, 2),
            "discount_amount": discount_amount,
            "tax_total": flt(total_tax, 2),
            "grand_total": flt(grand_total, 2)
        },
        "items": items,
        "taxes": taxes
    }

    
@frappe.whitelist(allow_guest = False)
def create_quotation(data):
    data = frappe.parse_json(data)

    validation = validate_quotation(data)
    if not validation["valid"]:
        return {
            "valid": False,
            "errors": validation["errors"]
        }

    try:
        quotation_id = data.get("name") or data.get("quotation_id")

        if quotation_id and frappe.db.exists("Quotation", quotation_id):
            doc = frappe.get_doc("Quotation", quotation_id)
            doc.items = []
            doc.taxes = []
        else:
            doc = frappe.new_doc("Quotation")

        doc.quotation_to = data.get("quotation_to")
        doc.party_name = data.get("party_name")
        doc.discount_amount = data.get("discount_amount")
        doc.apply_discount_on = data.get("discount_on")
        doc.custom_kind_attn = data.get("kind_attention")
        doc.custom_region = data.get("territory")
        doc.custom_phone = data.get("custom_phone")
        doc.tax_category = frappe.db.get_value("Customer", data.get("party_name"), "tax_category") or data.get("tax_category")
        doc.company = frappe.db.get_single_value('Mobile App Settings','default_company') or data.get("company")

        doc.price_list = frappe.db.get_single_value('Mobile App Settings','default_price_list') or data.get("price_list")
        doc.taxes_and_charges = frappe.db.get_single_value('Mobile App Settings','default_sales_taxes_and_charges_template') or data.get("tax_template")
        doc.custom_type_of_quotation = data.get("custom_type_of_quotation")

        for item in data.get("items", []):
            doc.append("items", {
                "item_code": item.get("item_code"),
                "qty": item.get("qty"),
                "uom": item.get("uom"),
                "rate": item.get("rate") - item.get("discount_amount", 0),
            })

        for tax in validation.get("taxes", []):
            doc.append("taxes", {
                "charge_type": "On Net Total",
                "account_head": tax.get("account_head"),
                "rate": tax.get("rate"),
                "description": tax.get("account_head"),
            })

        doc.set_missing_values()
        doc.calculate_taxes_and_totals()

        doc.save()

        return {
            "valid": True,
            "name": doc.name,
            "grand_total": doc.grand_total,
            "updated": bool(quotation_id)
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Create/Update Quotation Error")
        return {
            "valid": False,
            "errors": ["Something went wrong while saving quotation"]
        }


@frappe.whitelist(allow_guest = False)
def get_quotation_details(name):
    doc = frappe.get_doc("Quotation", name)

    return doc.as_dict()

@frappe.whitelist(allow_guest = False)
def get_quotation(id):
    if not id:
        frappe.throw("Quotation ID is required")

    if not frappe.db.exists("Quotation", id):
        frappe.throw("Quotation not found")

    doc = frappe.get_doc("Quotation", id)

    return {
        "name": doc.name,
        "quotation_to": doc.quotation_to,
        "party_name": doc.party_name,
        "discount_amount": doc.discount_amount,
        "discount_on": doc.apply_discount_on,
        "kind_attention": doc.custom_kind_attn,
        "territory": doc.custom_region,
        "custom_phone": doc.custom_phone,

        "items": [
            {
                "item_code": d.item_code,
                "item_name": d.item_name,
                "qty": d.qty,
                "uom": d.uom,
                "rate": d.rate,
                "discount_amount": d.discount_amount,
            }
            for d in doc.items
        ],

        "taxes": [
            {
                "charge_type": d.charge_type,
                "account_head": d.account_head,
                "rate": d.rate,
                "tax_amount": d.tax_amount,
            }
            for d in doc.taxes
        ],

        "totals": {
            "net_total": doc.net_total,
            "tax_total": doc.total_taxes_and_charges,
            "grand_total": doc.grand_total,
        }
    }

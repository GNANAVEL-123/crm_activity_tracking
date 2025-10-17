import frappe
import requests
from hrms.hr.doctype.leave_application.leave_application import get_leave_details
from frappe.utils import cint, comma_or, cstr, flt, format_time, formatdate, getdate, nowdate, today
import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

def leave_allocation():
    current_date = frappe.utils.nowdate()
    current_date = datetime.strptime(current_date, "%Y-%m-%d").date()

    # First and Last Day of Current Month
    start_date_current_month = current_date.replace(day=1)
    last_day_of_month = calendar.monthrange(current_date.year, current_date.month)[1]
    end_date_current_month = current_date.replace(day=last_day_of_month)

    # First and Last Day of Previous Month
    last_day_of_previous_month = start_date_current_month - relativedelta(days=1)
    first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

    # Run Only on 1st of Month
    if current_date == start_date_current_month:
        emp_list = frappe.db.get_all("Employee", filters={"status": "Active"}, fields=["name", "employee_name", "company"])

        if emp_list:
            for emp in emp_list:
                try:
                    # Create Leave Allocation
                    leave_allocation = frappe.new_doc("Leave Allocation")
                    leave_allocation.employee = emp.name
                    leave_allocation.leave_type = "Pay Leave"  # Change this if needed
                    leave_allocation.from_date = start_date_current_month
                    leave_allocation.to_date = end_date_current_month
                    leave_allocation.new_leaves_allocated = 1
                    leave_allocation.carry_forward = 1
                    leave_allocation.company = emp.company
                    leave_allocation.save()
                    leave_allocation.submit()

                    # Log Success
                    frappe.log_error(title="Leave Allocation - Success", message=f"{emp.employee_name} - {leave_allocation.name}")

                except Exception as e:
                    frappe.log_error(title="Leave Allocation - Error", message=f"Error for {emp.employee_name}: {str(e)}")

def schedule_whatsapp_message():
    list_of_docs = frappe.get_list('Whatsapp Log',{'status':'Not Sent'},limit='1')
    for doc in list_of_docs:
        request_url = frappe.get_value('Whatsapp Log',doc.name,'request_url')
        payload={}
        headers = {}
        try:
            response = requests.request("GET", request_url, headers=headers, data=payload)
            frappe.db.set_value('Whatsapp Log',doc.name,'status','Success')
            frappe.db.set_value('Whatsapp Log',doc.name,'response',str(response.json()))

        except Exception as e:
            frappe.db.set_value('Whatsapp Log',doc.name,'status','Failure')
            frappe.db.set_value('Whatsapp Log',doc.name,'response',str(response.json()))

import frappe
from frappe.utils import getdate, today

def quotation_tracking_email_send():
    # Get quotations in Draft, Open, or Expired status, excluding Cancelled
    quo_list = frappe.db.get_all(
        "Quotation",
        filters={
            "status": ["in", ["Draft", "Open", "Expired"]],
            "docstatus": ["!=", 2]
        },
        fields=["name"]
    )

    # Try to get the email template
    try:
        template_doc = frappe.get_doc("Email Template", "Quotation Tracking Email Template")
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Quotation Tracking: Failed to fetch Email Template")
        return

    if not template_doc:
        frappe.log_error("Missing Template", "Quotation Tracking Email Template not found")
        return

    # Process each quotation
    for quo in quo_list:
        quo_doc = frappe.get_doc("Quotation", quo.name)
        followups = quo_doc.custom_followup

        if followups:
            # Directly get the last follow-up srosw
            last_row = followups[-1]
            row_date = last_row.next_follow_up_date

            # If last follow-up date is today, send the email
            if row_date and getdate(row_date) == getdate(today()):
            # if quo.name == "HFP-QTN-2025-02578":
                # email_id = frappe.db.get_value("Address", quo_doc.customer_address, "email_id")
                email_id = quo_doc.custom_tracking_email_id
                if email_id:
                    message = frappe.render_template(template_doc.response_html, {"doc": quo_doc})
                    frappe.sendmail(
                        recipients=email_id,
                        subject=template_doc.subject or f"Quotation: {quo_doc.name}",
                        message=message,
                        reference_doctype="Quotation",
                        reference_name=quo_doc.name,
                        send_priority=1,
                        sender="admin@harshinifire.com",
                    )


def task_tracking_email_send():
    task_list = frappe.get_all(
        "Task",
        filters={
            "status": ["in", ["Open", "Overdue"]],
        },
        or_filters=[
            {"custom_refilling": 1},
            {"custom_amc": 1}
        ],
        fields=["name"]
    )

    try:
        template_doc = frappe.get_doc("Email Template", "Task Tracking Email Template")
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Task Tracking: Failed to fetch Email Template")
        return
    if not template_doc:
        frappe.log_error("Missing Template", "Task Tracking Email Template not found")
        return
    for task in task_list:
        task_doc = frappe.get_doc("Task", task.name)
        followups = task_doc.custom_view_follow_up_details_copy
        if followups and len(followups) > 0:
            for i in range(len(followups)):
                row = followups[i]
                if i == len(followups) - 1:
                    row_date = row.next_follow_up_date
                    if row_date and getdate(row_date) == getdate(today()):
                        email_id = task_doc.custom_email_id
                        if email_id:
                            message = frappe.render_template(template_doc.response_html, {"doc": task_doc})
                            frappe.sendmail(
                                recipients=email_id,
                                subject=template_doc.subject or f"Task: {task_doc.name}",
                                message=message,
                                reference_doctype="Task",
                                reference_name=task_doc.name,
                                send_priority=1,
                                sender="admin@harshinifire.com",
                            )
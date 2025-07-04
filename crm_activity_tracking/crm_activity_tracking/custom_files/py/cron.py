import frappe
import requests
from hrms.hr.doctype.leave_application.leave_application import get_leave_details
from frappe.utils import cint, comma_or, cstr, flt, format_time, formatdate, getdate, nowdate
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
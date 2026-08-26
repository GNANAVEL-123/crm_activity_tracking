# Copyright (c) 2026, CRM and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    filters = filters or {}

    validate_filters(filters)

    doctype = get_doctype(filters)
    columns = get_columns(doctype)
    data = get_data(doctype, filters)

    return columns, data


def validate_filters(filters):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    if from_date and to_date and from_date > to_date:
        frappe.throw("From Date cannot be greater than To Date.")

    fire_extinguisher = filters.get("fire_extinguisher")
    fire_alarm = filters.get("fire_alarm")
    fire_hydrant = filters.get("fire_hydrant")

    selected_count = sum(
        bool(value)
        for value in [
            fire_extinguisher,
            fire_alarm,
            fire_hydrant
        ]
    )

    if selected_count == 0:
        frappe.throw(
            "Please select Fire Extinguisher, Fire Alarm, or Fire Hydrant."
        )

    if selected_count > 1:
        frappe.throw(
            "Please select only one service type."
        )


def get_doctype(filters):
    if filters.get("fire_extinguisher"):
        return "AMC Visitor Tracking"

    elif filters.get("fire_alarm"):
        return "AMC Fire Alarm Tracking"

    elif filters.get("fire_hydrant"):
        return "AMC Fire Hydrant Tracking"

    return None


def get_columns(doctype):
    # Same column layout is used for all three service types
    # (Fire Extinguisher, Fire Alarm, Fire Hydrant)
    return [
        {
            "label": "S.No",
            "fieldname": "idx",
            "fieldtype": "Int",
            "width": 60
        },
        {
            "label": "Next Date",
            "fieldname": "next_date",
            "fieldtype": "Date",
            "width": 110
        },
        {
            "label": "Company",
            "fieldname": "company",
            "fieldtype": "Data",
            "width": 220
        },
        {
            "label": "Location",
            "fieldname": "location",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "No. of Extn Portable",
            "fieldname": "no_of_extn_portable",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "label": "No. of Extn Trolley",
            "fieldname": "no_of_extn_trolley",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "label": "AMC Service Date",
            "fieldname": "amc_service_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": "AMC Due",
            "fieldname": "next_amc_service_due_date",
            "fieldtype": "Date",
            "width": 150
        },
        {
            "label": "Invoice No",
            "fieldname": "invoice_no",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "Invoice Date",
            "fieldname": "invoice_date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": "QTN No",
            "fieldname": "qtn_no",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": "QTN Date",
            "fieldname": "qtn_date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": "Customer Mail ID",
            "fieldname": "customer_mail_id",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": "Customer Mobile Number",
            "fieldname": "customer_mobile_number",
            "fieldtype": "Data",
            "width": 140
        },
        {
            "label": "Service By",
            "fieldname": "service_by",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": "Status",
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 130
        }
    ]


def get_data(doctype, filters):
    if not doctype:
        return []

    return get_doctype_data(doctype, filters)


def get_doctype_data(doctype, filters):

    conditions = []
    values = {}

    if filters.get("from_date"):
        conditions.append(
            "amc_service_date >= %(from_date)s"
        )
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append(
            "amc_service_date <= %(to_date)s"
        )
        values["to_date"] = filters.get("to_date")

    where_condition = ""

    if conditions:
        where_condition = "WHERE " + " AND ".join(conditions)

    if doctype == "AMC Fire Alarm Tracking":
        query = f"""
            SELECT
                name,

                amc_service_date,
                next_amc_service_due_date,

                customer_name AS company,
                region AS location,

                NULL AS no_of_extn_portable,
                NULL AS no_of_extn_trolley,

                NULL AS invoice_no,

                mail_id AS customer_mail_id,

                cr__contact_number AS customer_mobile_number,

                employee_name  AS service_by,
                NULL AS status,
                NULL AS invoice_date,
                NULL AS qtn_no,
                NULL AS qtn_date

            FROM `tab{doctype}`

            {where_condition}

            ORDER BY amc_service_date
        """
    elif doctype == "AMC Fire Hydrant Tracking":
        query = f"""
            SELECT
                name,

                amc_service_date,
                next_amc_service_due_date,

                customer_name AS company,
                region AS location,

                NULL AS no_of_extn_portable,
                NULL AS no_of_extn_trolley,

                invoice_no,

                mail_id AS customer_mail_id,

                cr__contact_number AS customer_mobile_number,

                service_by,
                NULL AS status,
                NULL AS invoice_date,

                quotation_no AS qtn_no,
                NULL AS qtn_date

            FROM `tab{doctype}`

            {where_condition}

            ORDER BY amc_service_date
        """
    else:
        query = f"""
            SELECT
                name,

                amc_service_date,
                next_amc_service_due_date,

                customer_name AS company,
                location,

                number_of_portable_fire_extinguisher
                    AS no_of_extn_portable,

                number_of_trolley_fireextinguisher
                    AS no_of_extn_trolley,

                invoice_number AS invoice_no,

                mail_id AS customer_mail_id,

                contact_number AS customer_mobile_number,

                service_by, status,

                NULL AS invoice_date,
                NULL AS qtn_no,
                NULL AS qtn_date

            FROM `tab{doctype}`

            {where_condition}

            ORDER BY amc_service_date
        """

    data = frappe.db.sql(
        query,
        values,
        as_dict=True
    )

    for idx, row in enumerate(data, start=1):
        row["idx"] = idx
        row["next_date"] = row.get(
            "next_amc_service_due_date"
        )

    return data
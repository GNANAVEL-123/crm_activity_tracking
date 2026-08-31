# Copyright (c) 2026, CRM and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    filters = filters or {}

    validate_filters(filters)

    doctypes = get_doctypes(filters)
    columns = get_columns()
    data = get_data(doctypes, filters)

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


def get_doctypes(filters):
    # Returns a list of doctypes to pull data from, based on
    # which checkboxes are selected. Multiple can be selected
    # together now, so this returns all matching doctypes.
    doctypes = []

    if filters.get("fire_extinguisher"):
        doctypes.append("AMC Visitor Tracking")

    if filters.get("fire_alarm"):
        doctypes.append("AMC Fire Alarm Tracking")

    if filters.get("fire_hydrant"):
        doctypes.append("AMC Fire Hydrant Tracking")

    return doctypes


def get_columns():
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
            "label": "Service Type",
            "fieldname": "service_type",
            "fieldtype": "Data",
            "width": 130
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


def get_data(doctypes, filters):
    if not doctypes:
        return []

    all_data = []

    for doctype in doctypes:
        rows = get_doctype_data(doctype, filters)
        all_data.extend(rows)

    # Sort combined results by AMC due date
    all_data.sort(
        key=lambda r: (r.get("next_amc_service_due_date") is None, r.get("next_amc_service_due_date"))
    )

    for idx, row in enumerate(all_data, start=1):
        row["idx"] = idx

    return all_data


def get_doctype_data(doctype, filters):

    conditions = []
    values = {}

    if filters.get("from_date"):
        conditions.append(
            "next_amc_service_due_date >= %(from_date)s"
        )
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append(
            "next_amc_service_due_date <= %(to_date)s"
        )
        values["to_date"] = filters.get("to_date")

    # "region" is stored under a different column per doctype:
    # - AMC Fire Alarm Tracking / AMC Fire Hydrant Tracking -> "region"
    # - AMC Visitor Tracking (Fire Extinguisher)             -> "location"
    if filters.get("region"):
        if doctype == "AMC Visitor Tracking":
            conditions.append("location = %(region)s")
        else:
            conditions.append("region = %(region)s")
        values["region"] = filters.get("region")

    where_condition = ""

    if conditions:
        where_condition = "WHERE " + " AND ".join(conditions)

    if doctype == "AMC Fire Alarm Tracking":
        service_type_label = "Fire Alarm"
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

            ORDER BY next_amc_service_due_date
        """
    elif doctype == "AMC Fire Hydrant Tracking":
        service_type_label = "Fire Hydrant"
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

            ORDER BY next_amc_service_due_date
        """
    else:
        service_type_label = "Fire Extinguisher"
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

            ORDER BY next_amc_service_due_date
        """

    data = frappe.db.sql(
        query,
        values,
        as_dict=True
    )

    for row in data:
        row["service_type"] = service_type_label
        row["next_date"] = row.get("next_amc_service_due_date")
        row["next_amc_service_due_date"] = None

    return data
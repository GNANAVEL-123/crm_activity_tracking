// Copyright (c) 2026, CRM and contributors
// For license information, please see license.txt

frappe.query_reports["AMC Visitor Tracking Reports"] = {
    filters: [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.month_start()
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.get_today()
        },
        {
            fieldname: "fire_extinguisher",
            label: "Fire Extinguisher",
            fieldtype: "Check",
            default:1,
            on_change: function () {
                let checked = frappe.query_report.get_filter_value("fire_extinguisher");

                if (checked) {
                    frappe.query_report.set_filter_value("fire_alarm", 0);
                    frappe.query_report.set_filter_value("fire_hydrant", 0);
                }
            }
        },
        {
            fieldname: "fire_alarm",
            label: "Fire Alarm",
            fieldtype: "Check",
            on_change: function () {
                let checked = frappe.query_report.get_filter_value("fire_alarm");

                if (checked) {
                    frappe.query_report.set_filter_value("fire_extinguisher", 0);
                    frappe.query_report.set_filter_value("fire_hydrant", 0);
                }
            }
        },
        {
            fieldname: "fire_hydrant",
            label: "Fire Hydrant",
            fieldtype: "Check",
            on_change: function () {
                let checked = frappe.query_report.get_filter_value("fire_hydrant");

                if (checked) {
                    frappe.query_report.set_filter_value("fire_extinguisher", 0);
                    frappe.query_report.set_filter_value("fire_alarm", 0);
                }
            }
        }
    ],

    onload: function (report) {
        report.page.add_inner_button("Clear Selection", function () {
            frappe.query_report.set_filter_value("fire_extinguisher", 0);
            frappe.query_report.set_filter_value("fire_alarm", 0);
            frappe.query_report.set_filter_value("fire_hydrant", 0);
            frappe.query_report.refresh();
        });
    },

    before_refresh: function (report) {
        let from_date = frappe.query_report.get_filter_value("from_date");
        let to_date = frappe.query_report.get_filter_value("to_date");

        if (from_date && to_date && from_date > to_date) {
            frappe.throw("From Date cannot be greater than To Date.");
        }

        let fire_extinguisher = frappe.query_report.get_filter_value("fire_extinguisher");
        let fire_alarm = frappe.query_report.get_filter_value("fire_alarm");
        let fire_hydrant = frappe.query_report.get_filter_value("fire_hydrant");

        if (!fire_extinguisher && !fire_alarm && !fire_hydrant) {
            frappe.throw("Please select Fire Extinguisher, Fire Alarm, or Fire Hydrant.");
        }
    }
};
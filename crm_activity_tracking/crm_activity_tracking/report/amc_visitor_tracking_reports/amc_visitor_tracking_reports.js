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
            fieldname: "region",
            label: "Region",
            fieldtype: "Link",
            options: "Territory",
        },
        {
            fieldname: "fire_extinguisher",
            label: "Fire Extinguisher",
            fieldtype: "Check",
            default: 1
            // no longer unchecks the other two — multiple can be selected together
        },
        {
            fieldname: "fire_alarm",
            label: "Fire Alarm",
            fieldtype: "Check"
        },
        {
            fieldname: "fire_hydrant",
            label: "Fire Hydrant",
            fieldtype: "Check"
        }
    ],

    onload: function (report) {
        report.page.add_inner_button("Clear Selection", function () {
            frappe.query_report.set_filter_value("fire_extinguisher", 0);
            frappe.query_report.set_filter_value("fire_alarm", 0);
            frappe.query_report.set_filter_value("fire_hydrant", 0);
            frappe.query_report.refresh();
        });
		report.page.add_inner_button("Print View", function () {
			print_amc_report(report);
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


function format_ddmmyyyy(date_str) {
	if (!date_str) return "";
	// Handles "YYYY-MM-DD" or "YYYY-MM-DD HH:mm:ss" input
	const datePart = String(date_str).split(" ")[0];
	const parts = datePart.split("-");
	if (parts.length !== 3) return date_str; // fallback: return as-is if unexpected format
	const [yyyy, mm, dd] = parts;
	return `${dd}-${mm}-${yyyy}`;
}

function print_amc_report(report) {
	// Pull the currently rendered report rows
	const data = frappe.query_report.data || [];

	if (!data.length) {
		frappe.msgprint("No data to print. Please run the report first.");
		return;
	}

	const filters = frappe.query_report.get_filter_values() || {};

	// Title reflects which checkbox(es) are selected
	const selected_labels = [];
	if (filters.fire_extinguisher) selected_labels.push("Fire Extinguisher");
	if (filters.fire_alarm) selected_labels.push("Fire Alarm");
	if (filters.fire_hydrant) selected_labels.push("Fire Hydrant");

	let title = "AMC Service Report";
	if (selected_labels.length === 1) {
		title = `${selected_labels[0]} Service Report`;
	} else if (selected_labels.length > 1) {
		title = `${selected_labels.join(" + ")} Service Report`;
	}

	const rows = data
		.map(
			(row, i) => `
		<tr>
			<td class="num-col">${i + 1}</td>
			<td>${row.service_type || ""}</td>
			<td>${format_ddmmyyyy(row.next_date)}</td>
			<td>${row.company || ""}</td>
			<td>${row.location || ""}</td>
			<td class="num-col">${row.no_of_extn_portable || ""}</td>
			<td class="num-col">${row.no_of_extn_trolley || ""}</td>
			<td>${format_ddmmyyyy(row.amc_service_date)}</td>
			<td>${format_ddmmyyyy(row.next_amc_service_due_date)}</td>
			<td>${row.invoice_no || ""}</td>
			<td>${format_ddmmyyyy(row.invoice_date)}</td>
			<td>${row.qtn_no || ""}</td>
			<td>${format_ddmmyyyy(row.qtn_date)}</td>
			<td>${row.customer_mail_id || ""}</td>
			<td>${row.customer_mobile_number || ""}</td>
			<td>${row.service_by || ""}</td>
		</tr>`
		)
		.join("");

	const html = `
	<!DOCTYPE html>
	<html>
	<head>
		<meta charset="utf-8">
		<title>${title}</title>
		<style>
			* {
				box-sizing: border-box;
			}
			body {
				font-family: 'Segoe UI', Arial, sans-serif;
				color: #1f2937;
				padding: 18px 22px;
				margin: 0;
			}
			.amc-header {
				display: flex;
				justify-content: space-between;
				align-items: center;
				background: linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%);
				color: #ffffff;
				border-radius: 8px;
				padding: 14px 20px;
				margin-bottom: 16px;
				box-shadow: 0 2px 6px rgba(0,0,0,0.15);
			}
			.amc-header .title-block h1 {
				font-size: 20px;
				margin: 0;
				letter-spacing: 0.4px;
				font-weight: 700;
			}
			.amc-header .title-block p {
				margin: 4px 0 0;
				font-size: 10.5px;
				opacity: 0.85;
			}
			.amc-header .meta-block {
				text-align: right;
				font-size: 10.5px;
				line-height: 1.6;
			}
			.amc-header .meta-block b {
				font-weight: 700;
			}
			table.amc-table {
				width: 100%;
				border-collapse: collapse;
				font-size: 9.5px;
				table-layout: fixed;
			}
			table.amc-table thead th {
				background: linear-gradient(180deg, #dc2626 0%, #991b1b 100%);
				color: #ffffff;
				text-align: left;
				padding: 8px 6px;
				font-weight: 600;
				border: 1px solid #7f1d1d;
				white-space: normal;
				word-break: break-word;
				line-height: 1.25;
				vertical-align: bottom;
			}
			table.amc-table tbody td {
				padding: 6px;
				border: 1px solid #e5e7eb;
				word-wrap: break-word;
				vertical-align: top;
			}
			table.amc-table tbody tr:nth-child(even) {
				background: #fef2f2;
			}
			table.amc-table tbody tr:hover {
				background: #fee2e2;
			}
			table.amc-table tbody td.num-col {
				text-align: center;
			}
			.amc-footer {
				margin-top: 14px;
				display: flex;
				justify-content: space-between;
				font-size: 9.5px;
				color: #6b7280;
				border-top: 2px solid #b91c1c;
				padding-top: 6px;
			}
			@media print {
				body { padding: 8px 12px; }
				.amc-header,
				table.amc-table thead th,
				table.amc-table tbody tr:nth-child(even) {
					-webkit-print-color-adjust: exact;
					print-color-adjust: exact;
				}
			}
		</style>
	</head>
	<body>
		<div class="amc-header">
			<div class="title-block">
				<h1>${title}</h1>
				<p>AMC Tracking &amp; Service Schedule</p>
			</div>
			<div class="meta-block">
				<div>Printed on: <b>${format_ddmmyyyy(frappe.datetime.get_today())}</b></div>
				${filters.from_date ? `<div>From: <b>${format_ddmmyyyy(filters.from_date)}</b></div>` : ""}
				${filters.to_date ? `<div>To: <b>${format_ddmmyyyy(filters.to_date)}</b></div>` : ""}
			</div>
		</div>

		<table class="amc-table">
			<thead>
				<tr>
					<th style="width:3%;">S.No</th>
					<th style="width:7%;">Service Type</th>
					<th style="width:6%;">Next Date</th>
					<th style="width:12%;">Company</th>
					<th style="width:7%;">Location</th>
					<th style="width:6%;">No. of Extn Portable</th>
					<th style="width:6%;">No. of Extn Trolly</th>
					<th style="width:6%;">AMC Date</th>
					<th style="width:6%;">AMC Due</th>
					<th style="width:6%;">Invoice No</th>
					<th style="width:6%;">Invoice Date</th>
					<th style="width:5%;">QTN No</th>
					<th style="width:5%;">QTN Date</th>
					<th style="width:9%;">Customer Mail ID</th>
					<th style="width:6.5%;">Customer Mobile Number</th>
					<th style="width:7.5%;">Service Person Names</th>
				</tr>
			</thead>
			<tbody>
				${rows}
			</tbody>
		</table>

		<div class="amc-footer">
			<span>Total Records: ${data.length}</span>
			<span>Generated via CRM — ${title}</span>
		</div>
	</body>
	</html>
	`;

	const print_window = window.open("", "_blank");
	print_window.document.write(html);
	print_window.document.close();

	// give the browser a moment to render before triggering print
	setTimeout(() => {
		print_window.focus();
		print_window.print();
	}, 300);
}
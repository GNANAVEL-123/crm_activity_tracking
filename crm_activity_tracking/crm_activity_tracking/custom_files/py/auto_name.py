import frappe
from frappe.model.naming import parse_naming_series, make_autoname, revert_series_if_last
from datetime import date
from erpnext.accounts.utils import get_fiscal_year


def sales_inv_naming(doc, event):
    fy_year = get_fiscal_year(doc.posting_date, as_dict=True)  # Use posting date for fiscal year
    if fy_year:
        start_year = str(fy_year["year_start_date"].year)[-2:]  # Extract last 2 digits
        end_year = str(fy_year["year_end_date"].year)[-2:]
        fy_string = f"{start_year}-{end_year}"
        if not doc.is_return:
            doc.name = make_autoname(f"HFPES/{fy_string}/.#")

def si_delete(doc, event):
    fy_year = get_fiscal_year(doc.posting_date, as_dict=True)
    if fy_year:
        start_year = str(fy_year["year_start_date"].year)[-2:]
        end_year = str(fy_year["year_end_date"].year)[-2:]
        fy_string = f"{start_year}-{end_year}"
        if not doc.is_return:
            revert_series_if_last(f"HFPES/{fy_string}/.#", doc.name)

def dn_naming(doc, event):
    fy_year = get_fiscal_year(doc.posting_date, as_dict=True)  # Use posting date for fiscal year
    if fy_year:
        start_year = str(fy_year["year_start_date"].year)[-2:]  # Extract last 2 digits
        end_year = str(fy_year["year_end_date"].year)[-2:]
        fy_string = f"{start_year}-{end_year}"
        if not doc.is_return:
            doc.name = make_autoname(f"HFPES/{fy_string}/DC-.#")

def dn_delete(doc, event):
    fy_year = get_fiscal_year(doc.posting_date, as_dict=True)
    if fy_year:
        start_year = str(fy_year["year_start_date"].year)[-2:]
        end_year = str(fy_year["year_end_date"].year)[-2:]
        fy_string = f"{start_year}-{end_year}"
        if not doc.is_return:
            revert_series_if_last(f"HFPES/{fy_string}/DC-.#", doc.name)

def po_naming(doc, event):
    fy_year = get_fiscal_year(doc.transaction_date, as_dict=True)  # Use posting date for fiscal year
    if fy_year:
        start_year = str(fy_year["year_start_date"].year)[-2:]  # Extract last 2 digits
        end_year = str(fy_year["year_end_date"].year)[-2:]
        fy_string = f"{start_year}-{end_year}"
        doc.name = make_autoname(f"HFPES/{fy_string}/PO-.#")

def po_delete(doc, event):
    fy_year = get_fiscal_year(doc.transaction_date, as_dict=True)
    if fy_year:
        start_year = str(fy_year["year_start_date"].year)[-2:]
        end_year = str(fy_year["year_end_date"].year)[-2:]
        fy_string = f"{start_year}-{end_year}"
        revert_series_if_last(f"HFPES/{fy_string}/PO-.#", doc.name)
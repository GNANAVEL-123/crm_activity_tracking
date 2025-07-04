from erpnext.controllers.taxes_and_totals import get_itemised_tax
import frappe
from frappe.utils.data import cint

def get_invoice_item_and_tax_details(voucher_type, voucher_no):
    doc = frappe.get_doc(voucher_type, voucher_no)
    itemised_tax = get_itemised_tax(doc.taxes)
    items = doc.items
    instate = False
    total_cgst, total_sgst, total_igst = 0, 0, 0
    tax_details = {}

    for row in items:
        if row.item_code in itemised_tax:
            cgst, sgst, igst = 0, 0, 0
            row.cgst = row.sgst = row.igst = 0
            row.cgst_percent = row.sgst_percent = row.igst_percent = "0%"

            for tax_type, tax_data in itemised_tax.get(row.item_code).items():
                tax_rate = tax_data.get("tax_rate", 0)

                if "cgst" in tax_type.lower():
                    instate = True
                    row.cgst = tax_rate
                    row.cgst_percent = f"{cint(tax_rate) if cint(tax_rate) == tax_rate else tax_rate}%"
                    cgst += row.amount * tax_rate / 100

                elif "sgst" in tax_type.lower():
                    instate = True
                    row.sgst = tax_rate
                    row.sgst_percent = f"{cint(tax_rate) if cint(tax_rate) == tax_rate else tax_rate}%"
                    sgst += row.amount * tax_rate / 100

                elif "igst" in tax_type.lower():
                    instate = False
                    row.igst = tax_rate
                    row.igst_percent = f"{cint(tax_rate) if cint(tax_rate) == tax_rate else tax_rate}%"
                    igst += row.amount * tax_rate / 100

            row.cgst_amount = cgst
            row.sgst_amount = sgst
            row.igst_amount = igst

            # Create unique key using HSN and total tax percentage
            hsn_code = row.get("gst_hsn_code") or "Unknown"
            total_tax_rate = round(row.cgst + row.sgst + row.igst, 2)
            tax_key = f"{hsn_code}|{total_tax_rate}"

            if tax_key not in tax_details:
                tax_details[tax_key] = {
                    'tax_percentage': total_tax_rate,
                    'hsn_code': hsn_code,
                    'taxable_amount': row.net_amount or 0,
                    'cgst': cgst,
                    'sgst': sgst,
                    'igst': igst,
                    'total_tax_amount': cgst + sgst + igst
                }
            else:
                tax_details[tax_key]['taxable_amount'] += row.net_amount or 0
                tax_details[tax_key]['cgst'] += cgst
                tax_details[tax_key]['sgst'] += sgst
                tax_details[tax_key]['igst'] += igst
                tax_details[tax_key]['total_tax_amount'] += cgst + sgst + igst

            total_cgst += cgst
            total_sgst += sgst
            total_igst += igst

    return {
        "items": items,
        "instate": instate,
        "tax_details": list(tax_details.values()) + [{
            'tax_percentage': 'Total',
            'taxable_amount': doc.net_total,
            'cgst': total_cgst,
            'sgst': total_sgst,
            'igst': total_igst,
            'total_tax_amount': total_cgst + total_sgst + total_igst
        }],
        "cgst": total_cgst,
        "sgst": total_sgst,
        "igst": total_igst,
    }

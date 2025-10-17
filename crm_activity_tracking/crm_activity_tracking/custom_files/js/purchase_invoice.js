frappe.ui.form.on("Purchase Invoice", {
	refresh(frm) {
        setTimeout(() => {
            var is_pr = 1
            if(frm.doc.items){
                frm.doc.items.forEach((i)=>{
                    if(!i.pr_detail){
                        is_pr = 0
                    }
                })
            }
            if(frm.doc.update_stock == 1 || is_pr == 1){
                frm.remove_custom_button("Purchase Receipt", "Create")
            }
            frm.remove_custom_button("Quality Inspection(s)", "Create")
            frm.remove_custom_button("Payment Request", "Create")

            frm.remove_custom_button("Purchase Order", "Get Items From")

            frm.remove_custom_button('Accounting Ledger', 'View');

            $("[data-doctype='Asset']").hide();
            $("[data-doctype='Bill of Entry']").hide();
            $("[data-doctype='Landed Cost Voucher']").hide();

            $($("[data-doctype='Auto Repeat']")[0].parentElement).hide();

		}, 500);
    },
})
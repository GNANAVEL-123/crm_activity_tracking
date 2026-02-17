frappe.ui.form.on("User", {
    remove_device: function (frm) {
        frappe.confirm(
            "Are you sure you want to remove this device?",
            function () {
                let otp = Math.floor(100000 + Math.random() * 900000);

                frm.set_value("otp", otp);
                frm.set_value("device_info",'');

                frappe.msgprint({
                    title: "OTP Generated",
                    message: `OTP <b>${otp}</b> has been generated.`,
                    indicator: "green"
                });
                frm.save()
            },
            function () {
            }
        );
    }
});

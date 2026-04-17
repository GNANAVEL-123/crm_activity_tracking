frappe.listview_settings["Supply and Erection Detail Quotation"] = {
    add_fields: ["status"],  // ✅ IMPORTANT

    get_indicator: function(doc) {
        if (doc.status === "Open") {
            return ["Open", "blue", "status,=,Open"];
        } else if (doc.status === "Ordered") {
            return ["Ordered", "green", "status,=,Ordered"];
        } else if (doc.status === "Cancelled") {
            return ["Cancelled", "red", "status,=,Cancelled"];
        }

        // ✅ fallback (avoid no color issue)
        return [doc.status || "Draft", "gray", "status,=," + doc.status];
    }
};
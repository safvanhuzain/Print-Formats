import frappe

@frappe.whitelist()
def test(doc):
    frappe.msgprint(str(doc))
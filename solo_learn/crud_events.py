import frappe
from frappe import _, enqueue


class SerialNoQtyError(frappe.ValidationError):
	pass


def generate_gst_invoice(doc, method=None):
	gst_naming_series = frappe.db.get_value(
		'GST Company', {'company': doc.company}, 'gst_naming_series')
	if not gst_naming_series:
		return

	if doc.naming_series != gst_naming_series:
		enqueue('solo_learn.crud_events.insert_gst_invoice', oldDoc=doc)


def insert_gst_invoice(oldDoc):
	cmp = frappe.db.get_value('GST Company', {'company': oldDoc.company}, [
		'gst_naming_series', 'gst_company', 'cost_center', 'submit_gst', 'charge_type', 'out_state_igst', 'in_state_sgst', 'in_state_cgst'
	], as_dict=1)

	newDoc = frappe.new_doc('Sales Invoice')
	newDoc.naming_series = cmp.gst_naming_series
	newDoc.company = cmp.gst_company
	newDoc.customer = oldDoc.customer
	newDoc.docstatus = cmp.submit_gst
	newDoc.update_stock = 0
	newDoc.posting_date = oldDoc.posting_date
	newDoc.due_date = oldDoc.due_date
	newDoc.cost_center = cmp.cost_center

	for item in oldDoc.items:
		row = newDoc.append('items', {})
		row.item_code = item.item_code
		row.item_name = item.item_name
		row.qty = item.qty
		row.description = item.description
		row.uom = item.uom
		row.conversion_factor = item.conversion_factor
		if item.use_same_rate or oldDoc.gst_same_rate:
			row.rate = item.rate
		else:
			row.rate = item.rate * (100 - item.gst_cut) / 100
		row.cost_center = cmp.cost_center

	tax = [cmp.in_state_sgst, cmp.in_state_cgst] if not newDoc.is_out_state else [
		cmp.out_state_igst]
	for gst in tax:
		row = newDoc.append('taxes', {})
		row.charge_type = cmp.charge_type
		row.account_head = gst
		row.cost_center = cmp.cost_center
		row.rate = 18 / len(tax)
		row.description = gst[:-4] + '@ ' + str(row.rate)

	newDoc.insert(ignore_permissions=True, ignore_mandatory=True)

def generate_payment_entry(doc, method=None):
	cmp = frappe.db.get_value('GST Company', {'company': doc.company}, ['gst_company', 'default_bank_account', 'creditors_account'], as_dict=1)
	if not cmp or not doc.auto_creation:
		return
	if doc.mode_of_payment == 'Wire Transfer':
		newDoc = frappe.new_doc('Payment Entry')
		newDoc.payment_type = doc.payment_type
		newDoc.posting_date = doc.posting_date
		newDoc.company = cmp.gst_company
		newDoc.mode_of_payment = doc.mode_of_payment
		newDoc.party_type = doc.party_type
		newDoc.party = doc.party
		newDoc.party_name = doc.party_name
		newDoc.paid_amount = doc.paid_amount
		if doc.payment_type == 'Pay':
			newDoc.paid_from = cmp.default_bank_account
			newDoc.paid_to = cmp.creditors_account
		else:
			newDoc.paid_to = cmp.default_bank_account
		newDoc.paid_from_account_currency = doc.paid_from_account_currency
		newDoc.paid_to_account_currency = doc.paid_to_account_currency
		newDoc.source_exchange_rate = doc.source_exchange_rate
		newDoc.base_paid_amount = doc.base_paid_amount
		newDoc.received_amount = doc.received_amount
		newDoc.target_exchange_rate= doc.target_exchange_rate
		newDoc.base_received_amount = doc.base_received_amount
		newDoc.reference_no = doc.reference_no
		newDoc.reference_date = doc.reference_date
		newDoc.clearance_date = doc.clearance_date

		newDoc.insert(ignore_permissions=True,ignore_mandatory=True)
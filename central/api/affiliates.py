import frappe

from central.signups.doctype.affiliate.affiliate import Affiliate


@frappe.whitelist(methods=["POST"])
def apply() -> dict:
	"""Ask to become an affiliate. Safe to repeat."""
	return Affiliate.request_for(frappe.session.user).get_state()


@frappe.whitelist(methods=["GET"])
def get_affiliate() -> dict | None:
	"""The caller's own affiliate account, or None when they never applied."""
	name = frappe.db.get_value("Affiliate", {"user": frappe.session.user}, "name")
	return frappe.get_doc("Affiliate", name).get_state() if name else None

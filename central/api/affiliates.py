import frappe
from frappe import _

from central.signups.affiliate_summary import get_affiliate_summary
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


@frappe.whitelist(methods=["GET"])
def get_summary(from_date: str, to_date: str) -> dict:
	"""The caller's own funnel for the dates, both included. Only an Active affiliate has one."""
	affiliate = frappe.db.get_value("Affiliate", {"user": frappe.session.user, "status": "Active"}, "name")
	if not affiliate:
		frappe.throw(_("Only an active affiliate has a summary."), frappe.PermissionError)

	return get_affiliate_summary(affiliate, from_date, to_date)

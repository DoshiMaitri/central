# Copyright (c) 2026, frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AffiliateVisit(Document):
	pass


def on_doctype_update():
	# An affiliate's summary counts its visits in a date range.
	frappe.db.add_index("Affiliate Visit", ["affiliate", "creation"])

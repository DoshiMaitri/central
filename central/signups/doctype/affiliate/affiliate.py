# Copyright (c) 2026, frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class Affiliate(Document):
	def before_validate(self) -> None:
		# The unique index allows many NULLs but only one empty string, so an unset code is NULL.
		self.affiliate_code = (self.affiliate_code or "").strip().lower() or None

	def validate(self) -> None:
		previous = self.get_doc_before_save()
		if previous and previous.affiliate_code and self.has_value_changed("affiliate_code"):
			frappe.throw(_("The affiliate code cannot change after it is set."))


def on_doctype_update():
	frappe.db.add_index("Affiliate", ["status"])

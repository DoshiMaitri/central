# Copyright (c) 2026, frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class Affiliate(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		affiliate_code: DF.Data | None
		rejection_reason: DF.SmallText | None
		requested_on: DF.Datetime | None
		reviewed_by: DF.Link | None
		reviewed_on: DF.Datetime | None
		status: DF.Literal["Pending", "Active", "Rejected", "Disabled"]
		user: DF.Link
	# end: auto-generated types

	def before_validate(self) -> None:
		# The unique index allows many NULLs but only one empty string, so an unset code is NULL.
		self.affiliate_code = (self.affiliate_code or "").strip().lower() or None

	def validate(self) -> None:
		previous = self.get_doc_before_save()
		if previous and previous.affiliate_code and self.has_value_changed("affiliate_code"):
			frappe.throw(_("The affiliate code cannot change after it is set."))

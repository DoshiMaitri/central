# Copyright (c) 2026, frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

UTM_FIELDS = ("utm_source", "utm_medium", "utm_campaign")


class AffiliateVisit(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		affiliate: DF.Link
		last_clicked_on: DF.Datetime
		product: DF.Link | None
		utm_campaign: DF.Data | None
		utm_medium: DF.Data | None
		utm_source: DF.Data | None
	# end: auto-generated types

	@classmethod
	def record_click(cls, affiliate: str, product: str | None, utm: dict, earlier: str | None) -> str:
		"""The visit a click belongs to. A click like the browser's earlier one reuses that visit."""
		values = {"affiliate": affiliate, "product": product, **utm}
		row = frappe.db.get_value("Affiliate Visit", earlier, list(values), as_dict=True) if earlier else None
		if row and all((row[field] or None) == (value or None) for field, value in values.items()):
			frappe.db.set_value("Affiliate Visit", earlier, "last_clicked_on", now_datetime())
			return earlier

		visit = frappe.get_doc({"doctype": "Affiliate Visit", **values, "last_clicked_on": now_datetime()})
		# A guest clicks the link, and a visit holds nothing personal.
		return visit.insert(ignore_permissions=True).name

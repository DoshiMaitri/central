# Copyright (c) 2026, frappe and contributors
# For license information, please see license.txt

from frappe.model.document import Document


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

	pass

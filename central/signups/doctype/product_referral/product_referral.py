# Copyright (c) 2026, frappe and contributors
# For license information, please see license.txt

from frappe.model.document import Document

from central.signups.doctype.product.product import FRAPPE_CLOUD_PRODUCT_KEY


class ProductReferral(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		affiliate: DF.Link
		product: DF.Link | None
		referred_team: DF.Link
		utm_campaign: DF.Data | None
		utm_medium: DF.Data | None
		utm_source: DF.Data | None
		visit: DF.Link | None
	# end: auto-generated types

	def autoname(self) -> None:
		# The name is the unique key, so the database rejects a second referral for a team and product.
		self.name = referral_name(self.referred_team, self.product)


def referral_name(team: str, product: str | None) -> str:
	return f"{team}::{product or FRAPPE_CLOUD_PRODUCT_KEY}"

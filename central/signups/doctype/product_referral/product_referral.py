# Copyright (c) 2026, frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from central.signups.doctype.product.product import FRAPPE_CLOUD_PRODUCT_KEY


class ProductReferral(Document):
	def autoname(self) -> None:
		# The name is the unique key, so the database rejects a second referral for a team and product.
		self.name = referral_name(self.referred_team, self.product)


def referral_name(team: str, product: str | None) -> str:
	return f"{team}::{product or FRAPPE_CLOUD_PRODUCT_KEY}"


def on_doctype_update():
	frappe.db.add_index("Product Referral", ["referred_team"])
	# An affiliate's summary counts its signups in a date range.
	frappe.db.add_index("Product Referral", ["affiliate", "creation"])

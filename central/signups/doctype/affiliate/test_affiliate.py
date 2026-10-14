# Copyright (c) 2026, frappe and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

from central.tests.test_iam import ensure_user

AFFILIATE_DOCTYPES = ("Affiliate", "Affiliate Visit", "Product Referral")


def make_affiliate(email: str, **values) -> "frappe.Document":
	return frappe.get_doc({"doctype": "Affiliate", "user": ensure_user(email), **values}).insert()


class IntegrationTestAffiliate(IntegrationTestCase):
	"""An affiliate's code is set once, and only a System Manager reaches affiliate records."""

	def setUp(self):
		super().setUp()
		frappe.set_user("Administrator")
		self.addCleanup(frappe.db.rollback)

	def test_pending_affiliates_without_a_code_do_not_clash(self):
		first = make_affiliate("affiliate.pending.one@example.test", affiliate_code="")
		second = make_affiliate("affiliate.pending.two@example.test")

		for affiliate in (first, second):
			self.assertIsNone(frappe.db.get_value("Affiliate", affiliate.name, "affiliate_code"))

	def test_code_is_unique(self):
		make_affiliate("affiliate.code.one@example.test", affiliate_code="abcd2345")

		with self.assertRaises(frappe.UniqueValidationError):
			make_affiliate("affiliate.code.two@example.test", affiliate_code="abcd2345")

	def test_code_cannot_change_once_set(self):
		affiliate = make_affiliate("affiliate.code.fixed@example.test")
		affiliate.update({"status": "Active", "affiliate_code": "ABCD2345"})
		affiliate.save()
		self.assertEqual(affiliate.affiliate_code, "abcd2345")

		affiliate.affiliate_code = "wxyz6789"
		with self.assertRaises(frappe.ValidationError):
			affiliate.save()

		affiliate.reload()
		affiliate.affiliate_code = None
		with self.assertRaises(frappe.ValidationError):
			affiliate.save()

	def test_only_a_system_manager_reaches_affiliate_records(self):
		customer = ensure_user("affiliate.customer@example.test")

		for doctype in AFFILIATE_DOCTYPES:
			for permission in ("read", "write", "create"):
				with self.subTest(doctype=doctype, permission=permission):
					self.assertFalse(frappe.has_permission(doctype, permission, user=customer))
					self.assertTrue(frappe.has_permission(doctype, permission, user="Administrator"))

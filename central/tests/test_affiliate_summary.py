import json

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, now_datetime, today

from central.api.affiliates import get_summary
from central.signups.doctype.affiliate.test_affiliate import make_affiliate
from central.tests.test_iam import ensure_user


class IntegrationTestAffiliateSummary(IntegrationTestCase):
	"""An affiliate sees their own visits, signups and paying signups, and never a team name."""

	def setUp(self):
		super().setUp()
		frappe.set_user("Administrator")
		self.addCleanup(frappe.db.rollback)
		self.addCleanup(frappe.set_user, "Administrator")
		frappe.get_doc(
			{"doctype": "Product", "product_key": "summary-raven", "title": "Raven", "signup_app": "raven"}
		).insert()
		self.affiliate = make_affiliate("summary.affiliate@example.test")
		self.affiliate.approve()
		other = make_affiliate("summary.other@example.test")
		other.approve()
		self.other = other.name

	def test_the_funnel_counts_visits_signups_and_paying_signups(self):
		for source, product in (
			("youtube", None),
			("youtube", "summary-raven"),
			("linkedin", None),
			(None, None),
		):
			self.visit(source, product)
		self.visit("youtube", None, affiliate=self.other)
		self.visit("youtube", None, days_ago=40)

		for label, product, source, invoice in (
			("Paying", None, "youtube", {}),
			("Product Paying", "summary-raven", "youtube", {}),
			("Credit Only", None, "linkedin", {"amount_paid": 0}),
			("Cost Report", None, None, {"invoice_type": "Cost Report"}),
		):
			team = self.team(label)
			self.referral(team, product, source)
			self.invoice(team, **invoice)

		summary = self.summary()

		self.assertEqual(summary["totals"], {"visited": 4, "signed_up": 4, "converted": 2})
		by_source = {row["source"]: row for row in summary["by_source"]}
		self.assertEqual(
			by_source["youtube"], {"source": "youtube", "visited": 2, "signed_up": 2, "converted": 2}
		)
		self.assertEqual(by_source["(none)"]["visited"], 1)
		by_product = {row["product"]: row for row in summary["by_product"]}
		self.assertEqual(
			by_product["summary-raven"],
			{"product": "summary-raven", "visited": 1, "signed_up": 1, "converted": 1},
		)
		self.assertEqual(by_product["(none)"]["signed_up"], 3)

	def test_a_product_referral_takes_the_conversion_from_a_frappe_cloud_referral(self):
		team = self.team("Both")
		self.referral(team, None, "youtube")
		self.referral(team, "summary-raven", "youtube", affiliate=self.other)
		self.invoice(team)

		self.assertEqual(self.summary()["totals"]["converted"], 0)

		frappe.set_user(frappe.db.get_value("Affiliate", self.other, "user"))
		self.assertEqual(get_summary(add_days(today(), -7), today())["totals"]["converted"], 1)

	def test_recent_signups_name_no_team(self):
		team = self.team("Secret Customer")
		self.referral(team, "summary-raven", "youtube")
		self.invoice(team)

		summary = self.summary()

		self.assertEqual(
			summary["recent_signups"],
			[
				{
					"date": frappe.utils.getdate(),
					"product": "summary-raven",
					"source": "youtube",
					"status": "Converted",
				}
			],
		)
		self.assertNotIn(team, json.dumps(summary, default=str))
		self.assertNotIn("Secret Customer", json.dumps(summary, default=str))

	def test_only_an_active_affiliate_has_a_summary(self):
		frappe.set_user(ensure_user("summary.stranger@example.test"))
		with self.assertRaises(frappe.PermissionError):
			get_summary(today(), today())

		frappe.set_user("Administrator")
		self.affiliate.disable()
		with self.assertRaises(frappe.PermissionError):
			self.summary()

	def test_the_start_must_not_be_after_the_end(self):
		frappe.set_user(self.affiliate.user)

		with self.assertRaises(frappe.ValidationError):
			get_summary(today(), add_days(today(), -1))

	def summary(self) -> dict:
		frappe.set_user(self.affiliate.user)
		return get_summary(add_days(today(), -7), today())

	def visit(
		self, source: str | None, product: str | None, affiliate: str | None = None, days_ago: int = 0
	) -> None:
		visit = frappe.get_doc(
			{
				"doctype": "Affiliate Visit",
				"affiliate": affiliate or self.affiliate.name,
				"product": product,
				"utm_source": source,
				"last_clicked_on": now_datetime(),
			}
		).insert()
		if days_ago:
			visit.db_set("creation", add_days(now_datetime(), -days_ago), update_modified=False)

	def team(self, label: str) -> str:
		owner = ensure_user(f"summary.{label.lower().replace(' ', '.')}@example.test")
		team = frappe.get_doc(
			{
				"doctype": "Team",
				"team_name": label,
				"owner_user": owner,
				"members": [{"user": owner, "role": "Owner", "status": "Active"}],
			}
		).insert()
		return team.name

	def referral(
		self, team: str, product: str | None, source: str | None, affiliate: str | None = None
	) -> None:
		frappe.get_doc(
			{
				"doctype": "Product Referral",
				"referred_team": team,
				"product": product,
				"affiliate": affiliate or self.affiliate.name,
				"utm_source": source,
			}
		).insert()

	def invoice(self, team: str, amount_paid: float = 10, invoice_type: str = "Billable") -> None:
		invoice = frappe.get_doc(
			{
				"doctype": "Invoice",
				"team": team,
				"status": "Paid",
				"invoice_type": invoice_type,
				"amount_paid": amount_paid,
			}
		)
		invoice.name = f"summary-{frappe.generate_hash(length=8)}"
		# Only the paid row matters here, not the billing that would create it.
		invoice.db_insert()

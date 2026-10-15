from collections import defaultdict
from datetime import date

import frappe
from frappe import _
from frappe.query_builder.functions import Count
from frappe.utils import add_days, getdate

NONE_LABEL = "(none)"
RECENT_SIGNUPS = 20


def get_affiliate_summary(affiliate: str, from_date: str | date, to_date: str | date) -> dict:
	"""The funnel of one affiliate for the dates, both included. Visits count by their creation,
	and signups and conversions by the referral's creation. Team names never leave this function."""
	# The affiliate holds no permission on these records, so every read filters on the affiliate.
	start, end = getdate(from_date), add_days(getdate(to_date), 1)
	if start >= end:
		frappe.throw(_("The start date must not be after the end date."))

	visits = get_visit_counts(affiliate, start, end)
	referrals = get_referral_rows(affiliate, start, end)
	rows = visits + referrals

	return {
		"totals": count(rows),
		"by_source": group(rows, "utm_source", "source"),
		"by_product": group(rows, "product", "product"),
		"recent_signups": [
			{
				"date": getdate(row.creation),
				"product": row.product or NONE_LABEL,
				"source": row.utm_source or NONE_LABEL,
				"status": "Converted" if row.converted else "Signed up",
			}
			for row in referrals[:RECENT_SIGNUPS]
		],
	}


def get_visit_counts(affiliate: str, start: date, end: date) -> list[dict]:
	visit = frappe.qb.DocType("Affiliate Visit")
	return (
		frappe.qb.from_(visit)
		.select(visit.utm_source, visit.product, Count("*").as_("visited"))
		.where((visit.affiliate == affiliate) & (visit.creation >= start) & (visit.creation < end))
		.groupby(visit.utm_source, visit.product)
	).run(as_dict=True)


def get_referral_rows(affiliate: str, start: date, end: date) -> list[dict]:
	"""The affiliate's referrals in the dates, each marked converted or not."""
	referrals = frappe.get_all(
		"Product Referral",
		filters=[["affiliate", "=", affiliate], ["creation", ">=", start], ["creation", "<", end]],
		fields=["referred_team", "product", "utm_source", "creation"],
		order_by="creation desc",
	)
	teams = {row.referred_team for row in referrals}
	paid_teams = get_paying_teams(teams)
	product_teams = get_teams_with_product_referral(teams)

	for row in referrals:
		# A team's payment belongs to its product referrals. A Frappe Cloud referral converts only
		# when the team has no product referral from any affiliate.
		row.converted = row.referred_team in paid_teams and (
			bool(row.product) or row.referred_team not in product_teams
		)
		row.signed_up = 1

	return referrals


def get_paying_teams(teams: set[str]) -> set[str]:
	"""Teams with a paid billable invoice that took real money. A refund does not undo it."""
	if not teams:
		return set()

	return set(
		frappe.get_all(
			"Invoice",
			filters={
				"team": ["in", list(teams)],
				"status": "Paid",
				"invoice_type": "Billable",
				"amount_paid": [">", 0],
			},
			pluck="team",
			distinct=True,
		)
	)


def get_teams_with_product_referral(teams: set[str]) -> set[str]:
	if not teams:
		return set()

	return set(
		frappe.get_all(
			"Product Referral",
			filters={"referred_team": ["in", list(teams)], "product": ["is", "set"]},
			pluck="referred_team",
			distinct=True,
		)
	)


def count(rows: list[dict]) -> dict:
	return {
		"visited": sum(row.get("visited", 0) for row in rows),
		"signed_up": sum(row.get("signed_up", 0) for row in rows),
		"converted": sum(1 for row in rows if row.get("converted")),
	}


def group(rows: list[dict], field: str, label: str) -> list[dict]:
	"""The funnel for each value of a field, largest first. An empty value reads "(none)"."""
	groups = defaultdict(list)
	for row in rows:
		groups[row[field] or NONE_LABEL].append(row)

	table = [{label: value, **count(group_rows)} for value, group_rows in groups.items()]
	return sorted(table, key=lambda row: (row["visited"], row["signed_up"]), reverse=True)

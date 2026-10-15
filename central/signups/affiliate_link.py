import re
from urllib.parse import urlencode

import frappe
from frappe.rate_limiter import rate_limit
from frappe.utils import cint
from frappe.website.page_renderers.base_renderer import BaseRenderer
from werkzeug.wrappers import Response

from central.signups.affiliate_cookie import read_visit_cookie, write_visit_cookie
from central.signups.doctype.affiliate_visit.affiliate_visit import UTM_FIELDS, AffiliateVisit
from central.signups.doctype.product.product import FRAPPE_CLOUD_PRODUCT_KEY, get_enabled_product_key
from central.site_provisioning import first_touch

LINK_PATH = re.compile(r"r/([a-z0-9]{1,32})", re.IGNORECASE)
CLICKS_PER_HOUR = 60
# Crawlers and link previews open a shared link without a person behind it. Most name themselves
# "...bot", such as Googlebot. A lowercase letter must come first, so a phone brand like CUBOT
# does not match. Do not match an app whose in-app browser a person uses, such as Telegram.
BOT_USER_AGENT = re.compile(
	r"[a-z][Bb]ot\b|(?i:crawl|spider|slurp|preview|facebookexternalhit|whatsapp|embedly|curl|wget|python|headless)"
)


class AffiliateLinkPage(BaseRenderer):
	"""Serves /r/<code>: counts a person's click and sends them to signup."""

	def can_render(self) -> bool:
		return bool(LINK_PATH.fullmatch(self.path))

	def render(self) -> Response:
		if frappe.request.method not in ("GET", "HEAD"):
			return Response(status=405, headers={"Allow": "GET, HEAD"})

		code = LINK_PATH.fullmatch(self.path).group(1).lower()
		product = get_enabled_product_key(frappe.request.args.get("product"))
		touch = first_touch(**{field: frappe.request.args.get(field) for field in UTM_FIELDS})
		utm = {field: touch[field] for field in UTM_FIELDS}

		if is_person_clicking() and (affiliate := get_clicked_affiliate(code)):
			try:
				count_click(affiliate, product, utm)
			except frappe.RateLimitExceededError:
				# The visitor still reaches signup. The click just does not count.
				pass

		return Response(
			status=302, headers={"Location": get_signup_url(product, utm), "Cache-Control": "no-store"}
		)


@rate_limit(limit=lambda: CLICKS_PER_HOUR, seconds=60 * 60)
def count_click(affiliate: str, product: str | None, utm: dict) -> None:
	"""Record the click and keep its visit in the visitor's cookie."""
	if cint(frappe.db.get_single_value("Central Settings", "affiliate_cookie_days")) <= 0:
		# A cookie that expires at once can never lead to a referral.
		return

	key = product or FRAPPE_CLOUD_PRODUCT_KEY
	visits = read_visit_cookie()
	earlier = visits.pop(key, None)
	visits[key] = AffiliateVisit.record_click(affiliate, product, utm, earlier)
	write_visit_cookie(visits)
	# Frappe rolls back a GET request unless it is told to commit.
	frappe.local.flags.commit = True


def is_person_clicking() -> bool:
	user_agent = frappe.request.headers.get("User-Agent", "")
	return frappe.request.method == "GET" and bool(user_agent) and not BOT_USER_AGENT.search(user_agent)


def get_clicked_affiliate(code: str) -> str | None:
	"""The Active affiliate of the code, unless the visitor is that affiliate."""
	affiliate = frappe.db.get_value(
		"Affiliate", {"affiliate_code": code, "status": "Active"}, ["name", "user"], as_dict=True
	)
	return affiliate.name if affiliate and affiliate.user != frappe.session.user else None


def get_signup_url(product: str | None, utm: dict) -> str:
	query = {key: value for key, value in {"product": product, **utm}.items() if value}
	return f"/dashboard/signup?{urlencode(query)}" if query else "/dashboard/signup"

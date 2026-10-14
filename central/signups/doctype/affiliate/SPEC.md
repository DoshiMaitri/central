# Affiliates

## Purpose

An affiliate is a person who shares a link to Frappe Cloud or to a [Product](../product/SPEC.md). Central records the visits that the link brings and the teams that sign up from it, so a System Manager can see which affiliate brought which signup. Commission and payouts are not part of Central yet.

## Records

All three DocTypes are in the Signups module. Only a System Manager can read, create or change them. An affiliate never reads them directly.

| DocType | Name | One record is |
|---|---|---|
| Affiliate | `AFF-00001` | A person who applied to be an affiliate. |
| Affiliate Visit | A random hash | A click on an affiliate link, for one product and one set of UTM values. The visitor's cookie holds this name. |
| Product Referral | `<team>::<product key>` | The affiliate credited with a team's signup for a product. |

### Affiliate

| Field | Rule |
|---|---|
| User | The applicant. One Affiliate for each user. It cannot change. |
| Status | Pending, Active, Rejected or Disabled. |
| Affiliate Code | The code in the link `/r/<code>`. Central sets it once, at the first approval. It cannot change after that. It is empty until then. |
| Requested On, Reviewed By, Reviewed On, Rejection Reason | The last request and the last review. Track Changes keeps the earlier values. |

### Affiliate Visit

A visit holds the affiliate, the product, the `utm_source`, `utm_medium` and `utm_campaign` of the link, and Last Clicked On. An empty product is a link to Frappe Cloud itself. A visit holds no personal data: no IP address and no email.

### Product Referral

A referral holds the referred team, the product, the affiliate, the visit, and the UTM values copied from the visit. Its name is `<team>::<product key>`, for example `TEAM-00012::raven`. A signup to Frappe Cloud itself has an empty product and uses the key `fc`, for example `TEAM-00012::fc`. No Product can use the key `fc`.

The name is the unique key. The database refuses a second referral for the same team and product, so the first referral is final. A team can have one referral for each product and one for `fc`.

## Configuration

| Central Settings field | Default | Meaning |
|---|---|---|
| Affiliate Cookie Days | 30 | Days a click on an affiliate link is remembered. A signup after this gets no referral. |

## Known behavior

| Action | Result |
|---|---|
| Delete a Team that has a Product Referral | Refused. The referral keeps the team. |
| Delete an Affiliate Visit that a Product Referral links to | Refused. |
| Delete an Affiliate that has visits or referrals | Refused. Disable it instead. |

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

## Operation

### Apply

A signed-in user calls `POST central.api.affiliates.apply`. It needs no form fields. It is safe to repeat.

| Current status | Result |
|---|---|
| No Affiliate | Central creates one as Pending. |
| Pending or Active | Nothing changes. |
| Rejected | The same Affiliate becomes Pending again with a new Requested On. Central clears the review fields. |
| Disabled | Refused. Only a System Manager can enable the affiliate again. |

`GET central.api.affiliates.get_affiliate` returns the caller's own `status`, the `affiliate_code` when Active, and the `rejection_reason` when Rejected. It returns nothing when the caller never applied. Both calls return only the caller's own record.

### Review

A System Manager acts on an Affiliate in Desk. Each button shows only in the status that allows it.

| Action | From | To | Effect |
|---|---|---|---|
| **Approve** | Pending | Active | Sets the code at the first approval, and Reviewed By and Reviewed On. |
| **Reject** | Pending | Rejected | Stores the reason, and Reviewed By and Reviewed On. The reason is required. The applicant sees it. |
| **Disable** | Active | Disabled | Pauses the affiliate. Use it to stop an active affiliate. |
| **Enable** | Disabled | Active | Keeps the same code. |

Every action locks the row. When an operator approves or rejects a request that another operator already decided, nothing changes and Central says who decided first, for example "Already approved by admin@example.com". Any other action from the wrong status is refused.

The code has 8 characters from lowercase letters and digits, without the look-alikes `0`, `o`, `1`, `l` and `i`. Central draws again when a code is taken. If two approvals draw the same new code at the same time, the second one fails and the operator approves again.

### Affiliate link

An Active affiliate shares `/r/<code>`, for example `/r/k7m2x9pa?product=raven&utm_source=youtube`. The code matches in any case. Central sends the visitor to `/dashboard/signup` with the `product`, `utm_source`, `utm_medium` and `utm_campaign` of the link. It ignores every other parameter, so the link cannot send a visitor to another site. The product key matches in any case. An unknown or disabled product is dropped, and the click counts for Frappe Cloud. The link answers GET and HEAD only, and the answer is never cached.

A click records an Affiliate Visit and sets the `central_affiliate` cookie. The cookie holds one visit for each product key, such as `{"raven": "m3x8k2qa", "fc": "t7w2p5nc"}`. A new click for a product replaces that product's visit and leaves the others. A click with the same affiliate, product and UTM values as the browser's visit for that product updates Last Clicked On instead of adding a visit. The cookie is HttpOnly, SameSite Lax, Secure on HTTPS, and lasts Affiliate Cookie Days. Central ignores a cookie that it cannot read or that names a deleted visit.

The visitor always reaches signup. Central records nothing when:

- the code is unknown or the affiliate is not Active
- the request is HEAD, has no user agent, or comes from a crawler or link preview
- the signed-in user is the affiliate
- the IP address made more than 60 counted clicks in the last hour
- Affiliate Cookie Days is 0

### Referral

Central credits a signup in two places. Both read the visit for one product key in the cookie, and do not use the entry of another product.

| When | Product key |
|---|---|
| The signup flow creates a new user's first Team (`central.api.sites.create_trial_team`) | The product of the current signup, from `signup_product`. An unknown or disabled product, or none, uses `fc`. A user who already has a Team gets no new Team and no referral. |
| A Team starts a product trial site (`central.api.sites.create_trial_site` with a product) | That product. Only when the Team has no earlier Site of that product, terminated sites included, and no earlier request for one. A trial without a product records nothing here. |

Central creates the Product Referral only when all of these are true:

- the cookie has a visit for the product key, and the visit exists and is for that product
- the visit's affiliate is Active now
- the last click is not older than Affiliate Cookie Days, checked on the server
- the affiliate is not a member of the Team
- the Team has no referral for that product yet

The referral copies the affiliate, the visit and the UTM values of the visit. Central then removes that product's entry from the cookie and keeps the others. The first referral for a Team and product is final. A later click on another affiliate's link records a visit and changes nothing else. A referral error is written to the Error Log, and the signup continues.

## Configuration

| Central Settings field | Default | Meaning |
|---|---|---|
| Affiliate Cookie Days | 30 | Days a click on an affiliate link is remembered. A signup after this gets no referral. 0 stops recording clicks. |

## Known behavior

| Action | Result |
|---|---|
| Delete a Team that has a Product Referral | Refused. The referral keeps the team. |
| Delete an Affiliate Visit that a Product Referral links to | Refused. |
| Delete an Affiliate that has visits or referrals | Refused. Disable it instead. |

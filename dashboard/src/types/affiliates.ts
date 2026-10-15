export type AffiliateStatus = 'Pending' | 'Active' | 'Rejected' | 'Disabled'

/** The signed-in user's own affiliate account (get_affiliate, apply). */
export interface AffiliateState {
	status: AffiliateStatus
	affiliate_code: string | null
	rejection_reason: string | null
}

export interface FunnelCounts {
	visited: number
	signed_up: number
	converted: number
}

/** One row of a breakdown table: a source or a product, and its funnel. */
export interface FunnelRow extends FunnelCounts {
	label: string
}

export interface SourceFunnel extends FunnelCounts {
	source: string
}

export interface ProductFunnel extends FunnelCounts {
	product: string
}

export interface RecentSignup {
	date: string
	product: string
	source: string
	status: 'Signed up' | 'Converted'
}

/** The affiliate's funnel for a date range (get_summary). It never names a team. */
export interface AffiliateSummary {
	totals: FunnelCounts
	by_source: SourceFunnel[]
	by_product: ProductFunnel[]
	recent_signups: RecentSignup[]
}

export interface LinkProduct {
	name: string
	title: string
}

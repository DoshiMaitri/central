import { dayjs, useCall } from 'frappe-ui'
import { computed, ref, watch } from 'vue'
import { API, method } from '@/api/methods'
import { submitOrThrow } from '@/lib/frappeCall'
import type {
	AffiliateState,
	AffiliateSummary,
	FunnelRow,
	LinkProduct,
} from '@/types/affiliates'

export const AFFILIATE_RANGES = [
	{ label: 'Last 7 days', value: '7' },
	{ label: 'Last 30 days', value: '30' },
	{ label: 'Last 90 days', value: '90' },
	{ label: 'This year', value: 'year' },
]

/** The sources the link builder offers. They become `utm_source`. */
export const AFFILIATE_SOURCES = [
	{ label: 'YouTube', value: 'youtube' },
	{ label: 'Instagram', value: 'instagram' },
	{ label: 'LinkedIn', value: 'linkedin' },
	{ label: 'Other', value: 'other' },
]

// The signed-in user's own affiliate account: its status, and once Active, its link
// products and funnel for the chosen range. Not team-scoped, so a team switch changes nothing.
export function useAffiliate() {
	const account = useCall<AffiliateState | null>({
		url: method(API.affiliate),
	})
	const applyCall = useCall<AffiliateState, Record<string, never>>({
		url: method(API.applyAffiliate),
		method: 'POST',
		immediate: false,
	})

	const range = ref('30')
	const fromDate = computed(() =>
		range.value === 'year'
			? dayjs().startOf('year').format('YYYY-MM-DD')
			: dayjs()
					.subtract(Number(range.value) - 1, 'day')
					.format('YYYY-MM-DD'),
	)
	const summary = useCall<
		AffiliateSummary,
		{ from_date: string; to_date: string }
	>({
		url: method(API.affiliateSummary),
		params: () => ({
			from_date: fromDate.value,
			to_date: dayjs().format('YYYY-MM-DD'),
		}),
		immediate: false,
		refetch: true,
	})
	const products = useCall<LinkProduct[]>({
		url: method(API.affiliateLinkProducts),
		immediate: false,
	})

	const isActive = computed(() => account.data?.status === 'Active')
	watch(
		isActive,
		(active) => {
			if (!active) return
			summary.reload()
			products.reload()
		},
		{ immediate: true },
	)

	const applying = ref(false)
	const applyError = ref<unknown>(null)
	async function apply(): Promise<void> {
		applying.value = true
		applyError.value = null
		try {
			await submitOrThrow(applyCall, {})
			account.reload()
		} catch (error) {
			applyError.value = error
		} finally {
			applying.value = false
		}
	}

	const bySource = computed<FunnelRow[]>(() =>
		(summary.data?.by_source ?? []).map(({ source, ...counts }) => ({
			label: source,
			...counts,
		})),
	)
	const byProduct = computed<FunnelRow[]>(() =>
		(summary.data?.by_product ?? []).map(({ product, ...counts }) => ({
			label: product,
			...counts,
		})),
	)

	return {
		account,
		summary,
		bySource,
		byProduct,
		products: computed<LinkProduct[]>(() => products.data ?? []),
		range,
		applying,
		applyError,
		apply,
	}
}

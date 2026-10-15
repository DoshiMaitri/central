<script setup lang="ts">
import { Alert, LoadingText, Select } from 'frappe-ui'
import AffiliateBreakdownCard from '@/components/affiliate/AffiliateBreakdownCard.vue'
import AffiliateFunnelCard from '@/components/affiliate/AffiliateFunnelCard.vue'
import AffiliateLinkCard from '@/components/affiliate/AffiliateLinkCard.vue'
import AffiliateSignupsCard from '@/components/affiliate/AffiliateSignupsCard.vue'
import AffiliateStatusCard from '@/components/affiliate/AffiliateStatusCard.vue'
import { AFFILIATE_RANGES, useAffiliate } from '@/composables/useAffiliate'

const {
	account,
	summary,
	bySource,
	byProduct,
	products,
	range,
	applying,
	applyError,
	apply,
} = useAffiliate()
</script>

<template>
	<Teleport defer to="#header-actions">
		<Select
			v-if="account.data?.status === 'Active'"
			v-model="range"
			:options="AFFILIATE_RANGES"
			aria-label="Period"
			class="w-36"
		/>
	</Teleport>

	<div
		class="grid h-full auto-rows-max grid-cols-[min(64rem,100%)] content-start justify-center gap-4 overflow-y-auto px-3 pb-24 pt-3 md:gap-5 md:px-6 md:pt-7"
	>
		<LoadingText v-if="!account.isFinished" :lines="4" />
		<Alert
			v-else-if="account.error"
			theme="red"
			title="Couldn't load your affiliate account"
			:primary-action="{ label: 'Retry', onClick: () => account.reload() }"
		/>
		<AffiliateStatusCard
			v-else-if="account.data?.status !== 'Active'"
			:status="account.data?.status ?? null"
			:rejection-reason="account.data?.rejection_reason ?? null"
			:applying="applying"
			:apply-error="applyError"
			@apply="apply"
		/>
		<template v-else>
			<AffiliateLinkCard
				:code="account.data.affiliate_code ?? ''"
				:products="products"
			/>
			<LoadingText v-if="!summary.data && !summary.error" :lines="6" />
			<Alert
				v-else-if="summary.error"
				theme="red"
				title="Couldn't load your numbers"
				:primary-action="{ label: 'Retry', onClick: () => summary.reload() }"
			/>
			<template v-else-if="summary.data">
				<AffiliateFunnelCard :totals="summary.data.totals" />
				<div class="grid gap-4 md:grid-cols-2 md:gap-5">
					<AffiliateBreakdownCard
						title="By source"
						label="Source"
						:rows="bySource"
					/>
					<AffiliateBreakdownCard
						title="By product"
						label="Product"
						:rows="byProduct"
					/>
				</div>
				<AffiliateSignupsCard :signups="summary.data.recent_signups" />
			</template>
		</template>
	</div>
</template>

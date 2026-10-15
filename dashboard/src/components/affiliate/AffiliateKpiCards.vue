<script setup lang="ts">
import { Tooltip } from 'frappe-ui'
import { NumberCard } from 'frappe-ui/charts'
import { computed } from 'vue'
import { sampleEarningsPerClick } from '@/composables/useAffiliate'
import type { AffiliateSummary } from '@/types/affiliates'

interface AffiliateKpiCardsProps {
	summary: AffiliateSummary
}

const props = defineProps<AffiliateKpiCardsProps>()

const COMPARED = 'vs previous period'

/** The change from the previous period in percent, or null when there is nothing to compare. */
function change(current: number, previous: number): number | null {
	return previous ? Math.round(((current - previous) / previous) * 100) : null
}

const cards = computed(() => {
	const { totals, previous_totals: previous, daily } = props.summary
	const earnings = sampleEarningsPerClick(totals)
	const clickToPaid = totals.visited
		? (totals.converted / totals.visited) * 100
		: 0

	return [
		{
			title: 'Clicks',
			help: 'How many times people opened your links.',
			value: totals.visited,
			delta: change(totals.visited, previous.visited),
			sparkline: {
				data: daily.map((day) => day.clicks),
				color: 'var(--ink-blue-5)',
			},
		},
		{
			title: 'Signups',
			help: 'People who signed up for Frappe Cloud after opening your link.',
			value: totals.signed_up,
			delta: change(totals.signed_up, previous.signed_up),
			sparkline: {
				data: daily.map((day) => day.signups),
				color: 'var(--ink-purple-5)',
			},
		},
		{
			title: 'Paying customers',
			help: 'Signups who paid their first invoice.',
			value: totals.converted,
			delta: change(totals.converted, previous.converted),
			sparkline: {
				data: daily.map((day) => day.paying),
				color: 'var(--ink-green-5)',
			},
		},
		{
			title: 'Click → paid',
			help: 'The share of clicks that became paying customers.',
			value: clickToPaid,
			format: (value: number) => `${value.toFixed(1)}%`,
			caption: `${totals.converted} of ${totals.visited.toLocaleString()} clicks`,
		},
		{
			title: 'Earnings per click',
			help: 'What you earn on average for each click.',
			value: earnings,
			format: (value: number) => `$${value.toFixed(2)}`,
			delta: change(earnings, sampleEarningsPerClick(previous)),
		},
	]
})
</script>

<template>
	<div class="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">
		<NumberCard
			v-for="card in cards"
			:key="card.title"
			:title="card.title"
			:value="card.value"
			:format="card.format"
			:delta="card.delta"
			delta-suffix="%"
			:delta-caption="card.caption ?? (card.delta === null ? undefined : COMPARED)"
			:sparkline="card.sparkline"
		>
			<template #title-suffix>
				<Tooltip :text="card.help">
					<span
						class="lucide-info size-3.5 text-ink-gray-4"
						:aria-label="card.help"
					/>
				</Tooltip>
			</template>
		</NumberCard>
	</div>
</template>

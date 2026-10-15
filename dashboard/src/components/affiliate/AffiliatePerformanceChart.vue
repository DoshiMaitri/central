<script setup lang="ts">
import { Tooltip } from 'frappe-ui'
import { AreaChart } from 'frappe-ui/charts'
import type { DailyCounts } from '@/types/affiliates'

interface AffiliatePerformanceChartProps {
	daily: DailyCounts[]
}

defineProps<AffiliatePerformanceChartProps>()

const HELP =
	'Clicks on your links, signups, and signups who became paying customers, each day.'

// "2026-09-24" reads as "24 Sep" on the axis.
const MONTHS = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(' ')
const shortDay = (day: string): string => {
	const [, month, date] = day.split('-')
	return `${Number(date)} ${MONTHS[Number(month) - 1]}`
}
const dayAxis = { type: 'category' as const, format: shortDay }
const seriesConfig = {
	clicks: { label: 'Clicks', smooth: true, color: 'var(--ink-blue-5)' },
	signups: { label: 'Signups', smooth: true, color: 'var(--ink-purple-5)' },
	paying: {
		label: 'Paying customers',
		smooth: true,
		color: 'var(--ink-green-5)',
	},
}
</script>

<template>
	<section
		class="flex min-w-0 flex-col gap-3 rounded-6 border border-outline-gray-1 bg-surface-base p-5"
	>
		<h2 class="flex items-center gap-1.5 text-base-semibold text-ink-gray-8">
			Performance Overview
			<Tooltip :text="HELP">
				<span class="lucide-info size-3.5 text-ink-gray-4" :aria-label="HELP" />
			</Tooltip>
		</h2>
		<div class="min-h-72 flex-1">
			<AreaChart
				:data="daily"
				x="day"
				:y="['clicks', 'signups', 'paying']"
				:series-config="seriesConfig"
				:x-axis="dayAxis"
				:y-axis="{ min: 0 }"
			/>
		</div>
	</section>
</template>

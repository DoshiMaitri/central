<script setup lang="ts">
import { Tooltip } from 'frappe-ui'
import { NumberCard } from 'frappe-ui/charts'
import { computed } from 'vue'
import type { AffiliateRetention } from '@/types/affiliates'

interface AffiliateRetentionCardProps {
	retention: AffiliateRetention
}

const props = defineProps<AffiliateRetentionCardProps>()

const HELP =
	'All time, not the period above. A customer is active when they paid an invoice in that time. Retention counts customers still paying that many months after their first payment.'
const MILESTONES = [1, 3, 6, 12]

const shareOfCustomers = (count: number): string =>
	props.retention.customers
		? `${Math.round((count / props.retention.customers) * 100)}% of paid customers`
		: ''

// The 1, 3, 6 and 12 month points. A milestone no customer has reached yet has no point.
const bars = computed(() =>
	MILESTONES.map((month) => ({
		label: `${month} ${month === 1 ? 'month' : 'months'}`,
		point: props.retention.curve.find((point) => point.month === month),
	})),
)
</script>

<template>
	<section
		class="flex flex-col gap-4 rounded-6 border border-outline-gray-1 bg-surface-base p-5"
	>
		<div class="flex flex-col gap-1">
			<h2 class="flex items-center gap-1.5 text-base-semibold text-ink-gray-8">
				Retention
				<Tooltip :text="HELP">
					<span
						class="lucide-info size-3.5 text-ink-gray-4"
						:aria-label="HELP"
					/>
				</Tooltip>
			</h2>
			<p class="text-p-sm text-ink-gray-5">
				Among the customers you referred, how many keep paying.
			</p>
		</div>

		<p v-if="!retention.customers" class="text-p-sm text-ink-gray-5">
			No paying customers yet. When people you referred pay, this shows how long
			they keep paying.
		</p>
		<div
			v-else
			class="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(0,1.3fr)]"
		>
			<NumberCard
				title="Active customers (last 30 days)"
				:value="retention.active_30_days"
				:delta-caption="shareOfCustomers(retention.active_30_days)"
				:sparkline="{
					data: retention.trend.slice(-6),
					color: 'var(--ink-green-5)',
				}"
			/>
			<NumberCard
				title="Active customers (last 90 days)"
				:value="retention.active_90_days"
				:delta-caption="shareOfCustomers(retention.active_90_days)"
				:sparkline="{ data: retention.trend, color: 'var(--ink-purple-5)' }"
			/>
			<div
				class="flex flex-col gap-3 rounded-6 border border-outline-gray-1 p-4"
			>
				<h3 class="text-base-medium text-ink-gray-8">
					Paid customer retention
				</h3>
				<div
					v-for="bar in bars"
					:key="bar.label"
					class="grid grid-cols-[5rem_minmax(0,1fr)_6rem] items-center gap-3 text-sm"
				>
					<span class="text-ink-gray-6">{{ bar.label }}</span>
					<span class="h-2 overflow-hidden rounded-full bg-surface-gray-3">
						<span
							v-if="bar.point"
							class="block h-full rounded-full bg-surface-blue-5"
							:style="{ width: `${bar.point.percent}%` }"
						/>
					</span>
					<span
						v-if="bar.point"
						class="text-right tabular-nums text-ink-gray-8"
					>
						{{ bar.point.still_paying }}
						({{ bar.point.percent }}%)
					</span>
					<span v-else class="text-right text-ink-gray-4">Not yet</span>
				</div>
			</div>
		</div>
	</section>
</template>

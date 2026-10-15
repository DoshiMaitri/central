<script setup lang="ts">
import { computed } from 'vue'
import type { FunnelCounts } from '@/types/affiliates'

interface AffiliateFunnelCardProps {
	totals: FunnelCounts
}

const props = defineProps<AffiliateFunnelCardProps>()

const steps = computed(() => [
	{ label: 'Visited', value: props.totals.visited },
	{ label: 'Signed up', value: props.totals.signed_up },
	{ label: 'Converted', value: props.totals.converted },
])
const largest = computed(() =>
	Math.max(...steps.value.map((step) => step.value), 1),
)
</script>

<template>
	<section
		aria-labelledby="affiliate-funnel-heading"
		class="flex flex-col gap-4 rounded-6 border border-outline-gray-1 bg-surface-base p-5"
	>
		<h2
			id="affiliate-funnel-heading"
			class="text-base-semibold text-ink-gray-8"
		>
			Funnel
		</h2>
		<dl class="flex flex-col gap-3">
			<div
				v-for="step in steps"
				:key="step.label"
				class="grid grid-cols-[6rem_4rem_minmax(0,1fr)] items-center gap-3"
			>
				<dt class="text-sm text-ink-gray-6">{{ step.label }}</dt>
				<dd class="text-right text-base-medium tabular-nums text-ink-gray-9">
					{{ step.value.toLocaleString() }}
				</dd>
				<dd class="flex min-w-0 items-center">
					<span
						class="h-1.5 rounded-full bg-surface-gray-9"
						:style="{ width: `${Math.max((step.value / largest) * 100, step.value ? 1 : 0)}%` }"
						aria-hidden="true"
					/>
				</dd>
			</div>
		</dl>
		<p class="text-p-sm text-ink-gray-5">
			Customers pay their first invoice some weeks after they sign up, so recent
			signups may still convert.
		</p>
	</section>
</template>

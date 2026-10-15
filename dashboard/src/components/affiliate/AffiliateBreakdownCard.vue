<script setup lang="ts">
import { TabButtons } from 'frappe-ui'
import { computed, ref } from 'vue'
import Table from '@/components/common/Table.vue'
import type { FunnelRow } from '@/types/affiliates'

interface BreakdownView {
	/** The switch label, such as "Country". It also heads the first column. */
	label: string
	rows: FunnelRow[]
}

interface AffiliateBreakdownCardProps {
	views: BreakdownView[]
}

const props = defineProps<AffiliateBreakdownCardProps>()

const chosen = ref(props.views[0]?.label ?? '')
const view = computed(
	() =>
		props.views.find((item) => item.label === chosen.value) ?? props.views[0],
)
const columns = computed(() => [
	{ key: 'label', label: view.value?.label ?? '' },
	{ key: 'visited', label: 'Clicks' },
	{ key: 'signed_up', label: 'Signups' },
	{ key: 'converted', label: 'Paying' },
])
const options = computed(() =>
	props.views.map(({ label }) => ({ label, value: label })),
)
</script>

<template>
	<section
		class="flex min-w-0 flex-col gap-3 rounded-6 border border-outline-gray-1 bg-surface-base p-5"
	>
		<div class="flex flex-wrap items-center justify-between gap-3">
			<h2 class="text-base-semibold text-ink-gray-8">Breakdown</h2>
			<TabButtons v-if="views.length > 1" v-model="chosen" :options="options" />
		</div>
		<p v-if="!view?.rows.length" class="text-p-sm text-ink-gray-5">
			No visits or signups in this period.
		</p>
		<Table v-else :columns="columns" :rows="view.rows" />
	</section>
</template>

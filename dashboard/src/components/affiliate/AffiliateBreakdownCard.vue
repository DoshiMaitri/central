<script setup lang="ts">
import Table from '@/components/common/Table.vue'
import type { FunnelRow } from '@/types/affiliates'

interface AffiliateBreakdownCardProps {
	title: string
	/** The heading of the first column, such as "Source". */
	label: string
	rows: FunnelRow[]
}

const props = defineProps<AffiliateBreakdownCardProps>()

const columns = [
	{ key: 'label', label: props.label },
	{ key: 'visited', label: 'Visited' },
	{ key: 'signed_up', label: 'Signups' },
	{ key: 'converted', label: 'Converted' },
]
</script>

<template>
	<section
		class="flex min-w-0 flex-col gap-3 rounded-6 border border-outline-gray-1 bg-surface-base p-5"
	>
		<h2 class="text-base-semibold text-ink-gray-8">{{ title }}</h2>
		<p v-if="!rows.length" class="text-p-sm text-ink-gray-5">
			No visits or signups in this period.
		</p>
		<Table v-else :columns="columns" :rows="rows" />
	</section>
</template>

<script setup lang="ts">
import { Badge } from 'frappe-ui'
import Table from '@/components/common/Table.vue'
import { formatDate } from '@/lib/format'
import type { RecentSignup } from '@/types/affiliates'

interface AffiliateSignupsCardProps {
	signups: RecentSignup[]
}

defineProps<AffiliateSignupsCardProps>()

const columns = [
	{ key: 'date', label: 'Date' },
	{ key: 'product', label: 'Product' },
	{ key: 'source', label: 'Source' },
	{ key: 'status', label: 'Status' },
]
</script>

<template>
	<section
		class="flex min-w-0 flex-col gap-3 rounded-6 border border-outline-gray-1 bg-surface-base p-5"
	>
		<h2 class="text-base-semibold text-ink-gray-8">Recent signups</h2>
		<p v-if="!signups.length" class="text-p-sm text-ink-gray-5">
			No signups in this period yet.
		</p>
		<Table v-else :columns="columns" :rows="signups">
			<template #date="{ row }">{{ formatDate(String(row.date)) }}</template>
			<template #status="{ row }">
				<Badge
					:theme="row.status === 'Converted' ? 'green' : 'gray'"
					:label="String(row.status)"
				/>
			</template>
		</Table>
	</section>
</template>

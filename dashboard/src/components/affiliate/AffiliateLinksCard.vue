<script setup lang="ts">
import { Badge } from 'frappe-ui'
import Table from '@/components/common/Table.vue'
import type { LinkRow } from '@/composables/useAffiliate'

interface AffiliateLinksCardProps {
	links: LinkRow[]
}

defineProps<AffiliateLinksCardProps>()

const columns = [
	{ key: 'slug', label: 'Campaign' },
	{ key: 'product', label: 'Product' },
	{ key: 'utm_source', label: 'Source' },
	{ key: 'visited', label: 'Clicks' },
	{ key: 'signed_up', label: 'Signups' },
	{ key: 'converted', label: 'Paying' },
]
</script>

<template>
	<section
		class="flex min-w-0 flex-col gap-3 rounded-6 border border-outline-gray-1 bg-surface-base p-5"
	>
		<h2 class="text-base-semibold text-ink-gray-8">Campaigns</h2>
		<Table :columns="columns" :rows="links">
			<template #slug="{ row }">
				<span class="flex items-center gap-2 text-base text-ink-gray-9">
					{{ row.slug }}
					<Badge v-if="row.isMain" theme="gray" label="Main" />
				</span>
			</template>
			<template #product="{ row }"
				>{{ row.product ?? 'Frappe Cloud' }}</template
			>
			<template #utm_source="{ row }">{{ row.utm_source ?? '–' }}</template>
		</Table>
	</section>
</template>

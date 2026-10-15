<script setup lang="ts">
import { Button, Select, Tooltip } from 'frappe-ui'
import { computed, ref } from 'vue'
import AffiliateCountriesDialog from '@/components/affiliate/AffiliateCountriesDialog.vue'
import AffiliateCountryMap from '@/components/affiliate/AffiliateCountryMap.vue'
import { countryPlace } from '@/lib/countries'
import { flagEmoji } from '@/lib/serverMap'
import type { FunnelRow } from '@/types/affiliates'

interface AffiliateCountriesCardProps {
	rows: FunnelRow[]
}

const props = defineProps<AffiliateCountriesCardProps>()

const HELP =
	'Where the people who clicked your links are, and how many signed up.'
const TOP = 5

const chosen = ref('')
const dialogOpen = ref(false)

// Countries with the most signups first; clicks break a tie.
const ranked = computed(() =>
	[...props.rows].sort(
		(a, b) => b.signed_up - a.signed_up || b.visited - a.visited,
	),
)
const top = computed(() =>
	ranked.value.slice(0, TOP).map((row, index) => ({ ...row, rank: index + 1 })),
)
const options = computed(() => [
	{ label: 'All countries', value: '' },
	...ranked.value.map(({ label }) => ({ label, value: label })),
])
const mapRows = computed(() =>
	chosen.value
		? props.rows.filter((row) => row.label === chosen.value)
		: props.rows,
)

const rate = (row: FunnelRow): string =>
	row.signed_up ? `${Math.round((row.converted / row.signed_up) * 100)}%` : '–'
</script>

<template>
	<section
		class="grid overflow-hidden rounded-6 border border-outline-gray-1 bg-surface-base lg:grid-cols-[minmax(0,1fr)_24rem]"
	>
		<div class="flex min-w-0 flex-col gap-4 p-5">
			<div class="flex flex-wrap items-center justify-between gap-3">
				<h2
					class="flex items-center gap-1.5 text-base-semibold text-ink-gray-8"
				>
					Where your customers come from
					<Tooltip :text="HELP">
						<span
							class="lucide-info size-3.5 text-ink-gray-4"
							:aria-label="HELP"
						/>
					</Tooltip>
				</h2>
				<Select
					v-model="chosen"
					:options="options"
					aria-label="Country"
					class="w-44"
				/>
			</div>
			<p v-if="!rows.length" class="text-p-sm text-ink-gray-5">
				No visits in this period.
			</p>
			<template v-else>
				<AffiliateCountryMap :rows="mapRows" />
				<div class="flex items-center gap-5 text-sm text-ink-gray-6">
					<span class="flex items-center gap-2">
						<span class="size-3.5 rounded-full bg-surface-blue-5" />
						More signups
					</span>
					<span class="flex items-center gap-2">
						<span class="size-2 rounded-full bg-surface-blue-5" />
						Fewer signups
					</span>
				</div>
			</template>
		</div>

		<div
			class="flex min-w-0 flex-col gap-3 border-t border-outline-gray-1 p-5 lg:border-l lg:border-t-0"
		>
			<h2 class="text-base-semibold text-ink-gray-8">
				Top countries by signups
			</h2>
			<p v-if="!rows.length" class="text-p-sm text-ink-gray-5">
				No signups in this period.
			</p>
			<template v-else>
				<div
					class="flex flex-col text-sm"
					role="table"
					aria-label="Top countries by signups"
				>
					<div
						class="grid grid-cols-[1.5rem_minmax(0,1fr)_3.5rem_4.5rem] gap-2 rounded-6 bg-surface-gray-2 px-3 py-2 text-ink-gray-5"
						role="row"
					>
						<span role="columnheader">#</span>
						<span role="columnheader">Country</span>
						<span class="text-right" role="columnheader">Signups</span>
						<span class="text-right" role="columnheader">Conversion</span>
					</div>
					<div
						v-for="row in top"
						:key="row.label"
						class="grid grid-cols-[1.5rem_minmax(0,1fr)_3.5rem_4.5rem] items-center gap-2 border-b border-outline-gray-1 px-3 py-2.5 last:border-b-0"
						role="row"
					>
						<span class="text-ink-gray-5" role="cell">{{ row.rank }}</span>
						<span
							class="flex min-w-0 items-center gap-2 text-ink-gray-9"
							role="cell"
						>
							<span aria-hidden="true">
								{{ flagEmoji(countryPlace(row.label)?.code) }}
							</span>
							<span class="truncate">{{ row.label }}</span>
						</span>
						<span class="text-right tabular-nums text-ink-gray-9" role="cell">
							{{ row.signed_up }}
						</span>
						<span class="text-right tabular-nums text-ink-gray-9" role="cell">
							{{ rate(row) }}
						</span>
					</div>
				</div>
				<Button
					variant="ghost"
					class="w-fit"
					icon-right="lucide-arrow-right"
					label="View all countries"
					@click="dialogOpen = true"
				/>
			</template>
		</div>
		<AffiliateCountriesDialog v-model="dialogOpen" :rows="ranked" />
	</section>
</template>

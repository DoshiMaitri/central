<script setup lang="ts">
import { computed, ref } from 'vue'
import WorldDots from '@/components/servers/WorldDots.vue'
import { countryPlace } from '@/lib/countries'
import { MAP_HEIGHT, MAP_WIDTH, project } from '@/lib/serverMap'
import type { FunnelRow } from '@/types/affiliates'

interface AffiliateCountryMapProps {
	rows: FunnelRow[]
}

const props = defineProps<AffiliateCountryMapProps>()

const SMALLEST = 8
const LARGEST = 36

// One dot per known country, sized by its signups so the strongest countries stand out.
const points = computed(() => {
	const most = Math.max(...props.rows.map((row) => row.signed_up), 1)
	return props.rows.flatMap((row) => {
		const place = countryPlace(row.label)
		if (!place) return []
		const { x, y } = project(place)
		const size =
			SMALLEST + (LARGEST - SMALLEST) * Math.sqrt(row.signed_up / most)
		return [
			{
				...row,
				left: `${(x / MAP_WIDTH) * 100}%`,
				top: `${(y / MAP_HEIGHT) * 100}%`,
				size: `${size}px`,
			},
		]
	})
})
const hovered = computed(() =>
	points.value.find((point) => point.label === hoveredLabel.value),
)
const hoveredLabel = ref('')
</script>

<template>
	<div
		class="relative w-full"
		:style="{ aspectRatio: `${MAP_WIDTH} / ${MAP_HEIGHT}` }"
	>
		<WorldDots class="absolute inset-0 h-full w-full text-ink-gray-3" />
		<button
			v-for="point in points"
			:key="point.label"
			type="button"
			class="absolute -translate-x-1/2 -translate-y-1/2 rounded-full bg-surface-blue-5 opacity-80 transition-opacity hover:opacity-100 focus-visible:opacity-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-outline-gray-4"
			:style="{
				left: point.left,
				top: point.top,
				width: point.size,
				height: point.size,
			}"
			:aria-label="`${point.label}: ${point.visited} clicks, ${point.signed_up} signups, ${point.converted} paying`"
			@mouseenter="hoveredLabel = point.label"
			@mouseleave="hoveredLabel = ''"
			@focus="hoveredLabel = point.label"
			@blur="hoveredLabel = ''"
		/>
		<div
			v-if="hovered"
			class="pointer-events-none absolute z-10 -translate-x-1/2 whitespace-nowrap rounded-6 bg-surface-elevation-2 px-3 py-2 text-sm shadow-xl"
			:style="{
				left: hovered.left,
				top: `calc(${hovered.top} + ${hovered.size} / 2 + 6px)`,
			}"
		>
			<p class="text-sm-medium text-ink-gray-9">{{ hovered.label }}</p>
			<p class="tabular-nums text-ink-gray-6">
				{{ hovered.visited }}
				clicks · {{ hovered.signed_up }} signups ·
				{{ hovered.converted }}
				paying
			</p>
		</div>
	</div>
</template>

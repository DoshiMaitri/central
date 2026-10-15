<script setup lang="ts">
import { Select } from 'frappe-ui'
import { computed, ref } from 'vue'
import CopyableValue from '@/components/common/CopyableValue.vue'
import CopyButton from '@/components/common/CopyButton.vue'
import { AFFILIATE_SOURCES } from '@/composables/useAffiliate'
import type { LinkProduct } from '@/types/affiliates'

interface AffiliateLinkCardProps {
	code: string
	products: LinkProduct[]
}

const props = defineProps<AffiliateLinkCardProps>()

// "fc" is the reserved key for Frappe Cloud itself, so it never clashes with a product.
const FRAPPE_CLOUD = 'fc'

const product = ref(FRAPPE_CLOUD)
const source = ref(AFFILIATE_SOURCES[0].value)

const productOptions = computed(() => [
	{ label: 'Frappe Cloud', value: FRAPPE_CLOUD },
	...props.products.map(({ name, title }) => ({ label: title, value: name })),
])
const link = computed(() => `${window.location.origin}/r/${props.code}`)
const builtLink = computed(() => {
	const query = new URLSearchParams()
	if (product.value !== FRAPPE_CLOUD) query.set('product', product.value)
	query.set('utm_source', source.value)
	return `${link.value}?${query}`
})
</script>

<template>
	<section
		aria-labelledby="affiliate-link-heading"
		class="flex flex-col gap-5 rounded-6 border border-outline-gray-1 bg-surface-base p-5"
	>
		<div class="flex flex-col gap-2">
			<h2
				id="affiliate-link-heading"
				class="text-base-semibold text-ink-gray-8"
			>
				Your link
			</h2>
			<div class="flex items-center gap-2">
				<CopyableValue :value="link" label="Affiliate link" block />
				<CopyButton :text="link" />
			</div>
		</div>

		<div class="flex flex-col gap-3 border-t border-outline-gray-1 pt-5">
			<h3 class="text-base-medium text-ink-gray-8">Link builder</h3>
			<p class="text-p-sm text-ink-gray-5">
				Make a link for one product and channel, so you can see which one brings
				signups.
			</p>
			<div class="grid gap-3 md:grid-cols-2">
				<Select v-model="product" :options="productOptions" label="Product" />
				<Select v-model="source" :options="AFFILIATE_SOURCES" label="Source" />
			</div>
			<div class="flex items-center gap-2">
				<CopyableValue :value="builtLink" label="Affiliate link" block />
				<CopyButton :text="builtLink" />
			</div>
		</div>
	</section>
</template>

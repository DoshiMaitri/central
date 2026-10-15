<script setup lang="ts">
import { Alert, Button, Select, TextInput } from 'frappe-ui'
import { computed, ref, watch } from 'vue'
import CopyableValue from '@/components/common/CopyableValue.vue'
import CopyButton from '@/components/common/CopyButton.vue'
import { AFFILIATE_SOURCES, affiliateUrl } from '@/composables/useAffiliate'
import { getErrorMessage, successToast } from '@/lib/feedback'
import type { LinkProduct, NewAffiliateLink } from '@/types/affiliates'

interface AffiliateLinkCardProps {
	code: string
	products: LinkProduct[]
	create: (link: NewAffiliateLink) => Promise<string>
}

const props = defineProps<AffiliateLinkCardProps>()

// "fc" is the reserved key for Frappe Cloud itself, so it never clashes with a product.
const FRAPPE_CLOUD = 'fc'

const slug = ref('')
const product = ref(FRAPPE_CLOUD)
const source = ref(AFFILIATE_SOURCES[0].value)
const campaign = ref('')
const creating = ref(false)
const createError = ref('')
// The slug saved last, so its link can be copied once it exists.
const savedSlug = ref('')

const productOptions = computed(() => [
	{ label: 'Frappe Cloud', value: FRAPPE_CLOUD },
	...props.products.map(({ name, title }) => ({ label: title, value: name })),
])
const cleanSlug = computed(() => slug.value.trim().toLowerCase())
const cleanCampaign = computed(() => campaign.value.trim())
const link = computed(() => affiliateUrl(props.code))

// Without a slug the main link carries the choices in its query. A slug is a saved
// link that keeps them itself, so its address is just /r/<slug>.
const builtLink = computed(() => {
	if (cleanSlug.value) return affiliateUrl(cleanSlug.value)

	const query = new URLSearchParams()
	if (product.value !== FRAPPE_CLOUD) query.set('product', product.value)
	query.set('utm_source', source.value)
	query.set('utm_campaign', cleanCampaign.value)
	return `${link.value}?${query}`
})
const isSaved = computed(
	() => !cleanSlug.value || cleanSlug.value === savedSlug.value,
)

watch([slug, product, source, campaign], () => {
	createError.value = ''
	if (cleanSlug.value !== savedSlug.value) savedSlug.value = ''
})

async function create(): Promise<void> {
	creating.value = true
	try {
		savedSlug.value = await props.create({
			slug: cleanSlug.value,
			product: product.value === FRAPPE_CLOUD ? '' : product.value,
			utm_source: source.value,
			utm_campaign: cleanCampaign.value,
		})
		successToast(`Link ${affiliateUrl(savedSlug.value)} created`)
	} catch (error) {
		createError.value = getErrorMessage(error, "The link couldn't be created.")
	} finally {
		creating.value = false
	}
}
</script>

<template>
	<section
		aria-labelledby="affiliate-link-heading"
		class="flex min-w-0 flex-col gap-5 rounded-6 border border-outline-gray-1 bg-surface-base p-5"
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
			<TextInput
				v-model="campaign"
				label="Campaign"
				placeholder="erpnext v16"
				maxlength="140"
			/>
			<div class="grid grid-cols-2 gap-3">
				<Select v-model="product" :options="productOptions" label="Product" />
				<Select v-model="source" :options="AFFILIATE_SOURCES" label="Source" />
			</div>
			<TextInput
				v-model="slug"
				label="Link slug (optional)"
				placeholder="bwh"
				maxlength="32"
			/>
			<Alert v-if="createError" theme="red" :title="createError" />

			<div v-if="cleanCampaign && isSaved" class="flex items-center gap-2">
				<CopyableValue :value="builtLink" label="Affiliate link" block />
				<CopyButton :text="builtLink" />
			</div>
			<template v-else-if="cleanCampaign">
				<p
					class="break-all rounded-4 bg-surface-gray-2 px-3 py-2 font-mono text-p-sm text-ink-gray-6"
				>
					{{ builtLink }}
				</p>
				<Button
					variant="solid"
					label="Create link"
					:loading="creating"
					@click="create"
				/>
			</template>
		</div>
	</section>
</template>

<template>
	<div class="layout-navbars-close-full" v-if="isTagsViewCurrenFull">
		<div class="layout-navbars-close-full-icon">
			<SvgIcon name="ele-Close" :title="$t('message.tagsView.closeFullscreen')" @click="onCloseFullscreen" />
		</div>
	</div>
</template>

<script setup lang="ts" name="layoutCloseFull">
import { storeToRefs } from 'pinia';
import { useTagsViewRoutes } from '/@/stores/tagsViewRoutes';

const stores = useTagsViewRoutes();
const { isTagsViewCurrenFull } = storeToRefs(stores);

const onCloseFullscreen = () => {
	stores.setCurrenFullscreen(false);
};
</script>

<style scoped lang="scss">
.layout-navbars-close-full {
	position: fixed;
	z-index: 9999999999;
	right: 26px;
	top: 26px;

	.layout-navbars-close-full-icon {
		width: 52px;
		height: 52px;
		border-radius: 18px;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		background: rgba(255, 255, 255, 0.82);
		backdrop-filter: blur(10px);
		box-shadow: 0 18px 30px rgba(27, 45, 72, 0.12);
		transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;

		:deep(i) {
			color: #294255;
			font-size: 20px;
			transition: color 0.2s ease;
		}
	}

	&:hover {
		.layout-navbars-close-full-icon {
			transform: translateY(-2px);
			background: rgba(255, 255, 255, 0.95);
			box-shadow: 0 22px 36px rgba(27, 45, 72, 0.16);
		}

		:deep(i) {
			color: #1f6f58;
		}
	}
}
</style>

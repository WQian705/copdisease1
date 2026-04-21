<template>
	<div class="layout-logo" v-if="setShowLogo" @click="onThemeConfigChange">
		<div class="layout-logo-mark">
			<img :src="logoMini" class="layout-logo-medium-img" />
		</div>
		<div class="layout-logo-copy">
			<strong>Crop AI</strong>
			<span>智慧农业监测平台</span>
		</div>
	</div>
	<div class="layout-logo-size" v-else @click="onThemeConfigChange">
		<div class="layout-logo-size-mark">
			<img :src="logoMini" class="layout-logo-size-img" />
		</div>
	</div>
</template>

<script setup lang="ts" name="layoutLogo">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useThemeConfig } from '/@/stores/themeConfig';
// import logoMini from '/@/assets/logo-mini.svg';
import logoMini from '/@/assets/logo.png';

// 定义变量内容
const storesThemeConfig = useThemeConfig();
const { themeConfig } = storeToRefs(storesThemeConfig);

// 设置 logo 的显示。classic 经典布局默认显示 logo
const setShowLogo = computed(() => {
	let { isCollapse, layout } = themeConfig.value;
	return !isCollapse || layout === 'classic' || document.body.clientWidth < 1000;
});
// logo 点击实现菜单展开/收起
const onThemeConfigChange = () => {
	if (themeConfig.value.layout === 'transverse') return false;
	themeConfig.value.isCollapse = !themeConfig.value.isCollapse;
};
</script>

<style scoped lang="scss">
.layout-logo {
	width: 220px;
	height: 78px;
	display: flex;
	align-items: center;
	justify-content: flex-start;
	padding: 0 16px;
	gap: 12px;
	border-bottom: 1px solid rgba(213, 225, 217, 0.72);
	cursor: pointer;
	animation: logoAnimation 0.3s ease-in-out;

	&-mark {
		width: 42px;
		height: 42px;
		border-radius: 14px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, #eef7f0 0%, #e4eef8 100%);
		box-shadow: inset 0 0 0 1px rgba(68, 118, 87, 0.08);
	}

	&-medium-img {
		width: 28px;
		height: 28px;
		object-fit: contain;
	}

	&-copy {
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	&-copy strong {
		color: #18334a;
		font-size: 16px;
		line-height: 1.2;
	}

	&-copy span {
		margin-top: 4px;
		color: #759080;
		font-size: 12px;
		white-space: nowrap;
	}
}
.layout-logo-size {
	width: 100%;
	height: 78px;
	display: flex;
	cursor: pointer;
	animation: logoAnimation 0.3s ease-in-out;
	border-bottom: 1px solid rgba(213, 225, 217, 0.72);

	&-mark {
		width: 42px;
		height: 42px;
		border-radius: 14px;
		display: flex;
		margin: auto;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, #eef7f0 0%, #e4eef8 100%);
		box-shadow: inset 0 0 0 1px rgba(68, 118, 87, 0.08);
	}

	&-img {
		width: 24px;
		height: 24px;
		object-fit: contain;
	}
	&:hover {
		transform: translateY(-1px);
	}
}
</style>

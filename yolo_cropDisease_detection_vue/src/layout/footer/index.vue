<template>
	<div class="layout-footer pb15">
		<div class="layout-footer-warp">
			<div class="footer-brand">CropGuard Smart Platform</div>
			<div class="footer-copy">基于 YOLO + AI 的农作物病虫害检测与环境监测系统</div>
		</div>
	</div>
</template>

<script setup lang="ts" name="layoutFooter">
</script>

<style scoped lang="scss">
.layout-footer {
	width: 100%;
	display: flex;

	&-warp {
		margin: auto;
		padding: 14px 20px;
		border-radius: 18px;
		text-align: center;
		background: rgba(255, 255, 255, 0.72);
		box-shadow: 0 10px 24px rgba(31, 52, 84, 0.05);
		animation: error-num 0.3s ease;
	}
}

.footer-brand {
	font-size: 14px;
	font-weight: 700;
	color: #294255;
	letter-spacing: 0.08em;
}

.footer-copy {
	margin-top: 6px;
	font-size: 12px;
	color: #718090;
}
</style>

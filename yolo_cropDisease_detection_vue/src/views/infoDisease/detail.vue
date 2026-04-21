<template>
	<div>
		<el-dialog
			v-model="state.isShowDialog"
			width="1180px"
			draggable
			:close-on-click-modal="false"
			:close-on-press-escape="false"
			class="detail-dialog"
		>
			<div class="disease-detail">
				<div class="detail-header">
					<span class="detail-badge">病害详情</span>
					<div class="title">{{ state.disease.name }}</div>
				</div>
				<div class="detail-content">
					<div class="content-left">
						<div class="section">
							<div class="section-title">
								<el-icon><ele-Warning /></el-icon>
								病害症状
							</div>
							<div class="section-content">{{ state.disease.symptoms }}</div>
						</div>
						<div class="section">
							<div class="section-title">
								<el-icon><ele-InfoFilled /></el-icon>
								发生因素
							</div>
							<div class="section-content">{{ state.disease.causes }}</div>
						</div>
						<div class="section">
							<div class="section-title">
								<el-icon><ele-Operation /></el-icon>
								防治方法
							</div>
							<div class="section-content">{{ state.disease.prevention }}</div>
						</div>
					</div>
					<div class="content-right">
						<div class="section image-section">
							<div class="section-title">
								<el-icon><ele-Picture /></el-icon>
								案例图片
							</div>
							<div class="section-content image-content">
								<el-image
									class="detail-image"
									:src="state.disease.image"
									:preview-src-list="[state.disease.image]"
									:preview-teleported="true"
									:hide-on-click-modal="true"
									fit="cover"
									:preview-options="{ zoom: false, closeOnPressEscape: true, toolbar: false }"
								/>
							</div>
						</div>
					</div>
				</div>
			</div>
		</el-dialog>
	</div>
</template>

<script setup lang="ts" name="diseaseDetail">
import { reactive } from 'vue';

const state = reactive({
	isShowDialog: false,
	disease: {} as any,
});

const openDialog = (row: any) => {
	state.disease = row;
	state.isShowDialog = true;
};

defineExpose({ openDialog });
</script>

<style scoped lang="scss">
.disease-detail {
	padding: 0 12px 12px;
}

.detail-header {
	margin-bottom: 20px;
	padding: 22px 24px;
	border-radius: 24px;
	background: linear-gradient(135deg, #163d33 0%, #246757 56%, #276f95 100%);
	color: #fff;
}

.detail-badge {
	display: inline-flex;
	padding: 7px 12px;
	border-radius: 999px;
	background: rgba(255, 255, 255, 0.12);
	font-size: 12px;
	letter-spacing: 0.12em;
}

.title {
	margin-top: 14px;
	font-size: 30px;
	font-weight: 700;
}

.detail-content {
	display: grid;
	grid-template-columns: minmax(0, 1.2fr) 430px;
	gap: 20px;
}

.section {
	margin-bottom: 18px;
	padding: 20px;
	border-radius: 22px;
	background: linear-gradient(180deg, #ffffff 0%, #f7faf8 100%);
	box-shadow: 0 18px 34px rgba(31, 52, 84, 0.06);
}

.section-title {
	display: flex;
	align-items: center;
	margin-bottom: 14px;
	font-size: 19px;
	font-weight: 700;
	color: #24384d;
}

.section-title .el-icon {
	margin-right: 8px;
	font-size: 20px;
	color: #2b79a5;
}

.section-content {
	padding: 18px;
	border-radius: 18px;
	background: #f5f8f6;
	line-height: 1.9;
	color: #435768;
}

.image-content {
	display: flex;
	justify-content: center;
}

.detail-image {
	width: 100%;
	max-width: 380px;
	height: 380px;
	border-radius: 18px;
	box-shadow: 0 14px 28px rgba(31, 52, 84, 0.12);
}

@media (max-width: 1100px) {
	.detail-content {
		grid-template-columns: 1fr;
	}
}
</style>

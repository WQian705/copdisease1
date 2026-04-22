<template>
	<div class="detail-page layout-padding">
		<div class="detail-panel layout-padding-auto layout-padding-view">
			<section class="detail-hero">
				<div>
					<span class="hero-badge">图片记录详情</span>
					<h2>查看单条图片识别记录与识别结果明细</h2>
					<p>支持同时查看原始图片、预测图片、识别摘要以及每个病虫害标签的识别置信度。</p>
				</div>
				<div class="hero-side">
					<span>识别用户</span>
					<strong>{{ state.form.username || '未加载' }}</strong>
				</div>
			</section>

			<section class="meta-card">
				<div class="meta-grid">
					<div class="meta-item">
						<span>作物种类</span>
						<strong>{{ state.form.kind || '--' }}</strong>
					</div>
					<div class="meta-item">
						<span>识别模型</span>
						<strong>{{ state.form.weight || '--' }}</strong>
					</div>
					<div class="meta-item">
						<span>最小阈值</span>
						<strong>{{ state.form.conf || '--' }}</strong>
					</div>
					<div class="meta-item">
						<span>识别时间</span>
						<strong>{{ state.form.startTime || '--' }}</strong>
					</div>
				</div>
			</section>

			<section class="content-grid">
				<section class="image-card">
					<div class="card-head">
						<h3>图片对比</h3>
						<p>左侧查看原始图片，右侧查看模型输出结果。</p>
					</div>
					<div class="image-grid">
						<div class="image-pane">
							<div class="pane-label">原始图片</div>
							<img v-if="state.form.inputImg" :src="state.form.inputImg" class="detail-image" />
							<div v-else class="empty-pane">暂无原始图片</div>
						</div>
						<div class="image-pane">
							<div class="pane-label">预测图片</div>
							<img v-if="state.form.outImg" :src="state.form.outImg" class="detail-image" />
							<div v-else class="empty-pane">暂无预测图片</div>
						</div>
					</div>
				</section>

				<section class="result-card">
					<div class="card-head">
						<h3>识别摘要</h3>
						<p>这里会显示这次识别的主要结果、最高置信度和总耗时。</p>
					</div>
					<div class="summary-grid">
						<div class="summary-item">
							<span>识别条目</span>
							<strong>{{ state.results.length }}</strong>
						</div>
						<div class="summary-item">
							<span>主要识别结果</span>
							<strong>{{ primaryResult?.label || '暂无结果' }}</strong>
						</div>
						<div class="summary-item">
							<span>最高置信度</span>
							<strong>{{ primaryResult?.confidenceText || '-' }}</strong>
						</div>
						<div class="summary-item">
							<span>总用时</span>
							<strong>{{ formatDuration(state.form.allTime) }}</strong>
						</div>
					</div>

					<div class="result-list">
						<div class="list-title">识别结果明细</div>
						<div v-if="state.results.length" class="tag-grid">
							<div v-for="item in state.results" :key="`${item.label}-${item.confidenceText}`" class="tag-item">
								<div class="tag-main">
									<span>{{ item.label || '未知结果' }}</span>
									<strong>{{ item.confidenceText }}</strong>
								</div>
								<div class="tag-sub">识别时间：{{ item.startTime || state.form.startTime || '--' }}</div>
							</div>
						</div>
						<div v-else class="empty-pane">当前记录暂无识别结果。</div>
					</div>
				</section>
			</section>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import request from '/@/utils/request';
import { useRoute } from 'vue-router';
import { resolveFileUrl } from '/@/utils/serviceUrl';

type ResultItem = {
	label: string;
	confidence: string | number;
	confidenceText: string;
	startTime?: string;
};

const route = useRoute();

const state = reactive({
	id: '',
	form: {} as any,
	results: [] as ResultItem[],
});

const isSuccessCode = (code: string | number) => String(code) === '0';

const normalizeArray = (value: string | string[]) => {
	if (Array.isArray(value)) return value;
	if (!value) return [];
	try {
		const parsed = JSON.parse(value);
		return Array.isArray(parsed) ? parsed : [parsed];
	} catch {
		return [value];
	}
};

const normalizeConfidenceText = (value: string | number) => {
	const numericValue = Number(String(value).replace(/[%\[\]"]/g, ''));
	if (Number.isFinite(numericValue)) {
		return `${numericValue.toFixed(2)}%`;
	}
	return String(value || '-');
};

const formatDuration = (value?: string | number) => {
	const numericValue = Number(String(value || '').replace(/[^\d.]/g, ''));
	if (Number.isFinite(numericValue) && numericValue > 0) {
		return `${numericValue.toFixed(3)} 秒`;
	}
	return value || '-';
};

const primaryResult = computed(() => {
	if (!state.results.length) return null;
	return [...state.results].sort((a, b) => {
		const aValue = Number(String(a.confidence).replace(/[%\[\]"]/g, ''));
		const bValue = Number(String(b.confidence).replace(/[%\[\]"]/g, ''));
		return (Number.isFinite(bValue) ? bValue : -1) - (Number.isFinite(aValue) ? aValue : -1);
	})[0];
});

const getData = () => {
	request
		.get(`/api/imgRecords/${state.id}`)
		.then((res) => {
			if (!isSuccessCode(res.code)) {
				ElMessage.error(res.msg);
				return;
			}
			const form = { ...res.data };
			form.inputImg = resolveFileUrl(form.inputImg);
			form.outImg = resolveFileUrl(form.outImg);
			state.form = form;

			const labels = normalizeArray(form.label);
			const confidences = normalizeArray(form.confidence);
			state.results = labels.map((label: string, index: number) => ({
				label,
				confidence: confidences[index] || '-',
				confidenceText: normalizeConfidenceText(confidences[index] || '-'),
				startTime: form.startTime,
			}));
		})
		.catch(() => {
			ElMessage.error('加载图片记录详情失败');
		});
};

onMounted(() => {
	state.id = String(route.query.id || '');
	getData();
});
</script>

<style scoped lang="scss">
.detail-page {
	position: relative;
	left: auto;
	top: auto;
	height: auto;
	min-height: 100%;
	overflow: visible;

	.detail-panel {
		padding: 18px;
		height: auto;
		min-height: 100%;
		overflow: visible;
		background: rgba(255, 255, 255, 0.88);
	}
}

.detail-hero {
	display: flex;
	justify-content: space-between;
	gap: 16px;
	padding: 24px;
	border-radius: 24px;
	background: linear-gradient(135deg, #1a3444 0%, #1c6259 54%, #2b7a9d 100%);
	color: #fff;
}

.hero-badge {
	display: inline-flex;
	padding: 7px 12px;
	border-radius: 999px;
	background: rgba(255, 255, 255, 0.12);
	font-size: 12px;
	letter-spacing: 0.12em;
}

.detail-hero h2 {
	margin: 14px 0 8px;
	font-size: 28px;
}

.detail-hero p {
	color: rgba(255, 255, 255, 0.8);
	line-height: 1.8;
}

.hero-side {
	min-width: 150px;
	padding: 18px;
	border-radius: 20px;
	background: rgba(255, 255, 255, 0.12);
}

.hero-side span {
	color: rgba(255, 255, 255, 0.72);
	font-size: 13px;
}

.hero-side strong {
	display: block;
	margin-top: 10px;
	font-size: 26px;
	word-break: break-word;
}

.meta-card,
.image-card,
.result-card {
	border-radius: 22px;
	background: linear-gradient(180deg, #ffffff 0%, #f7faf8 100%);
	box-shadow: 0 18px 34px rgba(31, 52, 84, 0.06);
}

.meta-card {
	margin-top: 16px;
	padding: 18px;
}

.meta-grid {
	display: grid;
	grid-template-columns: repeat(4, minmax(0, 1fr));
	gap: 12px;
}

.meta-item,
.summary-item {
	padding: 16px 18px;
	border-radius: 18px;
	background: #f5f8f6;
}

.meta-item span,
.summary-item span {
	display: block;
	color: #738294;
	font-size: 13px;
}

.meta-item strong,
.summary-item strong {
	display: block;
	margin-top: 10px;
	color: #23394b;
	font-size: 18px;
	word-break: break-word;
}

.content-grid {
	display: grid;
	grid-template-columns: minmax(0, 1.1fr) minmax(340px, 0.9fr);
	gap: 16px;
	margin-top: 16px;
}

.image-card,
.result-card {
	padding: 18px;
}

.card-head h3,
.list-title {
	margin: 0 0 6px;
	color: #24384d;
}

.card-head p {
	margin: 0 0 16px;
	color: #7d8a98;
}

.image-grid {
	display: grid;
	grid-template-columns: repeat(2, minmax(0, 1fr));
	gap: 16px;
}

.image-pane {
	padding: 18px;
	border-radius: 20px;
	background: #f4f8f6;
}

.pane-label {
	margin-bottom: 12px;
	font-size: 13px;
	color: #66788b;
}

.detail-image {
	width: 100%;
	min-height: 320px;
	max-height: 520px;
	object-fit: contain;
	border-radius: 18px;
	background: #fff;
	box-shadow: 0 20px 36px rgba(15, 23, 32, 0.08);
}

.summary-grid {
	display: grid;
	grid-template-columns: repeat(2, minmax(0, 1fr));
	gap: 12px;
}

.result-list {
	margin-top: 16px;
}

.tag-grid {
	display: grid;
	gap: 10px;
}

.tag-item {
	padding: 12px 14px;
	border-radius: 14px;
	background: #f6faf7;
}

.tag-main {
	display: flex;
	justify-content: space-between;
	gap: 12px;
}

.tag-main span {
	color: #23465f;
	font-weight: 600;
}

.tag-main strong {
	color: #1f6d57;
}

.tag-sub,
.empty-pane {
	margin-top: 8px;
	color: #7c8a97;
}

@media (max-width: 1200px) {
	.content-grid {
		grid-template-columns: 1fr;
	}
}

@media (max-width: 992px) {
	.detail-hero {
		flex-direction: column;
	}

	.meta-grid,
	.image-grid,
	.summary-grid {
		grid-template-columns: 1fr;
	}
}
</style>

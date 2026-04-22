<template>
	<div class="predict-page layout-padding">
		<div class="predict-panel layout-padding-auto layout-padding-view">
			<section class="predict-hero">
				<div>
					<span class="hero-badge">图片检测</span>
					<h2>上传作物图片并获得病虫害识别结果</h2>
					<p>保留模型选择、置信度设置、识别请求与 AI 建议生成流程，只优化展示和交互体验。</p>
				</div>
				<div class="hero-side">
					<span>当前作物</span>
					<strong>{{ selectedKindLabel }}</strong>
				</div>
			</section>

			<section class="control-card">
				<div class="control-grid">
					<el-select v-model="kind" placeholder="请选择作物种类" size="large" @change="getData">
						<el-option v-for="item in state.kind_items" :key="item.value" :label="item.label" :value="item.value" />
					</el-select>
					<el-select v-model="weight" placeholder="请选择模型" size="large">
						<el-option v-for="item in state.weight_items" :key="item.value" :label="item.label" :value="item.value" />
					</el-select>
					<div class="slider-wrap">
						<div class="slider-label">最小置信度阈值</div>
						<el-slider v-model="conf" :format-tooltip="formatTooltip" />
					</div>
					<div class="action-wrap">
						<el-button type="primary" @click="upData" class="predict-button">开始预测</el-button>
					</div>
				</div>
			</section>

			<section class="workspace-grid">
				<el-card shadow="never" class="workspace-card">
					<template #header>
						<div class="card-title">原图图片</div>
					</template>
					<el-upload
						v-model="state.img"
						ref="uploadFile"
						class="upload-box"
						:action="uploadActionUrl"
						:show-file-list="false"
						:on-success="handleAvatarSuccessone"
					>
						<el-image v-if="imageUrl" :src="imageUrl" class="preview-image" fit="contain" />
						<div v-else class="empty-box">
							<el-icon class="empty-icon"><Plus /></el-icon>
							<div>点击上传图片</div>
						</div>
					</el-upload>
				</el-card>

				<el-card shadow="never" class="workspace-card">
					<template #header>
						<div class="card-title">预测结果</div>
					</template>
					<el-image v-if="predictedImageUrl" :src="predictedImageUrl" class="preview-image result-image" fit="contain" />
					<div v-else class="empty-box">
						<el-icon class="empty-icon"><Picture /></el-icon>
						<div>预测完成后将在这里显示结果</div>
					</div>
				</el-card>

				<el-card shadow="never" class="workspace-card">
					<template #header>
						<div class="card-title">智能建议</div>
					</template>
					<div v-if="state.aiSuggestion" class="suggestion-box">
						<div class="suggestion-text">{{ state.aiSuggestion }}</div>
					</div>
					<div v-else class="empty-box">
						<el-icon class="empty-icon"><ChatLineRound /></el-icon>
						<div>预测完成后将自动生成智能建议</div>
					</div>
				</el-card>
			</section>

			<section class="result-card">
				<div class="result-head">
					<h3>识别摘要</h3>
					<p>展示识别结果、预测概率与总耗时</p>
				</div>
				<div v-if="state.predictionResult.label" class="result-grid">
					<div class="result-column">
						<div class="result-label">识别结果</div>
						<div v-for="(label, index) in formatLabelArray(state.predictionResult.label)" :key="index" class="result-item">
							{{ label }}
						</div>
					</div>
					<div class="result-column">
						<div class="result-label">预测概率</div>
						<div v-for="(item, index) in formatConfidenceArray(state.predictionResult.confidence)" :key="index" class="result-item">
							{{ item }}
						</div>
					</div>
					<div class="result-column">
						<div class="result-label">总时间</div>
						<div class="result-item">{{ formatTime(state.predictionResult.allTime) }}</div>
					</div>
				</div>
				<div v-else class="result-empty">
					<el-icon><Picture /></el-icon>
					<span>预测结果将在这里显示</span>
				</div>
			</section>
		</div>
	</div>
</template>

<script setup lang="ts" name="personal">
import { reactive, ref, onMounted, computed } from 'vue';
import type { UploadInstance, UploadProps } from 'element-plus';
import { ElMessage } from 'element-plus';
import request from '/@/utils/request';
import { Plus, ChatLineRound, Picture } from '@element-plus/icons-vue';
import { useUserInfo } from '/@/stores/userInfo';
import { storeToRefs } from 'pinia';
import { formatDate } from '/@/utils/formatTime';
import axios from 'axios';
import { uploadActionUrl } from '/@/utils/serviceUrl';

const imageUrl = ref('');
const conf = ref('0');
const weight = ref('');
const kind = ref('');
const uploadFile = ref<UploadInstance>();
const stores = useUserInfo();
const { userInfos } = storeToRefs(stores);
const predictedImageUrl = ref('');
const state = reactive({
	weight_items: [] as Array<{ value: string; label: string }>,
	kind_items: [
		{ value: 'corn', label: '玉米' },
		{ value: 'rice', label: '水稻' },
		{ value: 'wheat', label: '小麦' },
		{ value: 'potato', label: '马铃薯' },
		{ value: 'tomato', label: '番茄' },
		{ value: 'cotton', label: '棉花' },
		{ value: 'apple', label: '苹果' },
		{ value: 'grape', label: '葡萄' },
		{ value: 'strawberry', label: '草莓' },
	],
	img: '',
	predictionResult: {
		label: '',
		confidence: '',
		allTime: '',
	},
	form: {
		username: '',
		inputImg: null as any,
		weight: '',
		conf: null as any,
		kind: '',
		startTime: '',
	},
	aiSuggestion: '',
	suggestionLoading: false,
});

const selectedKindLabel = computed(() => {
	return state.kind_items.find((item) => item.value === kind.value)?.label || '未选择';
});

const formatTooltip = (val: number) => {
	return val / 100;
};

const handleAvatarSuccessone: UploadProps['onSuccess'] = (response, uploadFile) => {
	imageUrl.value = URL.createObjectURL(uploadFile.raw!);
	state.img = response.data;
};

const getData = () => {
	request.get('/api/flask/file_names').then((res) => {
		if (String(res.code) === '0') {
			const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;
			state.weight_items = (data.weight_items || []).filter((item: { value: string; label: string }) => item.value.includes(kind.value));
		} else {
			ElMessage.error(res.msg);
		}
	});
};

const upData = () => {
	state.form.weight = weight.value;
	state.form.conf = parseFloat(conf.value) / 100;
	state.form.username = userInfos.value.userName;
	state.form.inputImg = state.img;
	state.form.kind = kind.value;
	state.form.startTime = formatDate(new Date(), 'YYYY-mm-dd HH:MM:SS');
	request.post('/api/flask/predict', state.form).then((res) => {
		if (String(res.code) === '0') {
			try {
				res.data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;
				if (typeof res.data.label === 'string') {
					res.data.label = JSON.parse(res.data.label);
				}
				if (Array.isArray(res.data.label)) {
					state.predictionResult.label = res.data.label.map((item: string) =>
						item.replace(/\\u([\dA-Fa-f]{4})/g, (_, code) => String.fromCharCode(parseInt(code, 16)))
					);
				}
				state.predictionResult.confidence = res.data.confidence;
				state.predictionResult.allTime = res.data.allTime;
				if (res.data.outImg) predictedImageUrl.value = res.data.outImg;
			} catch (error) {
				console.error('解析 JSON 时出错', error);
			}
			ElMessage.success('预测成功');
			getAISuggestion();
		} else {
			ElMessage.error(res.msg);
		}
	});
};

const getAISuggestion = async () => {
	if (!state.predictionResult.label) {
		ElMessage.warning('请先进行预测');
		return;
	}
	state.suggestionLoading = true;
	try {
		const apiKey = 'sk-3rG1hl3sdDbbRoqEHr7utZpcbqbufy1miSD9XhLvVxJGAb4W';
		const prompt = `作为一个专业的农作物病害专家，请对以下情况进行详细分析：
1. 基本信息：
- 作物类型：${state.kind_items.find((item) => item.value === kind.value)?.label || kind.value}
- 检测到的病害：${state.predictionResult.label}
- 检测置信度：${state.predictionResult.confidence}

2. 请提供以下方面的专业分析：
(1) 病害危害程度：
1. 当前病害的严重程度评估
2. 对作物生长的影响
3. 可能造成的产量损失

(2) 防治建议：
1. 立即可采取的防治措施
2. 推荐使用的农药或生物防治方法
3. 施药注意事项和防护措施

(3) 预防措施：
1. 日常管理建议
2. 环境控制要点
3. 预防性保护措施

请用专业但易懂的语言回答，并尽可能提供具体的操作建议。`;

		const response = await axios.post(
			'https://api.chatanywhere.tech/v1/chat/completions',
			{
				model: 'gpt-3.5-turbo',
				messages: [{ role: 'user', content: prompt }],
				temperature: 0.7,
			},
			{
				headers: {
					Authorization: `Bearer ${apiKey}`,
					'Content-Type': 'application/json',
				},
			}
		);

		state.aiSuggestion = response.data.choices[0].message.content;
		ElMessage.success('分析完成');
	} catch (error) {
		console.error('获取 AI 建议出错:', error);
		ElMessage.error('获取建议失败，请检查网络连接或 API 配置');
	} finally {
		state.suggestionLoading = false;
	}
};

const formatLabelArray = (label: any) => {
	if (Array.isArray(label)) return label.map((item) => item.replace(/[\[\]"]/g, '').trim());
	if (typeof label === 'string') return [label.replace(/[\[\]"]/g, '').trim()];
	return ['未知'];
};

const formatConfidenceArray = (confidence: string) => {
	if (!confidence) return ['0%'];
	try {
		let confidences: any = confidence;
		if (typeof confidence === 'string') confidences = JSON.parse(confidence);
		if (Array.isArray(confidences)) {
			return confidences.map((conf) => `${parseFloat(String(conf).replace(/[\[\]"%]/g, '')).toFixed(2)}%`);
		}
		return [`${parseFloat(String(confidence).replace(/[\[\]"%]/g, '')).toFixed(2)}%`];
	} catch (error) {
		console.error('解析置信度出错', error);
		return ['0%'];
	}
};

const formatTime = (time: string) => {
	if (!time) return '0 秒';
	const value = parseFloat(String(time).replace(/[^\d.]/g, '')) || 0;
	return `${value.toFixed(3)} 秒`;
};

onMounted(() => {
	getData();
});
</script>

<style scoped lang="scss">
.predict-page {
	position: relative;
	left: auto;
	top: auto;
	height: auto;
	min-height: 100%;
	overflow: visible;

	.predict-panel {
		padding: 18px;
		height: auto;
		min-height: 100%;
		overflow: visible;
		background: rgba(255, 255, 255, 0.88);
	}
}

.predict-hero {
	display: flex;
	justify-content: space-between;
	gap: 16px;
	padding: 24px;
	border-radius: 24px;
	background: linear-gradient(135deg, #163d33 0%, #246757 56%, #276f95 100%);
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

.predict-hero h2 {
	margin: 14px 0 8px;
	font-size: 28px;
}

.predict-hero p {
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
}

.control-card,
.workspace-card,
.result-card {
	margin-top: 16px;
	border: none;
	border-radius: 22px;
	background: linear-gradient(180deg, #ffffff 0%, #f7faf8 100%);
	box-shadow: 0 18px 34px rgba(31, 52, 84, 0.06);
}

.control-card {
	padding: 18px;
}

.control-grid {
	display: grid;
	grid-template-columns: repeat(2, minmax(0, 220px)) minmax(0, 1fr) auto;
	gap: 12px;
	align-items: center;
}

.slider-wrap {
	padding: 10px 14px;
	border-radius: 16px;
	background: #f5f8f6;
}

.slider-label {
	margin-bottom: 8px;
	font-size: 13px;
	color: #607286;
}

.action-wrap {
	display: flex;
	justify-content: flex-end;
}

.workspace-grid {
	display: grid;
	grid-template-columns: repeat(3, minmax(0, 1fr));
	gap: 16px;
	margin-top: 16px;
}

.card-title {
	font-size: 17px;
	font-weight: 700;
	color: #23384d;
}

.upload-box {
	width: 100%;
}

:deep(.upload-box .el-upload) {
	width: 100%;
}

.preview-image,
.empty-box,
.suggestion-box {
	width: 100%;
	height: 360px;
	border-radius: 18px;
	background: #f5f8f6;
}

.preview-image {
	display: block;
}

.result-image {
	box-shadow: 0 12px 24px rgba(31, 52, 84, 0.12);
}

.empty-box {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: 12px;
	color: #8291a1;
}

.empty-icon {
	font-size: 30px;
}

.suggestion-box {
	padding: 18px;
	overflow-y: auto;
}

.suggestion-text {
	line-height: 1.9;
	color: #34495e;
	white-space: pre-wrap;
}

.result-card {
	padding: 20px;
}

.result-head h3 {
	margin: 0 0 6px;
	color: #24384d;
}

.result-head p {
	margin: 0;
	color: #7d8a98;
}

.result-grid {
	display: grid;
	grid-template-columns: repeat(3, minmax(0, 1fr));
	gap: 16px;
	margin-top: 18px;
}

.result-column {
	padding: 18px;
	border-radius: 18px;
	background: #f6faf7;
}

.result-label {
	margin-bottom: 12px;
	color: #6b7c8d;
	font-size: 13px;
}

.result-item {
	margin-bottom: 8px;
	color: #1f6d57;
	font-weight: 700;
}

.result-empty {
	margin-top: 18px;
	min-height: 110px;
	border-radius: 18px;
	background: #f6faf7;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
	color: #8593a2;
}

.predict-button {
	min-width: 140px;
	height: 46px;
	border: none;
	border-radius: 16px;
	background: linear-gradient(135deg, #1f6f58 0%, #2f8b70 55%, #2c79a5 100%);
	box-shadow: 0 18px 32px rgba(39, 103, 91, 0.2);
}

:deep(.el-select .el-input__wrapper),
:deep(.el-input__wrapper) {
	border-radius: 14px;
	background: #f5f8f6;
	box-shadow: inset 0 0 0 1px rgba(106, 128, 115, 0.12) !important;
}

@media (max-width: 1200px) {
	.workspace-grid {
		grid-template-columns: 1fr;
	}
}

@media (max-width: 992px) {
	.predict-hero,
	.control-grid,
	.result-grid {
		grid-template-columns: 1fr;
	}

	.predict-hero {
		flex-direction: column;
	}

	.action-wrap {
		justify-content: flex-start;
	}
}
</style>

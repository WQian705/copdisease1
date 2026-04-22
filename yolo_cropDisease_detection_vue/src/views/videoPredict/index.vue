<template>
	<div class="predict-page layout-padding">
		<div class="predict-panel layout-padding-auto layout-padding-view">
			<section class="predict-hero">
				<div>
					<span class="hero-badge">视频检测</span>
					<h2>上传视频并实时查看病虫害识别结果</h2>
					<p>处理时同步展示时间戳、当前帧识别结果和最近识别日志，结束后自动保存到识别记录。</p>
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
					<div class="action-row">
						<el-upload
							v-model="state.form.inputVideo"
							ref="uploadFile"
							class="upload-trigger"
							:action="uploadActionUrl"
							:show-file-list="false"
							:on-success="handleAvatarSuccessone"
						>
							<el-button type="info" class="secondary-button">上传视频</el-button>
						</el-upload>
						<el-button type="primary" @click="upData" class="predict-button">开始处理</el-button>
					</div>
				</div>
				<div v-if="state.isShow" class="progress-wrap">
					<el-progress :text-inside="true" :stroke-width="20" :percentage="state.percentage">
						<span>{{ state.type_text }} {{ state.percentage.toFixed(0) }}%</span>
					</el-progress>
				</div>
			</section>

			<section class="workspace-card">
				<div class="workspace-head">
					<div>
						<h3>处理结果预览</h3>
						<p>左侧显示缩小后的视频流，右侧实时显示当前帧时间戳、检测结果和逐帧记录。</p>
					</div>
					<div class="live-state">
						<span>当前时间戳</span>
						<strong>{{ currentFrame.timestamp || '--:--:--.---' }}</strong>
					</div>
				</div>

				<div class="workspace-grid">
					<div class="video-stage">
						<img v-if="state.video_path" class="video-stream" :src="state.video_path" />
						<div v-else class="video-empty">
							<span>上传视频并开始处理后，这里会显示实时识别画面。</span>
						</div>
					</div>

					<div class="result-panel">
						<div class="result-summary">
							<div class="summary-card">
								<span>当前帧</span>
								<strong>#{{ currentFrame.frameIndex ?? '--' }}</strong>
							</div>
							<div class="summary-card">
								<span>检测数量</span>
								<strong>{{ currentFrame.detectionCount ?? 0 }}</strong>
							</div>
						</div>

						<div class="current-card">
							<div class="panel-title">当前病虫害检测结果</div>
							<div v-if="currentFrame.topLabels?.length" class="tag-list">
								<div v-for="item in currentFrame.topLabels" :key="`${item.label}-${item.confidence}`" class="result-tag">
									<span>{{ item.label }}</span>
									<strong>{{ formatPercent(item.confidence) }}</strong>
								</div>
							</div>
							<div v-else class="empty-text">当前帧未检测到明显病虫害。</div>
						</div>

						<div class="timeline-card">
							<div class="panel-title">逐帧识别记录</div>
							<div class="timeline-list">
								<div v-for="item in displayFrameResults" :key="`${item.frameIndex}-${item.timestamp}`" class="timeline-item">
									<div class="timeline-meta">
										<strong>{{ item.timestamp }}</strong>
										<span>第 {{ item.frameIndex }} 帧</span>
									</div>
									<div class="timeline-text">{{ item.summaryText || '未检测到病虫害' }}</div>
								</div>
								<div v-if="!displayFrameResults.length" class="empty-text">识别开始后，这里会持续追加每一帧的检测结果。</div>
							</div>
						</div>
					</div>
				</div>
			</section>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import request from '/@/utils/request';
import { useUserInfo } from '/@/stores/userInfo';
import { storeToRefs } from 'pinia';
import type { UploadInstance, UploadProps } from 'element-plus';
import { SocketService } from '/@/utils/socket';
import { formatDate } from '/@/utils/formatTime';
import { buildFlaskStreamUrl, uploadActionUrl } from '/@/utils/serviceUrl';

type FrameResult = {
	frameIndex?: number;
	timestamp?: string;
	timestampSeconds?: number;
	detectionCount?: number;
	summaryText?: string;
	topLabels?: Array<{ label: string; confidence: number }>;
	source?: string;
};

const uploadFile = ref<UploadInstance>();
const stores = useUserInfo();
const conf = ref('0');
const kind = ref('');
const weight = ref('');
const { userInfos } = storeToRefs(stores);

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
	video_path: '',
	type_text: '正在保存',
	percentage: 0,
	isShow: false,
	form: {
		username: '',
		inputVideo: null as any,
		weight: '',
		conf: null as any,
		kind: '',
		startTime: '',
	},
});

const socketService = new SocketService();
const frameResults = ref<FrameResult[]>([]);
const currentFrame = ref<FrameResult>({});

const selectedKindLabel = computed(() => {
	return state.kind_items.find((item) => item.value === kind.value)?.label || '未选择';
});

const displayFrameResults = computed(() => frameResults.value.slice(0, 120));
const isSuccessCode = (code: string | number) => String(code) === '0';

const resetLiveState = () => {
	frameResults.value = [];
	currentFrame.value = {};
	state.percentage = 0;
	state.isShow = false;
};

const handleAvatarSuccessone: UploadProps['onSuccess'] = (response) => {
	ElMessage.success('上传成功');
	state.form.inputVideo = response.data;
};

const formatTooltip = (val: number) => val / 100;
const formatPercent = (confidence?: number) => `${((confidence || 0) * 100).toFixed(1)}%`;

const getData = () => {
	request.get('/api/flask/file_names').then((res) => {
		if (!isSuccessCode(res.code)) {
			ElMessage.error(res.msg);
			return;
		}
		const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;
		state.weight_items = (data.weight_items || []).filter((item: { value: string; label: string }) => item.value.includes(kind.value));
		if (!state.weight_items.some((item) => item.value === weight.value)) {
			weight.value = '';
		}
	});
};

const upData = () => {
	if (!state.form.inputVideo) {
		ElMessage.warning('请先上传视频');
		return;
	}
	resetLiveState();
	state.form.weight = weight.value;
	state.form.conf = parseFloat(conf.value) / 100;
	state.form.username = userInfos.value.userName;
	state.form.kind = kind.value;
	state.form.startTime = formatDate(new Date(), 'YYYY-mm-dd HH:MM:SS');
	const queryParams = new URLSearchParams(state.form as Record<string, string>).toString();
	state.video_path = buildFlaskStreamUrl('predictVideo', queryParams);
	ElMessage.success('正在加载视频检测流');
};

socketService.on('message', (data: string) => {
	if (data && !String(data).includes('Connected to WebSocket server')) {
		ElMessage.success(data);
	}
});

socketService.on('progress', (data: string | number) => {
	state.percentage = parseFloat(String(data)) || 0;
	if (state.percentage < 100) {
		state.isShow = true;
	} else {
		setTimeout(() => {
			state.isShow = false;
			state.percentage = 0;
		}, 2000);
	}
});

socketService.on('frame_result', (data: FrameResult) => {
	if (data?.source !== 'video') return;
	currentFrame.value = data;
	frameResults.value = [data, ...frameResults.value].slice(0, 300);
});

onMounted(() => {
	getData();
});

onUnmounted(() => {
	socketService.disconnect();
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
	background: linear-gradient(135deg, #183742 0%, #216357 52%, #2c7396 100%);
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
.workspace-card {
	margin-top: 16px;
	padding: 18px;
	border-radius: 22px;
	background: linear-gradient(180deg, #ffffff 0%, #f7faf8 100%);
	box-shadow: 0 18px 34px rgba(31, 52, 84, 0.06);
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

.action-row {
	display: flex;
	flex-wrap: wrap;
	justify-content: flex-end;
	gap: 10px;
}

.progress-wrap {
	margin-top: 16px;
}

.workspace-head {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	gap: 16px;
	margin-bottom: 18px;
}

.workspace-head h3 {
	margin: 0 0 6px;
	color: #24384d;
}

.workspace-head p {
	margin: 0;
	color: #7d8a98;
}

.live-state {
	min-width: 180px;
	padding: 14px 16px;
	border-radius: 18px;
	background: #f5f8f6;
}

.live-state span {
	display: block;
	font-size: 13px;
	color: #718294;
}

.live-state strong {
	display: block;
	margin-top: 8px;
	font-size: 20px;
	color: #1d6b59;
}

.workspace-grid {
	display: grid;
	grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.85fr);
	gap: 16px;
	align-items: start;
}

.video-stage {
	min-height: 420px;
	padding: 20px;
	border-radius: 22px;
	background: #f4f8f6;
	display: flex;
	align-items: center;
	justify-content: center;
	overflow: hidden;
}

.video-stream {
	width: 100%;
	max-width: 820px;
	max-height: 480px;
	border-radius: 18px;
	object-fit: contain;
	background: #0f1720;
	box-shadow: 0 20px 36px rgba(15, 23, 32, 0.14);
}

.video-empty,
.empty-text {
	color: #8694a3;
}

.result-panel {
	display: grid;
	gap: 16px;
}

.result-summary {
	display: grid;
	grid-template-columns: repeat(2, minmax(0, 1fr));
	gap: 12px;
}

.summary-card,
.current-card,
.timeline-card {
	padding: 16px;
	border-radius: 18px;
	background: #f5f8f6;
}

.summary-card span,
.panel-title {
	display: block;
	color: #687c91;
	font-size: 13px;
}

.summary-card strong {
	display: block;
	margin-top: 8px;
	font-size: 24px;
	color: #24445b;
}

.panel-title {
	margin-bottom: 12px;
	font-weight: 700;
}

.tag-list {
	display: flex;
	flex-wrap: wrap;
	gap: 10px;
}

.result-tag {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 10px;
	width: 100%;
	padding: 10px 12px;
	border-radius: 14px;
	background: #ffffff;
	box-shadow: inset 0 0 0 1px rgba(106, 128, 115, 0.12);
}

.result-tag span {
	color: #2f4b61;
}

.result-tag strong {
	color: #1f6d57;
}

.timeline-list {
	max-height: 360px;
	overflow-y: auto;
	display: grid;
	gap: 10px;
}

.timeline-item {
	padding: 12px;
	border-radius: 14px;
	background: #ffffff;
	box-shadow: inset 0 0 0 1px rgba(106, 128, 115, 0.1);
}

.timeline-meta {
	display: flex;
	justify-content: space-between;
	gap: 12px;
	font-size: 13px;
	color: #66788b;
}

.timeline-meta strong {
	color: #22455e;
}

.timeline-text {
	margin-top: 8px;
	line-height: 1.6;
	color: #3d5368;
	word-break: break-word;
}

.predict-button,
.secondary-button {
	height: 46px;
	border: none;
	border-radius: 16px;
}

.predict-button {
	background: linear-gradient(135deg, #1f6f58 0%, #2f8b70 55%, #2c79a5 100%);
	box-shadow: 0 18px 32px rgba(39, 103, 91, 0.2);
}

.secondary-button {
	background: linear-gradient(135deg, #798998 0%, #667685 100%);
	color: #fff;
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
	.workspace-head {
		flex-direction: column;
	}

	.control-grid {
		grid-template-columns: 1fr;
	}

	.action-row {
		justify-content: flex-start;
	}
}
</style>

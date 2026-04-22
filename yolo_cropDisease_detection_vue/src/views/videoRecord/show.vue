<template>
	<div class="compare-page layout-padding">
		<div class="compare-panel layout-padding-auto layout-padding-view">
			<section class="compare-hero">
				<div>
					<span class="hero-badge">{{ isCameraMode ? '摄像头记录详情' : '视频记录详情' }}</span>
					<h2>{{ isCameraMode ? '查看摄像头识别回放与逐帧结果' : '同步查看原始视频、识别结果与逐帧日志' }}</h2>
					<p>播放视频时，右侧会根据当前播放时间自动匹配对应帧的病虫害识别结果与时间戳。</p>
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
						<span>开始时间</span>
						<strong>{{ state.form.startTime || '--' }}</strong>
					</div>
				</div>
				<div class="action-row">
					<el-button type="primary" class="play-button" @click="playVideos">开始播放</el-button>
					<el-button type="info" plain class="pause-button" @click="pauseVideos">暂停播放</el-button>
				</div>
			</section>

			<section class="content-grid">
				<section class="video-card">
					<div class="stage-header">
						<div>
							<h3>{{ isCameraMode ? '检测视频回放' : '视频对比回放' }}</h3>
							<p>{{ isCameraMode ? '回放摄像头识别结果，并与右侧逐帧日志联动。' : '同时查看原始视频和识别结果，右侧同步显示当前帧病虫害信息。' }}</p>
						</div>
					</div>

					<div v-if="isCameraMode" class="single-stage">
						<video
							ref="resultVideoRef"
							class="video"
							v-if="state.form.outVideo"
							preload="metadata"
							controls
							@timeupdate="syncCurrentFrame(resultVideoRef)"
						>
							<source :src="state.form.outVideo" type="video/mp4" />
						</video>
						<div v-else class="empty-pane">暂无检测视频</div>
					</div>

					<div v-else class="double-stage">
						<div class="stage-pane">
							<div class="pane-label">原始视频</div>
							<video
								ref="inputVideoRef"
								class="video"
								v-if="state.form.inputVideo"
								preload="metadata"
								controls
								@timeupdate="syncCurrentFrame(inputVideoRef)"
							>
								<source :src="state.form.inputVideo" type="video/mp4" />
							</video>
							<div v-else class="empty-pane">暂无原始视频</div>
						</div>
						<div class="stage-pane">
							<div class="pane-label">识别结果</div>
							<video
								ref="resultVideoRef"
								class="video"
								v-if="state.form.outVideo"
								preload="metadata"
								controls
								@timeupdate="syncCurrentFrame(resultVideoRef)"
							>
								<source :src="state.form.outVideo" type="video/mp4" />
							</video>
							<div v-else class="empty-pane">暂无识别结果视频</div>
						</div>
					</div>
				</section>

				<section class="timeline-card">
					<div class="timeline-current">
						<div class="current-title">当前播放帧结果</div>
						<div class="current-time">{{ currentFrame.timestamp || '--:--:--.---' }}</div>
						<div class="current-meta">
							<span>第 {{ currentFrame.frameIndex ?? '--' }} 帧</span>
							<span>检测数量 {{ currentFrame.detectionCount ?? 0 }}</span>
						</div>
						<div v-if="currentFrame.topLabels?.length" class="tag-list">
							<div v-for="item in currentFrame.topLabels" :key="`${item.label}-${item.confidence}`" class="result-tag">
								<span>{{ item.label }}</span>
								<strong>{{ formatPercent(item.confidence) }}</strong>
							</div>
						</div>
						<div v-else class="empty-text">当前时间点未检测到明显病虫害。</div>
					</div>

					<div class="timeline-list">
						<div class="timeline-title">逐帧病虫害检测记录</div>
						<div v-if="state.frameResults.length" class="frame-list">
							<div
								v-for="item in state.frameResults"
								:key="`${item.frameIndex}-${item.timestamp}`"
								class="frame-item"
								:class="{ active: item.frameIndex === currentFrame.frameIndex }"
							>
								<div class="frame-meta">
									<strong>{{ item.timestamp }}</strong>
									<span>第 {{ item.frameIndex }} 帧</span>
								</div>
								<div class="frame-text">{{ item.summaryText || '未检测到病虫害' }}</div>
							</div>
						</div>
						<div v-else class="empty-text">当前记录暂无逐帧识别结果。</div>
					</div>
				</section>
			</section>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import request from '/@/utils/request';
import { useRoute } from 'vue-router';
import { resolveFileUrl } from '/@/utils/serviceUrl';

type FrameResult = {
	frameIndex?: number;
	timestamp?: string;
	timestampSeconds?: number;
	detectionCount?: number;
	summaryText?: string;
	topLabels?: Array<{ label: string; confidence: number }>;
};

const route = useRoute();
const inputVideoRef = ref<HTMLVideoElement | null>(null);
const resultVideoRef = ref<HTMLVideoElement | null>(null);

const state = reactive({
	form: {} as any,
	id: '',
	frameResults: [] as FrameResult[],
});

const currentFrame = ref<FrameResult>({});
const isCameraMode = computed(() => route.query.mode === 'camera' || route.name === 'cameraShow');
const isSuccessCode = (code: string | number) => String(code) === '0';

const resolveMediaUrl = (url?: string) => resolveFileUrl(url);

const parseFrameResults = (frameResults: string | FrameResult[]) => {
	if (!frameResults) return [];
	if (Array.isArray(frameResults)) return frameResults;
	try {
		const parsed = JSON.parse(frameResults);
		return Array.isArray(parsed) ? parsed : [];
	} catch (error) {
		console.error('解析逐帧结果失败', error);
		return [];
	}
};

const formatPercent = (confidence?: number) => `${((confidence || 0) * 100).toFixed(1)}%`;

const syncCurrentFrame = (videoRef: HTMLVideoElement | null) => {
	if (!videoRef || !state.frameResults.length) return;
	const currentTime = videoRef.currentTime;
	let bestMatch = state.frameResults[0];
	let minDiff = Infinity;

	state.frameResults.forEach((item) => {
		const diff = Math.abs((item.timestampSeconds || 0) - currentTime);
		if (diff < minDiff) {
			minDiff = diff;
			bestMatch = item;
		}
	});

	currentFrame.value = bestMatch;
};

const getData = () => {
	const api = isCameraMode.value ? '/api/cameraRecords/' : '/api/videoRecords/';
	request
		.get(api + state.id)
		.then((res) => {
			if (!isSuccessCode(res.code)) {
				ElMessage.error(res.msg);
				return;
			}
			const form = { ...res.data };
			form.inputVideo = resolveMediaUrl(form.inputVideo);
			form.outVideo = resolveMediaUrl(form.outVideo);
			state.form = form;
			state.frameResults = parseFrameResults(form.frameResults);
			currentFrame.value = state.frameResults[0] || {};
		})
		.catch(() => {
			ElMessage.error('加载记录详情失败');
		});
};

const playVideos = () => {
	if (inputVideoRef.value) inputVideoRef.value.play();
	if (resultVideoRef.value) resultVideoRef.value.play();
};

const pauseVideos = () => {
	if (inputVideoRef.value) inputVideoRef.value.pause();
	if (resultVideoRef.value) resultVideoRef.value.pause();
};

onMounted(() => {
	state.id = String(route.query.id || '');
	getData();
});
</script>

<style scoped lang="scss">
.compare-page {
	position: relative;
	left: auto;
	top: auto;
	height: auto;
	min-height: 100%;
	overflow: visible;

	.compare-panel {
		padding: 18px;
		height: auto;
		min-height: 100%;
		overflow: visible;
		background: rgba(255, 255, 255, 0.88);
	}
}

.compare-hero {
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

.compare-hero h2 {
	margin: 14px 0 8px;
	font-size: 28px;
}

.compare-hero p {
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
.video-card,
.timeline-card {
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

.meta-item {
	padding: 16px 18px;
	border-radius: 18px;
	background: #f5f8f6;
}

.meta-item span {
	display: block;
	color: #738294;
	font-size: 13px;
}

.meta-item strong {
	display: block;
	margin-top: 10px;
	color: #23394b;
	font-size: 18px;
	word-break: break-word;
}

.action-row {
	display: flex;
	flex-wrap: wrap;
	gap: 10px;
	margin-top: 16px;
}

.play-button,
.pause-button {
	height: 46px;
	border: none;
	border-radius: 16px;
}

.play-button {
	background: linear-gradient(135deg, #1f6f58 0%, #2f8b70 55%, #2c79a5 100%);
	box-shadow: 0 18px 32px rgba(39, 103, 91, 0.2);
}

.pause-button {
	color: #355363;
	background: rgba(116, 144, 159, 0.12);
	box-shadow: inset 0 0 0 1px rgba(116, 144, 159, 0.16);
}

.content-grid {
	display: grid;
	grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.85fr);
	gap: 16px;
	margin-top: 16px;
}

.video-card,
.timeline-card {
	padding: 18px;
}

.stage-header h3,
.timeline-title,
.current-title {
	margin: 0 0 6px;
	color: #24384d;
}

.stage-header p {
	margin: 0 0 16px;
	color: #7d8a98;
}

.double-stage {
	display: grid;
	grid-template-columns: repeat(2, minmax(0, 1fr));
	gap: 16px;
}

.single-stage {
	display: flex;
}

.stage-pane,
.single-stage {
	padding: 18px;
	border-radius: 20px;
	background: #f4f8f6;
}

.pane-label {
	margin-bottom: 12px;
	font-size: 13px;
	color: #66788b;
}

.video {
	width: 100%;
	max-height: 420px;
	border-radius: 18px;
	object-fit: contain;
	background: #0f1720;
	box-shadow: 0 20px 36px rgba(15, 23, 32, 0.14);
}

.empty-pane,
.empty-text {
	color: #7c8a97;
}

.timeline-card {
	display: grid;
	gap: 16px;
}

.timeline-current {
	padding: 16px;
	border-radius: 18px;
	background: #f5f8f6;
}

.current-time {
	font-size: 26px;
	font-weight: 700;
	color: #1d6b59;
}

.current-meta {
	display: flex;
	flex-wrap: wrap;
	gap: 12px;
	margin-top: 8px;
	color: #64778b;
	font-size: 13px;
}

.tag-list {
	display: grid;
	gap: 10px;
	margin-top: 14px;
}

.result-tag {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 10px;
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

.frame-list {
	max-height: 620px;
	overflow-y: auto;
	display: grid;
	gap: 10px;
}

.frame-item {
	padding: 12px;
	border-radius: 14px;
	background: #f6faf7;
	border: 1px solid transparent;
}

.frame-item.active {
	border-color: rgba(31, 111, 88, 0.35);
	background: #edf7f2;
}

.frame-meta {
	display: flex;
	justify-content: space-between;
	gap: 12px;
	color: #64778b;
	font-size: 13px;
}

.frame-meta strong {
	color: #23465f;
}

.frame-text {
	margin-top: 8px;
	line-height: 1.6;
	color: #41576b;
	word-break: break-word;
}

@media (max-width: 1200px) {
	.content-grid {
		grid-template-columns: 1fr;
	}
}

@media (max-width: 992px) {
	.compare-hero {
		flex-direction: column;
	}

	.meta-grid,
	.double-stage {
		grid-template-columns: 1fr;
	}
}
</style>

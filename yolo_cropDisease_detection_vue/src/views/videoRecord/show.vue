<template>
	<div class="compare-page layout-padding">
		<div class="compare-panel layout-padding-auto layout-padding-view">
			<section class="compare-hero">
				<div>
					<span class="hero-badge">视频详情对比</span>
					<h2>同屏查看原始视频与识别结果</h2>
					<p>保留原有详情查询、播放控制与拖拽分栏功能，只提升信息展示层次和整体观感。</p>
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

			<section class="compare-card">
				<div class="stage-header">
					<div>
						<h3>双画面对比</h3>
						<p>拖动中间分隔条，可自由调整左右预览比例。</p>
					</div>
					<div class="view-labels">
						<span>原始视频</span>
						<span>识别结果</span>
					</div>
				</div>

				<div class="cards" ref="cardsContainer">
					<div class="left stage-pane" :style="{ width: leftWidth + '%' }">
						<video class="video" v-if="state.form.inputVideo" preload="auto" controls>
							<source :src="state.form.inputVideo" type="video/mp4" />
						</video>
						<div v-else class="empty-pane">暂无原始视频</div>
					</div>

					<div class="splitter" @mousedown="startDrag"></div>

					<div class="right stage-pane" :style="{ width: 100 - leftWidth + '%' }">
						<video class="video" v-if="state.form.outVideo" preload="auto" controls>
							<source :src="state.form.outVideo" type="video/mp4" />
						</video>
						<div v-else class="empty-pane">暂无处理结果</div>
					</div>
				</div>
			</section>
		</div>
	</div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import request from '/@/utils/request';
import { useRoute } from 'vue-router';

const route = useRoute();
const leftWidth = ref(50);
const state = reactive({
	form: {} as any,
	id: '' as any,
});

const getData = () => {
	request.get('/api/videoRecords/' + state.id).then((res) => {
		if (res.code == 0) {
			state.form = res.data;
		} else {
			ElMessage.error(res.msg);
		}
	});
};

const playVideos = () => {
	const leftVideo = document.querySelector('.left .video') as HTMLVideoElement;
	const rightVideo = document.querySelector('.right .video') as HTMLVideoElement;

	if (leftVideo) leftVideo.play();
	if (rightVideo) rightVideo.play();
};

const pauseVideos = () => {
	const leftVideo = document.querySelector('.left .video') as HTMLVideoElement;
	const rightVideo = document.querySelector('.right .video') as HTMLVideoElement;

	if (leftVideo) leftVideo.pause();
	if (rightVideo) rightVideo.pause();
};

const startDrag = (e: MouseEvent) => {
	const cardsContainer = document.querySelector('.cards') as HTMLElement;
	const startX = e.clientX;
	const startLeftWidth = leftWidth.value;
	const cardsContainerWidth = cardsContainer.offsetWidth;

	const onMouseMove = (moveEvent: MouseEvent) => {
		const deltaX = moveEvent.clientX - startX;
		let newLeftWidth = startLeftWidth + (deltaX / cardsContainerWidth) * 100;
		newLeftWidth = Math.min(Math.max(newLeftWidth, 0), 100);
		leftWidth.value = newLeftWidth;
	};

	const onMouseUp = () => {
		document.removeEventListener('mousemove', onMouseMove);
		document.removeEventListener('mouseup', onMouseUp);
	};

	document.addEventListener('mousemove', onMouseMove);
	document.addEventListener('mouseup', onMouseUp);
};

onMounted(() => {
	state.id = route.query.id;
	getData();
});
</script>

<style scoped lang="scss">
.compare-page {
	.compare-panel {
		padding: 18px;
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
.compare-card {
	margin-top: 16px;
	padding: 18px;
	border-radius: 22px;
	background: linear-gradient(180deg, #ffffff 0%, #f7faf8 100%);
	box-shadow: 0 18px 34px rgba(31, 52, 84, 0.06);
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

.stage-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: 16px;
	margin-bottom: 18px;
}

.stage-header h3 {
	margin: 0 0 6px;
	color: #24384d;
}

.stage-header p {
	margin: 0;
	color: #7d8a98;
}

.view-labels {
	display: flex;
	gap: 12px;
}

.view-labels span {
	padding: 8px 14px;
	border-radius: 999px;
	background: #f3f7f5;
	color: #516273;
	font-size: 13px;
}

.cards {
	display: flex;
	min-height: 560px;
	border-radius: 22px;
	overflow: hidden;
	background: #eef4f1;
}

.stage-pane {
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 16px;
	background: radial-gradient(circle at top, #f7fbf9 0%, #edf4f1 100%);
}

.video {
	width: 100%;
	max-height: 100%;
	border-radius: 18px;
	object-fit: contain;
	background: #0f1720;
	box-shadow: 0 20px 36px rgba(15, 23, 32, 0.14);
}

.empty-pane {
	color: #7c8a97;
}

.splitter {
	width: 6px;
	cursor: ew-resize;
	background: linear-gradient(180deg, #c8d7e1 0%, #7ca2b7 50%, #c8d7e1 100%);
	box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.3);
}

@media (max-width: 1100px) {
	.compare-hero,
	.stage-header {
		flex-direction: column;
		align-items: flex-start;
	}

	.meta-grid {
		grid-template-columns: repeat(2, minmax(0, 1fr));
	}
}

@media (max-width: 768px) {
	.meta-grid {
		grid-template-columns: 1fr;
	}

	.cards {
		flex-direction: column;
		min-height: auto;
	}

	.splitter {
		width: 100%;
		height: 6px;
		cursor: ns-resize;
	}
}
</style>

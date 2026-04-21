<template>
	<div class="predict-page layout-padding">
		<div class="predict-panel layout-padding-auto layout-padding-view">
			<section class="predict-hero">
				<div>
					<span class="hero-badge">实时摄像检测</span>
					<h2>连接摄像头后实时查看病害识别画面</h2>
					<p>保留原有摄像头推流、模型选择、置信度设置与录制保存流程，只优化视觉呈现与操作节奏。</p>
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
						<el-button type="primary" class="predict-button" @click="start">开始录制</el-button>
						<el-button type="info" plain class="secondary-button" @click="stop">结束录制</el-button>
					</div>
				</div>
				<div v-if="state.isShow" class="progress-wrap">
					<el-progress :text-inside="true" :stroke-width="20" :percentage="state.percentage">
						<span>{{ state.type_text }} {{ state.percentage }}%</span>
					</el-progress>
				</div>
			</section>

			<section class="video-card">
				<div class="video-head">
					<h3>摄像头识别画面</h3>
					<p>开始录制后，下方将实时显示检测流。</p>
				</div>
				<div class="video-stage">
					<img v-if="state.cameraisShow" class="video-stream" :src="state.video_path" />
					<div v-else class="video-empty">
						<span>选择作物和模型后开始录制，检测结果会显示在这里。</span>
					</div>
				</div>
			</section>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import request from '/@/utils/request';
import { useUserInfo } from '/@/stores/userInfo';
import { storeToRefs } from 'pinia';
import { SocketService } from '/@/utils/socket';
import { formatDate } from '/@/utils/formatTime';

const stores = useUserInfo();
const conf = ref('0');
const kind = ref('');
const weight = ref('');
const { userInfos } = storeToRefs(stores);

const state = reactive({
	weight_items: [] as any,
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
	data: {} as any,
	video_path: '',
	type_text: '正在保存',
	percentage: 50,
	isShow: false,
	cameraisShow: false,
	form: {
		username: '',
		weight: '',
		conf: null as any,
		kind: '',
		startTime: '',
	},
});

const selectedKindLabel = computed(() => {
	return state.kind_items.find((item) => item.value === kind.value)?.label || '未选择';
});

const socketService = new SocketService();

socketService.on('message', (data) => {
	ElMessage.success(data);
});

const formatTooltip = (val: number) => {
	return val / 100;
};

socketService.on('progress', (data) => {
	state.percentage = parseInt(data);
	if (parseInt(data) < 100) {
		state.isShow = true;
	} else {
		ElMessage.success('保存成功');
		setTimeout(() => {
			state.isShow = false;
			state.percentage = 0;
		}, 2000);
	}
});

const getData = () => {
	request.get('/api/flask/file_names').then((res) => {
		if (res.code == 0) {
			res.data = JSON.parse(res.data);
			state.weight_items = res.data.weight_items.filter((item) => item.value.includes(kind.value));
		} else {
			ElMessage.error(res.msg);
		}
	});
};

const start = () => {
	state.form.weight = weight.value;
	state.form.kind = kind.value;
	state.form.conf = parseFloat(conf.value) / 100;
	state.form.username = userInfos.value.userName;
	state.form.startTime = formatDate(new Date(), 'YYYY-mm-dd HH:MM:SS');
	const queryParams = new URLSearchParams(state.form).toString();
	state.cameraisShow = true;
	state.video_path = `http://127.0.0.1:5000/predictCamera?${queryParams}`;
};

const stop = () => {
	request.get('/flask/stopCamera').then((res) => {
		if (res.code == 0) {
			res.data = JSON.parse(res.data);
			state.weight_items = res.data.weight_items;
		} else {
			ElMessage.error(res.msg);
		}
	});
	state.cameraisShow = false;
};

onMounted(() => {
	getData();
});
</script>

<style scoped lang="scss">
.predict-page {
	.predict-panel {
		padding: 18px;
		background: rgba(255, 255, 255, 0.88);
	}
}

.predict-hero {
	display: flex;
	justify-content: space-between;
	gap: 16px;
	padding: 24px;
	border-radius: 24px;
	background: linear-gradient(135deg, #173843 0%, #1d6b59 52%, #2d7b9d 100%);
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
.video-card {
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

.video-head h3 {
	margin: 0 0 6px;
	color: #24384d;
}

.video-head p {
	margin: 0;
	color: #7d8a98;
}

.video-stage {
	margin-top: 18px;
	min-height: 520px;
	border-radius: 20px;
	background: #f4f8f6;
	display: flex;
	align-items: center;
	justify-content: center;
	overflow: hidden;
}

.video-stream {
	width: 100%;
	height: auto;
	object-fit: contain;
}

.video-empty {
	color: #8694a3;
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
	color: #355363;
	background: rgba(116, 144, 159, 0.12);
	box-shadow: inset 0 0 0 1px rgba(116, 144, 159, 0.16);
}

:deep(.el-select .el-input__wrapper),
:deep(.el-input__wrapper) {
	border-radius: 14px;
	background: #f5f8f6;
	box-shadow: inset 0 0 0 1px rgba(106, 128, 115, 0.12) !important;
}

@media (max-width: 992px) {
	.predict-hero,
	.control-grid {
		grid-template-columns: 1fr;
	}

	.predict-hero {
		flex-direction: column;
	}

	.action-row {
		justify-content: flex-start;
	}
}
</style>

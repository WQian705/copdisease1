<template>
	<div class="env-page layout-padding">
		<div class="env-panel layout-padding-auto layout-padding-view">
			<section class="env-hero">
				<div>
					<span class="hero-badge">环境详情</span>
					<h2>查看温室环境参数并获取智能调节建议</h2>
					<p>保留原有温室切换、设备开关状态和 AI 建议请求逻辑，只优化信息分组与展示体验。</p>
				</div>
				<div class="hero-side">
					<span>当前温室</span>
					<strong>{{ selectedGreenhouse }}</strong>
				</div>
			</section>

			<section class="content-grid">
				<div class="metrics-card">
					<div class="section-head">
						<div>
							<h3>环境监测</h3>
							<p>选择温室后查看当前核心环境指标。</p>
						</div>
						<el-select v-model="selectedGreenhouse" placeholder="请选择温室" class="greenhouse-select">
							<el-option v-for="(greenhouse, index) in greenhouses" :key="index" :label="greenhouse" :value="greenhouse" />
						</el-select>
					</div>

					<div class="metric-grid">
						<div v-for="(item, index) in firstRow" :key="'a' + index" class="metric-item">
							<i :class="`iconfontjs ${item.icon}`" class="metric-icon"></i>
							<div class="metric-label">{{ item.label }}</div>
							<div class="metric-value">{{ item.value }}</div>
						</div>
						<div v-for="(item, index) in secondRow" :key="'b' + index" class="metric-item">
							<i :class="`iconfontjs ${item.icon}`" class="metric-icon"></i>
							<div class="metric-label">{{ item.label }}</div>
							<div class="metric-value">{{ item.value }}</div>
						</div>
					</div>

					<div class="device-head">
						<h4>设备状态</h4>
						<p>当前控制设备可手动切换显示状态。</p>
					</div>
					<div class="device-grid">
						<div v-for="(item, index) in thirdRow" :key="'c' + index" class="device-item">
							<div class="device-meta">
								<i :class="`iconfontjs ${item.icon}`" :style="{ color: item.status ? '#2c79a5' : '#90a0ad' }" class="metric-icon"></i>
								<div>
									<div class="metric-label">{{ item.label }}</div>
									<div class="device-state">{{ item.status ? '已开启' : '已关闭' }}</div>
								</div>
							</div>
							<el-switch v-model="item.status" active-color="#2c79a5" inactive-color="#c7d1d8"></el-switch>
						</div>
					</div>
				</div>

				<div class="suggestion-card">
					<div class="section-head column">
						<div>
							<h3>智能建议</h3>
							<p>结合当前环境参数，快速获取种植调整方向。</p>
						</div>
						<el-button type="primary" class="suggest-button" @click="getSuggestions" :loading="loading">获取建议</el-button>
					</div>

					<div v-if="suggestions.length" class="suggestion-list">
						<p v-for="(suggestion, index) in suggestions" :key="index">{{ suggestion }}</p>
					</div>
					<div v-else class="suggestion-empty">
						<span>点击“获取建议”后，系统将在这里生成当前温室的环境调节建议。</span>
					</div>
				</div>
			</section>
		</div>
	</div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

const greenhouses = ref(['1号温室', '2号温室', '3号温室', '4号温室', '5号温室', '6号温室', '7号温室', '8号温室', '9号温室']);
const selectedGreenhouse = ref(greenhouses.value[0]);

const firstRow = ref([
	{ icon: 'icon-daqiwendu', label: '室内温度', value: '25.5°C' },
	{ icon: 'icon-kongqishidu_kongqishidu', label: '空气湿度', value: '62.3%' },
	{ icon: 'icon-turangshidu', label: '土壤湿度', value: '64.7%' },
]);

const secondRow = ref([
	{ icon: 'icon-eryanghuatan', label: '二氧化碳', value: '434ppm' },
	{ icon: 'icon-turangPH', label: 'pH值', value: '6.5' },
	{ icon: 'icon-guangzhaoqiangdu', label: '光照强度', value: '893lux' },
]);

const thirdRow = ref([
	{ icon: 'icon-shuibeng', label: '水泵', status: false },
	{ icon: 'icon-a-buguangdengzidong', label: '补光灯', status: true },
	{ icon: 'icon-fengshan', label: '风扇', status: false },
]);

const suggestions = ref([]);
const loading = ref(false);
const apiKey = 'sk-3rG1hl3sdDbbRoqEHr7utZpcbqbufy1miSD9XhLvVxJGAb4W';

async function getSuggestions() {
	loading.value = true;
	try {
		const cropInfo = selectedGreenhouse.value === '1号温室' ? '当前种植作物是玉米。' : '当前种植作物信息未提供。';
		const response = await axios.post(
			'https://api.chatanywhere.tech/v1/chat/completions',
			{
				model: 'gpt-3.5-turbo',
				messages: [
					{
						role: 'system',
						content: '根据以下环境数据和种植作物提供当前环境的调节建议，如果暂时不需要调整，也请说明原因。',
					},
					{ role: 'user', content: cropInfo },
					...firstRow.value.map((item) => ({ role: 'user', content: `${item.label}: ${item.value}` })),
					...secondRow.value.map((item) => ({ role: 'user', content: `${item.label}: ${item.value}` })),
				],
				temperature: 0.7,
			},
			{
				headers: {
					Authorization: `Bearer ${apiKey}`,
					'Content-Type': 'application/json',
				},
			}
		);

		suggestions.value = response.data.choices[0].message.content.split('\n');
	} catch (error) {
		console.error('Error:', error);
	} finally {
		loading.value = false;
	}
}
</script>

<style scoped lang="scss">
.env-page {
	.env-panel {
		padding: 18px;
		background: rgba(255, 255, 255, 0.88);
	}
}

.env-hero {
	display: flex;
	justify-content: space-between;
	gap: 16px;
	padding: 24px;
	border-radius: 24px;
	background: linear-gradient(135deg, #173843 0%, #1f6859 54%, #2d7996 100%);
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

.env-hero h2 {
	margin: 14px 0 8px;
	font-size: 28px;
}

.env-hero p {
	margin: 0;
	line-height: 1.8;
	color: rgba(255, 255, 255, 0.82);
}

.hero-side {
	min-width: 160px;
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

.content-grid {
	margin-top: 16px;
	display: grid;
	grid-template-columns: 1.2fr 0.8fr;
	gap: 16px;
}

.metrics-card,
.suggestion-card {
	padding: 18px;
	border-radius: 22px;
	background: linear-gradient(180deg, #ffffff 0%, #f7faf8 100%);
	box-shadow: 0 18px 34px rgba(31, 52, 84, 0.06);
}

.section-head {
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: 12px;
}

.section-head.column {
	flex-direction: column;
	align-items: flex-start;
}

.section-head h3,
.device-head h4 {
	margin: 0 0 6px;
	color: #24384d;
}

.section-head p,
.device-head p {
	margin: 0;
	color: #7d8a98;
}

.greenhouse-select {
	width: 180px;
}

.metric-grid,
.device-grid {
	margin-top: 18px;
	display: grid;
	grid-template-columns: repeat(3, minmax(0, 1fr));
	gap: 14px;
}

.metric-item,
.device-item {
	padding: 18px 16px;
	border-radius: 20px;
	background: #f5f8f6;
	box-shadow: inset 0 0 0 1px rgba(106, 128, 115, 0.08);
}

.metric-icon {
	font-size: 34px;
	color: #2c79a5;
}

.metric-label {
	margin-top: 12px;
	font-size: 14px;
	color: #607286;
}

.metric-value {
	margin-top: 8px;
	font-size: 22px;
	font-weight: 700;
	color: #22384a;
}

.device-head {
	margin-top: 26px;
}

.device-item {
	display: flex;
	align-items: center;
	justify-content: space-between;
}

.device-meta {
	display: flex;
	align-items: center;
	gap: 12px;
}

.device-state {
	margin-top: 6px;
	font-size: 13px;
	color: #90a0ad;
}

.suggest-button {
	height: 46px;
	border: none;
	border-radius: 16px;
	background: linear-gradient(135deg, #1f6f58 0%, #2f8b70 55%, #2c79a5 100%);
	box-shadow: 0 18px 32px rgba(39, 103, 91, 0.2);
}

.suggestion-list {
	margin-top: 18px;
	padding: 18px;
	border-radius: 20px;
	background: #f5f8f6;
	line-height: 1.8;
	color: #334658;
}

.suggestion-list p {
	margin: 0 0 10px;
}

.suggestion-list p:last-child {
	margin-bottom: 0;
}

.suggestion-empty {
	margin-top: 18px;
	min-height: 320px;
	padding: 24px;
	border-radius: 20px;
	display: flex;
	align-items: center;
	justify-content: center;
	background: linear-gradient(180deg, #f7faf8 0%, #eef4f1 100%);
	color: #8695a3;
	text-align: center;
}

:deep(.el-select .el-input__wrapper) {
	border-radius: 14px;
	background: #f5f8f6;
	box-shadow: inset 0 0 0 1px rgba(106, 128, 115, 0.12) !important;
}

@media (max-width: 1100px) {
	.env-hero,
	.content-grid {
		grid-template-columns: 1fr;
	}

	.env-hero {
		flex-direction: column;
	}

	.metric-grid,
	.device-grid {
		grid-template-columns: 1fr;
	}

	.section-head {
		flex-direction: column;
		align-items: flex-start;
	}
}
</style>

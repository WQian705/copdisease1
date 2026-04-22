<template>
	<div class="datav-page layout-padding">
		<div class="datav-panel layout-padding-auto layout-padding-view">
			<section class="datav-hero">
				<div>
					<span class="hero-badge">数据大屏</span>
					<h2>从系统页内快速进入可视化总览</h2>
					<p>保留原有大屏地址与 iframe 加载方式，只补一层更完整的承载布局，让入口观感更统一。</p>
				</div>
				<div class="hero-side">
					<span>展示模式</span>
					<strong>全景总览</strong>
				</div>
			</section>

			<section class="screen-card">
				<div class="screen-head">
					<h3>数据驾驶舱</h3>
					<p>下方直接嵌入原有数据大屏页面。</p>
				</div>
				<div class="screen-frame">
					<iframe id="fream" src="/data/index.html" scrolling="auto" frameborder="0"></iframe>
				</div>
			</section>
		</div>
	</div>
</template>

<script>
export default {
	data() {
		return {};
	},
	methods: {},
	created() {},
};
</script>

<style scoped lang="scss">
.datav-page {
	width: 100%;
	position: relative;
	height: auto !important;
	min-height: 100%;
	overflow: visible;
}

.datav-panel {
	padding: 18px;
	background: rgba(255, 255, 255, 0.88);
	height: auto !important;
	min-height: 100%;
	overflow: visible;
}

.datav-hero {
	display: flex;
	justify-content: space-between;
	gap: 16px;
	padding: 24px;
	border-radius: 24px;
	background: linear-gradient(135deg, #132c43 0%, #1f5f63 52%, #347694 100%);
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

.datav-hero h2 {
	margin: 14px 0 8px;
	font-size: 28px;
}

.datav-hero p {
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

.screen-card {
	margin-top: 16px;
	padding: 18px;
	border-radius: 22px;
	background: linear-gradient(180deg, #ffffff 0%, #f7faf8 100%);
	box-shadow: 0 18px 34px rgba(31, 52, 84, 0.06);
}

.screen-head h3 {
	margin: 0 0 6px;
	color: #24384d;
}

.screen-head p {
	margin: 0 0 18px;
	color: #7d8a98;
}

.screen-frame {
	overflow: hidden;
	border-radius: 22px;
	background: #0f1720;
	box-shadow: 0 22px 40px rgba(15, 23, 32, 0.18);
}

.screen-frame iframe {
	width: 100%;
	height: 980px;
	min-height: 980px;
	border: 0;
	display: block;
}

@media (max-width: 992px) {
	.datav-hero {
		flex-direction: column;
	}

	.screen-frame iframe {
		height: 760px;
		min-height: 760px;
	}
}
</style>

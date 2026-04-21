<template>
	<div class="error-page layout-padding">
		<div class="layout-padding-auto layout-padding-view">
			<div class="error-shell">
				<section class="error-copy">
					<span class="error-tag">404</span>
					<h1>{{ $t('message.notFound.foundTitle') }}</h1>
					<p>{{ $t('message.notFound.foundMsg') }}</p>
					<div class="error-actions">
						<el-button type="primary" class="action-button" @click="onGoHome">{{ $t('message.notFound.foundBtn') }}</el-button>
					</div>
				</section>
				<section class="error-visual">
					<div class="orb orb-one"></div>
					<div class="orb orb-two"></div>
					<div class="visual-card">
						<div class="visual-code">404</div>
						<div class="visual-text">Missing</div>
					</div>
				</section>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts" name="notFound">
import { useRouter } from 'vue-router';

const router = useRouter();

const onGoHome = () => {
	router.push('/');
};
</script>

<style scoped lang="scss">
.error-page {
	height: 100%;
	display: flex;
	align-items: center;
}

.error-shell {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 22px;
	min-height: 420px;
	padding: 28px;
	border-radius: 30px;
	background: linear-gradient(180deg, #ffffff 0%, #f7faf8 100%);
	box-shadow: 0 24px 56px rgba(27, 45, 72, 0.08);
}

.error-copy,
.error-visual {
	border-radius: 26px;
}

.error-copy {
	padding: 34px;
	display: flex;
	flex-direction: column;
	justify-content: center;
	background: linear-gradient(135deg, #163443 0%, #245b58 54%, #337895 100%);
	color: #fff;
}

.error-tag {
	display: inline-flex;
	width: fit-content;
	padding: 6px 12px;
	border-radius: 999px;
	background: rgba(255, 255, 255, 0.12);
	font-size: 12px;
	letter-spacing: 0.16em;
}

.error-copy h1 {
	margin: 20px 0 10px;
	font-size: 38px;
}

.error-copy p {
	margin: 0;
	line-height: 1.8;
	color: rgba(255, 255, 255, 0.8);
}

.error-actions {
	margin-top: 28px;
}

.action-button {
	height: 48px;
	border: none;
	border-radius: 16px;
	background: linear-gradient(135deg, #1f6f58 0%, #2f8b70 55%, #2c79a5 100%);
	box-shadow: 0 18px 32px rgba(39, 103, 91, 0.2);
}

.error-visual {
	position: relative;
	overflow: hidden;
	display: flex;
	align-items: center;
	justify-content: center;
	background: radial-gradient(circle at top, #eef5f2 0%, #dfeae5 100%);
}

.orb {
	position: absolute;
	border-radius: 50%;
	filter: blur(10px);
}

.orb-one {
	width: 160px;
	height: 160px;
	top: 28px;
	right: 36px;
	background: rgba(52, 123, 143, 0.22);
}

.orb-two {
	width: 220px;
	height: 220px;
	left: 24px;
	bottom: 22px;
	background: rgba(44, 121, 165, 0.12);
}

.visual-card {
	position: relative;
	z-index: 1;
	width: 240px;
	height: 240px;
	border-radius: 40px;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	background: rgba(255, 255, 255, 0.82);
	box-shadow: 0 24px 50px rgba(31, 52, 84, 0.12);
}

.visual-code {
	font-size: 78px;
	font-weight: 800;
	color: #28495e;
	line-height: 1;
}

.visual-text {
	margin-top: 12px;
	font-size: 18px;
	letter-spacing: 0.24em;
	color: #688092;
	text-transform: uppercase;
}

@media (max-width: 992px) {
	.error-shell {
		grid-template-columns: 1fr;
	}
}
</style>

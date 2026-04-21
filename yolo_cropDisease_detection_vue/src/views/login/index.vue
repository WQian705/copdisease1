<template>
	<div class="login-container">
		<div class="login-backdrop">
			<span class="backdrop-orb orb-one"></span>
			<span class="backdrop-orb orb-two"></span>
			<span class="backdrop-grid"></span>
		</div>

		<div class="login-shell animate__animated animate__fadeIn">
			<section class="login-intro">
				<span class="login-badge">YOLO + AI 智慧农业平台</span>
				<h1>作物病害检测与环境监测一体化平台</h1>
				<p>
					集中管理图片检测、视频检测、病害数据与温室信息，保持业务流程不变，只让进入体验更清晰顺手。
				</p>
				<div class="intro-cards">
					<div class="intro-card">
						<strong>图片 / 视频</strong>
						<span>快速进入病害识别模块</span>
					</div>
					<div class="intro-card">
						<strong>病害 / 温室</strong>
						<span>统一查看数据与历史记录</span>
					</div>
				</div>
			</section>

			<section class="login-panel">
				<div class="panel-header">
					<h2>欢迎登录</h2>
					<p>请输入账号和密码进入系统</p>
				</div>

				<el-form :model="ruleForm" :rules="registerRules" ref="ruleFormRef" size="large">
					<el-form-item prop="username">
						<el-input v-model="ruleForm.username" placeholder="请输入用户名" prefix-icon="User" class="custom-input" />
					</el-form-item>

					<el-form-item prop="password">
						<el-input
							v-model="ruleForm.password"
							type="password"
							placeholder="请输入密码"
							prefix-icon="Lock"
							show-password
							class="custom-input"
						/>
					</el-form-item>

					<el-form-item>
						<el-button type="primary" class="login-btn" @click="submitForm(ruleFormRef)">登录系统</el-button>
					</el-form-item>
				</el-form>

				<div class="options">
					<router-link to="/register">注册账号</router-link>
					<span>|</span>
					<a href="javascript:void(0)">忘记密码</a>
				</div>
			</section>
		</div>
	</div>
</template>

<script lang="ts" setup>
import { reactive, computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useI18n } from 'vue-i18n';
import Cookies from 'js-cookie';
import { storeToRefs } from 'pinia';
import { useThemeConfig } from '/@/stores/themeConfig';
import { initFrontEndControlRoutes } from '/@/router/frontEnd';
import { initBackEndControlRoutes } from '/@/router/backEnd';
import { Session } from '/@/utils/storage';
import { formatAxis } from '/@/utils/formatTime';
import { NextLoading } from '/@/utils/loading';
import type { FormInstance, FormRules } from 'element-plus';
import request from '/@/utils/request';

const { t } = useI18n();
const storesThemeConfig = useThemeConfig();
const { themeConfig } = storeToRefs(storesThemeConfig);
const route = useRoute();
const router = useRouter();
const ruleFormRef = ref<FormInstance>();

const ruleForm = reactive({
	username: '',
	password: '',
});

const registerRules = reactive<FormRules>({
	username: [
		{ required: true, message: '请输入账号', trigger: 'blur' },
		{ min: 3, max: 20, message: '长度在 3-20 个字符', trigger: 'blur' },
	],
	password: [
		{ required: true, message: '请输入密码', trigger: 'blur' },
		{ min: 3, max: 20, message: '长度在 3-20 个字符', trigger: 'blur' },
	],
});

const currentTime = computed(() => {
	return formatAxis(new Date());
});

const onSignIn = async () => {
	Session.set('token', Math.random().toString(36).substr(0));
	Cookies.set('userName', ruleForm.username);
	if (!themeConfig.value.isRequestRoutes) {
		const isNoPower = await initFrontEndControlRoutes();
		signInSuccess(isNoPower);
	} else {
		const isNoPower = await initBackEndControlRoutes();
		signInSuccess(isNoPower);
	}
};

const signInSuccess = (isNoPower: boolean | undefined) => {
	if (isNoPower) {
		ElMessage.warning('抱歉，您没有登录权限');
		Session.clear();
	} else {
		const currentTimeInfo = currentTime.value;
		if (route.query?.redirect) {
			router.push({
				path: <string>route.query?.redirect,
				query: Object.keys(<string>route.query?.params).length > 0 ? JSON.parse(<string>route.query?.params) : '',
			});
		} else {
			router.push('/');
		}
		const signInText = t('message.signInText');
		ElMessage.success(`${currentTimeInfo}，${signInText}`);
		NextLoading.start();
	}
};

const submitForm = (formEl: FormInstance | undefined) => {
	if (!formEl) return;
	formEl.validate((valid) => {
		if (valid) {
			request.post('/api/user/login', ruleForm).then((res) => {
				if (res.code == 0) {
					Cookies.set('role', res.data.role);
					onSignIn();
				} else {
					ElMessage({
						type: 'error',
						message: res.msg,
					});
				}
			});
		} else {
			return false;
		}
	});
};
</script>

<style scoped lang="scss">
.login-container {
	position: relative;
	min-height: 100vh;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 28px;
	overflow: hidden;
	background:
		radial-gradient(circle at top left, rgba(61, 153, 113, 0.28), transparent 28%),
		radial-gradient(circle at bottom right, rgba(38, 111, 172, 0.24), transparent 26%),
		linear-gradient(135deg, #0f2f2a 0%, #18483e 40%, #1a4f72 100%);
}

.login-backdrop {
	position: absolute;
	inset: 0;
	overflow: hidden;
}

.backdrop-orb {
	position: absolute;
	border-radius: 50%;
	filter: blur(10px);
	opacity: 0.55;
}

.orb-one {
	top: 8%;
	left: 8%;
	width: 260px;
	height: 260px;
	background: radial-gradient(circle, rgba(255, 210, 120, 0.42) 0%, rgba(255, 210, 120, 0) 70%);
}

.orb-two {
	right: 6%;
	bottom: 10%;
	width: 360px;
	height: 360px;
	background: radial-gradient(circle, rgba(102, 217, 174, 0.34) 0%, rgba(102, 217, 174, 0) 72%);
}

.backdrop-grid {
	position: absolute;
	inset: 0;
	background-image:
		linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px),
		linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px);
	background-size: 34px 34px;
	mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.35), transparent 90%);
}

.login-shell {
	position: relative;
	z-index: 1;
	width: min(1120px, 100%);
	display: grid;
	grid-template-columns: minmax(0, 1.15fr) minmax(380px, 430px);
	border-radius: 30px;
	background: rgba(255, 255, 255, 0.08);
	border: 1px solid rgba(255, 255, 255, 0.12);
	box-shadow: 0 24px 80px rgba(5, 20, 21, 0.32);
	backdrop-filter: blur(18px);
	overflow: hidden;
}

.login-intro {
	padding: 54px 52px;
	color: #fff;
	background: linear-gradient(180deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.02));
}

.login-badge {
	display: inline-flex;
	padding: 8px 14px;
	border-radius: 999px;
	background: rgba(255, 255, 255, 0.12);
	font-size: 12px;
	letter-spacing: 0.12em;
}

.login-intro h1 {
	margin: 20px 0 18px;
	font-size: 38px;
	line-height: 1.22;
	letter-spacing: 0.02em;
}

.login-intro p {
	max-width: 540px;
	font-size: 15px;
	line-height: 1.9;
	color: rgba(255, 255, 255, 0.78);
}

.intro-cards {
	display: grid;
	grid-template-columns: repeat(2, minmax(0, 1fr));
	gap: 14px;
	margin-top: 34px;
}

.intro-card {
	padding: 18px;
	border-radius: 22px;
	background: rgba(255, 255, 255, 0.08);
	border: 1px solid rgba(255, 255, 255, 0.08);
}

.intro-card strong {
	display: block;
	font-size: 17px;
	margin-bottom: 8px;
}

.intro-card span {
	color: rgba(255, 255, 255, 0.72);
	line-height: 1.7;
	font-size: 13px;
}

.login-panel {
	padding: 42px 34px;
	background: rgba(248, 251, 248, 0.96);
	display: flex;
	flex-direction: column;
	justify-content: center;
}

.panel-header {
	margin-bottom: 26px;
}

.panel-header h2 {
	font-size: 28px;
	color: #1c3148;
	margin-bottom: 10px;
}

.panel-header p {
	color: #7b8795;
	line-height: 1.7;
}

:deep(.el-form-item) {
	margin-bottom: 22px;
}

:deep(.custom-input .el-input__wrapper) {
	border-radius: 18px;
	padding: 12px 16px;
	background: #f3f7f4;
	box-shadow: inset 0 0 0 1px rgba(72, 96, 83, 0.08);
	transition: box-shadow 0.25s ease, transform 0.25s ease, background 0.25s ease;
}

:deep(.custom-input .el-input__wrapper:hover) {
	background: #f8fbf8;
	box-shadow: inset 0 0 0 1px rgba(58, 122, 96, 0.18);
}

:deep(.custom-input .el-input__wrapper.is-focus) {
	background: #fff;
	box-shadow: 0 0 0 3px rgba(58, 139, 107, 0.14);
}

:deep(.custom-input .el-input__prefix-inner) {
	color: #4e6e62;
}

.login-btn {
	width: 100%;
	height: 52px;
	border: none;
	border-radius: 18px;
	font-size: 15px;
	font-weight: 700;
	letter-spacing: 0.08em;
	background: linear-gradient(135deg, #1d6a54 0%, #2f8d71 55%, #2e78a4 100%);
	box-shadow: 0 18px 32px rgba(36, 112, 86, 0.22);
	transition: transform 0.22s ease, box-shadow 0.22s ease, filter 0.22s ease;
}

.login-btn:hover {
	transform: translateY(-2px);
	filter: brightness(1.03);
	box-shadow: 0 20px 34px rgba(36, 112, 86, 0.28);
}

.login-btn:active {
	transform: translateY(0);
}

.options {
	margin-top: 6px;
	text-align: center;
	font-size: 14px;
}

.options a {
	color: #2b7a68;
	text-decoration: none;
	font-weight: 600;
}

.options span {
	margin: 0 12px;
	color: #c0c8cf;
}

.options a:hover {
	color: #1f5f95;
}

@media (max-width: 980px) {
	.login-shell {
		grid-template-columns: 1fr;
		max-width: 620px;
	}

	.login-intro {
		padding: 36px 30px 24px;
	}

	.login-intro h1 {
		font-size: 30px;
	}

	.login-panel {
		padding: 28px 24px 30px;
	}
}

@media (max-width: 640px) {
	.login-container {
		padding: 16px;
	}

	.login-shell {
		border-radius: 24px;
	}

	.login-intro {
		padding: 28px 20px 18px;
	}

	.login-panel {
		padding: 24px 18px 24px;
	}

	.login-intro h1 {
		font-size: 24px;
	}

	.intro-cards {
		grid-template-columns: 1fr;
	}
}
</style>

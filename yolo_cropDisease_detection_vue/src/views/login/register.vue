<template>
	<div class="register-page">
		<div class="register-backdrop"></div>
		<div class="register-grid">
			<section class="register-brand animate__animated animate__fadeInLeft">
				<span class="brand-tag">账号注册</span>
				<h1>创建你的智慧农业平台账号</h1>
				<p>保留原有注册接口与校验逻辑，只升级表单布局、视觉层次和登录注册切换体验。</p>
				<ul class="brand-points">
					<li>快速创建个人账号</li>
					<li>继续使用现有登录流程</li>
					<li>统一系统整体视觉风格</li>
				</ul>
			</section>

			<section class="register-card animate__animated animate__fadeInUp">
				<div class="card-head">
					<h2>注册新用户</h2>
					<p>填写基础账号信息后即可进入平台登录。</p>
				</div>

				<el-form ref="ruleFormRef" :model="ruleForm" :rules="registerRules" class="register-form">
					<el-form-item prop="username">
						<el-input v-model="ruleForm.username" placeholder="请输入用户名" prefix-icon="User" class="custom-input" />
					</el-form-item>

					<el-form-item prop="password">
						<el-input v-model="ruleForm.password" type="password" placeholder="请输入密码" prefix-icon="Lock" show-password class="custom-input" />
					</el-form-item>

					<el-form-item prop="confirm">
						<el-input v-model="ruleForm.confirm" type="password" placeholder="请确认密码" prefix-icon="Lock" show-password class="custom-input" />
					</el-form-item>

					<el-form-item>
						<el-button type="primary" class="register-btn" @click="submitForm(ruleFormRef)">注册账号</el-button>
					</el-form-item>
				</el-form>

				<div class="options">
					<router-link to="/login">已有账号？去登录</router-link>
				</div>
			</section>
		</div>
	</div>
</template>

<script lang="ts" setup>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import type { FormInstance, FormRules } from 'element-plus';
import request from '/@/utils/request';

const router = useRouter();
const ruleFormRef = ref<FormInstance>();

const ruleForm = reactive({
	username: '',
	password: '',
	confirm: '',
});

const registerRules = reactive<FormRules>({
	username: [
		{ required: true, message: '请输入账号', trigger: 'blur' },
		{ min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' },
	],
	password: [
		{ required: true, message: '请输入密码', trigger: 'blur' },
		{ min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' },
	],
	confirm: [
		{ required: true, message: '请确认密码', trigger: 'blur' },
		{
			validator: (rule, value, callback) => {
				if (value !== ruleForm.password) {
					callback(new Error('两次密码不一致'));
				} else {
					callback();
				}
			},
			trigger: 'blur',
		},
	],
});

const submitForm = (formEl: FormInstance | undefined) => {
	if (!formEl) return;
	formEl.validate((valid) => {
		if (valid) {
			request.post('/api/user/register', ruleForm).then((res) => {
				if (res.code == 0) {
					router.push('/login');
					ElMessage.success('注册成功');
				} else {
					ElMessage.error('用户名已存在');
				}
			});
		} else {
			return false;
		}
	});
};
</script>

<style scoped lang="scss">
.register-page {
	position: relative;
	min-height: 100vh;
	padding: 28px;
	display: flex;
	align-items: center;
	justify-content: center;
	overflow: hidden;
	background:
		radial-gradient(circle at 15% 20%, rgba(229, 173, 74, 0.22), transparent 36%),
		radial-gradient(circle at 80% 18%, rgba(58, 126, 160, 0.24), transparent 30%),
		linear-gradient(135deg, #153244 0%, #1e584f 45%, #285f83 100%);
}

.register-backdrop {
	position: absolute;
	inset: 0;
	background: url('/bg.png') center/cover no-repeat;
	opacity: 0.15;
	filter: saturate(0.8);
}

.register-grid {
	position: relative;
	z-index: 1;
	width: min(1120px, 100%);
	display: grid;
	grid-template-columns: 1.05fr 0.95fr;
	gap: 24px;
	align-items: stretch;
}

.register-brand,
.register-card {
	border-radius: 30px;
	backdrop-filter: blur(16px);
	box-shadow: 0 24px 60px rgba(13, 24, 35, 0.2);
}

.register-brand {
	padding: 42px 40px;
	background: rgba(15, 33, 47, 0.46);
	color: #fff;
	display: flex;
	flex-direction: column;
	justify-content: center;
}

.brand-tag {
	display: inline-flex;
	width: fit-content;
	padding: 7px 14px;
	border-radius: 999px;
	background: rgba(255, 255, 255, 0.12);
	font-size: 12px;
	letter-spacing: 0.14em;
}

.register-brand h1 {
	margin: 22px 0 14px;
	font-size: 42px;
	line-height: 1.18;
}

.register-brand p {
	margin: 0;
	font-size: 16px;
	line-height: 1.85;
	color: rgba(255, 255, 255, 0.78);
}

.brand-points {
	margin: 28px 0 0;
	padding: 0;
	list-style: none;
	display: grid;
	gap: 12px;
}

.brand-points li {
	padding: 14px 16px;
	border-radius: 18px;
	background: rgba(255, 255, 255, 0.08);
}

.register-card {
	padding: 38px 38px 30px;
	background: rgba(255, 255, 255, 0.94);
}

.card-head {
	margin-bottom: 26px;
	text-align: center;
}

.card-head h2 {
	margin: 0 0 8px;
	font-size: 30px;
	color: #22384a;
}

.card-head p {
	margin: 0;
	color: #718090;
}

.register-form {
	margin-top: 4px;
}

:deep(.custom-input .el-input__wrapper) {
	border-radius: 16px;
	padding: 14px 16px;
	background: #f5f8f6;
	box-shadow: inset 0 0 0 1px rgba(106, 128, 115, 0.12) !important;
}

:deep(.custom-input .el-input__wrapper.is-focus) {
	background: #fff;
	box-shadow: 0 0 0 1px rgba(44, 121, 165, 0.42) !important;
}

.register-btn {
	width: 100%;
	height: 50px;
	border: none;
	border-radius: 16px;
	font-size: 16px;
	font-weight: 600;
	background: linear-gradient(135deg, #1f6f58 0%, #2f8b70 55%, #2c79a5 100%);
	box-shadow: 0 18px 32px rgba(39, 103, 91, 0.2);
}

.options {
	margin-top: 20px;
	text-align: center;
}

.options a {
	color: #1f6f58;
	font-weight: 600;
	text-decoration: none;
}

.options a:hover {
	color: #2c79a5;
}

@media (max-width: 960px) {
	.register-grid {
		grid-template-columns: 1fr;
	}

	.register-brand h1 {
		font-size: 32px;
	}
}
</style>

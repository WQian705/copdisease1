<template>
	<div class="personal-container">
		<div class="profile-hero">
			<div>
				<span class="profile-badge">个人中心</span>
				<h1>维护账号资料与头像信息</h1>
				<p>仅优化页面展示与交互层，原有上传地址、查询和更新接口保持不变。</p>
			</div>
			<div class="hero-mini-card">
				<span>当前角色</span>
				<strong>{{ state.form.role || '未加载' }}</strong>
			</div>
		</div>

		<div class="personal-wrapper">
			<div class="content-wrapper">
				<div class="left-section">
					<div class="avatar-card">
						<div class="avatar-card__top">
							<span>头像设置</span>
							<strong>Profile</strong>
						</div>
						<div class="avatar-wrapper">
							<el-upload
								v-model="state.form.avatar"
								ref="uploadFile"
								class="avatar-uploader"
								action="http://localhost:9999/files/upload"
								:show-file-list="false"
								:on-success="handleAvatarSuccessone"
							>
								<div class="avatar-content">
									<img v-if="imageUrl" :src="imageUrl" class="avatar-image" />
									<div v-else class="avatar-placeholder">
										<el-icon class="upload-icon"><Plus /></el-icon>
										<span>点击上传头像</span>
									</div>
								</div>
							</el-upload>
						</div>
						<h3 class="welcome-text">欢迎回来</h3>
						<div class="user-role">{{ state.form.role }}</div>
						<p class="avatar-tip">建议使用清晰头像图片，上传后会自动更新到当前账号资料。</p>
					</div>
				</div>

				<div class="right-section">
					<div class="info-card">
						<div class="section-head">
							<div>
								<h2 class="section-title">个人信息</h2>
								<p>修改后将通过原有用户更新接口提交。</p>
							</div>
						</div>
						<el-form ref="formRef" :model="state.form" :rules="rules" label-width="92px" class="info-form">
							<div class="form-grid">
								<el-form-item label="账号" prop="username">
									<el-input v-model="state.form.username" placeholder="请输入账号">
										<template #prefix>
											<el-icon><User /></el-icon>
										</template>
									</el-input>
								</el-form-item>
								<el-form-item label="密码" prop="password">
									<el-input v-model="state.form.password" type="password" placeholder="请输入密码" show-password>
										<template #prefix>
											<el-icon><Lock /></el-icon>
										</template>
									</el-input>
								</el-form-item>
								<el-form-item label="姓名" prop="name">
									<el-input v-model="state.form.name" placeholder="请输入姓名">
										<template #prefix>
											<el-icon><UserFilled /></el-icon>
										</template>
									</el-input>
								</el-form-item>
								<el-form-item label="性别" prop="sex">
									<el-select v-model="state.form.sex" placeholder="请选择性别">
										<template #prefix>
											<el-icon><UserFilled /></el-icon>
										</template>
										<el-option label="男" value="男" />
										<el-option label="女" value="女" />
									</el-select>
								</el-form-item>
								<el-form-item label="邮箱" prop="email">
									<el-input v-model="state.form.email" placeholder="请输入邮箱">
										<template #prefix>
											<el-icon><Message /></el-icon>
										</template>
									</el-input>
								</el-form-item>
								<el-form-item label="手机号" prop="tel">
									<el-input v-model="state.form.tel" placeholder="请输入手机号">
										<template #prefix>
											<el-icon><Phone /></el-icon>
										</template>
									</el-input>
								</el-form-item>
							</div>
							<div class="form-footer">
								<el-button type="primary" @click="submitForm" :icon="Check" class="submit-button">确认修改</el-button>
							</div>
						</el-form>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts" name="personal">
import { reactive, ref, onMounted } from 'vue';
import type { UploadInstance, UploadProps, FormInstance } from 'element-plus';
import { ElMessage } from 'element-plus';
import request from '/@/utils/request';
import { useUserInfo } from '/@/stores/userInfo';
import { storeToRefs } from 'pinia';
import { Plus, Check, User, Lock, UserFilled, Message, Phone } from '@element-plus/icons-vue';

const imageUrl = ref('');
const uploadFile = ref<UploadInstance>();
const formRef = ref<FormInstance>();

const rules = {
	username: [
		{ required: true, message: '请输入账号', trigger: 'blur' },
		{ min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' },
	],
	password: [
		{ required: true, message: '请输入密码', trigger: 'blur' },
		{ min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' },
	],
	name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
	sex: [{ required: true, message: '请选择性别', trigger: 'change' }],
	email: [
		{ required: true, message: '请输入邮箱地址', trigger: 'blur' },
		{ type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' },
	],
	tel: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
};

const handleAvatarSuccessone: UploadProps['onSuccess'] = (response, uploadFile) => {
	imageUrl.value = URL.createObjectURL(uploadFile.raw!);
	state.form.avatar = response.data;
};

const state = reactive({
	form: {} as any,
});

const stores = useUserInfo();
const { userInfos } = storeToRefs(stores);

const getTableData = () => {
	request.get('/api/user/' + userInfos.value.userName).then((res) => {
		if (res.code == 0) {
			state.form = res.data;
			if (state.form['role'] == 'admin') {
				state.form['role'] = '管理员';
			} else if (state.form['role'] == 'common') {
				state.form['role'] = '普通用户';
			} else if (state.form['role'] == 'others') {
				state.form['role'] = '其他用户';
			}
			imageUrl.value = state.form.avatar;
		} else {
			ElMessage({
				type: 'error',
				message: res.msg,
			});
		}
	});
};

const submitForm = async () => {
	if (!formRef.value) return;

	await formRef.value.validate((valid) => {
		if (valid) {
			upData();
		} else {
			ElMessage.error('请完善必填信息');
			return false;
		}
	});
};

const upData = () => {
	if (state.form['role'] == '管理员') {
		state.form['role'] = 'admin';
	} else if (state.form['role'] == '普通用户') {
		state.form['role'] = 'common';
	} else if (state.form['role'] == '其他用户') {
		state.form['role'] = 'others';
	}
	request.post('/api/user/update', state.form).then((res) => {
		if (res.code == 0) {
			ElMessage.success('修改成功');
		} else {
			ElMessage({
				type: 'error',
				message: res.msg,
			});
		}
	});
	setTimeout(() => {
		getTableData();
	}, 200);
};

onMounted(() => {
	getTableData();
});
</script>

<style scoped lang="scss">
.personal-container {
	min-height: calc(100vh - 60px);
	padding: 24px;
	background:
		radial-gradient(circle at top left, rgba(68, 160, 108, 0.12), transparent 22%),
		linear-gradient(180deg, #edf5ef 0%, #f6faf8 100%);
}

.profile-hero {
	display: flex;
	align-items: stretch;
	justify-content: space-between;
	gap: 18px;
	padding: 28px 30px;
	margin-bottom: 20px;
	border-radius: 28px;
	background: linear-gradient(135deg, #153d33 0%, #216655 58%, #2a6f95 100%);
	box-shadow: 0 20px 46px rgba(21, 61, 51, 0.18);
	color: #fff;
}

.profile-badge {
	display: inline-flex;
	padding: 8px 14px;
	border-radius: 999px;
	background: rgba(255, 255, 255, 0.12);
	font-size: 12px;
	letter-spacing: 0.12em;
}

.profile-hero h1 {
	margin: 16px 0 10px;
	font-size: 30px;
}

.profile-hero p {
	max-width: 640px;
	color: rgba(255, 255, 255, 0.8);
	line-height: 1.8;
}

.hero-mini-card {
	min-width: 180px;
	padding: 20px;
	border-radius: 22px;
	background: rgba(255, 255, 255, 0.12);
	display: flex;
	flex-direction: column;
	justify-content: center;
}

.hero-mini-card span {
	color: rgba(255, 255, 255, 0.72);
	font-size: 13px;
}

.hero-mini-card strong {
	margin-top: 10px;
	font-size: 24px;
}

.content-wrapper {
	display: grid;
	grid-template-columns: 320px minmax(0, 1fr);
	gap: 20px;
}

.avatar-card,
.info-card {
	border-radius: 28px;
	background: rgba(255, 255, 255, 0.9);
	box-shadow: 0 18px 40px rgba(31, 52, 84, 0.08);
	border: 1px solid rgba(223, 232, 225, 0.95);
}

.avatar-card {
	padding: 28px 24px;
	text-align: center;
}

.avatar-card__top {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 22px;
	color: #789180;
}

.avatar-card__top strong {
	color: #1d354b;
	font-size: 18px;
}

.avatar-content {
	width: 190px;
	height: 190px;
	margin: 0 auto;
	border-radius: 50%;
	overflow: hidden;
	cursor: pointer;
	background: linear-gradient(135deg, #f1f8f3 0%, #eef5fb 100%);
	border: 4px solid rgba(255, 255, 255, 0.95);
	box-shadow: 0 14px 28px rgba(33, 74, 57, 0.12);
	transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.avatar-content:hover {
	transform: translateY(-3px);
	box-shadow: 0 18px 34px rgba(33, 74, 57, 0.16);
}

.avatar-image {
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.avatar-placeholder {
	height: 100%;
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;
	color: #6f8192;
}

.upload-icon {
	font-size: 40px;
	margin-bottom: 12px;
}

.welcome-text {
	margin: 24px 0 14px;
	font-size: 22px;
	color: #1e3349;
}

.user-role {
	display: inline-flex;
	padding: 8px 18px;
	border-radius: 999px;
	background: rgba(42, 123, 97, 0.12);
	color: #1c7857;
	font-weight: 600;
}

.avatar-tip {
	margin-top: 18px;
	color: #7f8b99;
	line-height: 1.8;
	font-size: 13px;
}

.info-card {
	padding: 30px;
}

.section-head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 28px;
}

.section-title {
	margin: 0 0 8px;
	font-size: 28px;
	color: #19324a;
}

.section-head p {
	color: #8390a0;
	line-height: 1.7;
}

.form-grid {
	display: grid;
	grid-template-columns: repeat(2, minmax(0, 1fr));
	gap: 24px 28px;
}

:deep(.el-form-item) {
	margin-bottom: 0;
}

:deep(.el-form-item__label) {
	font-weight: 600;
	color: #324557;
}

:deep(.el-input__wrapper),
:deep(.el-select .el-input__wrapper) {
	height: 46px;
	border-radius: 16px;
	background: #f5f8f6;
	box-shadow: inset 0 0 0 1px rgba(99, 122, 108, 0.1) !important;
	transition: box-shadow 0.25s ease, background 0.25s ease;
}

:deep(.el-input__wrapper:hover),
:deep(.el-select .el-input__wrapper:hover) {
	background: #fbfdfc;
	box-shadow: inset 0 0 0 1px rgba(42, 123, 97, 0.22) !important;
}

:deep(.el-input__wrapper.is-focus),
:deep(.el-select .el-input__wrapper.is-focus) {
	background: #fff;
	box-shadow: 0 0 0 3px rgba(42, 123, 97, 0.12) !important;
}

:deep(.el-input__prefix) {
	color: #688171;
}

.form-footer {
	margin-top: 34px;
	display: flex;
	justify-content: flex-end;
}

.submit-button {
	height: 48px;
	padding: 0 32px;
	border: none;
	border-radius: 16px;
	font-size: 15px;
	font-weight: 700;
	background: linear-gradient(135deg, #1f6e57 0%, #2f8b70 55%, #2b79a5 100%);
	box-shadow: 0 18px 32px rgba(39, 103, 91, 0.2);
}

.submit-button:hover {
	transform: translateY(-2px);
}

@media screen and (max-width: 992px) {
	.profile-hero,
	.content-wrapper {
		grid-template-columns: 1fr;
	}

	.profile-hero {
		flex-direction: column;
	}

	.hero-mini-card {
		min-width: 0;
	}

	.form-grid {
		grid-template-columns: 1fr;
	}
}

@media screen and (max-width: 768px) {
	.personal-container {
		padding: 16px;
	}

	.profile-hero,
	.avatar-card,
	.info-card {
		border-radius: 22px;
	}

	.profile-hero {
		padding: 22px 20px;
	}

	.profile-hero h1 {
		font-size: 24px;
	}

	.info-card {
		padding: 22px 18px;
	}
}
</style>

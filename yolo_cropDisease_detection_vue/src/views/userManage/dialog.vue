<template>
	<div class="user-dialog">
		<el-dialog :title="state.dialog.title" v-model="state.dialog.isShowDialog" width="820px" class="dialog-shell">
			<div class="dialog-banner">
				<div>
					<span class="banner-tag">用户资料</span>
					<h3>{{ state.dialog.title }}</h3>
					<p>填写账号信息、身份角色、联系方式和头像。</p>
				</div>
			</div>

			<div class="avatar-section">
				<el-upload
					v-model="state.form.avatar"
					ref="uploadFile"
					class="avatar-uploader"
					action="http://localhost:9999/files/upload"
					:show-file-list="false"
					:on-success="handleAvatarSuccessone"
				>
					<div class="avatar-frame">
						<img v-if="imageUrl" :src="imageUrl" class="avatar" />
						<div v-else class="avatar-empty">
							<el-icon><Plus /></el-icon>
							<span>上传头像</span>
						</div>
					</div>
				</el-upload>
			</div>

			<el-form ref="roleDialogFormRef" :model="state.form" size="default" label-width="88px" :rules="rules" class="dialog-form">
				<el-row :gutter="20">
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="账号" prop="username">
							<el-input v-model="state.form.username" placeholder="请输入账号" clearable />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="密码" prop="password">
							<el-input v-model="state.form.password" placeholder="请输入密码" clearable />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="姓名" prop="name">
							<el-input v-model="state.form.name" placeholder="请输入姓名" clearable />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="性别" prop="sex">
							<el-select v-model="state.form.sex" placeholder="请选择性别" style="width: 100%">
								<el-option label="男" value="男" />
								<el-option label="女" value="女" />
							</el-select>
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="邮箱" prop="email">
							<el-input v-model="state.form.email" placeholder="请输入邮箱" clearable />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="手机号" prop="tel">
							<el-input v-model="state.form.tel" placeholder="请输入手机号" clearable />
						</el-form-item>
					</el-col>
					<el-col :xs="24" class="mb16">
						<el-form-item label="角色" prop="role">
							<el-select v-model="state.form.role" value-key="id" placeholder="请选择注册角色" style="width: 100%">
								<el-option v-for="item in option" :key="item.id" :label="item.label" :value="item.role" />
							</el-select>
						</el-form-item>
					</el-col>
				</el-row>
			</el-form>

			<template #footer>
				<div class="dialog-footer">
					<el-button @click="onCancel">取消</el-button>
					<el-button type="primary" class="submit-button" @click="onSubmit">{{ state.dialog.submitTxt }}</el-button>
				</div>
			</template>
		</el-dialog>
	</div>
</template>

<script setup lang="ts" name="systemRoleDialog">
import { nextTick, reactive, ref } from 'vue';
import type { UploadInstance, UploadProps } from 'element-plus';
import { ElMessage } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import request from '/@/utils/request';

const emit = defineEmits(['refresh']);

const imageUrl = ref('');
const uploadFile = ref<UploadInstance>();

const handleAvatarSuccessone: UploadProps['onSuccess'] = (response, uploadFile) => {
	imageUrl.value = URL.createObjectURL(uploadFile.raw!);
	state.form.avatar = response.data;
};

const option = [
	{ id: 1, label: '管理员', role: 'admin' },
	{ id: 2, label: '普通用户', role: 'common' },
];

const roleDialogFormRef = ref();
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
		{ required: true, message: '请输入邮箱', trigger: 'blur' },
		{ type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
	],
	tel: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
	role: [{ required: true, message: '请选择角色', trigger: 'change' }],
};

const state = reactive({
	form: {} as any,
	menuData: [] as TreeType[],
	menuProps: {
		children: 'children',
		label: 'label',
	},
	submitTxt: '',
	dialog: {
		isShowDialog: false,
		type: '',
		title: '',
		submitTxt: '',
	},
});

const openDialog = (type: string, row: RowRoleType) => {
	if (type === 'edit') {
		state.form = { ...row };
		state.dialog.title = '修改用户信息';
		state.dialog.submitTxt = '保存修改';
		imageUrl.value = state.form.avatar;
	} else {
		state.dialog.title = '新增用户信息';
		state.dialog.submitTxt = '确认新增';
		nextTick(() => {
			uploadFile.value?.clearFiles();
			imageUrl.value = '';
			state.form = {
				id: null,
				username: '',
				password: '',
				name: '',
				sex: '',
				email: '',
				tel: '',
				role: '',
				avatar: '',
			};
		});
	}
	state.dialog.isShowDialog = true;
};

const closeDialog = () => {
	state.dialog.isShowDialog = false;
};

const onCancel = () => {
	closeDialog();
};

const onSubmit = () => {
	if (!roleDialogFormRef.value) return;
	roleDialogFormRef.value.validate((valid: boolean) => {
		if (!valid) {
			ElMessage.error('请完善必填信息');
			return false;
		}

		if (state.form.role == '管理员') {
			state.form.role = 'admin';
		} else if (state.form.role == '普通用户') {
			state.form.role = 'common';
		} else if (state.form.role == '其他用户') {
			state.form.role = 'others';
		}

		if (state.dialog.title == '修改用户信息') {
			request.post('/api/user/update', state.form).then((res) => {
				if (res.code == 0) {
					ElMessage.success('修改成功');
					setTimeout(() => {
						closeDialog();
						emit('refresh');
					}, 500);
				} else {
					ElMessage.error(res.msg);
				}
			});
		} else {
			request.post('/api/user/', state.form).then((res) => {
				if (res.code == 0) {
					ElMessage.success('新增成功');
				} else {
					ElMessage.error(res.msg);
				}
				setTimeout(() => {
					closeDialog();
					emit('refresh');
				}, 500);
			});
		}
	});
};

defineExpose({
	openDialog,
});
</script>

<style scoped lang="scss">
:deep(.dialog-shell .el-dialog) {
	border-radius: 26px;
	overflow: hidden;
	background: linear-gradient(180deg, #ffffff 0%, #f8fbf9 100%);
}

:deep(.dialog-shell .el-dialog__header) {
	display: none;
}

:deep(.dialog-shell .el-dialog__body) {
	padding: 0 0 18px;
}

:deep(.dialog-shell .el-dialog__footer) {
	padding: 0 24px 24px;
}

.dialog-banner {
	padding: 24px 24px 18px;
	background: linear-gradient(135deg, #173743 0%, #1d6e5d 55%, #2f7898 100%);
	color: #fff;
}

.banner-tag {
	display: inline-flex;
	padding: 6px 12px;
	border-radius: 999px;
	background: rgba(255, 255, 255, 0.12);
	font-size: 12px;
	letter-spacing: 0.12em;
}

.dialog-banner h3 {
	margin: 14px 0 8px;
	font-size: 26px;
}

.dialog-banner p {
	margin: 0;
	color: rgba(255, 255, 255, 0.82);
}

.avatar-section {
	display: flex;
	justify-content: center;
	padding: 22px 24px 0;
}

.avatar-frame {
	width: 132px;
	height: 132px;
	border-radius: 24px;
	display: flex;
	align-items: center;
	justify-content: center;
	background: linear-gradient(180deg, #f7faf8 0%, #eef4f1 100%);
	box-shadow: inset 0 0 0 1px rgba(86, 115, 126, 0.08);
	overflow: hidden;
	cursor: pointer;
}

.avatar-empty {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 8px;
	color: #6e8193;
}

.avatar {
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.dialog-form {
	padding: 22px 24px 0;
}

.mb16 {
	margin-bottom: 16px;
}

.dialog-footer {
	display: flex;
	justify-content: flex-end;
	gap: 10px;
}

.submit-button {
	border: none;
	border-radius: 14px;
	background: linear-gradient(135deg, #1f6f58 0%, #2f8b70 55%, #2c79a5 100%);
	box-shadow: 0 16px 28px rgba(39, 103, 91, 0.18);
}

:deep(.el-form-item__label) {
	color: #506273;
	font-weight: 600;
}

:deep(.el-input__wrapper),
:deep(.el-select .el-input__wrapper) {
	border-radius: 14px;
	background: #f5f8f6;
	box-shadow: inset 0 0 0 1px rgba(106, 128, 115, 0.12) !important;
}
</style>

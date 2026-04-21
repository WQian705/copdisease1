<template>
	<div class="system-role-dialog-container">
		<el-dialog :title="state.dialog.title" v-model="state.dialog.isShowDialog" width="920px" class="disease-dialog">
			<el-form ref="diseaseDialogFormRef" :model="state.form" size="default" label-width="92px" class="dialog-form">
				<el-row :gutter="20">
					<el-col :span="12" class="mb20">
						<el-form-item label="作物类型">
							<el-select v-model="state.form.cropType" placeholder="请选择作物类型" style="width: 100%">
								<el-option v-for="item in cropTypes" :key="item.value" :label="item.label" :value="item.value" />
							</el-select>
						</el-form-item>
					</el-col>
					<el-col :span="12" class="mb20">
						<el-form-item label="病害名称">
							<el-input v-model="state.form.name" placeholder="请输入病害名称" clearable />
						</el-form-item>
					</el-col>
					<el-col :span="24" class="mb20">
						<el-form-item label="病害症状">
							<el-input type="textarea" v-model="state.form.symptoms" placeholder="请输入病害症状" :rows="5" />
						</el-form-item>
					</el-col>
					<el-col :span="24" class="mb20">
						<el-form-item label="发病原因">
							<el-input type="textarea" v-model="state.form.causes" placeholder="请输入发病原因" :rows="4" />
						</el-form-item>
					</el-col>
					<el-col :span="24" class="mb20">
						<el-form-item label="防治方法">
							<el-input type="textarea" v-model="state.form.prevention" placeholder="请输入防治方法" :rows="5" />
						</el-form-item>
					</el-col>
					<el-col :span="24" class="mb20">
						<el-form-item label="图片">
							<el-upload
								ref="uploadFile"
								class="avatar-uploader"
								action="http://localhost:9999/files/upload"
								:show-file-list="false"
								:on-success="handleAvatarSuccess"
							>
								<img v-if="imageUrl" :src="imageUrl" class="avatar" />
								<div v-else class="upload-empty">
									<el-icon class="avatar-uploader-icon"><Plus /></el-icon>
									<span>点击上传图片</span>
								</div>
							</el-upload>
						</el-form-item>
					</el-col>
				</el-row>
			</el-form>
			<template #footer>
				<span class="dialog-footer">
					<el-button @click="onCancel" size="default">取消</el-button>
					<el-button type="primary" @click="onSubmit" size="default">{{ state.dialog.submitTxt }}</el-button>
				</span>
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

const cropTypes = [
	{ value: '玉米', label: '玉米' },
	{ value: '小麦', label: '小麦' },
	{ value: '水稻', label: '水稻' },
	{ value: '马铃薯', label: '马铃薯' },
	{ value: '棉花', label: '棉花' },
	{ value: '苹果', label: '苹果' },
	{ value: '葡萄', label: '葡萄' },
	{ value: '番茄', label: '番茄' },
	{ value: '草莓', label: '草莓' },
];

const diseaseDialogFormRef = ref();
const state = reactive({
	form: {
		id: null,
		cropType: '',
		name: '',
		symptoms: '',
		causes: '',
		prevention: '',
		images: '',
	},
	dialog: {
		isShowDialog: false,
		type: '',
		title: '',
		submitTxt: '',
	},
});

const openDialog = (type: string, row: any) => {
	if (type === 'edit') {
		state.form = { ...row };
		state.dialog.title = '修改病害信息';
		state.dialog.submitTxt = '保存修改';
		imageUrl.value = state.form.images;
	} else {
		state.dialog.title = '新增病害信息';
		state.dialog.submitTxt = '确认新增';
		nextTick(() => {
			uploadFile.value!.clearFiles();
			imageUrl.value = '';
			state.form = {
				id: null,
				cropType: '',
				name: '',
				symptoms: '',
				causes: '',
				prevention: '',
				images: '',
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
	if (state.dialog.title === '修改病害信息') {
		request
			.put('/api/disease', state.form)
			.then((res) => {
				if (res.code == 0) {
					ElMessage.success('修改成功');
					setTimeout(() => {
						closeDialog();
						emit('refresh');
					}, 500);
				} else {
					ElMessage({ type: 'error', message: res.msg });
				}
			})
			.catch((error) => {
				ElMessage({ type: 'error', message: '修改失败：' + error.message });
			});
	} else {
		request
			.post('/api/disease', state.form)
			.then((res) => {
				if (res.code == 0) {
					ElMessage.success('添加成功');
				} else {
					ElMessage({ type: 'error', message: res.msg });
				}
				setTimeout(() => {
					closeDialog();
					emit('refresh');
				}, 500);
			})
			.catch((error) => {
				ElMessage({ type: 'error', message: '添加失败：' + error.message });
			});
	}
};

const handleAvatarSuccess: UploadProps['onSuccess'] = (response, uploadFile) => {
	imageUrl.value = URL.createObjectURL(uploadFile.raw!);
	state.form.images = response.data;
};

defineExpose({
	openDialog,
});
</script>

<style scoped lang="scss">
:deep(.disease-dialog .el-dialog) {
	margin-top: 7vh !important;
	border-radius: 26px;
	overflow: hidden;
}

:deep(.disease-dialog .el-dialog__header) {
	padding: 22px 24px;
	border-bottom: 1px solid #e3ebe6;
	background: linear-gradient(180deg, #fbfdfc 0%, #f5f9f7 100%);
}

:deep(.disease-dialog .el-dialog__body) {
	padding: 22px 24px 12px;
}

:deep(.disease-dialog .el-dialog__footer) {
	padding: 18px 24px 22px;
	border-top: 1px solid #e3ebe6;
}

.avatar-uploader {
	:deep(.el-upload) {
		width: 220px;
		height: 220px;
		border-radius: 20px;
		border: 1px dashed #cfd9d2;
		background: #f6faf7;
		display: flex;
		align-items: center;
		justify-content: center;
		overflow: hidden;
		transition: border-color 0.2s ease, transform 0.2s ease;

		&:hover {
			border-color: #2c79a5;
			transform: translateY(-1px);
		}
	}
}

.upload-empty {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 10px;
	color: #7e8d9c;
}

.avatar-uploader-icon {
	font-size: 30px;
}

.avatar {
	width: 100%;
	height: 100%;
	object-fit: contain;
	display: block;
}

.mb20 {
	margin-bottom: 16px;
}

:deep(.dialog-form .el-form-item__label) {
	font-weight: 600;
	color: #34495d;
}

:deep(.dialog-form .el-input__wrapper),
:deep(.dialog-form .el-select .el-input__wrapper),
:deep(.dialog-form .el-textarea__inner) {
	border-radius: 14px;
	background: #f5f8f6;
	box-shadow: inset 0 0 0 1px rgba(106, 128, 115, 0.12) !important;
}

.dialog-footer {
	display: flex;
	justify-content: flex-end;
	gap: 10px;
}
</style>

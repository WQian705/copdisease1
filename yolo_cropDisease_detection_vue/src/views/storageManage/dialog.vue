<template>
	<div class="storage-dialog">
		<el-dialog :title="state.dialog.title" v-model="state.dialog.isShowDialog" width="760px" class="dialog-shell">
			<div class="dialog-banner">
				<div>
					<span class="banner-tag">库存表单</span>
					<h3>{{ state.dialog.title }}</h3>
					<p>填写库存基础信息、仓储位置和负责人资料。</p>
				</div>
			</div>

			<el-form ref="storageDialogFormRef" :model="state.form" :rules="state.rules" label-width="88px" class="dialog-form">
				<el-row :gutter="20">
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="产品" prop="product">
							<el-input v-model="state.form.product" placeholder="请输入产品" clearable />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="仓库" prop="warehouse">
							<el-input v-model="state.form.warehouse" placeholder="请输入仓库" clearable />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="存储区" prop="storageArea">
							<el-select v-model="state.form.storageArea" placeholder="请选择存储区" style="width: 100%">
								<el-option label="1号仓储区" value="1号仓储区" />
								<el-option label="2号仓储区" value="2号仓储区" />
								<el-option label="3号仓储区" value="3号仓储区" />
								<el-option label="4号仓储区" value="4号仓储区" />
								<el-option label="5号仓储区" value="5号仓储区" />
							</el-select>
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="数量" prop="quantity">
							<el-input-number v-model="state.form.quantity" :min="0" style="width: 100%" />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="管理员" prop="manager">
							<el-input v-model="state.form.manager" placeholder="请输入仓库管理员" clearable />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="手机号" prop="phone">
							<el-input v-model="state.form.phone" placeholder="请输入手机号" clearable />
						</el-form-item>
					</el-col>
					<el-col :xs="24" class="mb16">
						<el-form-item label="备注" prop="remark">
							<el-input v-model="state.form.remark" type="textarea" :rows="4" placeholder="请输入备注信息" />
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
import { ElMessage } from 'element-plus';
import type { FormInstance } from 'element-plus';
import request from '/@/utils/request';

const emit = defineEmits(['refresh']);

const storageDialogFormRef = ref<FormInstance>();
const state = reactive({
	form: {
		id: null,
		product: '',
		warehouse: '',
		storageArea: '',
		quantity: 0,
		manager: '',
		phone: '',
		remark: '',
	},
	rules: {
		product: [{ required: true, message: '请输入产品', trigger: 'blur' }],
		warehouse: [{ required: true, message: '请输入仓库', trigger: 'blur' }],
		storageArea: [{ required: true, message: '请选择存储区', trigger: 'change' }],
		quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
		manager: [{ required: true, message: '请输入管理员', trigger: 'blur' }],
		phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
		remark: [{ required: true, message: '请输入备注信息', trigger: 'blur' }],
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
		state.dialog.title = '修改库存信息';
		state.dialog.submitTxt = '保存修改';
	} else {
		state.dialog.title = '新增库存信息';
		state.dialog.submitTxt = '确认新增';
		nextTick(() => {
			state.form = {
				id: null,
				product: '',
				warehouse: '',
				storageArea: '',
				quantity: 0,
				manager: '',
				phone: '',
				remark: '',
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
	if (!storageDialogFormRef.value) return;
	storageDialogFormRef.value.validate((valid: boolean) => {
		if (valid) {
			if (state.dialog.title === '修改库存信息') {
				request.post('/api/storage/update', state.form).then((res) => {
					if (res.code == 0) {
						ElMessage.success('修改成功');
						closeDialog();
						emit('refresh');
					} else {
						ElMessage.error(res.msg);
					}
				});
			} else {
				request.post('/api/storage', state.form).then((res) => {
					if (res.code == 0) {
						ElMessage.success('新增成功');
						closeDialog();
						emit('refresh');
					} else {
						ElMessage.error(res.msg);
					}
				});
			}
		} else {
			return false;
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
	background: linear-gradient(135deg, #183743 0%, #216a59 55%, #2b7897 100%);
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
:deep(.el-textarea__inner),
:deep(.el-select .el-input__wrapper) {
	border-radius: 14px;
	background: #f5f8f6;
	box-shadow: inset 0 0 0 1px rgba(106, 128, 115, 0.12) !important;
}

:deep(.el-input-number) {
	width: 100%;
}
</style>

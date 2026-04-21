<template>
	<div class="purchase-dialog">
		<el-dialog :title="state.dialog.title" v-model="state.dialog.isShowDialog" width="780px" class="dialog-shell">
			<div class="dialog-banner">
				<div>
					<span class="banner-tag">采购表单</span>
					<h3>{{ state.dialog.title }}</h3>
					<p>填写产品采购信息、供应商资料与联系人信息。</p>
				</div>
			</div>

			<el-form ref="purchaseDialogFormRef" :model="state.form" :rules="state.rules" label-width="92px" class="dialog-form">
				<el-row :gutter="20">
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="产品名称" prop="productName">
							<el-input v-model="state.form.productName" placeholder="请输入产品名称" clearable />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="供应商" prop="supplier">
							<el-input v-model="state.form.supplier" placeholder="请输入供应商" clearable />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="价格" prop="price">
							<el-input-number v-model="state.form.price" :precision="2" :step="0.01" :min="0" style="width: 100%" />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="数量" prop="quantity">
							<el-input-number v-model="state.form.quantity" :min="0" style="width: 100%" />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="地区" prop="region">
							<el-input v-model="state.form.region" placeholder="请输入地区" clearable />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="电话" prop="phone">
							<el-input v-model="state.form.phone" placeholder="请输入电话" clearable />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="采购人" prop="manager">
							<el-input v-model="state.form.manager" placeholder="请输入采购人" clearable />
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

const purchaseDialogFormRef = ref<FormInstance>();
const state = reactive({
	form: {
		id: null,
		productName: '',
		price: 0,
		quantity: 0,
		supplier: '',
		region: '',
		phone: '',
		manager: '',
		remark: '',
	},
	rules: {
		productName: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
		price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
		quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
		supplier: [{ required: true, message: '请输入供应商', trigger: 'blur' }],
		region: [{ required: true, message: '请输入地区', trigger: 'blur' }],
		phone: [{ required: true, message: '请输入电话', trigger: 'blur' }],
		manager: [{ required: true, message: '请输入采购人', trigger: 'blur' }],
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
		state.dialog.title = '修改采购信息';
		state.dialog.submitTxt = '保存修改';
	} else {
		state.dialog.title = '新增采购信息';
		state.dialog.submitTxt = '确认新增';
		nextTick(() => {
			state.form = {
				id: null,
				productName: '',
				price: 0,
				quantity: 0,
				supplier: '',
				region: '',
				phone: '',
				manager: '',
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
	if (!purchaseDialogFormRef.value) return;
	purchaseDialogFormRef.value.validate((valid: boolean) => {
		if (valid) {
			if (state.dialog.title === '修改采购信息') {
				request.post('/api/purchase/update', state.form).then((res) => {
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
				request.post('/api/purchase', state.form).then((res) => {
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
	background: linear-gradient(135deg, #163744 0%, #2f6f56 55%, #347c8f 100%);
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

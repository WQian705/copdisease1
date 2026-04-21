<template>
	<div class="greenhouse-dialog">
		<el-dialog :title="state.dialog.title" v-model="state.dialog.isShowDialog" width="940px" class="dialog-shell">
			<div class="dialog-banner">
				<div>
					<span class="banner-tag">温室信息</span>
					<h3>{{ state.dialog.title }}</h3>
					<p>记录作物状态、环境参数和负责人信息，保留原有新增与更新接口。</p>
				</div>
			</div>

			<el-form ref="greenhouseDialogFormRef" :model="state.form" size="default" label-width="102px" :rules="state.rules" class="dialog-form">
				<el-row :gutter="20">
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="温室名称" prop="greenhouseName">
							<el-input v-model="state.form.greenhouseName" placeholder="请输入温室名称" clearable />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="作物类型" prop="cropType">
							<el-input v-model="state.form.cropType" placeholder="请输入作物类型" clearable />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="数量" prop="quantity">
							<el-input-number v-model="state.form.quantity" :min="0" style="width: 100%" />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="生长状态" prop="growthStatus">
							<el-input v-model="state.form.growthStatus" placeholder="请输入生长状态" clearable />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="温度(°C)" prop="temperature">
							<el-input-number v-model="state.form.temperature" :precision="1" :step="0.1" style="width: 100%" />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="空气湿度" prop="airHumidity">
							<el-input-number v-model="state.form.airHumidity" :min="0" :max="100" style="width: 100%" />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="土壤湿度" prop="soilHumidity">
							<el-input-number v-model="state.form.soilHumidity" :min="0" :max="100" style="width: 100%" />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="CO2浓度" prop="co2Concentration">
							<el-input-number v-model="state.form.co2Concentration" :min="0" style="width: 100%" />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="土壤pH" prop="soilPh">
							<el-input-number v-model="state.form.soilPh" :precision="1" :step="0.1" :min="0" :max="14" style="width: 100%" />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="光照强度" prop="lightIntensity">
							<el-input-number v-model="state.form.lightIntensity" :min="0" style="width: 100%" />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="负责人" prop="manager">
							<el-input v-model="state.form.manager" placeholder="请输入负责人" clearable />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="12" class="mb16">
						<el-form-item label="记录时间" prop="recordTime">
							<el-date-picker
								v-model="state.form.recordTime"
								type="datetime"
								placeholder="请选择记录时间"
								style="width: 100%"
								value-format="YYYY-MM-DD HH:mm:ss"
							/>
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

const greenhouseDialogFormRef = ref<FormInstance>();
const state = reactive({
	form: {
		id: null,
		greenhouseName: '',
		cropType: '',
		quantity: 0,
		growthStatus: '',
		temperature: 0,
		airHumidity: 0,
		soilHumidity: 0,
		co2Concentration: 0,
		soilPh: 0,
		lightIntensity: 0,
		supplementaryLight: '关闭',
		ventilation: '关闭',
		irrigation: '关闭',
		manager: '',
		recordTime: '',
	},
	rules: {
		greenhouseName: [{ required: true, message: '请输入温室名称', trigger: 'blur' }],
		cropType: [{ required: true, message: '请输入作物类型', trigger: 'blur' }],
		quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
		growthStatus: [{ required: true, message: '请输入生长状态', trigger: 'blur' }],
		temperature: [{ required: true, message: '请输入温度', trigger: 'blur' }],
		airHumidity: [{ required: true, message: '请输入空气湿度', trigger: 'blur' }],
		soilHumidity: [{ required: true, message: '请输入土壤湿度', trigger: 'blur' }],
		co2Concentration: [{ required: true, message: '请输入CO2浓度', trigger: 'blur' }],
		soilPh: [{ required: true, message: '请输入土壤pH', trigger: 'blur' }],
		lightIntensity: [{ required: true, message: '请输入光照强度', trigger: 'blur' }],
		manager: [{ required: true, message: '请输入负责人', trigger: 'blur' }],
		recordTime: [{ required: true, message: '请选择记录时间', trigger: 'change' }],
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
		state.dialog.title = '修改温室信息';
		state.dialog.submitTxt = '保存修改';
	} else {
		state.dialog.title = '新增温室信息';
		state.dialog.submitTxt = '确认新增';
		nextTick(() => {
			state.form = {
				id: null,
				greenhouseName: '',
				cropType: '',
				quantity: 0,
				growthStatus: '',
				temperature: 0,
				airHumidity: 0,
				soilHumidity: 0,
				co2Concentration: 0,
				soilPh: 0,
				lightIntensity: 0,
				supplementaryLight: '关闭',
				ventilation: '关闭',
				irrigation: '关闭',
				manager: '',
				recordTime: '',
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
	if (!greenhouseDialogFormRef.value) return;
	greenhouseDialogFormRef.value.validate((valid: boolean) => {
		if (valid) {
			if (state.dialog.title === '修改温室信息') {
				request.post('/api/greenhouse/update', state.form).then((res) => {
					if (res.code == 0) {
						ElMessage.success('修改成功');
						closeDialog();
						emit('refresh');
					} else {
						ElMessage.error(res.msg);
					}
				});
			} else {
				request.post('/api/greenhouse', state.form).then((res) => {
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
	background: linear-gradient(135deg, #173843 0%, #216959 55%, #2a7a95 100%);
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
:deep(.el-select .el-input__wrapper),
:deep(.el-date-editor.el-input__wrapper) {
	border-radius: 14px;
	background: #f5f8f6;
	box-shadow: inset 0 0 0 1px rgba(106, 128, 115, 0.12) !important;
}

:deep(.el-input-number) {
	width: 100%;
}
</style>

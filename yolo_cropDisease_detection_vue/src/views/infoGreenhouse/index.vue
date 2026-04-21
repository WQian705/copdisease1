<template>
	<div class="page-shell layout-padding">
		<div class="page-panel layout-padding-auto layout-padding-view">
			<section class="page-hero">
				<div>
					<span class="page-badge">温室信息</span>
					<h2>温室环境与作物状态管理</h2>
					<p>保留原有温室增删改与分页逻辑，仅升级筛选栏和表格展示效果。</p>
				</div>
				<div class="hero-tip">
					<span>当前记录</span>
					<strong>{{ state.tableData.total }}</strong>
				</div>
			</section>

			<section class="toolbar-card">
				<div class="toolbar-grid toolbar-grid--wide">
					<el-input v-model="state.tableData.param.search" size="default" placeholder="请输入温室名称" />
					<el-input v-model="state.tableData.param.cropType" size="default" placeholder="请输入作物类型" />
					<el-input v-model="state.tableData.param.growthStatus" size="default" placeholder="请输入生长状态" />
					<el-input v-model="state.tableData.param.manager" size="default" placeholder="请输入负责人" />
					<div class="toolbar-actions">
						<el-button size="default" type="primary" @click="getTableData()">
							<el-icon><ele-Search /></el-icon>
							查询
						</el-button>
						<el-button size="default" type="success" @click="onOpenAddGreenhouse('add')">
							<el-icon><ele-FolderAdd /></el-icon>
							新增温室
						</el-button>
					</div>
				</div>
			</section>

			<section class="table-card">
				<el-table :data="state.tableData.data" v-loading="state.tableData.loading" style="width: 100%">
					<el-table-column prop="num" label="序号" width="80" align="center" />
					<el-table-column prop="greenhouseName" label="温室名称" show-overflow-tooltip width="110" align="center" />
					<el-table-column prop="cropType" label="作物类型" show-overflow-tooltip width="110" align="center" />
					<el-table-column prop="quantity" label="数量" width="90" align="center" />
					<el-table-column prop="growthStatus" label="生长状态" show-overflow-tooltip width="110" align="center" />
					<el-table-column prop="temperature" label="温度(℃)" width="100" align="center" />
					<el-table-column prop="airHumidity" label="空气湿度(%)" width="110" align="center" />
					<el-table-column prop="soilHumidity" label="土壤湿度(%)" width="110" align="center" />
					<el-table-column prop="co2Concentration" label="CO2浓度(ppm)" width="130" align="center" />
					<el-table-column prop="soilPh" label="土壤pH" width="90" align="center" />
					<el-table-column prop="lightIntensity" label="光照强度(lux)" width="130" align="center" />
					<el-table-column prop="manager" label="负责人" show-overflow-tooltip width="100" align="center" />
					<el-table-column prop="recordTime" label="记录时间" width="170" align="center" />
					<el-table-column label="操作" width="150" fixed="right" align="center">
						<template #default="scope">
							<el-button size="small" text type="primary" @click="onOpenEditGreenhouse('edit', scope.row)">修改</el-button>
							<el-button size="small" text type="danger" @click="onRowDel(scope.row)">删除</el-button>
						</template>
					</el-table-column>
				</el-table>
				<el-pagination
					@size-change="onHandleSizeChange"
					@current-change="onHandleCurrentChange"
					class="table-pagination"
					:pager-count="5"
					:page-sizes="[10, 20, 30]"
					v-model:current-page="state.tableData.param.pageNum"
					background
					v-model:page-size="state.tableData.param.pageSize"
					layout="total, sizes, prev, pager, next, jumper"
					:total="state.tableData.total"
				/>
			</section>
		</div>
		<GreenhouseDialog ref="greenhouseDialogRef" @refresh="getTableData()" />
	</div>
</template>

<script setup lang="ts" name="systemRole">
import { defineAsyncComponent, reactive, onMounted, ref } from 'vue';
import { ElMessageBox, ElMessage } from 'element-plus';
import request from '/@/utils/request';

const GreenhouseDialog = defineAsyncComponent(() => import('./dialog.vue'));

const greenhouseDialogRef = ref();
const state = reactive({
	tableData: {
		data: [] as any,
		total: 0,
		loading: false,
		param: {
			search: '',
			cropType: '',
			growthStatus: '',
			manager: '',
			recordTime: '',
			pageNum: 1,
			pageSize: 10,
		},
	},
});

const getTableData = () => {
	state.tableData.loading = true;
	request
		.get('/api/greenhouse', {
			params: state.tableData.param,
		})
		.then((res) => {
			if (res.code == 0) {
				state.tableData.data = [];
				setTimeout(() => {
					state.tableData.loading = false;
				}, 500);
				for (let i = 0; i < res.data.records.length; i++) {
					state.tableData.data[i] = res.data.records[i];
					state.tableData.data[i]['num'] = i + 1;
				}
				state.tableData.total = res.data.total;
			} else {
				ElMessage({ type: 'error', message: res.msg });
			}
		});
};

const onOpenAddGreenhouse = (type: string) => {
	greenhouseDialogRef.value.openDialog(type);
};

const onOpenEditGreenhouse = (type: string, row: Object) => {
	greenhouseDialogRef.value.openDialog(type, row);
};

const onRowDel = (row: any) => {
	ElMessageBox.confirm(`此操作将永久删除该温室信息，是否继续？`, '提示', {
		confirmButtonText: '确认',
		cancelButtonText: '取消',
		type: 'warning',
	})
		.then(() => {
			request.delete('/api/greenhouse/' + row.id).then((res) => {
				if (res.code == 0) {
					ElMessage({ type: 'success', message: '删除成功' });
					setTimeout(() => {
						getTableData();
					}, 500);
				} else {
					ElMessage({ type: 'error', message: res.msg });
				}
			});
		})
		.catch(() => {});
};

const onHandleSizeChange = (val: number) => {
	state.tableData.param.pageSize = val;
	getTableData();
};

const onHandleCurrentChange = (val: number) => {
	state.tableData.param.pageNum = val;
	getTableData();
};

onMounted(() => {
	getTableData();
});
</script>

<style scoped lang="scss">
.page-shell {
	.page-panel {
		padding: 18px;
		background: rgba(255, 255, 255, 0.88);
	}
}

.page-hero {
	display: flex;
	align-items: stretch;
	justify-content: space-between;
	gap: 16px;
	padding: 24px;
	border-radius: 24px;
	background: linear-gradient(135deg, #173f35 0%, #286a54 58%, #376b8e 100%);
	color: #fff;
}

.page-badge {
	display: inline-flex;
	padding: 7px 12px;
	border-radius: 999px;
	background: rgba(255, 255, 255, 0.12);
	font-size: 12px;
	letter-spacing: 0.12em;
}

.page-hero h2 {
	margin: 14px 0 8px;
	font-size: 28px;
}

.page-hero p {
	color: rgba(255, 255, 255, 0.8);
	line-height: 1.8;
}

.hero-tip {
	min-width: 140px;
	padding: 18px;
	border-radius: 20px;
	background: rgba(255, 255, 255, 0.12);
	display: flex;
	flex-direction: column;
	justify-content: center;
}

.hero-tip span {
	color: rgba(255, 255, 255, 0.72);
	font-size: 13px;
}

.hero-tip strong {
	margin-top: 8px;
	font-size: 28px;
}

.toolbar-card,
.table-card {
	margin-top: 16px;
	padding: 18px;
	border-radius: 22px;
	background: linear-gradient(180deg, #ffffff 0%, #f7faf8 100%);
	box-shadow: 0 18px 34px rgba(31, 52, 84, 0.06);
}

.toolbar-grid {
	display: grid;
	gap: 12px;
	align-items: center;
}

.toolbar-grid--wide {
	grid-template-columns: repeat(4, minmax(0, 1fr)) auto;
}

.toolbar-actions {
	display: flex;
	flex-wrap: wrap;
	justify-content: flex-end;
	gap: 10px;
}

.table-pagination {
	margin-top: 18px;
	display: flex;
	justify-content: flex-end;
}

:deep(.el-input__wrapper) {
	border-radius: 14px;
	background: #f5f8f6;
	box-shadow: inset 0 0 0 1px rgba(106, 128, 115, 0.12) !important;
}

:deep(.el-table) {
	border-radius: 18px;
	overflow: hidden;
}

:deep(.el-table th.el-table__cell) {
	background: #f3f8f5;
	color: #304558;
	font-weight: 700;
}

@media (max-width: 1200px) {
	.toolbar-grid--wide {
		grid-template-columns: repeat(2, minmax(0, 1fr));
	}
}

@media (max-width: 992px) {
	.page-hero {
		flex-direction: column;
	}

	.toolbar-grid--wide {
		grid-template-columns: 1fr;
	}

	.toolbar-actions,
	.table-pagination {
		justify-content: flex-start;
	}
}
</style>

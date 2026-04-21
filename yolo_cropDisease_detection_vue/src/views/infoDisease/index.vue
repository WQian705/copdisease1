<template>
	<div class="page-shell layout-padding">
		<div class="page-panel layout-padding-auto layout-padding-view">
			<section class="page-hero">
				<div>
					<span class="page-badge">病害资料库</span>
					<h2>作物病害信息统一管理</h2>
					<p>支持按病害名称和作物类型筛选，保留原有新增、详情、修改和删除流程。</p>
				</div>
				<div class="hero-tip">
					<span>当前条目</span>
					<strong>{{ state.tableData.total }}</strong>
				</div>
			</section>

			<section class="toolbar-card">
				<div class="toolbar-grid">
					<el-input v-model="state.tableData.param.name" size="default" placeholder="请输入病害名称" clearable />
					<el-select v-model="state.tableData.param.cropType" size="default" placeholder="请选择作物类型" clearable>
						<el-option v-for="item in state.cropTypes" :key="item" :label="item" :value="item"></el-option>
					</el-select>
					<div class="toolbar-actions">
						<el-button size="default" type="primary" @click="getTableData()">
							<el-icon><ele-Search /></el-icon>
							查询
						</el-button>
						<el-button size="default" type="success" @click="onOpenAddDisease('add')">
							<el-icon><ele-FolderAdd /></el-icon>
							新增病害
						</el-button>
					</div>
				</div>
			</section>

			<section class="table-card">
				<el-table :data="state.tableData.data" v-loading="state.tableData.loading" style="width: 100%">
					<el-table-column prop="num" label="序号" width="80" align="center" />
					<el-table-column prop="cropType" label="作物类型" show-overflow-tooltip width="110" align="center" />
					<el-table-column prop="name" label="病害名称" show-overflow-tooltip width="150" align="center" />
					<el-table-column prop="symptoms" label="病害症状" show-overflow-tooltip min-width="220" align="center" />
					<el-table-column prop="causes" label="发病原因" show-overflow-tooltip min-width="220" align="center" />
					<el-table-column prop="prevention" label="防治方法" show-overflow-tooltip min-width="220" align="center" />
					<el-table-column label="图片" width="100" align="center">
						<template #default="scope">
							<el-image
								class="thumb-image"
								:src="scope.row.image"
								:preview-src-list="[scope.row.image]"
								:preview-teleported="true"
								:hide-on-click-modal="true"
								fit="cover"
								:preview-options="{ zoom: false, closeOnPressEscape: true, toolbar: false }"
							/>
						</template>
					</el-table-column>
					<el-table-column label="操作" width="180" fixed="right" align="center">
						<template #default="scope">
							<el-button size="small" text type="primary" @click="onOpenDetail(scope.row)">详情</el-button>
							<el-button size="small" text type="primary" @click="onOpenEditDisease('edit', scope.row)">修改</el-button>
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
		<DiseaseDialog ref="diseaseDialogRef" @refresh="getTableData()" />
		<DiseaseDetail ref="diseaseDetailRef" />
	</div>
</template>

<script setup lang="ts" name="systemRole">
import { defineAsyncComponent, reactive, onMounted, ref } from 'vue';
import { ElMessageBox, ElMessage } from 'element-plus';
import request from '/@/utils/request';

const DiseaseDialog = defineAsyncComponent(() => import('./dialog.vue'));
const DiseaseDetail = defineAsyncComponent(() => import('./detail.vue'));

const diseaseDialogRef = ref();
const diseaseDetailRef = ref();
const state = reactive({
	tableData: {
		data: [] as any,
		total: 0,
		loading: false,
		param: {
			name: '',
			cropType: '',
			pageNum: 1,
			pageSize: 10,
		},
	},
	cropTypes: ['玉米', '水稻', '小麦', '马铃薯', '棉花', '苹果', '葡萄', '番茄', '草莓'],
});

const getTableData = () => {
	state.tableData.loading = true;
	request
		.get('/api/disease', {
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

const onOpenAddDisease = (type: string) => {
	diseaseDialogRef.value.openDialog(type);
};

const onOpenEditDisease = (type: string, row: Object) => {
	diseaseDialogRef.value.openDialog(type, row);
};

const onOpenDetail = (row: any) => {
	diseaseDetailRef.value.openDialog(row);
};

const onRowDel = (row: any) => {
	ElMessageBox.confirm(`此操作将永久删除该病害信息，是否继续？`, '提示', {
		confirmButtonText: '确认',
		cancelButtonText: '取消',
		type: 'warning',
	})
		.then(() => {
			request.delete('/api/disease/' + row.id).then((res) => {
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
	background: linear-gradient(135deg, #163f35 0%, #1f6c5a 58%, #2a739a 100%);
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
	grid-template-columns: repeat(2, minmax(0, 220px)) 1fr;
	gap: 12px;
	align-items: center;
}

.toolbar-actions {
	display: flex;
	flex-wrap: wrap;
	justify-content: flex-end;
	gap: 10px;
}

.thumb-image {
	width: 42px;
	height: 42px;
	border-radius: 12px;
	box-shadow: 0 8px 16px rgba(31, 52, 84, 0.12);
}

.table-pagination {
	margin-top: 18px;
	display: flex;
	justify-content: flex-end;
}

:deep(.el-input__wrapper),
:deep(.el-select .el-input__wrapper) {
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

@media (max-width: 992px) {
	.page-hero,
	.toolbar-grid {
		grid-template-columns: 1fr;
	}

	.page-hero {
		flex-direction: column;
	}

	.toolbar-actions,
	.table-pagination {
		justify-content: flex-start;
	}
}
</style>

<template>
	<div class="manage-page layout-padding">
		<div class="manage-panel layout-padding-auto layout-padding-view">
			<section class="manage-hero">
				<div>
					<span class="hero-badge">采购管理</span>
					<h2>梳理采购清单、供应商与负责人信息</h2>
					<p>保留原有查询、分页、新增、编辑和删除逻辑，仅重做页面布局和表格表现，让信息更清晰。</p>
				</div>
				<div class="hero-side">
					<span>管理重点</span>
					<strong>采购追踪</strong>
				</div>
			</section>

			<section class="toolbar-card">
				<div class="toolbar-grid">
					<el-input v-model="state.tableData.param.search" size="large" placeholder="请输入产品名称" clearable />
					<el-input v-model="state.tableData.param.supplier" size="large" placeholder="请输入供应商" clearable />
					<el-input v-model="state.tableData.param.region" size="large" placeholder="请输入地区" clearable />
					<el-input v-model="state.tableData.param.manager" size="large" placeholder="请输入采购人" clearable />
					<div class="action-row">
						<el-button size="large" type="primary" class="query-button" @click="getTableData()">
							<el-icon><ele-Search /></el-icon>
							查询
						</el-button>
						<el-button size="large" type="success" class="create-button" @click="onOpenAddPurchase('add')">
							<el-icon><ele-FolderAdd /></el-icon>
							新增采购
						</el-button>
					</div>
				</div>
			</section>

			<section class="table-card">
				<div class="table-head">
					<h3>采购列表</h3>
					<p>展示产品、价格、数量、供应商与采购负责人等关键字段。</p>
				</div>
				<el-table :data="state.tableData.data" v-loading="state.tableData.loading" class="manage-table">
					<el-table-column prop="num" label="序号" width="80" align="center" />
					<el-table-column prop="productName" label="产品名称" min-width="130" align="center" show-overflow-tooltip />
					<el-table-column prop="price" label="价格(元)" width="120" align="center" />
					<el-table-column prop="quantity" label="采购数量" width="120" align="center" />
					<el-table-column prop="supplier" label="供应商" min-width="130" align="center" show-overflow-tooltip />
					<el-table-column prop="region" label="地区" min-width="120" align="center" show-overflow-tooltip />
					<el-table-column prop="phone" label="电话" min-width="150" align="center" show-overflow-tooltip />
					<el-table-column prop="manager" label="采购人" min-width="120" align="center" show-overflow-tooltip />
					<el-table-column prop="remark" label="备注" min-width="150" align="center" show-overflow-tooltip />
					<el-table-column label="操作" width="160" fixed="right" align="center">
						<template #default="scope">
							<el-button size="small" text type="primary" @click="onOpenEditPurchase('edit', scope.row)">修改</el-button>
							<el-button size="small" text type="primary" @click="onRowDel(scope.row)">删除</el-button>
						</template>
					</el-table-column>
				</el-table>
				<div class="pagination-wrap">
					<el-pagination
						@size-change="onHandleSizeChange"
						@current-change="onHandleCurrentChange"
						:pager-count="5"
						:page-sizes="[10, 20, 30]"
						v-model:current-page="state.tableData.param.pageNum"
						v-model:page-size="state.tableData.param.pageSize"
						background
						layout="total, sizes, prev, pager, next, jumper"
						:total="state.tableData.total"
					/>
				</div>
			</section>
		</div>
		<PurchaseDialog ref="purchaseDialogRef" @refresh="getTableData()" />
	</div>
</template>

<script setup lang="ts" name="systemRole">
import { defineAsyncComponent, onMounted, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import request from '/@/utils/request';

const PurchaseDialog = defineAsyncComponent(() => import('./dialog.vue'));

const purchaseDialogRef = ref();
const state = reactive({
	tableData: {
		data: [] as any,
		total: 0,
		loading: false,
		param: {
			search: '',
			supplier: '',
			region: '',
			manager: '',
			pageNum: 1,
			pageSize: 10,
		},
	},
});

const getTableData = () => {
	state.tableData.loading = true;
	request
		.get('/api/purchase', {
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
					state.tableData.data[i].num = i + 1;
				}
				state.tableData.total = res.data.total;
			} else {
				ElMessage({
					type: 'error',
					message: res.msg,
				});
			}
		});
};

const onOpenAddPurchase = (type: string) => {
	purchaseDialogRef.value.openDialog(type);
};

const onOpenEditPurchase = (type: string, row: Object) => {
	purchaseDialogRef.value.openDialog(type, row);
};

const onRowDel = (row: any) => {
	ElMessageBox.confirm('此操作将永久删除该采购信息，是否继续？', '提示', {
		confirmButtonText: '确认',
		cancelButtonText: '取消',
		type: 'warning',
	})
		.then(() => {
			request.delete('/api/purchase/' + row.id).then((res) => {
				if (res.code == 0) {
					ElMessage({
						type: 'success',
						message: '删除成功',
					});
					setTimeout(() => {
						getTableData();
					}, 500);
				} else {
					ElMessage({
						type: 'error',
						message: res.msg,
					});
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
.manage-page {
	.manage-panel {
		padding: 18px;
		background: rgba(255, 255, 255, 0.88);
	}
}

.manage-hero {
	display: flex;
	justify-content: space-between;
	gap: 16px;
	padding: 24px;
	border-radius: 24px;
	background: linear-gradient(135deg, #163744 0%, #2f6f56 54%, #357b8f 100%);
	color: #fff;
}

.hero-badge {
	display: inline-flex;
	padding: 7px 12px;
	border-radius: 999px;
	background: rgba(255, 255, 255, 0.12);
	font-size: 12px;
	letter-spacing: 0.12em;
}

.manage-hero h2 {
	margin: 14px 0 8px;
	font-size: 28px;
}

.manage-hero p {
	color: rgba(255, 255, 255, 0.8);
	line-height: 1.8;
}

.hero-side {
	min-width: 150px;
	padding: 18px;
	border-radius: 20px;
	background: rgba(255, 255, 255, 0.12);
}

.hero-side span {
	color: rgba(255, 255, 255, 0.72);
	font-size: 13px;
}

.hero-side strong {
	display: block;
	margin-top: 10px;
	font-size: 26px;
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
	grid-template-columns: repeat(4, minmax(0, 1fr)) auto;
	gap: 12px;
	align-items: center;
}

.action-row {
	display: flex;
	flex-wrap: wrap;
	justify-content: flex-end;
	gap: 10px;
}

.query-button,
.create-button {
	height: 46px;
	padding: 0 20px;
	border: none;
	border-radius: 16px;
}

.query-button {
	background: linear-gradient(135deg, #1f6f58 0%, #2f8b70 55%, #2c79a5 100%);
	box-shadow: 0 18px 32px rgba(39, 103, 91, 0.2);
}

.create-button {
	background: linear-gradient(135deg, #d98530 0%, #ecb24f 100%);
	box-shadow: 0 18px 32px rgba(217, 133, 48, 0.22);
}

.table-head h3 {
	margin: 0 0 6px;
	color: #24384d;
}

.table-head p {
	margin: 0 0 18px;
	color: #7d8a98;
}

.pagination-wrap {
	display: flex;
	justify-content: flex-end;
	margin-top: 18px;
}

:deep(.el-table) {
	border-radius: 18px;
	overflow: hidden;
}

:deep(.el-table th.el-table__cell) {
	background: #f3f7f5;
	color: #52657a;
}

:deep(.el-table .el-table__row) {
	height: 54px;
}

:deep(.el-select .el-input__wrapper),
:deep(.el-input__wrapper) {
	border-radius: 14px;
	background: #f5f8f6;
	box-shadow: inset 0 0 0 1px rgba(106, 128, 115, 0.12) !important;
}

@media (max-width: 1200px) {
	.manage-hero,
	.toolbar-grid {
		grid-template-columns: 1fr;
	}

	.manage-hero {
		flex-direction: column;
	}

	.action-row,
	.pagination-wrap {
		justify-content: flex-start;
	}
}
</style>

<template>
	<div class="user-page layout-padding">
		<div class="user-panel layout-padding-auto layout-padding-view">
			<section class="user-hero">
				<div>
					<span class="hero-badge">用户管理</span>
					<h2>统一管理系统账号、角色与头像资料</h2>
					<p>保留原有查询、分页、新增、编辑和删除逻辑，只对列表层次、头像展示与操作区做统一升级。</p>
				</div>
				<div class="hero-side">
					<span>管理维度</span>
					<strong>账号权限</strong>
				</div>
			</section>

			<section class="toolbar-card">
				<div class="toolbar-row">
					<el-input v-model="state.tableData.param.search" size="large" placeholder="请输入用户名" clearable class="search-input" />
					<el-button size="large" type="primary" class="query-button" @click="getTableData()">
						<el-icon><ele-Search /></el-icon>
						查询
					</el-button>
					<el-button size="large" type="success" class="create-button" @click="onOpenAddRole('add')">
						<el-icon><ele-FolderAdd /></el-icon>
						新增用户
					</el-button>
				</div>
			</section>

			<section class="table-card">
				<div class="table-head">
					<h3>用户列表</h3>
					<p>展示账号信息、联系方式、角色身份与头像资料。</p>
				</div>
				<el-table :data="state.tableData.data" v-loading="state.tableData.loading" class="user-table">
					<el-table-column prop="num" label="序号" width="80" align="center" />
					<el-table-column prop="username" label="账号" min-width="120" align="center" show-overflow-tooltip />
					<el-table-column prop="password" label="密码" width="120" align="center" />
					<el-table-column prop="name" label="姓名" min-width="110" align="center" show-overflow-tooltip />
					<el-table-column prop="sex" label="性别" width="90" align="center" show-overflow-tooltip />
					<el-table-column prop="email" label="邮箱" min-width="180" align="center" show-overflow-tooltip />
					<el-table-column prop="tel" label="手机号" min-width="150" align="center" show-overflow-tooltip />
					<el-table-column prop="role" label="角色" min-width="120" align="center" show-overflow-tooltip>
						<template #default="scope">
							<el-tag class="role-tag" effect="plain">{{ scope.row.role }}</el-tag>
						</template>
					</el-table-column>
					<el-table-column prop="avatar" label="头像" width="120" align="center">
						<template #default="scope">
							<div class="avatar-card">
								<img :src="scope.row.avatar" alt="avatar" />
							</div>
						</template>
					</el-table-column>
					<el-table-column label="操作" width="160" align="center" fixed="right">
						<template #default="scope">
							<el-button size="small" text type="primary" @click="onOpenEditRole('edit', scope.row)">修改</el-button>
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
		<RoleDialog ref="roleDialogRef" @refresh="getTableData()" />
	</div>
</template>

<script setup lang="ts" name="systemRole">
import { defineAsyncComponent, onMounted, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import request from '/@/utils/request';

const RoleDialog = defineAsyncComponent(() => import('./dialog.vue'));

const roleDialogRef = ref();
const state = reactive<SysRoleState>({
	tableData: {
		data: [] as any,
		total: 0,
		loading: false,
		param: {
			search: '',
			pageNum: 1,
			pageSize: 10,
		},
	},
});

const getTableData = () => {
	state.tableData.loading = true;
	request
		.get('/api/user', {
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
					if (state.tableData.data[i].role == 'admin') {
						state.tableData.data[i].role = '管理员';
					} else if (state.tableData.data[i].role == 'common') {
						state.tableData.data[i].role = '普通用户';
					} else if (state.tableData.data[i].role == 'others') {
						state.tableData.data[i].role = '其他用户';
					}
				}
				state.tableData.total = res.data.total;
			} else {
				ElMessage.error(res.msg);
			}
		});
};

const onOpenAddRole = (type: string) => {
	roleDialogRef.value.openDialog(type);
};

const onOpenEditRole = (type: string, row: Object) => {
	roleDialogRef.value.openDialog(type, row);
};

const onRowDel = (row: any) => {
	ElMessageBox.confirm('此操作将永久删除该用户，是否继续？', '提示', {
		confirmButtonText: '确认',
		cancelButtonText: '取消',
		type: 'warning',
	})
		.then(() => {
			request.delete('/api/user/' + row.id).then((res) => {
				if (res.code == 0) {
					ElMessage.success('删除成功');
				} else {
					ElMessage.error(res.msg);
				}
			});
			setTimeout(() => {
				getTableData();
			}, 500);
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
.user-page {
	.user-panel {
		padding: 18px;
		background: rgba(255, 255, 255, 0.88);
	}
}

.user-hero {
	display: flex;
	justify-content: space-between;
	gap: 16px;
	padding: 24px;
	border-radius: 24px;
	background: linear-gradient(135deg, #173743 0%, #1c6d5d 54%, #2f7898 100%);
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

.user-hero h2 {
	margin: 14px 0 8px;
	font-size: 28px;
}

.user-hero p {
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

.toolbar-row {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	gap: 12px;
}

.search-input {
	width: 280px;
	max-width: 100%;
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

.avatar-card {
	display: flex;
	align-items: center;
	justify-content: center;
}

.avatar-card img {
	width: 54px;
	height: 54px;
	border-radius: 16px;
	object-fit: cover;
	box-shadow: 0 12px 20px rgba(22, 33, 46, 0.12);
}

.role-tag {
	border-radius: 999px;
	padding: 4px 10px;
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
	height: 66px;
}

:deep(.el-input__wrapper) {
	border-radius: 14px;
	background: #f5f8f6;
	box-shadow: inset 0 0 0 1px rgba(106, 128, 115, 0.12) !important;
}

@media (max-width: 992px) {
	.user-hero {
		flex-direction: column;
	}

	.pagination-wrap {
		justify-content: center;
	}
}
</style>

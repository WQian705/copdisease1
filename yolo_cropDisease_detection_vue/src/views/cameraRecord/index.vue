<template>
	<div class="record-page layout-padding">
		<div class="record-panel layout-padding-auto layout-padding-view">
			<section class="record-hero">
				<div>
					<span class="hero-badge">摄像检测记录</span>
					<h2>集中查看实时摄像识别后的处理结果</h2>
					<p>保留原有查询、分页与删除逻辑，只优化列表布局、视频预览卡片和筛选区层次。</p>
				</div>
				<div class="hero-side">
					<span>当前账号</span>
					<strong>{{ userInfos.userName }}</strong>
				</div>
			</section>

			<section class="toolbar-card">
				<div class="toolbar-row">
					<el-input
						v-model="state.tableData.param.search1"
						size="large"
						placeholder="请输入作物类型"
						clearable
						class="search-input"
					/>
					<el-button size="large" type="primary" class="query-button" @click="getTableData()">
						<el-icon><ele-Search /></el-icon>
						查询记录
					</el-button>
				</div>
			</section>

			<section class="table-card">
				<div class="table-head">
					<h3>录制结果列表</h3>
					<p>展示摄像识别视频、模型参数和识别时间。</p>
				</div>
				<el-table :data="state.tableData.data" v-loading="state.tableData.loading" class="record-table">
					<el-table-column prop="num" label="序号" width="90" align="center" />
					<el-table-column prop="outVideo" label="处理结果" width="220" align="center">
						<template #default="scope">
							<div class="video-preview-card">
								<video class="video" preload="auto" controls :key="scope.row.outVideo + uniqueKey">
									<source :src="scope.row.outVideo" type="video/mp4" />
								</video>
							</div>
						</template>
					</el-table-column>
					<el-table-column prop="kind" label="作物种类" align="center" />
					<el-table-column prop="weight" label="识别模型" align="center" />
					<el-table-column prop="conf" label="最小阈值" width="120" align="center" />
					<el-table-column prop="username" label="识别用户" align="center" show-overflow-tooltip />
					<el-table-column prop="startTime" label="识别时间" align="center" show-overflow-tooltip />
					<el-table-column label="操作" width="140" align="center" fixed="right">
						<template #default="scope">
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
	</div>
</template>

<script setup lang="ts" name="systemRole">
import { onMounted, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import request from '/@/utils/request';
import { useUserInfo } from '/@/stores/userInfo';
import { storeToRefs } from 'pinia';

const stores = useUserInfo();
const { userInfos } = storeToRefs(stores);

const state = reactive<SysRoleState>({
	tableData: {
		data: [] as any,
		total: 0,
		loading: false,
		param: {
			search: '',
			search3: '',
			search2: '',
			pageNum: 1,
			pageSize: 10,
		},
	},
});

const uniqueKey = ref(0);

const getTableData = () => {
	state.tableData.loading = true;
	if (userInfos.value.userName != 'admin') {
		state.tableData.param.search = userInfos.value.userName;
	}
	request
		.get('/api/cameraRecords', {
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
				uniqueKey.value++;
			} else {
				ElMessage({
					type: 'error',
					message: res.msg,
				});
			}
		});
};

const onRowDel = (row: any) => {
	ElMessageBox.confirm('此操作将永久删除该记录，是否继续？', '提示', {
		confirmButtonText: '确认',
		cancelButtonText: '取消',
		type: 'warning',
	})
		.then(() => {
			request.delete('/api/cameraRecords/' + row.id).then((res) => {
				if (res.code == 0) {
					ElMessage({
						type: 'success',
						message: '删除成功',
					});
				} else {
					ElMessage({
						type: 'error',
						message: res.msg,
					});
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
.record-page {
	.record-panel {
		padding: 18px;
		background: rgba(255, 255, 255, 0.88);
	}
}

.record-hero {
	display: flex;
	justify-content: space-between;
	gap: 16px;
	padding: 24px;
	border-radius: 24px;
	background: linear-gradient(135deg, #163642 0%, #1d715d 54%, #24759c 100%);
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

.record-hero h2 {
	margin: 14px 0 8px;
	font-size: 28px;
}

.record-hero p {
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
	word-break: break-word;
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
	gap: 12px;
	align-items: center;
}

.search-input {
	width: 280px;
	max-width: 100%;
}

.query-button {
	height: 46px;
	padding: 0 22px;
	border: none;
	border-radius: 16px;
	background: linear-gradient(135deg, #1f6f58 0%, #2f8b70 55%, #2c79a5 100%);
	box-shadow: 0 18px 32px rgba(39, 103, 91, 0.2);
}

.table-head h3 {
	margin: 0 0 6px;
	color: #24384d;
}

.table-head p {
	margin: 0 0 18px;
	color: #7d8a98;
}

.video-preview-card {
	padding: 10px;
	border-radius: 18px;
	background: linear-gradient(180deg, #f8fbf9 0%, #eef4f1 100%);
	box-shadow: inset 0 0 0 1px rgba(86, 115, 126, 0.08);
}

.video {
	width: 100%;
	max-height: 120px;
	border-radius: 12px;
	object-fit: contain;
	background: #0f1720;
}

.pagination-wrap {
	display: flex;
	justify-content: flex-end;
	margin-top: 18px;
}

.record-table {
	:deep(.el-table__row) {
		height: 148px;
	}

	:deep(.el-table__cell) {
		padding: 10px 0;
	}
}

:deep(.el-table) {
	border-radius: 18px;
	overflow: hidden;
}

:deep(.el-table th.el-table__cell) {
	background: #f3f7f5;
	color: #52657a;
}

:deep(.el-select .el-input__wrapper),
:deep(.el-input__wrapper) {
	border-radius: 14px;
	background: #f5f8f6;
	box-shadow: inset 0 0 0 1px rgba(106, 128, 115, 0.12) !important;
}

@media (max-width: 992px) {
	.record-hero {
		flex-direction: column;
	}

	.pagination-wrap {
		justify-content: center;
	}
}
</style>

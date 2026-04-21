<template>
	<div class="page-shell layout-padding">
		<div class="page-panel layout-padding-auto layout-padding-view">
			<section class="page-hero">
				<div>
					<span class="page-badge">图片检测记录</span>
					<h2>识别留痕与结果回看</h2>
					<p>支持按作物类型筛选，保留原有展开详情、删除和分页逻辑。</p>
				</div>
				<div class="hero-tip">
					<span>当前记录</span>
					<strong>{{ state.tableData.total }}</strong>
				</div>
			</section>

			<section class="toolbar-card">
				<div class="toolbar-grid">
					<el-input v-model="state.tableData.param.search1" size="default" placeholder="请输入农作物类型" />
					<div class="toolbar-actions">
						<el-button size="default" type="primary" @click="getTableData()">
							<el-icon><ele-Search /></el-icon>
							查询
						</el-button>
					</div>
				</div>
			</section>

			<section class="table-card">
				<el-table :data="state.tableData.data" v-loading="state.tableData.loading" style="width: 100%">
					<el-table-column type="expand">
						<template #default="props">
							<div class="expand-card">
								<p class="expand-title">详细识别结果</p>
								<el-table :data="props.row.family">
									<el-table-column prop="label" label="识别结果" align="center" />
									<el-table-column prop="confidence" label="置信度" show-overflow-tooltip align="center" />
									<el-table-column prop="startTime" label="识别时间" align="center" />
								</el-table>
							</div>
						</template>
					</el-table-column>
					<el-table-column prop="num" label="序号" width="80" align="center" />
					<el-table-column prop="inputImg" label="原始图片" width="140" align="center">
						<template #default="scope">
							<img :src="scope.row.inputImg" class="record-image" />
						</template>
					</el-table-column>
					<el-table-column prop="outImg" label="预测图片" width="140" align="center">
						<template #default="scope">
							<img :src="scope.row.outImg" class="record-image" />
						</template>
					</el-table-column>
					<el-table-column prop="cropType" label="农作物种类" show-overflow-tooltip align="center"></el-table-column>
					<el-table-column prop="weight" label="识别权重" show-overflow-tooltip align="center"></el-table-column>
					<el-table-column prop="conf" label="最小阈值" show-overflow-tooltip align="center"></el-table-column>
					<el-table-column prop="allTime" label="总用时" show-overflow-tooltip align="center"></el-table-column>
					<el-table-column prop="startTime" label="识别时间" width="180" align="center" />
					<el-table-column prop="username" label="识别用户" show-overflow-tooltip align="center"></el-table-column>
					<el-table-column label="操作" width="90" align="center">
						<template #default="scope">
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
	</div>
</template>

<script setup lang="ts" name="systemRole">
import { reactive, onMounted } from 'vue';
import { ElMessageBox, ElMessage } from 'element-plus';
import request from '/@/utils/request';
import { useUserInfo } from '/@/stores/userInfo';
import { storeToRefs } from 'pinia';

const stores = useUserInfo();
const { userInfos } = storeToRefs(stores);

const state = reactive({
	tableData: {
		data: [] as any,
		total: 0,
		loading: false,
		param: {
			search: '',
			search1: '',
			search2: '',
			pageNum: 1,
			pageSize: 10,
		},
	},
});

const getTableData = () => {
	state.tableData.loading = true;
	if (userInfos.value.userName != 'admin') {
		state.tableData.param.search = userInfos.value.userName;
	}
	request
		.get('/api/imgRecords', {
			params: state.tableData.param,
		})
		.then((res) => {
			if (res.code == 0) {
				state.tableData.data = [];
				setTimeout(() => {
					state.tableData.loading = false;
				}, 500);
				for (let i = 0; i < res.data.records.length; i++) {
					const confidences = JSON.parse(res.data.records[i].confidence);
					const labels = JSON.parse(res.data.records[i].label);
					const transformedData = transformData(res.data.records[i], confidences, labels);
					transformedData['num'] = i + 1;
					state.tableData.data[i] = transformedData;
				}
				state.tableData.total = res.data.total;
			} else {
				ElMessage({ type: 'error', message: res.msg });
			}
		});
};

const transformData = (originalData, confidences, labels) => {
	const family = labels.map((label, index) => ({
		label: label,
		confidence: confidences[index],
		startTime: originalData.startTime,
	}));

	return {
		id: originalData.id,
		inputImg: originalData.inputImg,
		outImg: originalData.outImg,
		cropType: originalData.kind || '-',
		weight: originalData.weight,
		allTime: originalData.allTime,
		conf: originalData.conf,
		startTime: originalData.startTime,
		username: originalData.username,
		family: family,
	};
};

const onRowDel = (row: any) => {
	ElMessageBox.confirm(`此操作将永久删除该信息，是否继续？`, '提示', {
		confirmButtonText: '确认',
		cancelButtonText: '取消',
		type: 'warning',
	})
		.then(() => {
			request.delete('/api/imgRecords/' + row.id).then((res) => {
				if (res.code == 0) {
					ElMessage({ type: 'success', message: '删除成功' });
				} else {
					ElMessage({ type: 'error', message: res.msg });
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
	background: linear-gradient(135deg, #183742 0%, #23615d 50%, #2a6e95 100%);
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
	grid-template-columns: minmax(0, 260px) 1fr;
	gap: 12px;
	align-items: center;
}

.toolbar-actions {
	display: flex;
	justify-content: flex-end;
}

.record-image {
	width: 120px;
	height: 64px;
	object-fit: cover;
	border-radius: 14px;
	box-shadow: 0 8px 16px rgba(31, 52, 84, 0.12);
}

.expand-card {
	padding: 12px;
	border-radius: 18px;
	background: linear-gradient(180deg, #f8fbf9 0%, #f2f7f5 100%);
}

.expand-title {
	margin: 0 0 12px;
	font-size: 16px;
	font-weight: 700;
	color: #294157;
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

:deep(.el-table__expanded-cell) {
	padding: 14px !important;
	background: #fbfdfc;
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

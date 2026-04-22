<template>
	<div class="page-shell layout-padding">
		<div class="page-panel layout-padding-auto layout-padding-view">
			<section class="page-hero">
				<div>
					<span class="page-badge">图片识别记录</span>
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
						<el-button size="default" type="primary" @click="getTableData">查询</el-button>
					</div>
				</div>
			</section>

			<section class="table-card">
				<el-table :data="state.tableData.data" v-loading="state.tableData.loading" style="width: 100%">
					<el-table-column type="expand">
						<template #default="props">
							<div class="expand-card">
								<div class="detail-summary">
									<div class="summary-item">
										<span>识别条目</span>
										<strong>{{ props.row.family.length }}</strong>
									</div>
									<div class="summary-item">
										<span>最高置信度</span>
										<strong>{{ props.row.bestConfidenceText }}</strong>
									</div>
									<div class="summary-item">
										<span>主要识别结果</span>
										<strong>{{ props.row.primaryLabel }}</strong>
									</div>
								</div>
								<p class="expand-title">详细识别结果</p>
								<el-table :data="props.row.family">
									<el-table-column prop="label" label="识别结果" align="center" />
									<el-table-column prop="confidenceText" label="置信度" show-overflow-tooltip align="center" />
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
					<el-table-column prop="cropType" label="农作物种类" show-overflow-tooltip align="center" />
					<el-table-column prop="weight" label="识别权重" show-overflow-tooltip align="center" />
					<el-table-column prop="conf" label="最小阈值" show-overflow-tooltip align="center" />
					<el-table-column prop="allTime" label="总用时" show-overflow-tooltip align="center" />
					<el-table-column prop="startTime" label="识别时间" width="180" align="center" />
					<el-table-column prop="username" label="识别用户" show-overflow-tooltip align="center" />
					<el-table-column label="操作" width="160" align="center">
						<template #default="scope">
							<el-button size="small" text type="primary" @click="show(scope.row)">查看详情</el-button>
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
					v-model:page-size="state.tableData.param.pageSize"
					background
					layout="total, sizes, prev, pager, next, jumper"
					:total="state.tableData.total"
				/>
			</section>
		</div>
	</div>
</template>

<script setup lang="ts" name="imgRecord">
import { onMounted, reactive } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import request from '/@/utils/request';
import { useUserInfo } from '/@/stores/userInfo';
import { storeToRefs } from 'pinia';
import { router } from '/@/router/index';
import { resolveFileUrl } from '/@/utils/serviceUrl';

const stores = useUserInfo();
const { userInfos } = storeToRefs(stores);

const state = reactive({
	tableData: {
		data: [] as any[],
		total: 0,
		loading: false,
		param: {
			search: '',
			search1: '',
			search2: '',
			search3: '',
			pageNum: 1,
			pageSize: 10,
		},
	},
});

const isSuccessCode = (code: string | number) => String(code) === '0';

const normalizeArray = (value: string | string[]) => {
	if (Array.isArray(value)) return value;
	if (!value) return [];
	try {
		return JSON.parse(value);
	} catch {
		return [value];
	}
};

const normalizeConfidenceText = (value: string | number) => {
	const numericValue = Number(String(value).replace(/[%\[\]"]/g, ''));
	if (Number.isFinite(numericValue)) {
		return `${numericValue.toFixed(2)}%`;
	}
	return String(value || '-');
};

const transformData = (originalData: any) => {
	const confidences = normalizeArray(originalData.confidence);
	const labels = normalizeArray(originalData.label);
	const family = labels.map((label: string, index: number) => ({
		label,
		confidence: confidences[index] || '-',
		confidenceText: normalizeConfidenceText(confidences[index] || '-'),
		startTime: originalData.startTime,
	}));
	const sortedFamily = [...family].sort((a, b) => {
		const aValue = Number(String(a.confidence).replace(/[%\[\]"]/g, ''));
		const bValue = Number(String(b.confidence).replace(/[%\[\]"]/g, ''));
		return (Number.isFinite(bValue) ? bValue : -1) - (Number.isFinite(aValue) ? aValue : -1);
	});
	const primaryResult = sortedFamily[0];

	return {
		id: originalData.id,
		inputImg: resolveFileUrl(originalData.inputImg),
		outImg: resolveFileUrl(originalData.outImg),
		cropType: originalData.kind || '-',
		weight: originalData.weight || '-',
		allTime: originalData.allTime || '-',
		conf: originalData.conf || '-',
		startTime: originalData.startTime || '-',
		username: originalData.username || '-',
		family,
		primaryLabel: primaryResult?.label || '暂无结果',
		bestConfidenceText: primaryResult?.confidenceText || '-',
	};
};

const show = (row: any) => {
	window.open(
		router.resolve({
			name: 'imgShow',
			query: { id: String(row.id), mode: 'img' },
		}).href
	);
};

const getTableData = () => {
	state.tableData.loading = true;
	if (userInfos.value.userName !== 'admin') {
		state.tableData.param.search = userInfos.value.userName;
	}
	request
		.get('/api/imgRecords', {
			params: state.tableData.param,
		})
		.then((res) => {
			state.tableData.loading = false;
			if (!isSuccessCode(res.code)) {
				ElMessage.error(res.msg);
				return;
			}
			state.tableData.data = (res.data.records || []).map((item: any, index: number) => ({
				...transformData(item),
				num: index + 1,
			}));
			state.tableData.total = res.data.total || 0;
		})
		.catch(() => {
			state.tableData.loading = false;
		});
};

const onRowDel = (row: any) => {
	ElMessageBox.confirm('此操作将永久删除该记录，是否继续？', '提示', {
		confirmButtonText: '确认',
		cancelButtonText: '取消',
		type: 'warning',
	})
		.then(() => {
			request.delete('/api/imgRecords/' + row.id).then((res) => {
				if (isSuccessCode(res.code)) {
					ElMessage.success('删除成功');
					getTableData();
				} else {
					ElMessage.error(res.msg);
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

.detail-summary {
	display: grid;
	grid-template-columns: repeat(3, minmax(0, 1fr));
	gap: 12px;
	margin-bottom: 14px;
}

.summary-item {
	padding: 12px 14px;
	border-radius: 14px;
	background: rgba(255, 255, 255, 0.72);
	box-shadow: inset 0 0 0 1px rgba(106, 128, 115, 0.12);
}

.summary-item span {
	display: block;
	color: #6b7c8d;
	font-size: 13px;
}

.summary-item strong {
	display: block;
	margin-top: 8px;
	color: #23465f;
	font-size: 18px;
	word-break: break-word;
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
	.page-hero {
		flex-direction: column;
	}

	.toolbar-grid {
		grid-template-columns: 1fr;
	}

	.detail-summary {
		grid-template-columns: 1fr;
	}

	.toolbar-actions,
	.table-pagination {
		justify-content: flex-start;
	}
}
</style>

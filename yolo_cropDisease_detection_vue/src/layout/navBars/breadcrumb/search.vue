<template>
	<div class="layout-search-dialog">
		<el-dialog v-model="state.isShowSearch" destroy-on-close :show-close="false" class="search-dialog-shell">
			<template #footer>
				<div class="search-panel">
					<div class="search-head">
						<div>
							<span class="search-tag">全局搜索</span>
							<h3>快速定位菜单与页面</h3>
						</div>
					</div>
					<el-autocomplete
						v-model="state.menuQuery"
						:fetch-suggestions="menuSearch"
						:placeholder="$t('message.user.searchPlaceholder')"
						ref="layoutMenuAutocompleteRef"
						@select="onHandleSelect"
						:fit-input-width="true"
					>
						<template #prefix>
							<el-icon class="el-input__icon">
								<ele-Search />
							</el-icon>
						</template>
						<template #default="{ item }">
							<div class="search-result-item">
								<SvgIcon :name="item.meta.icon" class="mr5" />
								{{ $t(item.meta.title) }}
							</div>
						</template>
					</el-autocomplete>
				</div>
			</template>
		</el-dialog>
	</div>
</template>

<script setup lang="ts" name="layoutBreadcrumbSearch">
import { reactive, ref, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { useTagsViewRoutes } from '/@/stores/tagsViewRoutes';

const storesTagsViewRoutes = useTagsViewRoutes();
const { tagsViewRoutes } = storeToRefs(storesTagsViewRoutes);
const layoutMenuAutocompleteRef = ref();
const { t } = useI18n();
const router = useRouter();
const state = reactive<SearchState>({
	isShowSearch: false,
	menuQuery: '',
	tagsViewList: [],
});

const openSearch = () => {
	state.menuQuery = '';
	state.isShowSearch = true;
	initTageView();
	nextTick(() => {
		setTimeout(() => {
			layoutMenuAutocompleteRef.value.focus();
		});
	});
};

const closeSearch = () => {
	state.isShowSearch = false;
};

const menuSearch = (queryString: string, cb: Function) => {
	let results = queryString ? state.tagsViewList.filter(createFilter(queryString)) : state.tagsViewList;
	cb(results);
};

const createFilter = (queryString: string) => {
	return (restaurant: RouteItem) => {
		return (
			restaurant.path.toLowerCase().indexOf(queryString.toLowerCase()) > -1 ||
			restaurant.meta!.title!.toLowerCase().indexOf(queryString.toLowerCase()) > -1 ||
			t(restaurant.meta!.title!).indexOf(queryString.toLowerCase()) > -1
		);
	};
};

const initTageView = () => {
	if (state.tagsViewList.length > 0) return false;
	tagsViewRoutes.value.map((v: RouteItem) => {
		if (!v.meta?.isHide) state.tagsViewList.push({ ...v });
	});
};

const onHandleSelect = (item: RouteItem) => {
	let { path, redirect } = item;
	if (item.meta?.isLink && !item.meta?.isIframe) window.open(item.meta?.isLink);
	else if (redirect) router.push(redirect);
	else router.push(path);
	closeSearch();
};

defineExpose({
	openSearch,
});
</script>

<style scoped lang="scss">
.layout-search-dialog {
	position: relative;
}

:deep(.search-dialog-shell .el-dialog) {
	width: min(720px, calc(100vw - 32px));
	margin-top: 12vh;
	border-radius: 28px;
	overflow: hidden;
	background: linear-gradient(180deg, #ffffff 0%, #f7faf8 100%);
	box-shadow: 0 24px 56px rgba(27, 45, 72, 0.12);
}

:deep(.search-dialog-shell .el-dialog__header),
:deep(.search-dialog-shell .el-dialog__body) {
	display: none;
}

:deep(.search-dialog-shell .el-dialog__footer) {
	padding: 0;
}

.search-panel {
	padding: 22px;
}

.search-head {
	margin-bottom: 16px;
}

.search-tag {
	display: inline-flex;
	padding: 6px 12px;
	border-radius: 999px;
	background: rgba(31, 111, 88, 0.08);
	color: #1f6f58;
	font-size: 12px;
	letter-spacing: 0.12em;
}

.search-head h3 {
	margin: 14px 0 0;
	color: #24384d;
	font-size: 24px;
}

:deep(.el-autocomplete) {
	width: 100%;
}

:deep(.el-autocomplete .el-input__wrapper) {
	border-radius: 18px;
	min-height: 56px;
	background: #f5f8f6;
	box-shadow: inset 0 0 0 1px rgba(106, 128, 115, 0.12) !important;
}

.search-result-item {
	display: flex;
	align-items: center;
	gap: 8px;
	color: #355063;
}
</style>

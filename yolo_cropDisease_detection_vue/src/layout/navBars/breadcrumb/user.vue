<template>
	<div class="layout-navbars-breadcrumb-user" :style="{ flex: layoutUserFlexNum }">
		<el-dropdown :show-timeout="70" :hide-timeout="50" trigger="click" @command="onComponentSizeChange" class="custom-dropdown">
			<div class="layout-navbars-breadcrumb-user-icon">
				<i class="iconfont icon-ziti" :title="$t('message.user.title0')"></i>
			</div>
			<template #dropdown>
				<el-dropdown-menu>
					<el-dropdown-item command="large" :disabled="state.disabledSize === 'large'">{{ $t('message.user.dropdownLarge') }}</el-dropdown-item>
					<el-dropdown-item command="default" :disabled="state.disabledSize === 'default'">{{ $t('message.user.dropdownDefault') }}</el-dropdown-item>
					<el-dropdown-item command="small" :disabled="state.disabledSize === 'small'">{{ $t('message.user.dropdownSmall') }}</el-dropdown-item>
				</el-dropdown-menu>
			</template>
		</el-dropdown>
		<div class="layout-navbars-breadcrumb-user-icon" @click="onSearchClick">
			<el-icon :title="$t('message.user.title2')">
				<ele-Search />
			</el-icon>
		</div>
		<div class="layout-navbars-breadcrumb-user-icon" @click="onLayoutSetingClick">
			<i class="icon-skin iconfont" :title="$t('message.user.title3')"></i>
		</div>
		<div class="layout-navbars-breadcrumb-user-icon" @click="onScreenfullClick">
			<i
				class="iconfont"
				:title="state.isScreenfull ? $t('message.user.title6') : $t('message.user.title5')"
				:class="!state.isScreenfull ? 'icon-fullscreen' : 'icon-tuichuquanping'"
			></i>
		</div>
		<el-dropdown :show-timeout="70" :hide-timeout="50" @command="onHandleCommandClick" class="custom-dropdown">
			<span class="layout-navbars-breadcrumb-user-link">
				<img :src="state.img || fallbackAvatar" class="layout-navbars-breadcrumb-user-link-photo" />
				<span class="layout-navbars-breadcrumb-user-link-name">{{ username }}</span>
				<el-icon class="el-icon--right">
					<ele-ArrowDown />
				</el-icon>
			</span>
			<template #dropdown>
				<el-dropdown-menu>
					<el-dropdown-item command="/">{{ $t('message.user.dropdown1') }}</el-dropdown-item>
					<el-dropdown-item divided command="logOut">{{ $t('message.user.dropdown5') }}</el-dropdown-item>
				</el-dropdown-menu>
			</template>
		</el-dropdown>
		<Search ref="searchRef" />
	</div>
</template>

<script setup lang="ts" name="layoutBreadcrumbUser">
import { defineAsyncComponent, ref, computed, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessageBox, ElMessage } from 'element-plus';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { useUserInfo } from '/@/stores/userInfo';
import { useThemeConfig } from '/@/stores/themeConfig';
import other from '/@/utils/other';
import request from '/@/utils/request';
import { Session, Local } from '/@/utils/storage';
import screenfull from 'screenfull';
import mittBus from '/@/utils/mitt';
import fallbackAvatar from '/@/assets/logo.png';

const Search = defineAsyncComponent(() => import('/@/layout/navBars/breadcrumb/search.vue'));

const { locale, t } = useI18n();
const router = useRouter();
const stores = useUserInfo();
const storesThemeConfig = useThemeConfig();
const { userInfos } = storeToRefs(stores);
const { themeConfig } = storeToRefs(storesThemeConfig);
const searchRef = ref();
const state = reactive({
	img: '',
	isScreenfull: false,
	disabledI18n: 'zh-cn',
	disabledSize: 'large',
});

const username = computed(() => userInfos.value.userName || '未登录用户');

const layoutUserFlexNum = computed(() => {
	let num: string | number = '';
	const { layout, isClassicSplitMenu } = themeConfig.value;
	const layoutArr: string[] = ['defaults', 'columns'];
	if (layoutArr.includes(layout) || (layout === 'classic' && !isClassicSplitMenu)) num = '1';
	else num = '';
	return num;
});

const onLayoutSetingClick = () => {
	mittBus.emit('openSetingsDrawer');
};

const onHandleCommandClick = (path: string) => {
	if (path === 'logOut') {
		ElMessageBox({
			closeOnClickModal: false,
			closeOnPressEscape: false,
			title: t('message.user.logOutTitle'),
			message: t('message.user.logOutMessage'),
			showCancelButton: true,
			confirmButtonText: t('message.user.logOutConfirm'),
			cancelButtonText: t('message.user.logOutCancel'),
			buttonSize: 'default',
			beforeClose: (action, instance, done) => {
				if (action === 'confirm') {
					instance.confirmButtonLoading = true;
					instance.confirmButtonText = t('message.user.logOutExit');
					setTimeout(() => {
						done();
						setTimeout(() => {
							instance.confirmButtonLoading = false;
						}, 300);
					}, 700);
				} else {
					done();
				}
			},
		})
			.then(async () => {
				Session.clear();
				window.location.reload();
			})
			.catch(() => {});
	} else {
		router.push(path);
	}
};

const onSearchClick = () => {
	searchRef.value.openSearch();
};

const onComponentSizeChange = (size: string) => {
	Local.remove('themeConfig');
	themeConfig.value.globalComponentSize = size;
	Local.set('themeConfig', themeConfig.value);
	initI18nOrSize('globalComponentSize', 'disabledSize');
	window.location.reload();
};

const onScreenfullClick = () => {
	if (!screenfull.isEnabled) {
		ElMessage.warning('暂不支持全屏');
		return false;
	}
	screenfull.toggle();
	screenfull.on('change', () => {
		state.isScreenfull = !!screenfull.isFullscreen;
	});
};

const onLanguageChange = (lang: string) => {
	Local.remove('themeConfig');
	themeConfig.value.globalI18n = lang;
	Local.set('themeConfig', themeConfig.value);
	locale.value = lang;
	other.useTitle();
	initI18nOrSize('globalI18n', 'disabledI18n');
};

const initI18nOrSize = (value: string, attr: string) => {
	state[attr] = Local.get('themeConfig')[value];
};

const getTableData = () => {
	request.get('/api/user/' + userInfos.value.userName).then((res) => {
		if (res.code == 0) {
			state.img = res.data.avatar;
		} else {
			ElMessage({
				type: 'error',
				message: res.msg,
			});
		}
	});
};

onMounted(() => {
	getTableData();
	if (Local.get('themeConfig')) {
		initI18nOrSize('globalComponentSize', 'disabledSize');
		initI18nOrSize('globalI18n', 'disabledI18n');
	}
});
</script>

<style scoped lang="scss">
.layout-navbars-breadcrumb-user {
	display: flex;
	align-items: center;
	justify-content: flex-end;
	gap: 8px;

	&-link {
		height: 48px;
		display: flex;
		align-items: center;
		padding: 0 16px 0 8px;
		border-radius: 16px;
		background: linear-gradient(135deg, #f7faf8 0%, #edf4fb 100%);
		box-shadow: inset 0 0 0 1px rgba(211, 221, 215, 0.9);
		color: #31485f;
		font-weight: 600;
		white-space: nowrap;

		&-photo {
			width: 36px;
			height: 36px;
			border-radius: 100%;
			margin-right: 10px;
			object-fit: cover;
			box-shadow: 0 8px 16px rgba(30, 70, 55, 0.12);
		}

		&-name {
			max-width: 96px;
			overflow: hidden;
			text-overflow: ellipsis;
		}
	}

	&-icon {
		cursor: pointer;
		color: #3a5569 !important;
		height: 44px;
		width: 44px;
		border-radius: 14px;
		background: linear-gradient(135deg, #f5faf6 0%, #edf4fb 100%);
		box-shadow: inset 0 0 0 1px rgba(212, 222, 216, 0.9);
		display: flex;
		align-items: center;
		justify-content: center;
		transition: background 0.2s ease, transform 0.2s ease, color 0.2s ease;

		&:hover {
			background: linear-gradient(135deg, rgba(42, 123, 97, 0.12), rgba(43, 121, 165, 0.12)) !important;
			color: #1e7259 !important;
			transform: translateY(-1px);
		}

		i {
			font-size: 16px;
		}
	}

	:deep(.el-dropdown) {
		color: #31485f;
	}
}

.custom-dropdown {
	.el-dropdown-menu {
		background-color: #ffffff;
		border: 1px solid #dfe7e2;
		border-radius: 14px;
		box-shadow: 0 18px 30px rgba(31, 52, 84, 0.12);
		overflow: hidden;
		padding: 5px;
	}

	.el-dropdown-item {
		color: #000000 !important;
		padding: 12px 20px;
		transition: background-color 0.3s ease;
		display: flex;
		align-items: center;
		justify-content: center;

		&:hover {
			background-color: #f3f8f5 !important;
		}
	}
}
</style>

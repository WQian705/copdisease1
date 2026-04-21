<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElCard } from 'element-plus'
import 'element-plus/dist/index.css'

const router = useRouter()

const statistics = ref([
  { label: '平台用户', value: 42, unit: '人', icon: 'icon-yh' },
  { label: '温室总数', value: 9, unit: '座', icon: 'icon-znws' },
  { label: '病害样本', value: 141, unit: '条', icon: 'icon-bingchonghai-1haichong' },
  { label: '累计产量', value: 1232, unit: 'kg', icon: 'icon-cc' }
])

const weatherInfo = ref({
  date: '',
  weekday: '',
  city: '北京',
  temperature: '--',
  weather: '数据加载中',
  wind: '--',
  airQuality: '--',
  notice: '正在同步天气信息，请稍候。'
})

const quickApps = [
  { title: '病虫害库', desc: '快速查看作物病害资料', icon: 'icon-bingchonghai-1haichong', path: '/infoDisease' },
  { title: '智能助手', desc: '辅助问答与诊断建议', icon: 'icon-znwd', path: '/smartChat' },
  { title: '图片检测', desc: '上传图片识别病害', icon: 'icon-tpjc', path: '/imgPredict' },
  { title: '图片记录', desc: '查看历史图片检测结果', icon: 'icon-tpjl', path: '/imgRecord' },
  { title: '视频检测', desc: '上传视频进行识别', icon: 'icon-spjc', path: '/videoPredict' },
  { title: '视频记录', desc: '浏览视频检测留痕', icon: 'icon-spjl', path: '/videoRecord' }
]

const cropTypes = ref([
  { name: '1号温室', crop: '玉米', status: '生长良好', plantCount: 350, diseaseCount: 20 },
  { name: '2号温室', crop: '水稻', status: '生长良好', plantCount: 400, diseaseCount: 15 },
  { name: '3号温室', crop: '小麦', status: '需要关注', plantCount: 350, diseaseCount: 18 },
  { name: '4号温室', crop: '马铃薯', status: '生长良好', plantCount: 250, diseaseCount: 12 },
  { name: '5号温室', crop: '棉花', status: '生长良好', plantCount: 300, diseaseCount: 16 },
  { name: '6号温室', crop: '苹果', status: '需要关注', plantCount: 8, diseaseCount: 14 },
  { name: '7号温室', crop: '葡萄', status: '生长良好', plantCount: 300, diseaseCount: 17 },
  { name: '8号温室', crop: '番茄', status: '生长良好', plantCount: 300, diseaseCount: 14 },
  { name: '9号温室', crop: '草莓', status: '生长良好', plantCount: 300, diseaseCount: 15 }
])

const agricultureLinks = ref([
  { name: '中国农村网', url: 'https://www.crnews.net/', icon: 'icon-znws' },
  { name: '中国农业网', url: 'https://www.zgny.com/', icon: 'icon-cc' },
  { name: '农业气象', url: 'http://www.nmc.cn/publish/agro/soil-moisture-monitoring-10cm.html', icon: 'icon-spjc' },
  { name: '病虫害服务站', url: 'https://farm.sino-eco.com/website/bingchonghai/', icon: 'icon-bingchonghai-1haichong' },
  { name: '国家农业数据中心', url: 'https://www.agridata.cn/', icon: 'icon-tpjl' },
  { name: '病虫害研究图库', url: 'http://www.icgroupcas.cn/website_bchtk/zhenduan.aspx', icon: 'icon-tpjc' },
  { name: '中国害虫防治网', url: 'http://zghcfzw.com/', icon: 'icon-znwd' },
  { name: '中国农科院', url: 'https://www.caas.cn/', icon: 'icon-yh' }
])

const overview = computed(() => {
  const warningCount = cropTypes.value.filter((item) => item.status === '需要关注').length
  const totalPlants = cropTypes.value.reduce((sum, item) => sum + item.plantCount, 0)
  return {
    warningCount,
    totalPlants
  }
})

const fetchWeatherData = async () => {
  try {
    const appid = '11569196'
    const appsecret = 'CJ5gx1ZS'
    const cityid = '101010100'
    const url = `http://v1.yiketianqi.com/api?unescape=1&version=v61&appid=${appid}&appsecret=${appsecret}&cityid=${cityid}`

    const response = await fetch(url)
    const data = await response.json()

    weatherInfo.value = {
      date: data.date || '',
      weekday: data.week || '',
      city: data.city || '北京',
      temperature: data.tem ? `${data.tem}°C` : '--',
      weather: data.wea || '暂无天气数据',
      wind: data.win && data.win_speed ? `${data.win} ${data.win_speed}` : data.win || '--',
      airQuality: data.air_level && data.air ? `${data.air_level} / AQI ${data.air}` : '--',
      notice: data.air_tips || '暂无特别提示'
    }
  } catch (error) {
    console.error('获取天气数据失败:', error)
    weatherInfo.value.notice = '天气服务暂时不可用，请稍后重试。'
  }
}

const goTo = (path: string) => {
  router.push(path)
}

const getStatusClass = (status: string) => {
  return status === '需要关注' ? 'is-warning' : 'is-good'
}

onMounted(() => {
  fetchWeatherData()
})
</script>

<template>
  <div class="home-page">
    <section class="hero-panel">
      <div class="hero-copy">
        <span class="hero-tag">智慧农业监测中心</span>
        <h1>作物病害检测与温室管理一体化看板</h1>
        <p>
          首页聚合常用入口、环境概览与天气信息，方便你直接进入图片、视频和病害数据模块。
        </p>
        <div class="hero-actions">
          <button class="hero-action primary" @click="goTo('/imgPredict')">开始图片检测</button>
          <button class="hero-action secondary" @click="goTo('/videoPredict')">进入视频检测</button>
        </div>
      </div>
      <div class="hero-metrics">
        <div class="metric-card glass">
          <span>重点关注温室</span>
          <strong>{{ overview.warningCount }}</strong>
          <small>当前需要重点巡查</small>
        </div>
        <div class="metric-card solid">
          <span>作物总株数</span>
          <strong>{{ overview.totalPlants }}</strong>
          <small>已纳入首页统计</small>
        </div>
      </div>
    </section>

    <section class="statistics-grid">
      <div v-for="item in statistics" :key="item.label" class="stat-card">
        <div class="stat-icon">
          <i class="iconfontjs" :class="item.icon"></i>
        </div>
        <div class="stat-content">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
          <small>{{ item.unit }}</small>
        </div>
      </div>
    </section>

    <section class="content-grid">
      <ElCard class="panel-card notice-card" shadow="never">
        <template #header>
          <div class="panel-header">
            <div>
              <span class="panel-title">平台公告</span>
              <p class="panel-subtitle">保持简洁提示，不干扰主要功能使用。</p>
            </div>
          </div>
        </template>
        <div class="notice-list">
          <div class="notice-item">
            <span class="dot"></span>
            <p>检测前请尽量保证图片主体清晰、光照充足，以提升识别效果。</p>
          </div>
          <div class="notice-item">
            <span class="dot"></span>
            <p>视频与图片检测记录可在对应历史模块中回看，不影响原有接口流程。</p>
          </div>
          <div class="notice-item">
            <span class="dot"></span>
            <p>若温室状态显示“需要关注”，建议优先进入病害库与检测模块复核。</p>
          </div>
        </div>
      </ElCard>

      <ElCard class="panel-card apps-card" shadow="never">
        <template #header>
          <div class="panel-header">
            <div>
              <span class="panel-title">常用应用</span>
              <p class="panel-subtitle">保留原有模块入口，只优化入口样式。</p>
            </div>
          </div>
        </template>
        <div class="apps-grid">
          <button v-for="app in quickApps" :key="app.path" class="app-item" @click="goTo(app.path)">
            <div class="app-item__icon">
              <i class="iconfontjs" :class="app.icon"></i>
            </div>
            <div class="app-item__content">
              <strong>{{ app.title }}</strong>
              <span>{{ app.desc }}</span>
            </div>
          </button>
        </div>
      </ElCard>

      <ElCard class="panel-card weather-card" shadow="never">
        <template #header>
          <div class="panel-header">
            <div>
              <span class="panel-title">天气预报显示</span>
              <p class="panel-subtitle">天气服务已更新为你提供的新密钥配置。</p>
            </div>
          </div>
        </template>
        <div class="weather-top">
          <div>
            <div class="weather-city">{{ weatherInfo.city }}</div>
            <div class="weather-date">{{ weatherInfo.date }} {{ weatherInfo.weekday }}</div>
          </div>
          <div class="weather-temp">{{ weatherInfo.temperature }}</div>
        </div>
        <div class="weather-summary">{{ weatherInfo.weather }}</div>
        <div class="weather-grid">
          <div class="weather-pill">
            <span>风况</span>
            <strong>{{ weatherInfo.wind }}</strong>
          </div>
          <div class="weather-pill">
            <span>空气质量</span>
            <strong>{{ weatherInfo.airQuality }}</strong>
          </div>
        </div>
        <div class="weather-notice">{{ weatherInfo.notice }}</div>
      </ElCard>
    </section>

    <section class="bottom-grid">
      <ElCard class="panel-card crop-card" shadow="never">
        <template #header>
          <div class="panel-header">
            <div>
              <span class="panel-title">温室作物概览</span>
              <p class="panel-subtitle">展示已有温室状态，不新增业务字段。</p>
            </div>
          </div>
        </template>
        <div class="crop-grid">
          <div v-for="item in cropTypes" :key="item.name" class="crop-item">
            <div class="crop-item__header">
              <strong>{{ item.name }}</strong>
              <span class="crop-chip" :class="getStatusClass(item.status)">{{ item.status }}</span>
            </div>
            <div class="crop-item__name">{{ item.crop }}</div>
            <div class="crop-item__meta">
              <span>种植数量 {{ item.plantCount }}</span>
              <span>病害数量 {{ item.diseaseCount }}</span>
            </div>
          </div>
        </div>
      </ElCard>

      <ElCard class="panel-card links-card" shadow="never">
        <template #header>
          <div class="panel-header">
            <div>
              <span class="panel-title">农业相关链接</span>
              <p class="panel-subtitle">外部资料入口做轻量整理，便于查阅。</p>
            </div>
          </div>
        </template>
        <div class="links-grid">
          <a
            v-for="link in agricultureLinks"
            :key="link.url"
            :href="link.url"
            target="_blank"
            rel="noreferrer"
            class="link-item"
          >
            <i class="iconfontjs" :class="link.icon"></i>
            <span>{{ link.name }}</span>
          </a>
        </div>
      </ElCard>
    </section>
  </div>
</template>

<style scoped lang="scss">
.home-page {
  min-height: 100vh;
  padding: 24px;
  background:
    radial-gradient(circle at top left, rgba(65, 184, 131, 0.18), transparent 30%),
    radial-gradient(circle at top right, rgba(28, 126, 214, 0.18), transparent 24%),
    linear-gradient(180deg, #eef7f2 0%, #f7fbff 44%, #f4f7fb 100%);
}

.hero-panel {
  display: grid;
  grid-template-columns: minmax(0, 1.8fr) minmax(280px, 0.9fr);
  gap: 20px;
  margin-bottom: 20px;
  padding: 28px;
  border-radius: 28px;
  background: linear-gradient(135deg, #123c2f 0%, #1d604d 52%, #2b7c64 100%);
  color: #fff;
  box-shadow: 0 22px 50px rgba(18, 60, 47, 0.2);
}

.hero-copy h1 {
  margin: 12px 0 14px;
  font-size: 32px;
  line-height: 1.25;
  letter-spacing: 0.02em;
}

.hero-copy p {
  max-width: 620px;
  color: rgba(255, 255, 255, 0.82);
  line-height: 1.8;
  font-size: 14px;
}

.hero-tag {
  display: inline-flex;
  align-items: center;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  font-size: 13px;
  letter-spacing: 0.08em;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 24px;
}

.hero-action {
  border: none;
  border-radius: 14px;
  padding: 12px 18px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.hero-action:hover {
  transform: translateY(-2px);
}

.hero-action.primary {
  background: #ffffff;
  color: #174637;
  box-shadow: 0 16px 30px rgba(255, 255, 255, 0.18);
}

.hero-action.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.hero-metrics {
  display: grid;
  gap: 14px;
}

.metric-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 138px;
  padding: 20px;
  border-radius: 24px;
}

.metric-card span,
.metric-card small {
  color: rgba(255, 255, 255, 0.72);
}

.metric-card strong {
  margin: 10px 0;
  font-size: 42px;
  line-height: 1;
}

.metric-card.glass {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(18px);
}

.metric-card.solid {
  background: linear-gradient(145deg, #f9c96b 0%, #f4aa3b 100%);
  color: #3f2600;
}

.metric-card.solid span,
.metric-card.solid small {
  color: rgba(63, 38, 0, 0.78);
}

.statistics-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card,
.panel-card {
  border: none;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.86);
  box-shadow: 0 18px 35px rgba(31, 52, 84, 0.08);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
}

.stat-icon {
  width: 54px;
  height: 54px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e3f5ea 0%, #dfeffd 100%);
  color: #1d6f59;
}

.stat-icon i {
  font-size: 24px;
}

.stat-content {
  display: grid;
  gap: 4px;
}

.stat-content span {
  color: #66758a;
  font-size: 13px;
}

.stat-content strong {
  color: #1f2d3d;
  font-size: 28px;
  line-height: 1;
}

.stat-content small {
  color: #8a96a8;
  font-size: 12px;
}

.content-grid {
  display: grid;
  grid-template-columns: 1.15fr 1.25fr 0.9fr;
  gap: 16px;
  margin-bottom: 20px;
}

.bottom-grid {
  display: grid;
  grid-template-columns: 1.4fr 0.9fr;
  gap: 16px;
}

:deep(.el-card__header) {
  padding: 22px 22px 0;
  border-bottom: none;
}

:deep(.el-card__body) {
  padding: 18px 22px 22px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.panel-title {
  display: block;
  color: #17324d;
  font-size: 18px;
  font-weight: 700;
}

.panel-subtitle {
  margin-top: 6px;
  color: #7f8a9d;
  font-size: 13px;
  line-height: 1.6;
}

.notice-list {
  display: grid;
  gap: 14px;
}

.notice-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 14px 16px;
  border-radius: 18px;
  background: linear-gradient(135deg, #f8fbf8 0%, #f5f8fd 100%);
}

.notice-item p {
  color: #4d5b6b;
  line-height: 1.8;
  font-size: 14px;
}

.dot {
  width: 10px;
  height: 10px;
  margin-top: 8px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2ea86f 0%, #5db2ff 100%);
  box-shadow: 0 0 0 6px rgba(93, 178, 255, 0.08);
  flex-shrink: 0;
}

.apps-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.app-item {
  border: none;
  width: 100%;
  padding: 16px;
  display: flex;
  gap: 12px;
  align-items: center;
  border-radius: 18px;
  background: linear-gradient(135deg, #f7fbff 0%, #eef8f2 100%);
  cursor: pointer;
  text-align: left;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.app-item:hover,
.link-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 26px rgba(53, 92, 145, 0.12);
}

.app-item__icon {
  width: 46px;
  height: 46px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  color: #2a7c61;
  box-shadow: inset 0 0 0 1px rgba(42, 124, 97, 0.08);
}

.app-item__icon i {
  font-size: 22px;
}

.app-item__content {
  display: grid;
  gap: 4px;
}

.app-item__content strong {
  color: #1f2d3d;
  font-size: 15px;
}

.app-item__content span {
  color: #7b8798;
  font-size: 12px;
  line-height: 1.5;
}

.weather-card {
  background: linear-gradient(180deg, #163f60 0%, #275d86 100%);
}

.weather-card .panel-title,
.weather-card .panel-subtitle,
.weather-city,
.weather-date,
.weather-temp,
.weather-summary,
.weather-pill span,
.weather-pill strong,
.weather-notice {
  color: #fff;
}

.weather-card .panel-subtitle {
  color: rgba(255, 255, 255, 0.72);
}

.weather-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.weather-city {
  font-size: 28px;
  font-weight: 700;
}

.weather-date {
  margin-top: 8px;
  color: rgba(255, 255, 255, 0.78);
}

.weather-temp {
  font-size: 38px;
  font-weight: 700;
  line-height: 1;
}

.weather-summary {
  margin: 18px 0 14px;
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
}

.weather-grid {
  display: grid;
  gap: 10px;
  margin-bottom: 14px;
}

.weather-pill {
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.12);
}

.weather-pill span {
  display: block;
  margin-bottom: 6px;
  color: rgba(255, 255, 255, 0.68);
  font-size: 12px;
}

.weather-pill strong {
  font-size: 14px;
  line-height: 1.6;
}

.weather-notice {
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.08);
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.85);
}

.crop-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.crop-item {
  padding: 16px;
  border-radius: 18px;
  background: linear-gradient(135deg, #fbfcfd 0%, #f2f7f4 100%);
  border: 1px solid rgba(78, 114, 142, 0.08);
}

.crop-item__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.crop-item__header strong {
  color: #203145;
  font-size: 15px;
}

.crop-chip {
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.crop-chip.is-good {
  color: #19794b;
  background: rgba(35, 181, 112, 0.14);
}

.crop-chip.is-warning {
  color: #ad6a00;
  background: rgba(248, 181, 0, 0.18);
}

.crop-item__name {
  margin: 14px 0 12px;
  color: #5f6e80;
  font-size: 14px;
}

.crop-item__meta {
  display: grid;
  gap: 6px;
  color: #7f8a9d;
  font-size: 13px;
}

.links-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.link-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px 16px;
  border-radius: 18px;
  background: linear-gradient(135deg, #f8fbff 0%, #f4fbf7 100%);
  text-decoration: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.link-item i {
  display: flex;
  width: 40px;
  height: 40px;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  background: #fff;
  color: #1d7b60;
  font-size: 18px;
}

.link-item span {
  color: #364659;
  line-height: 1.5;
  font-size: 14px;
}

@media (max-width: 1400px) {
  .content-grid,
  .bottom-grid,
  .hero-panel {
    grid-template-columns: 1fr;
  }

  .crop-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 992px) {
  .statistics-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .apps-grid,
  .links-grid,
  .crop-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .home-page {
    padding: 16px;
  }

  .hero-panel {
    padding: 22px;
    border-radius: 22px;
  }

  .hero-copy h1 {
    font-size: 26px;
  }

  .statistics-grid {
    grid-template-columns: 1fr;
  }

  .weather-top,
  .crop-item__header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>

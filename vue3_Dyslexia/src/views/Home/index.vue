<script setup>
import { ref, onUnmounted, onMounted } from 'vue'
import { useRouter } from 'vue-router' // 新增：导入路由
import CharacterGroup from './Components/CharacterGroup.vue'
import ImportCard from './Components/ImportCard.vue'
import BookSection from './Components/BookSection.vue'
import SettingsModal from './Components/SettingsModal.vue' // 系统设置弹窗
import AdminModal from './Components/AdminModal.vue'
import { useUserStore } from '@/stores/userStore'

// 新增：路由实例
const router = useRouter()

// 小人组件引用
const charGroupRef = ref(null)

// 弹窗显隐控制
const modalVisible = ref(false) // 系统设置弹窗
const approvalModalVisible = ref(false) // 管理员审批弹窗

// 打开系统设置弹窗
const openSettingsModal = (e) => {
  e.preventDefault() // 阻止a标签默认跳转
  modalVisible.value = true
}

// 关闭系统设置弹窗
const closeSettingsModal = () => {
  modalVisible.value = false
}

// 打开管理员审批弹窗（和系统设置弹窗逻辑一致）
const openApprovalModal = (e) => {
  e.preventDefault() // 阻止a标签默认跳转
  approvalModalVisible.value = true
}

// 关闭管理员审批弹窗
const closeApprovalModal = () => {
  approvalModalVisible.value = false
}

// 处理修改密码
const handleModifyPassword = (newPwd) => {
  // 这里写修改密码的逻辑，比如调用接口更新store
  console.log('新密码：', newPwd)
  // 示例：更新userStore中的密码
  // userStore.updatePassword(newPwd)

  // 提示用户修改成功（可替换为UI提示）
  alert('密码修改成功！')
}

// 审批操作成功回调（可选）
const handleApprovalSuccess = (data) => {
  console.log('审批操作完成：', data)
  alert(`${data.type === 'approve' ? '批准' : '拒绝'}请求成功！`)
}

// 统一处理所有元素hover，让小人微笑
const handleAllHover = () => {
  document.querySelectorAll('.char').forEach(char => char.classList.add('smile'))
}

// 统一处理所有元素leave，恢复小人状态
const handleAllLeave = () => {
  document.querySelectorAll('.char').forEach(char => {
    if (!char.matches(':hover')) char.classList.remove('smile')
  })
}

// 新增：安全退出核心逻辑
const handleLogout = (e) => {
  e.preventDefault() // 阻止a标签默认锚点跳转
  try {
    const userStore = useUserStore()
    // 1. 清空Pinia存储（根据实际store结构调整）
    // 方式1：调用store的重置方法（推荐，需在userStore中定义）
    if (userStore.resetStore) {
      userStore.resetStore()
    } else {
      // 方式2：手动清空核心字段（适配不同store结构）
      userStore.token = ''
      userStore.userInfo = null
      userStore.permissions = []
      // 或使用Pinia内置重置方法
      // userStore.$reset()
    }

    // 2. 可选：清空本地存储（防止残留）
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    sessionStorage.clear()

    // 3. 跳转到登录页
    router.push('/login')
  } catch (error) {
    console.error('退出登录失败：', error)
    // 兜底跳转
    router.push('/login')
  }
}

// 欢迎不同的同学
const userStore = useUserStore();

// 判断时间
const timeGreeting = ref('')
let timer = null

// 时间判断核心函数
const getTimeGreeting = () => {
  const hour = new Date().getHours() // 获取当前小时(0-23)
  if (hour >= 0 && hour < 6) return '深夜'
  if (hour >= 6 && hour < 9) return '早上'
  if (hour >= 9 && hour < 12) return '上午'
  if (hour >= 12 && hour < 18) return '下午'
  return '晚上' // 18:00-23:59
}

// 初始化 + 定时刷新（每1分钟更新一次）
onMounted(() => {
  timeGreeting.value = getTimeGreeting() // 初始赋值
  // 定时器：每60秒重新计算一次
  timer = setInterval(() => {
    timeGreeting.value = getTimeGreeting()
  }, 60 * 1000)
})

// 组件卸载时清除定时器（防止内存泄漏）
onUnmounted(() => {
  clearInterval(timer)
})
</script>

<template>
  <div class="login-page">
    <div class="scene">
      <!-- 小人组件 -->
      <CharacterGroup ref="charGroupRef" />

      <!-- 主内容区 -->
      <div class="main-box">
        <!-- 顶部导航 -->
        <div class="header">
          <div class="header-inner">
            <div class="logo">
              <div class="logo-icon">三</div>
              优读 EASE
            </div>
            <div class="header-right">
              <!-- 管理员审批入口（和系统设置样式/交互完全一致） -->
              <a href="#approval" class="nav-link" @mouseenter="handleAllHover" @mouseleave="handleAllLeave"
                @click="openApprovalModal">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                  stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round"
                    d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                审批管理
              </a>

              <!-- 系统设置 - 绑定打开弹窗事件 -->
              <a href="#settings" class="nav-link" @mouseenter="handleAllHover" @mouseleave="handleAllLeave"
                @click="openSettingsModal">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                  stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round"
                    d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.592c.55 0 1.02.398 1.11.94l.213 1.207c.26.95.996 1.685 1.932 1.962l1.086.317c.528.153.885.636.885 1.187 0 .217-.06.425-.169.604l-.73 1.186c-.287.465-.287 1.029 0 1.494l.73 1.186c.11.18.169.387.169.604 0 .551-.357 1.034-.885 1.187l-1.086.317c-.936.277-1.672 1.013-1.932-1.962l-.213 1.207c-.09.542-.56.94-1.11-.94h-2.592c-.55 0-1.02-.398-1.11-.94l-.213-1.207c-.26-.95-.996-1.685-1.932-1.962l-1.086-.317c-.528-.153-.885-.636-.885-1.187 0-.217.06-.425.169.604l.73-1.186c.287-.465.287-1.029 0-1.494l-.73-1.186A1.001 1.001 0 014 8.613c0-.551.357-1.034.885-1.187l1.086-.317c.936-.277 1.672-1.013 1.932-1.962l.213-1.207ZM12 15.75a3.75 3.75 0 100-7.5 3.75 3.75 0 000 7.5z" />
                </svg>
                系统设置
              </a>
              <!-- 安全退出 - 绑定点击事件 -->
              <a href="#logout" class="nav-link logout" @mouseenter="handleAllHover" @mouseleave="handleAllLeave"
                @click="handleLogout">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                  stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round"
                    d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m-6-6H6m0 0h6m-6 0v6m6-6v6" />
                </svg>
                安全退出
              </a>
            </div>
          </div>
        </div>

        <!-- 欢迎区域 -->
        <div class="welcome">
          <h1>{{ timeGreeting }}好，{{ userStore.userInfo.username }} 同学</h1>
          <p>今天也是充满阅读乐趣的一天。你想看点什么？</p>
        </div>

        <!-- 主内容布局 -->
        <div class="main">
          <!-- 导入卡片组件 -->
          <ImportCard @cardHover="handleAllHover" @cardLeave="handleAllLeave" />

          <!-- 书籍组件 -->
          <BookSection @cardHover="handleAllHover" @cardLeave="handleAllLeave" />
        </div>
      </div>
    </div>

    <!-- 系统设置弹窗组件 -->
    <SettingsModal :visible="modalVisible" :user-info="userStore.userInfo" @close="closeSettingsModal"
      @modifyPassword="handleModifyPassword" />

    <!-- 管理员审批弹窗组件（独立子组件） -->
    <AdminModal :visible="approvalModalVisible" :admin-info="userStore.userInfo" @close="closeApprovalModal"
      @approvalSuccess="handleApprovalSuccess" />
  </div>
</template>

<style scoped>
/* 原有样式保持不变 */
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 页面容器 */
.login-page {
  height: 100vh;
  background: linear-gradient(135deg, #f9f7ff, #e2e8ff);
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  padding: 20px;
}

/* 主容器 */
.scene {
  width: 1000px;
  height: 650px;
  background: white;
  border-radius: 32px;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.18), 0 5px 15px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  display: flex;
  position: relative;
  transition: transform 0.2s ease;
}

.scene:hover {
  transform: translateY(-5px);
  box-shadow: 0 40px 90px rgba(0, 0, 0, 0.22), 0 8px 20px rgba(0, 0, 0, 0.1);
}

/* 主盒子 */
.main-box {
  width: 100%;
  height: 100%;
  background: white;
  padding: 0;
  position: relative;
  z-index: 10;
}

/* 顶部导航 */
.header {
  background-color: white;
  padding: 24px 50px;
  border-bottom: 1px solid #f0f0f0;
}

.header-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 700;
  color: #9333ea;
  letter-spacing: -0.5px;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #9333ea, #7e22ce);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 16px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 18px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #4b5563;
  text-decoration: none;
  font-size: 1.05rem;
  font-weight: 500;
  transition: all 0.25s;
  padding: 10px 16px;
  border-radius: 20px;
}

.nav-link:hover {
  color: #9333ea;
  background-color: rgba(147, 51, 234, 0.08);
  transform: translateY(-2px);
}

.nav-link svg {
  width: 20px;
  height: 20px;
}

.logout {
  color: #dc2626;
}

.logout:hover {
  color: #b91c1c;
  background-color: rgba(220, 38, 38, 0.08);
}

/* 欢迎区 */
.welcome {
  padding: 40px 50px 20px;
}

.welcome h1 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 14px;
  color: #1f2937;
  letter-spacing: -0.5px;
}

.welcome p {
  font-size: 1.2rem;
  color: #6b7280;
  line-height: 1.6;
}

/* 主内容区 */
.main {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  padding: 0 50px 20px;
  height: calc(100% - 180px);
  overflow-y: auto;
}

/* 新增：提升ElMessage层级，避免弹窗内提示被遮挡 */
:deep(.el-message) {
  z-index: 10000 !important;
}
</style>

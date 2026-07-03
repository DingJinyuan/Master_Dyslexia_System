<script setup lang="js">
import { ref, onMounted, onUnmounted } from 'vue';
import { ElMessage } from 'element-plus';
import 'element-plus/theme-chalk/el-message.css'
import { loginRules } from '@/utils/validateRules';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/userStore'
import CharacterGroup from './Components/characterGroup.vue'

// 表情控制（统一显示笑脸）
const emotionType = ref('smiling') // 固定为笑脸类型
const isEmotionActive = ref(false)
const formArea = ref(null)

// 显示笑脸（所有表单交互都触发）
const showSmile = () => {
    emotionType.value = 'smiling' // 强制设置为笑脸
    isEmotionActive.value = true
}

// 隐藏笑脸（点击外部区域）
const hideSmile = () => {
    isEmotionActive.value = false
}

// 点击文档事件处理
const handleDocumentClick = (e) => {
    const isInForm = formArea.value?.contains(e.target)
    const isInCharacter = document.querySelector('.characters')?.contains(e.target)
    if (!isInForm && !isInCharacter) {
        hideSmile()
    }
}

// 表单逻辑
const loginFormRef = ref(null);
const router = useRouter()
const loginForm = ref({
    username: '',
    password: '',
    agree: false,
});

const doLogin = () => {
    const username = loginForm.value.username;
    const password = loginForm.value.password;

    loginFormRef.value.validate(async (valid) => {
        if (valid) {
            try {
                const userStore = useUserStore();
                await userStore.getUserInfo(username, password);
                ElMessage({ type: 'success', message: '登录成功' })
                router.replace({ path: '/' })
                hideSmile() // 登录成功后隐藏笑脸
            } catch (error) {
                ElMessage({ type: 'error', message: '登录失败：' + (error.message || '账号或密码错误') })
                hideSmile() // 登录失败也隐藏笑脸
            }
        } else {
            hideSmile() // 表单验证失败隐藏笑脸
        }
    });
};
// 登录链接点击事件：显示表情 + 跳转到登录页
const handleRegisterLinkClick = () => {
    showSmile() // 保留显示O型嘴的交互
    // 跳转到注册页（路由路径根据你的实际配置调整，比如 '/login'）
    router.push('/register')
    // 或用 router.replace('/注册')（替换当前页面，无法返回）
}

// 生命周期
onMounted(() => {
    document.addEventListener('click', handleDocumentClick);
    if (formArea.value) {
        formArea.value.addEventListener('click', (e) => e.stopPropagation());
    }
});
onUnmounted(() => {
    document.removeEventListener('click', handleDocumentClick);
});
</script>

<template>
    <div class="login-page">
        <div class="scene">
            <!-- 传递笑脸参数给子组件 -->
            <CharacterGroup :emotion-type="emotionType" :is-emotion-active="isEmotionActive" :stop-click="true" />

            <!-- 登录表单区域 -->
            <div class="login-form" ref="formArea">
                <div class="form-header">
                    <h1>Log in</h1>
                    <div class="subtitle">Welcome back! Sign in to your account</div>
                </div>

                <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" label-width="0"
                    class="el-form-custom">
                    <!-- 用户名 -->
                    <el-form-item prop="username" class="form-item">
                        <el-input v-model="loginForm.username" placeholder="Username" size="large" @click="showSmile"
                            @focus="showSmile" class="el-input-custom" clearable />
                    </el-form-item>

                    <!-- 密码 -->
                    <el-form-item prop="password" class="form-item">
                        <el-input v-model="loginForm.password" type="password"
                            placeholder="Password (min. 6 characters)" size="large" @click="showSmile"
                            @focus="showSmile" class="el-input-custom" clearable />
                        <div class="form-tip">Must include letters and numbers</div>
                    </el-form-item>

                    <!-- 协议复选框 -->
                    <el-form-item prop="agree" class="form-item checkbox-item">
                        <el-checkbox v-model="loginForm.agree" @click="showSmile" class="el-checkbox-custom">
                            我已同意隐私条款和服务条款
                        </el-checkbox>
                    </el-form-item>

                    <!-- 登录按钮 -->
                    <el-form-item class="form-item button-item">
                        <el-button type="primary" size="large" @click="doLogin" class="el-btn-custom">
                            Sign in
                        </el-button>
                    </el-form-item>
                </el-form>

                <div class="login-links">
                    <a href="#" @click="showSmile" class="forgot-link">Forgot password?</a>
                    <div class="register-link">
                        Don't have an account? <a href="#" @click.prevent="handleRegisterLinkClick">Sign up</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style lang="scss" scoped>
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

/* 笑脸表情样式（子组件样式穿透） */
:deep(.blob.smiling .eyes .eye) {
    transform: scale(1.15);
    transition: transform 0.3s ease;
}

:deep(.blob.orange.smiling .eyes .eye) {
    transform: scale(1.15);
}

:deep(.blob.purple.smiling .eyes .eye) {
    transform: scale(1.1);
}

:deep(.blob.black.smiling .eyes .eye) {
    transform: scale(1.12);
}

:deep(.blob.yellow.smiling .eyes .eye) {
    transform: scale(1.18);
}

:deep(.blob.orange.smiling .mouth) {
    width: 45px;
    height: 22px;
    top: 70%;
    background-color: #000;
    border-radius: 0 0 28px 28px;
}

:deep(.blob.purple.smiling .mouth) {
    width: 35px;
    height: 18px;
    top: 68%;
    background-color: #000;
    border-radius: 0 0 22px 22px;
}

:deep(.blob.black.smiling .mouth) {
    width: 28px;
    height: 15px;
    top: 65%;
    background-color: #fff;
    border-radius: 0 0 20px 20px;
}

:deep(.blob.yellow.smiling .mouth) {
    width: 40px;
    height: 20px;
    top: 69%;
    background-color: #000;
    border-radius: 0 0 25px 25px;
}

/* 登录表单区域 */
.login-form {
    width: 460px;
    padding: 70px 50px 60px 50px;
    display: flex;
    flex-direction: column;
    gap: 28px;
    background: white;
    border-left: 1px solid #f0f0f0;
    position: relative;
}

/* 表单头部 */
.form-header {
    margin-bottom: 8px;
}

h1 {
    font-size: 3rem;
    color: #1f2937;
    margin-bottom: 14px;
    font-weight: 700;
    letter-spacing: -0.5px;
}

.subtitle {
    color: #6b7280;
    font-size: 1.2rem;
    line-height: 1.6;
}

/* 表单项间距优化 */
.form-item {
    margin-bottom: 20px !important;
}

.checkbox-item {
    margin-top: 5px !important;
    margin-bottom: 22px !important;
}

.button-item {
    margin-top: 8px !important;
    margin-bottom: 5px !important;
}

/* 输入框样式优化 */
:deep(.el-form-custom) {
    width: 100%;
}

:deep(.el-input-custom) {
    --el-input-height-large: 58px;
    --el-input-border-radius: 20px;
    --el-input-border-color: #d1d5db;
    --el-input-focus-border-color: #9333ea;
    --el-input-focus-box-shadow: 0 0 0 4px rgba(147, 51, 234, 0.1);
    font-size: 1.1rem;
    padding: 0 22px;
}

/* 错误提示样式优化 */
:deep(.el-form-item__error) {
    color: #dc2626 !important;
    font-size: 0.95rem !important;
    font-weight: 500;
    padding-top: 6px;
    padding-left: 2px;
}

/* 密码规则提示 */
.form-tip {
    font-size: 0.98rem;
    color: #6b7280;
    margin-top: 8px;
    margin-bottom: 6px;
    line-height: 1.5;
    padding-left: 2px;
}

/* 复选框样式 */
:deep(.el-checkbox-custom) {
    font-size: 1.05rem;
    color: #4b5563;
    line-height: 1.6;
}

:deep(.el-checkbox__inner) {
    width: 20px;
    height: 20px;
    border-radius: 4px;
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
    background-color: #10b981;
    border-color: #10b981;
}

:deep(.el-checkbox-custom a) {
    color: #9333ea;
    text-decoration: none;
    font-weight: 500;
}

:deep(.el-checkbox-custom a:hover) {
    text-decoration: underline;
    color: #7e22ce;
}

/* 按钮样式 */
:deep(.el-btn-custom) {
    --el-button-height-large: 58px;
    --el-button-border-radius: 20px;
    --el-button-font-size: 1.2rem;
    --el-button-primary-bg-color: #10b981;
    --el-button-primary-hover-bg-color: #059669;
    --el-button-primary-active-bg-color: #047857;
    width: 100%;
    font-weight: 600;
    letter-spacing: 0.5px;
    transition: all 0.2s ease;
}

:deep(.el-btn-custom:hover) {
    transform: translateY(-2px);
    box-shadow: 0 8px 15px rgba(16, 185, 129, 0.2);
}

:deep(.el-btn-custom:active) {
    transform: translateY(0);
    box-shadow: 0 4px 8px rgba(16, 185, 129, 0.15);
}

/* 登录链接样式 */
.login-links {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 18px;
    margin-top: 12px;
}

.forgot-link {
    color: #9333ea;
    text-decoration: none;
    font-size: 1.1rem;
    font-weight: 500;
}

.forgot-link:hover {
    text-decoration: underline;
    color: #7e22ce;
}

.register-link {
    color: #6b7280;
    font-size: 1.05rem;
    line-height: 1.6;
}

.register-link a {
    color: #9333ea;
    text-decoration: none;
    font-weight: 600;
}

.register-link a:hover {
    text-decoration: underline;
    color: #7e22ce;
}
</style>
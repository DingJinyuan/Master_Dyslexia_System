<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ElInput, ElButton, ElCheckbox, ElForm, ElFormItem } from 'element-plus'
import Characters from '../Components/characterGroup.vue'
import 'element-plus/theme-chalk/el-message.css'

import { useRouter } from 'vue-router';
import { registerAPI } from '../../../apis/auth'
import { loginRules } from '../../../utils/validateRules'

// 路由
const router = useRouter()


// 角色表情控制：所有交互都显示O型嘴
const emotionType = ref('o-mouth') // 固定为O型嘴
const isEmotionActive = ref(false)
const formAreaRef = ref(null)

// 显示角色嘴巴（统一显示O型嘴）
const showMouth = () => {
    emotionType.value = 'o-mouth'
    isEmotionActive.value = true
}

// 隐藏角色嘴巴
const hideMouth = () => {
    isEmotionActive.value = false
}

// 输入框失焦处理
const handleInputBlur = () => {
    setTimeout(() => {
        const activeElement = document.activeElement
        const isFormElement = formAreaRef.value?.contains(activeElement)
        if (!isFormElement) {
            hideMouth()
        }
    }, 100)
}

// 表单数据
const registerForm = ref({
    username: '',
    email: '',
    password: '',
    agree: false
})
const registerFormRef = ref(null);

// 注册按钮点击逻辑（修复语法错误 + 统一逻辑）
const doRegister = async () => {
    showMouth() // 点击注册显示O型嘴

    registerFormRef.value.validate(async (valid) => {
        if (valid) {
            try {
                const { email, username, password, agree = undefined } = registerForm.value
                const mes = await registerAPI(email, username, password)
                ElMessage({ type: 'success', message: mes })
                router.replace({ path: '/login' }) // 注册成功跳登录页
                hideMouth()
            } catch (error) {
                ElMessage({
                    type: 'error',
                    message: '注册失败：' + (error.message || '服务器错误')
                })
                hideMouth()
            }
        } else {
            // 表单验证失败
            ElMessage({ type: 'warning', message: '请完善表单信息' })
            hideMouth()
        }
    })
}

// 点击页面其他区域隐藏嘴巴
const handleDocumentClick = (e) => {
    const isInForm = formAreaRef.value?.contains(e.target)
    const isInCharacters = e.target.closest('.characters')
    if (!isInForm && !isInCharacters) {
        hideMouth()
    }
}
// 登录链接点击事件：显示表情 + 跳转到登录页
const handleLoginLinkClick = () => {
    showMouth() // 保留显示O型嘴的交互
    // 跳转到登录页（路由路径根据你的实际配置调整，比如 '/login'）
    router.push('/login')
    // 或用 router.replace('/login')（替换当前页面，无法返回）
}

// 生命周期
onMounted(() => {
    document.addEventListener('click', handleDocumentClick)
    // 阻止表单区域点击事件冒泡
    if (formAreaRef.value) {
        formAreaRef.value.addEventListener('click', (e) => e.stopPropagation())
    }
})

onUnmounted(() => {
    document.removeEventListener('click', handleDocumentClick)
})




</script>

<template>
    <div class="register-page">
        <div class="scene">
            <!-- 父组件传递O型嘴参数给子组件 -->
            <Characters :emotion-type="emotionType" :is-emotion-active="isEmotionActive" :stop-click="true" />

            <div class="register-form" ref="formAreaRef" @click.stop>
                <div class="form-header">
                    <h1>Create Account</h1>
                    <div class="subtitle">Get started with your free account</div>
                </div>

                <!-- 重构为el-form格式（对齐登录页） -->
                <el-form ref="registerFormRef" :model="registerForm" :rules="loginRules" label-width="0"
                    class="el-form-custom">
                    <!-- 用户名 -->
                    <el-form-item prop="username" class="form-item">
                        <el-input v-model="registerForm.username" placeholder="Username" size="large" @click="showMouth"
                            @focus="showMouth" @blur="handleInputBlur" class="el-input-custom" clearable />
                    </el-form-item>

                    <!-- 邮箱 -->
                    <el-form-item prop="email" class="form-item">
                        <el-input v-model="registerForm.email" type="email" placeholder="Email address" size="large"
                            @click="showMouth" @focus="showMouth" @blur="handleInputBlur" class="el-input-custom"
                            clearable />
                    </el-form-item>

                    <!-- 密码 -->
                    <el-form-item prop="password" class="form-item">
                        <el-input v-model="registerForm.password" type="password"
                            placeholder="Password (min. 8 characters)" size="large" @click="showMouth"
                            @focus="showMouth" @blur="handleInputBlur" class="el-input-custom" clearable />
                        <div class="form-tip">Must include letters and numbers</div>
                    </el-form-item>

                    <!-- 协议复选框 -->
                    <el-form-item prop="agree" class="form-item checkbox-item">
                        <el-checkbox v-model="registerForm.agree" @click="showMouth" class="el-checkbox-custom">
                            I agree to the <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>
                        </el-checkbox>
                    </el-form-item>

                    <!-- 注册按钮 -->
                    <el-form-item class="form-item button-item">
                        <el-button type="primary" size="large" @click="doRegister" class="el-btn-custom">
                            Sign up
                        </el-button>
                    </el-form-item>
                </el-form>

                <!-- 登录链接：点击显示O型嘴，靠近Sign up按钮 -->
                <div class="login-link">
                    Already have an account?
                    <a href="#" @click.prevent="handleLoginLinkClick">Log in</a>
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
.register-page {
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

/* 角色区域背景 */
:deep(.characters) {
    background: #fffaf5 !important;
}

/* 注册表单区域 */
.register-form {
    width: 460px;
    padding: 70px 50px 60px 50px;
    display: flex;
    flex-direction: column;
    gap: 28px;
    /* 对齐登录页间距 */
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

/* 表单项样式（对齐登录页） */
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

/* 输入框样式（对齐登录页） */
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

/* 错误提示样式 */
:deep(.el-form-item__error) {
    color: #dc2626 !important;
    font-size: 0.95rem !important;
    font-weight: 500;
    padding-top: 6px;
    padding-left: 2px;
}

/* 密码提示 */
.form-tip {
    font-size: 0.98rem;
    color: #6b7280;
    margin-top: 8px;
    margin-bottom: 6px;
    line-height: 1.5;
    padding-left: 2px;
}

/* 复选框样式（对齐登录页） */
:deep(.el-checkbox-custom) {
    font-size: 1.05rem;
    color: #4b5563;
    line-height: 1.6;
}

:deep(.el-checkbox__inner) {
    width: 20px !important;
    height: 20px !important;
    border-radius: 4px !important;
    border: 1px solid #d1d5db !important;
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
    background-color: #9333ea !important;
    border-color: #9333ea !important;
}

.terms a {
    color: #9333ea;
    text-decoration: none;
    font-weight: 500;
}

.terms a:hover {
    text-decoration: underline;
    color: #7e22ce;
}

/* 按钮样式（对齐登录页） */
:deep(.el-btn-custom) {
    --el-button-height-large: 58px;
    --el-button-border-radius: 20px;
    --el-button-font-size: 1.2rem;
    --el-button-primary-bg-color: #9333ea;
    --el-button-primary-hover-bg-color: #7e22ce;
    --el-button-primary-active-bg-color: #6b21a8;
    width: 100%;
    font-weight: 600;
    letter-spacing: 0.5px;
    transition: all 0.2s ease;
}

:deep(.el-btn-custom:hover) {
    transform: translateY(-2px);
    box-shadow: 0 8px 15px rgba(147, 51, 234, 0.2);
}

:deep(.el-btn-custom:active) {
    transform: translateY(0);
    box-shadow: 0 4px 8px rgba(147, 51, 234, 0.15);
}

/* 登录链接：调整间距，靠近Sign up按钮 */
.login-link {
    text-align: center;
    color: #6b7280;
    font-size: 1.05rem;
    margin-top: 5px !important;
    line-height: 1.6;
}

.login-link a {
    color: #9333ea;
    text-decoration: none;
    font-weight: 600;
}

.login-link a:hover {
    text-decoration: underline;
    color: #7e22ce;
}
</style>
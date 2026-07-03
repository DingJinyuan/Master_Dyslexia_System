<template>
    <div class="forgot-page">
        <div class="scene">
            <!-- 复用角色组件：沮丧表情 -->
            <CharacterGroup emotion-class="sad" :is-emotion-active="isSad" :stop-click="true" :interaction-config="{
                pupilFollowRange: 12,
                blobTiltBase: 3,
                blobSwayBase: 5,
                blobScaleRatio: 0.015
            }" />

            <!-- 忘记密码表单区域 -->
            <div class="forgot-form" ref="formArea">
                <h1>Forgot Password</h1>
                <div class="subtitle">Enter your email to reset your password</div>

                <!-- Element Plus 表单容器 -->
                <el-form ref="forgotFormRef" :model="forgotForm" :rules="forgotRules" label-width="0"
                    class="el-form-custom">
                    <!-- 邮箱输入框 -->
                    <el-form-item prop="email">
                        <el-input v-model="forgotForm.email" placeholder="Your registered email" size="large"
                            type="email" @click="showSad" @focus="showSad" class="el-input-custom" />
                    </el-form-item>

                    <!-- 验证码输入框 -->
                    <el-form-item prop="code">
                        <div class="code-input-wrapper">
                            <el-input v-model="forgotForm.code" placeholder="Verification code" size="large"
                                @click="showSad" @focus="showSad" class="el-input-custom code-input" />
                            <el-button type="primary" size="large" @click="getVerifyCode" @mouseenter="showSad"
                                :disabled="codeDisabled" class="code-btn">
                                {{ codeText }}
                            </el-button>
                        </div>
                        <div class="form-tip">We'll send a 6-digit code to your email</div>
                    </el-form-item>

                    <!-- 提交按钮 -->
                    <el-form-item>
                        <el-button type="primary" size="large" @click="handleReset" @mouseenter="showSad"
                            class="el-btn-custom">
                            Send Reset Link
                        </el-button>
                    </el-form-item>
                </el-form>

                <!-- 返回登录链接 -->
                <div class="forgot-links">
                    <a href="/login" @click="showSad" class="back-link">Back to login</a>
                    <div class="contact-link">
                        Need help? <a href="/contact" @click="showSad">Contact support</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { ElMessage } from 'element-plus';
import 'element-plus/theme-chalk/el-message.css';
import { useRouter } from 'vue-router';
import CharacterGroup from './Components/characterGroup.vue';

// ======================================
// 角色交互逻辑（仅控制沮丧表情显示/隐藏）
// ======================================
const isSad = ref(false);
const formArea = ref(null);

// 显示沮丧表情
const showSad = () => {
    isSad.value = true;
};

// 点击页面其他区域隐藏沮丧表情
const handleDocumentClick = (e) => {
    const isInFormArea = formArea.value?.contains(e.target);
    const isInCharacterArea = document.querySelector('.characters')?.contains(e.target);

    if (!isInFormArea && !isInCharacterArea) {
        isSad.value = false;
    }
};

// ======================================
// 忘记密码表单逻辑
// ======================================
const router = useRouter();
const forgotFormRef = ref(null);
// 表单数据
const forgotForm = ref({
    email: '',
    code: ''
});

// 表单校验规则
const forgotRules = ref({
    email: [
        { required: true, message: 'Please enter your email', trigger: 'blur' },
        { type: 'email', message: 'Please enter a valid email', trigger: 'blur' }
    ],
    code: [
        { required: true, message: 'Please enter verification code', trigger: 'blur' },
        { len: 6, message: 'Verification code must be 6 digits', trigger: 'blur' }
    ]
});

// 验证码倒计时相关
const codeDisabled = ref(false);
const codeText = ref('Get Code');
let countdown = null;

// 获取验证码
const getVerifyCode = () => {
    // 先校验邮箱
    forgotFormRef.value.validateField('email', (error) => {
        if (!error) {
            // 模拟发送验证码
            ElMessage.success('Verification code sent to your email!');
            // 开始倒计时
            codeDisabled.value = true;
            let time = 60;
            codeText.value = `${time}s Resend`;

            countdown = setInterval(() => {
                time--;
                codeText.value = `${time}s Resend`;
                if (time <= 0) {
                    clearInterval(countdown);
                    codeDisabled.value = false;
                    codeText.value = 'Get Code';
                }
            }, 1000);
        } else {
            ElMessage.error('Please enter a valid email first');
            isSad.value = false; // 校验失败隐藏沮丧表情
        }
    });
};

// 提交重置请求
const handleReset = () => {
    forgotFormRef.value.validate(async (valid) => {
        if (valid) {
            try {
                // 模拟重置密码请求
                ElMessage.success('Reset link sent to your email!');
                // 3秒后跳回登录页
                setTimeout(() => {
                    router.replace({ path: '/login' });
                }, 3000);
            } catch (error) {
                ElMessage.error('Failed to send reset link: ' + (error.message || 'Unknown error'));
                isSad.value = false; // 请求失败隐藏沮丧表情
            }
        } else {
            ElMessage.error('Please fill in the form correctly');
            isSad.value = false; // 校验失败隐藏沮丧表情
        }
    });
};

// ======================================
// 生命周期钩子
// ======================================
onMounted(() => {
    // 绑定点击事件
    document.addEventListener('click', handleDocumentClick);
    // 初始隐藏沮丧表情
    isSad.value = false;
});

onUnmounted(() => {
    // 销毁事件和倒计时
    document.removeEventListener('click', handleDocumentClick);
    if (countdown) clearInterval(countdown);
});
</script>

<style lang="scss" scoped>
/* 页面容器 - PC 端适配（固定全屏） */
.forgot-page {
    height: 100vh;
    background: linear-gradient(135deg, #f9f7ff, #e2e8ff);
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    padding: 20px;
}

/* 主容器 - PC 端固定尺寸 + 交互增强 */
.scene {
    width: 1000px;
    height: 600px;
    background: white;
    border-radius: 32px;
    box-shadow: 0 30px 80px rgba(0, 0, 0, 0.18), 0 5px 15px rgba(0, 0, 0, 0.08);
    overflow: hidden;
    display: flex;
    position: relative;
    transition: transform 0.2s ease;
}

/* PC 端悬浮效果 */
.scene:hover {
    transform: translateY(-5px);
    box-shadow: 0 40px 90px rgba(0, 0, 0, 0.22), 0 8px 20px rgba(0, 0, 0, 0.1);
}

/* 角色组件样式穿透 - 沮丧表情专属样式 */
:deep(.characters) {
    flex: 1;
    background: #fffaf5;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    padding: 60px 30px 100px 30px;
}

/* 沮丧状态眼睛效果（PC端增强） */
:deep(#orange.sad .eyes) {
    transform: translateX(-50%) translateY(4px) scale(0.95);
}

:deep(#purple.sad .eyes) {
    transform: translateX(-50%) translateY(3px) scale(0.97);
}

:deep(#black.sad .eyes) {
    transform: translateX(-50%) translateY(2px) scale(0.96);
}

:deep(#yellow.sad .eyes) {
    transform: translateX(-50%) translateY(5px) scale(0.94);
}

/* 各角色沮丧嘴巴样式（PC端优化） */
:deep(#orange.sad .mouth) {
    width: 42px;
    height: 20px;
    top: 65%;
    background-color: #000;
    border-radius: 25px 25px 0 0;
    /* 沮丧是上半圆 */
}

:deep(#purple.sad .mouth) {
    width: 32px;
    height: 16px;
    top: 63%;
    background-color: #000;
    border-radius: 20px 20px 0 0;
}

:deep(#black.sad .mouth) {
    width: 26px;
    height: 13px;
    top: 60%;
    background-color: #fff;
    border-radius: 18px 18px 0 0;
}

:deep(#yellow.sad .mouth) {
    width: 38px;
    height: 18px;
    top: 64%;
    background-color: #000;
    border-radius: 22px 22px 0 0;
}

/* 忘记密码表单区域样式 - PC 端核心优化 */
.forgot-form {
    width: 420px;
    padding: 80px 50px 60px 50px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    background: white;
    border-left: 1px solid #f0f0f0;
    position: relative;
}

/* 表单标题 - PC 端排版优化 */
h1 {
    font-size: 2.8rem;
    color: #111827;
    margin-bottom: 12px;
    font-weight: 700;
    letter-spacing: -0.5px;
}

.subtitle {
    color: #6b7280;
    font-size: 1.1rem;
    margin-bottom: 15px;
    line-height: 1.5;
}

/* 验证码输入框容器 */
.code-input-wrapper {
    display: flex;
    gap: 10px;
    width: 100%;
}

.code-input {
    flex: 1;
}

.code-btn {
    width: 140px;
    --el-button-height-large: 56px;
    --el-button-border-radius: 18px;
    font-size: 1rem;
}

/* Element Plus 样式穿透 - PC端优化 */
:deep(.el-form-custom) {
    width: 100%;
}

/* 输入框 - PC 端交互增强 */
:deep(.el-input-custom) {
    --el-input-height-large: 56px;
    --el-input-border-radius: 18px;
    --el-input-border-color: #e5e7eb;
    --el-input-focus-border-color: #9333ea;
    --el-input-focus-box-shadow: 0 0 0 5px rgba(147, 51, 234, 0.12);
    font-size: 1.15rem;
    padding: 0 20px;
}

/* 按钮 - PC 端核心优化 */
:deep(.el-btn-custom) {
    --el-button-height-large: 56px;
    --el-button-border-radius: 18px;
    --el-button-font-size: 1.18rem;
    --el-button-primary-bg-color: #9333ea;
    --el-button-primary-hover-bg-color: #7e22ce;
    --el-button-primary-active-bg-color: #6b21a8;
    width: 100%;
    font-weight: 600;
    margin-top: 10px;
    margin-bottom: 0px;
    letter-spacing: 0.5px;
    transition: all 0.2s ease;
}

/* 按钮悬浮/点击效果 - PC 端增强 */
:deep(.el-btn-custom:hover) {
    transform: translateY(-2px);
    box-shadow: 0 8px 15px rgba(147, 51, 234, 0.2);
}

:deep(.el-btn-custom:active) {
    transform: translateY(0);
    box-shadow: 0 4px 8px rgba(147, 51, 234, 0.15);
}

/* 表单提示文字 */
.form-tip {
    font-size: 0.95rem;
    color: #6b7280;
    margin-top: 4px;
    margin-bottom: 12px;
    line-height: 1.4;
    padding-left: 2px;
}

/* 忘记密码链接样式 */
.forgot-links {
    width: 100%;
    margin-top: 0;
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.back-link {
    color: #9333ea;
    text-decoration: none;
    font-size: 1rem;
    font-weight: 500;
}

.back-link:hover {
    text-decoration: underline;
    color: #7e22ce;
}

.contact-link {
    color: #6b7280;
    font-size: 1rem;
    line-height: 1.5;
}

.contact-link a {
    color: #9333ea;
    text-decoration: none;
    font-weight: 600;
}

.contact-link a:hover {
    text-decoration: underline;
    color: #7e22ce;
}
</style>
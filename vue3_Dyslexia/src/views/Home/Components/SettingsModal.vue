<script setup>
import { ref, defineProps, defineEmits, watch } from 'vue'
import { ElForm, ElFormItem, ElInput, ElMessage } from 'element-plus'
// 导入你的密码校验规则和接口
import { loginRules } from '@/utils/validateRules'
import { password_changeAPI } from '../../../apis/auth' // 你的修改密码接口

// 接收父组件传值
const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
    userInfo: {
        type: Object,
        required: true,
        default: () => ({
            username: '',
            email: '',
            password: ''
        })
    }
})

// 定义事件
const emit = defineEmits(['close', 'modifyPassword'])

// 表单相关响应式数据（新增 oldPassword 原密码字段）
const pwdFormRef = ref(null)
const pwdForm = ref({
    oldPassword: '',    // 原密码
    newPassword: '',    // 新密码
    confirmPassword: '' // 确认新密码
})
const errorMsg = ref('')

// 绑定校验规则（复用 loginRules 里的 password 规则）
const pwdRules = ref({
    oldPassword: [...loginRules.password],  // 原密码校验规则
    newPassword: [...loginRules.password],  // 新密码校验规则
    confirmPassword: [...loginRules.password] // 确认密码基础规则
})

// 关闭弹窗
const closeModal = () => {
    emit('close')
    if (pwdFormRef.value) {
        pwdFormRef.value.resetFields()
    }
    errorMsg.value = ''
}

// 核心：修改密码方法（新增原密码校验）
const doChangePassword = () => {
    // 从用户信息获取真实原密码
    const real_old_password = props.userInfo.password;

    pwdFormRef.value.validate(async (valid) => {
        if (valid) {
            try {
                // 1. 校验输入的原密码是否正确
                if (pwdForm.value.oldPassword !== real_old_password) {
                    ElMessage({ type: 'error', message: '原密码输入错误' });
                    return;
                }

                // 2. 校验新密码和确认密码是否一致
                if (pwdForm.value.newPassword !== pwdForm.value.confirmPassword) {
                    ElMessage({ type: 'error', message: '两次输入的新密码不一致' });
                    return;
                }

                // 3. 校验新密码不能和原密码相同
                if (pwdForm.value.newPassword === real_old_password) {
                    ElMessage({ type: 'error', message: '新密码不能和原密码相同' });
                    return;
                }

                // 4. 调用接口修改密码（传递原密码和新密码）
                const res = await password_changeAPI({
                    old_password: pwdForm.value.oldPassword, // 传输入的原密码
                    new_password: pwdForm.value.newPassword,
                }
                );

                // 接口调用成功后的处理
                ElMessage({ type: 'success', message: '密码修改申请提交成功！' });
                closeModal(); // 关闭弹窗
                emit('modifyPassword', pwdForm.value.newPassword); // 通知父组件

            } catch (error) {
                ElMessage({
                    type: 'error',
                    message: '密码修改失败：' + (error.message || '服务器错误')
                });
            }
        } else {
            // 表单校验失败（会自动显示 loginRules 里的错误提示）
            ElMessage({ type: 'warning', message: '请检查密码输入是否符合要求' });
        }
    });
};

// 监听弹窗显隐，重置表单
watch(() => props.visible, (newVal) => {
    if (!newVal && pwdFormRef.value) {
        pwdFormRef.value.resetFields()
        errorMsg.value = ''
    }
})
</script>

<template>
    <!-- 遮罩层 -->
    <div class="modal-overlay" v-if="visible" @click="closeModal">
        <!-- 弹窗主体 -->
        <div class="modal-content" @click.stop>
            <div class="modal-header">
                <h3>系统设置 - 个人信息</h3>
                <button class="close-btn" @click="closeModal">×</button>
            </div>
            <div class="modal-body">
                <!-- 用户信息展示 -->
                <div class="user-info">
                    <div class="info-item">
                        <label>用户名：</label>
                        <span>{{ userInfo.username }}</span>
                    </div>
                    <div class="info-item">
                        <label>邮箱：</label>
                        <span>{{ userInfo.email }}</span>
                    </div>
                    <div class="info-item">
                        <label>密码：</label>
                        <span>●●●●●●●●</span> <!-- 脱敏显示原密码 -->
                    </div>
                </div>

                <!-- 完全保留原有样式，新增原密码输入框 -->
                <div class="password-modify">
                    <h4>修改密码</h4>
                    <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="0" class="el-form-custom">
                        <!-- 新增：原密码输入框 -->
                        <el-form-item prop="oldPassword" class="form-item">
                            <div class="row-item">
                                <span class="label-text">原密码：</span>
                                <el-input type="password" v-model="pwdForm.oldPassword" placeholder="请输入原密码"
                                    size="default" class="el-input-custom" show-password></el-input>
                            </div>
                        </el-form-item>

                        <!-- 新密码 -->
                        <el-form-item prop="newPassword" class="form-item">
                            <div class="row-item">
                                <span class="label-text">新密码：</span>
                                <el-input type="password" v-model="pwdForm.newPassword" placeholder="请输入新密码"
                                    size="default" class="el-input-custom" show-password></el-input>
                            </div>
                        </el-form-item>

                        <!-- 确认新密码 -->
                        <el-form-item prop="confirmPassword" class="form-item">
                            <div class="row-item">
                                <span class="label-text">确认新密码：</span>
                                <el-input type="password" v-model="pwdForm.confirmPassword" placeholder="请再次输入新密码"
                                    size="default" class="el-input-custom" show-password></el-input>
                            </div>
                        </el-form-item>
                    </el-form>
                    <div class="error-tip" v-if="errorMsg">{{ errorMsg }}</div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="cancel-btn" @click="closeModal">取消</button>
                <!-- 绑定核心方法 -->
                <button class="confirm-btn" @click="doChangePassword">确认修改</button>
            </div>
        </div>
    </div>
</template>

<!-- 样式部分完全保留，无任何修改 -->

<style scoped>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}


.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}

.modal-content {
    width: 600px;
    background: white;
    border-radius: 24px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    padding: 0;
    overflow: hidden;
}

.modal-header {
    padding: 24px 30px;
    border-bottom: 1px solid #f0f0f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-header h3 {
    font-size: 2rem;
    color: #1f2937;
    font-weight: 700;
    letter-spacing: -0.5px;
    margin: 0;
}

.close-btn {
    background: transparent;
    border: none;
    font-size: 28px;
    color: #6b7280;
    cursor: pointer;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: all 0.2s;
}

.close-btn:hover {
    background: #f9fafb;
    color: #1f2937;
}

.modal-body {
    padding: 30px;
}

.user-info {
    margin-bottom: 30px;
    padding-bottom: 24px;
    border-bottom: 1px solid #f0f0f0;
}

.info-item {
    display: flex;
    align-items: center;
    margin-bottom: 16px;
    font-size: 1.1rem;
}

.info-item label {
    width: 80px;
    color: #6b7280;
    font-weight: 500;
}

.info-item span {
    color: #1f2937;
}

.password-modify h4 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 24px;
    letter-spacing: -0.3px;
}

.el-form-custom {
    width: 100%;
}

.form-item {
    margin-bottom: 16px !important;
}

.row-item {
    display: flex;
    align-items: center;
    width: 100%;
}

.label-text {
    font-size: 1.1rem;
    color: #1f2937;
    font-weight: 500;
    width: 120px;
    text-align: right;
    margin-right: 16px;
}

:deep(.el-input-custom) {
    --el-input-height-default: 48px;
    --el-input-border-radius: 12px;
    --el-input-border-color: #d1d5db;
    --el-input-focus-border-color: #9333ea;
    --el-input-focus-box-shadow: 0 0 0 2px rgba(147, 51, 234, 0.1);
    font-size: 1rem;
    padding: 0 16px;
    flex: 1;
}

:deep(.el-form-item__error) {
    margin-left: 136px !important;
    padding-left: 0 !important;
    color: #dc2626 !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    padding-top: 4px !important;
}

.error-tip {
    font-size: 0.9rem;
    color: #dc2626;
    margin-top: 8px;
    margin-bottom: 6px;
    line-height: 1.5;
    padding-left: 0;
}

.modal-footer {
    padding: 24px 30px;
    border-top: 1px solid #f0f0f0;
    display: flex;
    justify-content: flex-end;
    gap: 16px;
}

.cancel-btn {
    padding: 12px 24px;
    border: 1px solid #d1d5db;
    border-radius: 12px;
    background: white;
    color: #6b7280;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
}

.cancel-btn:hover {
    background: #f9fafb;
    color: #1f2937;
}

.confirm-btn {
    padding: 12px 24px;
    border: none;
    border-radius: 12px;
    background: #9333ea;
    color: white;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.confirm-btn:hover {
    background: #7e22ce;
}
</style>
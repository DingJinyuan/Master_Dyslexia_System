<script setup>
import { ref, defineProps, defineEmits, onMounted, watch } from 'vue'
// Element Plus 组件导入
import {
    ElForm, ElFormItem, ElInput, ElMessage,
    ElTable, ElTableColumn, ElButton, ElTag,
    ElLoading
} from 'element-plus'
// 导入 API 方法
import {
    approval_requestAPI,
    approval_requestAPI_reject,
    approval_requestAPI_approve,
} from '@/apis/admin'

// 接收父组件传值
const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
    adminInfo: { // 管理员信息（可选）
        type: Object,
        default: () => ({
            username: '',
            role: 'admin'
        })
    }
})

// 定义事件
const emit = defineEmits(['close', 'approvalSuccess'])

// 响应式数据
const loading = ref(false) // 加载状态
const approvalList = ref([]) // 审批列表数据
const currentRequest = ref(null) // 当前选中的审批请求

// 关闭弹窗
const closeModal = () => {
    emit('close')
    // 重置状态
    approvalList.value = []
    currentRequest.value = null
    loading.value = false
}

// 获取审批列表（适配真实接口返回格式）
const getApprovalList = async () => {
    try {
        loading.value = true
        // 调用 API
        const res = await approval_requestAPI()
        // 适配真实返回：接口直接返回数组，无需取 res.data
        approvalList.value = res || []

        // 解析 payload_json 为对象，增强容错
        approvalList.value.forEach(item => {
            try {
                // 针对密码修改请求，隐藏敏感的密码哈希
                const payload = JSON.parse(item.payload_json || '{}')
                if (item.request_type === 'password_change' && payload.new_password_hash) {
                    payload.new_password_hash = '******（已隐藏敏感信息）'
                }
                item.payload = payload
            } catch (e) {
                console.warn('解析payload失败:', e)
                item.payload = { error: '解析失败', raw: item.payload_json }
            }
        })
    } catch (error) {
        console.error('获取审批列表异常:', error)
        ElMessage.error('获取审批列表失败：' + (error.message || '服务器错误'))
    } finally {
        loading.value = false
    }
}

// 批准请求
const approveRequest = async (requestId) => {
    try {
        loading.value = true
        const res = await approval_requestAPI_approve(requestId)
        ElMessage.success(res?.message || '批准成功！')
        // 刷新列表
        getApprovalList()
        emit('approvalSuccess', { type: 'approve', requestId })
    } catch (error) {
        ElMessage.error('批准失败：' + (error.response?.data?.detail || error.message || '服务器错误'))
    } finally {
        loading.value = false
    }
}

// 拒绝请求
const rejectRequest = async (requestId) => {
    try {
        loading.value = true
        const res = await approval_requestAPI_reject(requestId)
        ElMessage.success(res?.message || '拒绝成功！')
        // 刷新列表
        getApprovalList()
        emit('approvalSuccess', { type: 'reject', requestId })
    } catch (error) {
        ElMessage.error('拒绝失败：' + (error.response?.data?.detail || error.message || '服务器错误'))
    } finally {
        loading.value = false
    }
}

// 格式化请求类型显示
const formatRequestType = (type) => {
    const typeMap = {
        'register': '用户注册',
        'password_change': '密码修改',
        'info_update': '用户信息修改',
        'default': '未知请求'
    }
    return typeMap[type] || typeMap.default
}

// 格式化状态显示
const formatStatus = (status) => {
    const statusMap = {
        'pending': { text: '待审批', type: 'warning' },
        'approved': { text: '已批准', type: 'success' },
        'rejected': { text: '已拒绝', type: 'danger' },
        'default': { text: '未知状态', type: 'info' }
    }
    return statusMap[status] || statusMap.default
}

// 格式化时间（适配 ISO 时间格式）
const formatTime = (timeStr) => {
    if (!timeStr) return '暂无'
    // 处理 ISO 时间格式
    const date = new Date(timeStr)
    if (isNaN(date.getTime())) return '格式错误'

    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    })
}

// 组件挂载时加载数据
onMounted(() => {
    if (props.visible) {
        getApprovalList()
    }
})

// 监听弹窗显隐，打开时刷新列表
watch(() => props.visible, (newVal) => {
    if (newVal) {
        getApprovalList()
    }
})
</script>

<template>
    <!-- 遮罩层 -->
    <div class="modal-overlay" v-if="visible" @click="closeModal">
        <!-- 弹窗主体 - 调整为右侧显示 -->
        <div class="modal-content admin-approval-modal" @click.stop>
            <!-- 弹窗头部 -->
            <div class="modal-header">
                <h3>审批管理中心</h3>
                <button class="close-btn" @click="closeModal">×</button>
            </div>

            <!-- 弹窗主体内容 -->
            <div class="modal-body">
                <!-- 管理员信息展示 -->
                <div class="admin-info">
                    <div class="info-item">
                        <label>当前管理员：</label>
                        <span>{{ adminInfo.username || '超级管理员' }}</span>
                    </div>
                    <div class="info-item">
                        <label>权限等级：</label>
                        <el-tag type="primary" size="small">超级管理员</el-tag>
                    </div>
                </div>

                <!-- 审批列表 -->
                <div class="approval-list">
                    <h4>待处理审批请求</h4>
                    <!-- 空数据提示 -->
                    <div v-if="!loading && approvalList.length === 0" class="empty-tip">
                        暂无审批请求
                    </div>

                    <!-- Element Plus 表格 -->
                    <el-table v-loading="loading" :data="approvalList" border stripe highlight-current-row
                        @row-click="(row) => currentRequest = row" style="width: 100%; margin-top: 16px;" v-else>
                        <!-- 序号 -->
                        <el-table-column label="序号" type="index" width="80" align="center" />
                        <!-- 请求ID -->
                        <el-table-column prop="id" label="请求ID" width="120" align="center" />
                        <!-- 用户ID -->
                        <el-table-column prop="user_id" label="用户ID" width="120" align="center" />
                        <!-- 请求类型 -->
                        <el-table-column label="请求类型" width="140" align="center"
                            :formatter="(row) => formatRequestType(row.request_type)" />
                        <!-- 请求状态 -->
                        <el-table-column label="状态" width="120" align="center">
                            <template #default="scope">
                                <el-tag :type="formatStatus(scope.row.status).type" size="small">
                                    {{ formatStatus(scope.row.status).text }}
                                </el-tag>
                            </template>
                        </el-table-column>
                        <!-- 创建时间 -->
                        <el-table-column label="提交时间" width="200" align="center"
                            :formatter="(row) => formatTime(row.created_at)" />
                        <!-- 操作列 -->
                        <el-table-column label="操作" width="200" align="center">
                            <template #default="scope">
                                <el-button v-if="scope.row.status === 'pending'" type="success" size="small"
                                    icon="el-icon-check" @click.stop="approveRequest(scope.row.id)"
                                    style="margin-right: 8px;">
                                    批准
                                </el-button>
                                <el-button v-if="scope.row.status === 'pending'" type="danger" size="small"
                                    icon="el-icon-close" @click.stop="rejectRequest(scope.row.id)">
                                    拒绝
                                </el-button>
                                <span v-else class="disabled-text">已处理</span>
                            </template>
                        </el-table-column>
                    </el-table>

                    <!-- 请求详情（选中行时显示） -->
                    <div class="request-detail" v-if="currentRequest">
                        <h4 style="margin-top: 24px;">请求详情</h4>
                        <div class="detail-card">
                            <div class="detail-row">
                                <label class="detail-label">请求ID：</label>
                                <span>{{ currentRequest.id }}</span>
                            </div>
                            <div class="detail-row">
                                <label class="detail-label">用户ID：</label>
                                <span>{{ currentRequest.user_id }}</span>
                            </div>
                            <div class="detail-row">
                                <label class="detail-label">请求类型：</label>
                                <span>{{ formatRequestType(currentRequest.request_type) }}</span>
                            </div>
                            <div class="detail-row">
                                <label class="detail-label">提交时间：</label>
                                <span>{{ formatTime(currentRequest.created_at) }}</span>
                            </div>
                            <div class="detail-row">
                                <label class="detail-label">当前状态：</label>
                                <el-tag :type="formatStatus(currentRequest.status).type">
                                    {{ formatStatus(currentRequest.status).text }}
                                </el-tag>
                            </div>
                            <div class="detail-row" v-if="currentRequest.reviewed_at">
                                <label class="detail-label">处理时间：</label>
                                <span>{{ formatTime(currentRequest.reviewed_at) }}</span>
                            </div>
                            <div class="detail-row" v-if="currentRequest.reviewed_by">
                                <label class="detail-label">处理人ID：</label>
                                <span>{{ currentRequest.reviewed_by }}</span>
                            </div>
                            <div class="detail-row">
                                <label class="detail-label">请求内容：</label>
                                <pre class="payload-content">{{ JSON.stringify(currentRequest.payload, null, 2) }}</pre>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 弹窗底部 -->
            <div class="modal-footer">
                <el-button type="default" @click="closeModal" style="padding: 12px 24px; border-radius: 12px;">
                    关闭
                </el-button>
                <el-button type="primary" @click="getApprovalList" :loading="loading"
                    style="padding: 12px 24px; border-radius: 12px; background: #9333ea; border: none;">
                    刷新列表
                </el-button>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* 全局样式重置 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* 弹窗遮罩层 - 修改为居中显示 */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    /* 核心修改：从右侧改为居中 */
    justify-content: center;
    align-items: center;
    z-index: 9999;
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}

/* 弹窗主体 - 修改为居中弹窗样式 */
.admin-approval-modal {
    width: 1100px;
    /* 核心修改：最大高度改为80vh，移除100%高度 */
    max-height: 80vh;
    background: white;
    /* 核心修改：恢复圆角，移除右侧阴影 */
    border-radius: 24px;
    box-shadow: 0 30px 80px rgba(0, 0, 0, 0.18), 0 5px 15px rgba(0, 0, 0, 0.08);
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

/* 弹窗头部 */
.modal-header {
    padding: 24px 30px;
    border-bottom: 1px solid #f0f0f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-header h3 {
    font-size: 1.8rem;
    font-weight: 700;
    color: #1f2937;
    letter-spacing: -0.5px;
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

/* 弹窗主体内容 */
.modal-body {
    padding: 30px;
    flex: 1;
    overflow-y: auto;
}

/* 管理员信息 */
.admin-info {
    display: flex;
    gap: 24px;
    padding-bottom: 20px;
    border-bottom: 1px solid #f0f0f0;
    margin-bottom: 20px;
}

.info-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.1rem;
}

.info-item label {
    color: #6b7280;
    font-weight: 500;
}

.info-item span {
    color: #1f2937;
    font-weight: 600;
}

/* 审批列表 */
.approval-list h4 {
    font-size: 1.3rem;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 8px;
}

/* 空数据提示 */
.empty-tip {
    text-align: center;
    padding: 40px 0;
    color: #999;
    font-size: 16px;
}

/* 请求详情 */
.request-detail {
    margin-top: 20px;
}

.detail-card {
    background: #f9fafb;
    border-radius: 16px;
    padding: 20px;
    margin-top: 12px;
}

.detail-row {
    display: flex;
    align-items: flex-start;
    margin-bottom: 12px;
    font-size: 1rem;
}

.detail-label {
    width: 100px;
    color: #6b7280;
    font-weight: 500;
    flex-shrink: 0;
}

.payload-content {
    flex: 1;
    background: white;
    padding: 12px;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    color: #1f2937;
    font-size: 0.9rem;
    line-height: 1.6;
    max-height: 200px;
    overflow-y: auto;
}

/* 弹窗底部 */
.modal-footer {
    padding: 24px 30px;
    border-top: 1px solid #f0f0f0;
    display: flex;
    justify-content: flex-end;
    gap: 16px;
}

/* 已处理文本样式 */
.disabled-text {
    color: #999;
    cursor: not-allowed;
}

/* 适配 Element Plus 组件样式 */
:deep(.el-table) {
    --el-table-header-text-color: #1f2937;
    --el-table-row-hover-bg-color: rgba(147, 51, 234, 0.05);
    --el-table-border-color: #e5e7eb;
    border-radius: 12px;
    overflow: hidden;
}

:deep(.el-table th) {
    background: #f9fafb;
    font-weight: 600;
}

:deep(.el-button) {
    font-weight: 500;
    transition: all 0.2s;
}

:deep(.el-button--success):hover {
    background: #10b981;
    border-color: #10b981;
}

:deep(.el-button--danger):hover {
    background: #ef4444;
    border-color: #ef4444;
}

:deep(.el-button--primary):hover {
    background: #7e22ce;
}

:deep(.el-tag) {
    font-weight: 500;
}

/* 加载状态样式 */
:deep(.el-loading-mask) {
    border-radius: 12px;
}

/* 提升 ElMessage 层级 */
:deep(.el-message) {
    z-index: 10000 !important;
}
</style>
<!-- src/views/ReaderView/Components/SummaryModal.vue -->
<template>
  <teleport to="body">
    <div v-if="visible" class="modal-overlay" @click="handleClose">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>📝 文本摘要</h3>
          <button class="close-btn" @click="handleClose">×</button>
        </div>

        <div class="modal-body">
          <!-- 第一步：选择摘要长度 -->
          <div v-if="!selectedLength && !loading && !error && !result" class="length-selection">
            <h4>请选择摘要长度</h4>
            <div class="length-buttons">
              <button class="length-btn" @click="selectLength('简短')">
                简短（精炼核心，约100字）
              </button>
              <button class="length-btn" @click="selectLength('标准')">
                标准（完整覆盖，约300字）
              </button>
              <button class="length-btn" @click="selectLength('详细')">
                详细（深度解析，约500字）
              </button>
            </div>
          </div>

          <!-- 第二步：加载中（适配接口慢的提示） -->
          <div v-else-if="loading" class="loading-center">
            <div class="spinner"></div>
            <p>正在生成{{ selectedLength }}摘要（接口响应较慢，请耐心等待~）</p>
          </div>

          <!-- 第三步：错误 -->
          <div v-else-if="error" class="error-text">
            {{ error }}
            <button class="retry-btn" @click="resetSelection">重新选择长度</button>
          </div>

          <!-- 第四步：摘要结果（精准匹配返回字段） -->
          <div v-else-if="result" class="summary-container">
            <!-- 摘要文本（英文自动换行） -->
            <div class="summary-text">
              {{ result.summarizedText }}
            </div>

            <!-- 统计信息（完全匹配返回字段） -->
            <div class="summary-stats">
              <div class="stat-item">
                <span class="label">选择长度：</span>
                <span class="value">{{ selectedLength }}</span>
              </div>
              <div class="stat-item">
                <span class="label">语言类型：</span>
                <span class="value">{{ result.language === 'en' ? '英文' : '中文' }}</span>
              </div>
              <div class="stat-item">
                <span class="label">原文长度：</span>
                <span class="value">{{ result.originalLength }} 字符</span>
              </div>
              <div class="stat-item">
                <span class="label">摘要长度：</span>
                <span class="value">{{ result.summarizedLength }} 字符</span>
              </div>
              <div class="stat-item">
                <span class="label">可读性评分：</span>
                <span class="value">{{ result.readabilityScore.toFixed(1) }} / 100</span>
              </div>
              <div class="stat-item">
                <span class="label">易读等级：</span>
                <span class="value">{{ result.readabilityLevel }}</span>
              </div>
            </div>

            <!-- 重新生成按钮 -->
            <button class="regenerate-btn" @click="resetSelection">
              重新选择长度生成
            </button>
          </div>

          <!-- 兜底 -->
          <div v-else class="empty-text">
            <p>暂无摘要数据</p>
          </div>
        </div>

        <div class="modal-footer">
          <button class="confirm-btn" @click="handleClose">关闭</button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { defineProps, defineEmits, ref, watch } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  result: { type: [Object, null], default: null },
  originalText: { type: String, default: '' },
  selectedLength: { type: String, default: '' }
})

const emit = defineEmits(['close', 'generate-summary', 'reset-summary'])

// 选中的长度（优先用props，本地备份）
const localSelectedLength = ref(props.selectedLength)

// 选择长度
const selectLength = (length) => {
  localSelectedLength.value = length
  emit('generate-summary', length)
}

// 重置选择
const resetSelection = () => {
  localSelectedLength.value = ''
  emit('reset-summary')
}

const handleClose = () => {
  resetSelection()
  emit('close')
}

// 监听props变化
watch(() => props.selectedLength, (val) => {
  localSelectedLength.value = val
})

watch(() => props.visible, (isVisible) => {
  if (!isVisible) {
    localSelectedLength.value = ''
  }
})
</script>

<style scoped>
/* 基础样式 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  /* 加宽适配英文显示 */
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

/* 头部 */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #1f2937;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #6b7280;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #ef4444;
}

/* 主体 */
.modal-body {
  min-height: 200px;
  padding: 8px 0;
}

/* 长度选择 */
.length-selection {
  padding: 16px 0;
  text-align: center;
}

.length-selection h4 {
  margin: 0 0 20px 0;
  font-size: 16px;
  color: #1f2937;
}

.length-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.length-btn {
  padding: 12px;
  background: white;
  border: 1px solid #2563eb;
  border-radius: 8px;
  color: #2563eb;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.length-btn:hover {
  background: #eff6ff;
  border-color: #1d4ed8;
}

/* 加载状态 */
.loading-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  100% {
    transform: rotate(360deg);
  }
}

/* 错误提示 */
.error-text {
  color: #ef4444;
  text-align: center;
  padding: 16px;
  line-height: 1.5;
}

.retry-btn {
  margin-top: 12px;
  padding: 6px 12px;
  background: white;
  border: 1px solid #2563eb;
  border-radius: 4px;
  color: #2563eb;
  font-size: 12px;
  cursor: pointer;
}

/* 空数据提示 */
.empty-text {
  text-align: center;
  padding: 16px;
  color: #6b7280;
}

/* 摘要内容（适配英文换行） */
.summary-container {
  padding: 8px 0;
}

.summary-text {
  line-height: 1.8;
  color: #333;
  margin: 8px 0 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  white-space: pre-wrap;
  /* 英文自动换行 */
  word-wrap: break-word;
  /* 长单词换行 */
}

/* 统计信息 */
.summary-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  font-size: 14px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
}

.label {
  color: #6b7280;
}

.value {
  font-weight: 600;
  color: #1f2937;
}

/* 重新生成按钮 */
.regenerate-btn {
  margin-top: 16px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
  width: 100%;
}

.regenerate-btn:hover {
  background: #f9fafb;
}

/* 底部按钮 */
.modal-footer {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.confirm-btn {
  padding: 8px 24px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 14px;
}

.confirm-btn:hover {
  background: #1d4ed8;
}
</style>

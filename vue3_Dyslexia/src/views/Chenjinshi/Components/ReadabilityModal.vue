<template>
  <teleport to="body">
    <div v-if="visible" class="modal-overlay" @click="handleClose">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>📊 可读性评分结果</h3>
          <button class="close-btn" @click="handleClose">×</button>
        </div>

        <div class="modal-body">
          <!-- 加载中 -->
          <div v-if="loading" class="loading-center">
            <div class="spinner"></div>
            <p>正在计算评分...</p>
          </div>

          <!-- 错误 -->
          <div v-else-if="error" class="error-text">
            {{ error }}
          </div>

          <!-- 结果（实时响应 result 变化） -->
          <div v-else-if="result" class="result-container">
            <div class="score-row">
              <span class="label">综合评分：</span>
              <span class="value">{{ result.readabilityScore.toFixed(1) }} / 100</span>
            </div>
            <div class="score-row">
              <span class="label">语言类型：</span>
              <span class="value">{{ result.language === 'en' ? '英文' : '中文' }}</span>
            </div>
            <div class="score-row">
              <span class="label">易读等级：</span>
              <span class="value">{{ result.level }}</span>
            </div>
            <div class="stats-section" v-if="result.statistics">
              <h4>文本统计</h4>
              <div class="score-row">
                <span class="label">总词汇数：</span>
                <span class="value">{{ result.statistics.wordCount }}</span>
              </div>
              <div class="score-row">
                <span class="label">总句子数：</span>
                <span class="value">{{ result.statistics.sentenceCount }}</span>
              </div>
              <div class="score-row">
                <span class="label">平均句长：</span>
                <span class="value">{{ result.statistics.avgSentenceLength.toFixed(1) }} 词</span>
              </div>
            </div>
          </div>

          <!-- 兜底 -->
          <div v-else class="empty-text">
            <p>暂无评分数据</p>
          </div>
        </div>

        <div class="modal-footer">
          <button class="confirm-btn" @click="handleClose">确定</button>
        </div>
      </div>
    </div>
    <div class="debug-info" style="font-size:12px; color:#999;">
      result = {{ JSON.stringify(result) }}
    </div>
  </teleport>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  result: { type: [Object, null], default: null }
})

const emit = defineEmits(['close'])

const handleClose = () => {
  emit('close')
}
</script>

<style scoped>
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
  max-width: 420px;
  padding: 24px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #6b7280;
}

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

.error-text {
  color: #ef4444;
  text-align: center;
  padding: 16px;
}

.empty-text {
  text-align: center;
  padding: 16px;
  color: #6b7280;
}

.result-container {
  padding: 8px 0;
}

.score-row {
  display: flex;
  justify-content: space-between;
  margin: 10px 0;
}

.label {
  color: #6b7280;
}

.value {
  font-weight: 600;
}

.stats-section {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #eee;
}

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
}
</style>

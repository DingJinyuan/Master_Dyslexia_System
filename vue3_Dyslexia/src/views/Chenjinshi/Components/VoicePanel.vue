<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  ttsState: {
    type: Object,
    required: true
  }
})

const emit = defineEmits([
  'toggle-start',
  'stop-reading',
  'speed-input'
])

// 语音速度变化
const onSpeedInput = () => {
  emit('speed-input')
}

// 开始/暂停
const toggleStart = () => {
  emit('toggle-start')
}

// 停止朗读
const stopReading = () => {
  emit('stop-reading')
}
</script>

<template>
  <div class="voice-panel" :class="{ show: ttsState.showPanel }">
    <div class="panel-section">
      <!-- 错误提示 -->
      <div v-if="ttsState.errorMessage" class="error-message">
        {{ ttsState.errorMessage }}
      </div>

      <!-- 音色选择（写死为有道有小美，禁用选择） -->
      <div class="section-title">选择音色</div>
      <select class="voice-control" disabled>
        <option value="youxiaomei">有道智云 - 有小美 (en-US)</option>
      </select>

      <!-- 速度调节 -->
      <div class="section-title">朗读速度</div>
      <input type="range" class="voice-control" min="0.5" max="2.0" step="0.1" v-model.number="ttsState.speed"
        @input="onSpeedInput" :disabled="ttsState.playing">
      <div class="speed-tip">当前速度: {{ ttsState.speedDisplay }}倍</div>

      <!-- 功能按钮 -->
      <button class="func-btn primary" @click="toggleStart" :disabled="ttsState.playing">
        <template v-if="ttsState.playing">
          <span class="loading-dot">●●●</span> 生成音频中...
        </template>
        <template v-else>
          {{ ttsState.isPlaying ? '暂停朗读' : '开始朗读' }}
        </template>
      </button>
      <button class="func-btn" @click="stopReading" :disabled="ttsState.playing">
        停止朗读
      </button>
    </div>
  </div>
</template>

<style scoped>
.voice-panel {
  position: absolute;
  top: 45px;
  right: 0;
  width: 280px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  padding: 16px;
  display: none;
  z-index: 101;
}

.voice-panel.show {
  display: block;
}

.panel-section {
  margin-bottom: 16px;
}

.section-title {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
  font-weight: 500;
}

.voice-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  margin-bottom: 8px;
  transition: border-color 0.2s;
}

.voice-control:focus {
  outline: none;
  border-color: #2563eb;
}

.voice-control:disabled {
  background-color: #f9fafb;
  cursor: not-allowed;
  opacity: 0.7;
}

.speed-tip {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 12px;
}

.func-btn {
  width: 100%;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  font-size: 14px;
  cursor: pointer;
  margin-top: 4px;
  transition: all 0.2s;
}

.func-btn:hover:not(:disabled) {
  background: #e5e7eb;
}

.func-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.func-btn.primary {
  background: #2563eb;
  color: white;
  border: none;
}

.func-btn.primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.error-message {
  color: #ef4444;
  font-size: 12px;
  padding: 6px 8px;
  background: #fef2f2;
  border-radius: 4px;
  margin-bottom: 12px;
  border: 1px solid #fee2e2;
}

/* 加载动画 */
.loading-dot {
  display: inline-block;
  margin-right: 6px;
  font-size: 10px;
  animation: loading 1.2s infinite ease-in-out;
}

@keyframes loading {

  0%,
  100% {
    transform: scale(0.8);
    opacity: 0.5;
  }

  50% {
    transform: scale(1.2);
    opacity: 1;
  }
}

/* 响应式适配 */
@media (max-width: 480px) {
  .voice-panel {
    width: 250px;
    padding: 12px;
  }
}
</style>

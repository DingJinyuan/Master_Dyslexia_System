<script setup>
import { ref, defineProps, defineEmits } from 'vue'

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

// 语音速度变化时触发
const onSpeedInput = () => {
  emit('speed-input')
}

// 开始 / 暂停
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
      <div v-if="ttsState.errorMessage" class="error-message">
        {{ ttsState.errorMessage }}
      </div>

      <div class="section-title">选择音色</div>
      <select v-model="ttsState.voiceType" class="voice-control">
        <option value="female_soft">轻柔女声</option>
        <option value="male_deep">沉稳男声</option>
        <option value="child">童声</option>
      </select>

      <div class="section-title">朗读速度</div>
      <input type="range" class="voice-control" min="0.5" max="2.0" step="0.1" v-model.number="ttsState.speed"
        @input="onSpeedInput">
      <div class="speed-tip">当前速度: {{ ttsState.speedDisplay }}倍</div>

      <button class="func-btn primary" @click="toggleStart">
        {{ ttsState.isPlaying ? '暂停朗读' : '开始朗读' }}
      </button>
      <button class="func-btn" @click="stopReading">停止朗读</button>
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
}

.voice-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  margin-bottom: 8px;
}

.speed-tip {
  font-size: 12px;
  color: #6b7280;
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

.func-btn:hover {
  background: #e5e7eb;
}

.func-btn.primary {
  background: #2563eb;
  color: white;
  border: none;
}

.func-btn.primary:hover {
  background: #1d4ed8;
}

.error-message {
  color: #ef4444;
  font-size: 12px;
  padding: 4px;
  background: #fef2f2;
  border-radius: 4px;
  margin-bottom: 8px;
}
</style>

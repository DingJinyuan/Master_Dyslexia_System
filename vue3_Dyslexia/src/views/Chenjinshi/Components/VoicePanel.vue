<script setup>
import { computed } from 'vue'

const props = defineProps({
  ttsState: { type: Object, required: true },
  voiceList: { type: Array, default: () => [] },
  selectedVoice: { type: String, default: '' }
})

const emit = defineEmits(['toggle-start', 'stop-reading', 'speed-input', 'update:selectedVoice'])

// 按语言分组
const voiceGroups = computed(() => {
  const groups = { zh: [], en: [], other: [] }
  props.voiceList.forEach(v => {
    const locale = (v.locale || '').toLowerCase()
    if (locale.startsWith('zh')) groups.zh.push(v)
    else if (locale.startsWith('en')) groups.en.push(v)
    else groups.other.push(v)
  })
  return groups
})

const onVoiceChange = (e) => {
  emit('update:selectedVoice', e.target.value)
}

const onSpeedInput = () => emit('speed-input')
const toggleStart = () => emit('toggle-start')
const stopReading = () => emit('stop-reading')
</script>

<template>
  <div class="voice-panel" :class="{ show: ttsState.showPanel }">
    <div class="panel-section">
      <!-- 错误提示 -->
      <div v-if="ttsState.errorMessage" class="error-message">
        {{ ttsState.errorMessage }}
      </div>

      <!-- 音色选择 -->
      <div class="section-title">选择音色</div>
      <select class="voice-control" :value="selectedVoice" @change="onVoiceChange">
        <optgroup v-if="voiceGroups.zh.length" label="中文音色">
          <option v-for="v in voiceGroups.zh" :key="v.name" :value="v.name">
            {{ v.friendlyName }}
          </option>
        </optgroup>
        <optgroup v-if="voiceGroups.en.length" label="English Voices">
          <option v-for="v in voiceGroups.en" :key="v.name" :value="v.name">
            {{ v.friendlyName }}
          </option>
        </optgroup>
        <optgroup v-if="voiceGroups.other.length" label="其他语言">
          <option v-for="v in voiceGroups.other" :key="v.name" :value="v.name">
            {{ v.friendlyName }}
          </option>
        </optgroup>
      </select>

      <!-- 速度调节 -->
      <div class="section-title">朗读速度</div>
      <input type="range" class="voice-control" min="0.5" max="2.0" step="0.1"
        v-model.number="ttsState.speed" @input="onSpeedInput"
        :disabled="ttsState.playing">
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
  position: fixed;
  top: 80px;
  right: 340px;
  width: 300px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  padding: 16px;
  display: none;
  z-index: 10000;
}
.voice-panel.show { display: block; }
.panel-section { margin-bottom: 16px; }
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
.voice-control:focus { outline: none; border-color: #2563eb; }
.voice-control:disabled {
  background-color: #f9fafb;
  cursor: not-allowed;
  opacity: 0.7;
}
.speed-tip { font-size: 12px; color: #6b7280; margin-bottom: 12px; }
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
.func-btn:hover:not(:disabled) { background: #e5e7eb; }
.func-btn:disabled { cursor: not-allowed; opacity: 0.7; }
.func-btn.primary { background: #2563eb; color: white; border: none; }
.func-btn.primary:hover:not(:disabled) { background: #1d4ed8; }
.error-message {
  color: #ef4444;
  font-size: 12px;
  padding: 6px 8px;
  background: #fef2f2;
  border-radius: 4px;
  margin-bottom: 12px;
  border: 1px solid #fee2e2;
}
.loading-dot { display: inline-block; margin-right: 6px; font-size: 10px; animation: loading 1.2s infinite ease-in-out; }
@keyframes loading {
  0%, 100% { transform: scale(0.8); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 1; }
}
.mode-switch {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 12px;
}
.mode-switch input { cursor: pointer; }
.mode-label { font-size: 14px; color: #1f2937; }
@media (max-width: 480px) {
  .voice-panel { width: 260px; padding: 12px; }
}
</style>

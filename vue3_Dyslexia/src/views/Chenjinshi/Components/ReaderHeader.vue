<script setup>
import { defineProps, defineEmits } from 'vue'

// 接收父组件传递的参数
const props = defineProps({
  // 文档标题
  documentTitle: {
    type: String,
    default: '沉浸式阅读'
  },
  // 语音播放状态（仅用于按钮样式，不涉及 showPanel）
  isPlaying: {
    type: Boolean,
    default: false
  }
})

// 定义要触发的事件
const emit = defineEmits([
  'back',        // 返回按钮点击
  'toggleVoice', // 语音面板切换
  'openGuide'    // 指南弹窗打开
])

// 仅触发事件，逻辑由父组件处理
const handleBack = () => {
  emit('back')
}

// 语音面板切换 - 仅触发事件，不处理任何状态
const handleToggleVoice = (e) => {
  e.stopPropagation()
  emit('toggleVoice') // 父组件负责切换 showPanel 状态
}

// 打开指南弹窗
const handleOpenGuide = () => {
  emit('openGuide')
}
</script>

<template>
  <div class="top-bar">
    <!-- 左侧区域 -->
    <div class="top-left">
      <button class="back-btn" @click="handleBack()" title="返回上一页">←</button>
      <div class="book-title" :title="documentTitle">{{ documentTitle }}</div>
    </div>

    <!-- 右侧区域 - 仅根据 isPlaying 控制按钮样式，无 showPanel 引用 -->
    <div class="top-right">
      <button class="icon-btn" id="playBtn" :class="{ active: isPlaying }" @click="handleToggleVoice" title="语音朗读">
        {{ isPlaying ? '⏸️' : '🎧' }}
      </button>
      <button class="icon-btn" @click="handleOpenGuide" title="使用指南">❓</button>
    </div>
  </div>
</template>

<style scoped>
.top-bar {
  background: white;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e5e7eb;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  width: 100%;
  z-index: 9999;
  box-sizing: border-box;
  min-width: 280px;
  height: 70px;
}

.top-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  font-size: 20px;
  color: #4b5563;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.back-btn:hover {
  background: #f3f4f6;
  color: #1d4ed8;
}

.book-title {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
  flex-shrink: 1;
  line-height: 1;
}

.top-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.icon-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: #f9fafb;
  color: #4b5563;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.icon-btn:hover {
  background: #e5e7eb;
  color: #1d4ed8;
}

.icon-btn.active {
  background: #2563eb;
  color: #fff;
}

/* 小屏幕适配 */
@media (max-width: 480px) {
  .top-bar {
    padding: 12px 16px;
    height: 60px;
  }

  .book-title {
    max-width: 180px;
    font-size: 16px;
  }

  .back-btn,
  .icon-btn {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }
}

@media (max-width: 320px) {
  .book-title {
    max-width: 120px;
    font-size: 14px;
  }

  .back-btn,
  .icon-btn {
    width: 30px;
    height: 30px;
    font-size: 16px;
  }
}

:deep(.reader-container) {
  padding-top: 70px;
}

@media (max-width: 480px) {
  :deep(.reader-container) {
    padding-top: 60px;
  }
}
</style>

<!-- ReaderHeader.vue -->
<script setup>
import { defineProps, defineEmits } from 'vue'

// 接收父组件传递的参数
const props = defineProps({
  // 文档标题
  documentTitle: {
    type: String,
    default: '沉浸式阅读'
  },
  // 语音播放状态
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

// 语音面板切换
const handleToggleVoice = (e) => {
  e.stopPropagation()
  emit('toggleVoice')
}

// 打开指南弹窗
const handleOpenGuide = () => {
  emit('openGuide')
}
</script>

<template>
  <!-- 完全参考示例的外层容器结构 -->
  <div class="top-bar">
    <!-- 左侧区域：和示例完全一致 -->
    <div class="top-left">
      <button class="back-btn" @click="handleBack()">←</button>
      <div class="book-title">{{ documentTitle }}</div>
    </div>

    <!-- 右侧区域：替换示例的沉浸式按钮为语音+指南按钮 -->
    <div class="top-right">
      <button class="icon-btn" id="playBtn" :class="{ active: isPlaying }" @click="handleToggleVoice">
        🎧
      </button>
      <button class="icon-btn" @click="handleOpenGuide">❓</button>
    </div>
  </div>
</template>

<style scoped>
/* 完全复用示例的核心布局样式，仅微调右侧按钮样式 */
.top-bar {
  background: white;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  /* 核心：左右分布 */
  border-bottom: 1px solid #e5e7eb;
  position: fixed;
  /* 固定顶部 */
  top: 0;
  left: 0;
  right: 0;
  width: 100%;
  z-index: 9999;
  box-sizing: border-box;
  /* 内边距不影响宽度 */
  min-width: 280px;
  /* 最小宽度，防止布局崩溃 */
}

/* 左侧区域：完全复用示例样式 */
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
  /* 永不收缩 */
}

.back-btn:hover {
  background: #f3f4f6;
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
  /* 仅标题收缩 */
}

/* 右侧区域：适配两个图标按钮，保持布局对齐 */
.top-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  /* 永不收缩 */
}

.icon-btn {
  /* 对齐示例按钮的尺寸和交互 */
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
  /* 永不收缩 */
}

.icon-btn:hover {
  background: #e5e7eb;
}

.icon-btn.active {
  background: #2563eb;
  color: #fff;
}

/* 小屏幕适配：仅调整标题宽度，布局不变 */
@media (max-width: 480px) {
  .top-bar {
    padding: 12px 16px;
  }

  .book-title {
    max-width: 180px;
  }
}

/* 超小屏幕适配 */
@media (max-width: 320px) {
  .book-title {
    max-width: 120px;
    font-size: 16px;
  }

  .back-btn,
  .icon-btn {
    width: 32px;
    height: 32px;
    font-size: 18px;
  }
}

/* 兼容父容器的顶部内边距（和示例一致） */
:deep(.reader-container) {
  padding-top: 70px;
}
</style>

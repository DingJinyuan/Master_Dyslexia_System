<script setup>
import { useRouter, useRoute } from 'vue-router'

const props = defineProps({
  title: {
    type: String,
    default: '文档阅读'
  },
  // 必传：文档ID（用于跳转沉浸式页面）
  documentId: {
    type: [String, Number],
    required: true
  }
});

// 只保留back事件（toggle-panel无需向外暴露）
const emit = defineEmits(['back']);

// 路由实例
const router = useRouter()
const route = useRoute()

// 返回上一页（原有逻辑）
const handleBack = () => {
  emit('back')
}

// 组件内直接跳转沉浸式页面（核心）
const goToImmersive = () => {
  // 跳转到沉浸式路由 /chenjinshi/文档ID
  router.push({
    path: `/chenjinshi/${props.documentId}`,
    // 可选：记录跳转来源（方便沉浸式页面返回）
    query: { from: route.fullPath }
  })
}
</script>

<template>
  <div class="top-bar">
    <div class="top-left">
      <button class="back-btn" @click="handleBack">←</button>
      <div class="book-title">{{ title }}</div>
    </div>
    <!-- 点击直接触发组件内的跳转方法 -->
    <button class="immersive-btn" @click="goToImmersive">
      沉浸式阅读模式
    </button>
  </div>
</template>

<style scoped>
/* 样式完全保留不变 */
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
}

.immersive-btn {
  padding: 8px 16px;
  background: #1f2937;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.immersive-btn:hover {
  background: #374151;
}

:deep(.reader-container) {
  padding-top: 70px;
}
</style>

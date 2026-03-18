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

// 修改：返回按钮跳转到/upload页面
const handleBack = () => {
  // 先触发back事件（保留原有事件逻辑），再跳转
  //emit('back')
  router.push('/upload')
}

// 保持不变：沉浸式按钮跳转到原有沉浸式页面
const goToImmersive = () => {
  router.push({
    path: `/chenjinshi/${props.documentId}`,
    query: { from: route.fullPath }
  })
}
</script>

<template>
  <div class="top-bar">
    <div class="top-left">
      <!-- 返回按钮：点击跳转到/upload -->
      <button class="back-btn" @click="handleBack">←</button>
      <div class="book-title">{{ title }}</div>
    </div>
    <!-- 沉浸式按钮：保持原有跳转逻辑 -->
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

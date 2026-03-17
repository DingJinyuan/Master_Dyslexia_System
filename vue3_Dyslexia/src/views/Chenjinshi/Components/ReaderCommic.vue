<script setup>
import { ref, defineProps, defineEmits } from 'vue';

// 接收属性
const props = defineProps({
  // 漫画数据（生成后才有）
  comics: {
    type: Array,
    default: () => []
  },
  // 是否可见（生成漫画后显示）
  visible: {
    type: Boolean,
    default: false
  },
  // 是否正在生成漫画
  generating: {
    type: Boolean,
    default: false
  }
});

// 定义事件（移除 open-comic，只保留重新生成）
const emit = defineEmits(['regenerate-comic']);

// 重新生成漫画
const handleRegenerate = () => {
  emit('regenerate-comic');
};
</script>

<template>
  <div class="comic-panel-container">
    <!-- 漫画列主体 -->
    <div class="comic-panel" :style="{ transform: visible ? 'translateX(0)' : 'translateX(-100%)' }">
      <div class="panel-header">
        <span>🎨 生成的漫画</span>
        <button class="regenerate-btn" @click="handleRegenerate" :disabled="generating">
          {{ generating ? '生成中...' : '🔄 重新生成' }}
        </button>
      </div>

      <!-- 生成中提示 -->
      <div v-if="generating" class="generating-state">
        <div class="loading-spinner"></div>
        <p>正在为您生成漫画解读...</p>
      </div>

      <!-- 无漫画提示 -->
      <div v-else-if="comics.length === 0" class="no-comics">
        <p>点击右侧工具栏的「一键生成漫画」按钮</p>
        <p>即可为文档生成专属漫画解读</p>
      </div>

      <!-- 漫画列表（移除点击事件） -->
      <div v-else class="comics-list">
        <div v-for="comic in comics" :key="comic.id" class="comic-item">
          <img :src="comic.imageUrl" :alt="comic.caption" class="comic-thumbnail" loading="lazy"
            onerror="this.onerror=null; this.src='./static/default-comic.png';">
          <p class="comic-caption">{{ comic.caption }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 容器样式 */
.comic-panel-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 90;
  pointer-events: none;
}

/* 漫画列主体 */
.comic-panel {
  pointer-events: auto;
  width: 360px;
  height: 100vh;
  background: white;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.1);
  padding: 24px;
  overflow-y: auto;
  position: absolute;
  top: 40px;
  left: 0;
  transform: translateX(-100%);
  transition: transform 0.3s ease;

  /* 滚动条移到左侧 */
  direction: rtl;
  padding-left: 12px;
}

/* 滚动条样式（左侧） */
.comic-panel::-webkit-scrollbar {
  width: 6px;
  height: 6px;
  margin-left: 10px;
}

.comic-panel::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.comic-panel::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.comic-panel::-webkit-scrollbar-thumb:hover {
  background: #999;
}

/* 内部内容恢复正向排版 */
.comic-panel>* {
  direction: ltr;
}

/* 面板标题 */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
}

/* 重新生成按钮 */
.regenerate-btn {
  padding: 4px 8px;
  font-size: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  background: #f9fafb;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s;
}

.regenerate-btn:hover:not(:disabled) {
  background: #eff6ff;
  border-color: #2563eb;
  color: #2563eb;
}

.regenerate-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

/* 生成中状态 */
.generating-state {
  text-align: center;
  padding: 40px 20px;
  color: #666;
  font-size: 14px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

/* 无漫画提示 */
.no-comics {
  text-align: center;
  padding: 40px 20px;
  color: #666;
  font-size: 14px;
  line-height: 1.8;
}

/* 漫画列表 */
.comics-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 8px;
}

/* 漫画项（移除点击光标、hover阴影） */
.comic-item {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #eee;
}

/* 漫画缩略图 */
.comic-thumbnail {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

/* 漫画标题 */
.comic-caption {
  padding: 8px;
  font-size: 12px;
  color: #666;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>

<script setup>
import { ref, watch, computed, onErrorCaptured } from 'vue';

// 接收props
const props = defineProps({
  content: {
    type: String,
    default: ''
  },
  config: {
    type: Object,
    default: () => ({
      fontSize: 20,
      lineHeight: 1.8,
      letterSpacing: 0,
      selectedFont: 'system-ui',
      selectedTheme: 'warm'
    })
  },
  isPlainText: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['mouseup']);

// 错误状态
const hasError = ref(false);
const errorMessage = ref('');
const contentRef = ref(null);

// 处理纯文本转HTML（保留换行）
const processPlainText = (text) => {
  if (!text) return '<div style="color: #666; padding: 40px; text-align: center;">暂无内容</div>';
  // 转义特殊字符 + 替换换行
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
    .replace(/\n/g, '<br>');
};

// 计算属性：处理后的内容（核心：响应式更新）
const processedContent = computed(() => {
  console.log('【ReaderContent】内容更新：', props.content.substring(0, 50))
  if (props.isPlainText) {
    return processPlainText(props.content);
  }
  return props.content;
});

// 计算内容样式（整合主题颜色）
const contentStyle = computed(() => {
  const themeColorMap = {
    warm: '#92400e',
    dark: 'white',
    white: '#1f2937',
    blue: '#1e40af'
  };

  return {
    fontSize: `${props.config.fontSize || 20}px`,
    lineHeight: props.config.lineHeight || 1.8,
    letterSpacing: `${props.config.letterSpacing || 0}px`,
    wordSpacing: `${(props.config.wordSpacing || props.config.letterSpacing * 0.8) || 0}px`,
    fontFamily: props.config.selectedFont || 'system-ui',
    color: themeColorMap[props.config.selectedTheme] || '#92400e',
    transition: 'all 0.3s ease'
  };
});

// 捕获组件错误
onErrorCaptured((err, instance, info) => {
  console.error('ReaderContent 错误：', err, info);
  hasError.value = true;
  errorMessage.value = '内容渲染出错，请刷新重试';
  return true;
});

// 转发划词事件
const handleMouseUp = (e) => {
  emit('mouseup', e);
};
</script>

<template>
  <div class="reader-content-wrapper">
    <!-- 错误提示 -->
    <div v-if="hasError" class="error-container">
      <p class="error-text">{{ errorMessage }}</p>
      <button class="reload-btn" @click="hasError = false">重新加载</button>
    </div>

    <!-- 文档内容（核心修复：确保容器高度足够） -->
    <div v-else class="content-container" ref="contentRef">
      <div class="document-content" :style="contentStyle" v-html="processedContent" @mouseup="handleMouseUp"></div>
    </div>
  </div>
</template>

<style scoped>
/* 核心修复：确保内容容器占满父元素 */
.reader-content-wrapper {
  width: 100%;
  min-height: calc(100vh - 140px);
  /* 减去头部和padding高度 */
  overflow: hidden;
  position: relative;
}

/* 内容容器：允许滚动 */
.content-container {
  height: 100%;
  overflow-y: auto;
  padding: 20px;
  transition: background 0.3s ease, color 0.3s ease;
}

/* 文档内容：居中显示，优化排版 */
.document-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

/* 错误提示 */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
  color: #e53935;
}

.reload-btn {
  margin-top: 16px;
  padding: 8px 16px;
  border: 1px solid #e53935;
  border-radius: 4px;
  background: white;
  color: #e53935;
  cursor: pointer;
}

.reload-btn:hover {
  background: #ffebee;
}

/* 滚动条样式 */
.content-container::-webkit-scrollbar {
  width: 6px;
}

.content-container::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.content-container::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.content-container::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}
</style>

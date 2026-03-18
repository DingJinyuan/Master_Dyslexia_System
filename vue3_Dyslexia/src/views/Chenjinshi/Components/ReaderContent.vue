<script setup>
import { ref, watch, computed, onMounted, onErrorCaptured } from 'vue';

const props = defineProps({
  // ✅ 新增：接收词性标注加载状态
  posTaggingLoading: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  content: { type: String, default: '' },
  config: {
    type: Object,
    default: () => ({
      fontSize: 20,
      lineHeight: 1.8,
      letterSpacing: 0,
      selectedFont: 'system-ui',
    })
  },
  isPlainText: { type: Boolean, default: true },
  // ✅ 转发mouseup事件（划词功能需要）
  onMouseUp: { type: Function, default: () => { } }
});

// 定义事件（转发划词事件）
const emit = defineEmits(['mouseup']);

const hasError = ref(false);
const errorMessage = ref('');

// 核心：处理内容渲染（纯文本转义，HTML直接渲染）
const processContent = (text) => {
  if (props.isPlainText) {
    if (!text) return '<div style="color: #666; padding: 40px; text-align: center;">暂无内容</div>';
    // 纯文本转义，保留换行
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;')
      .replace(/\n/g, '<br>');
  } else {
    // HTML直接返回（词性标注后的内容），空内容显示加载提示
    return text || '<div style="color: #666; padding: 40px; text-align: center;">正在加载词性标注内容...</div>';
  }
};

// 计算最终渲染的内容
const processedContent = computed(() => {
  return processContent(props.content);
});

// 监听内容变化，重置错误状态
watch(() => props.content, () => {
  hasError.value = false;
  errorMessage.value = '';
}, { immediate: true });

// 计算内容样式
const contentStyle = computed(() => {
  if (!props.config) return {};
  return {
    fontSize: `${props.config.fontSize || 20}px`,
    lineHeight: props.config.lineHeight || 1.8,
    letterSpacing: `${props.config.letterSpacing || 0}px`,
    fontFamily: props.config.selectedFont || 'system-ui',
    // 确保词性标注的span能正常显示
    whiteSpace: 'normal',
    wordBreak: 'break-word'
  };
});

// 处理划词事件（转发给父组件）
const handleMouseUp = (e) => {
  emit('mouseup', e);
  // 兼容传入的onMouseUp函数
  if (typeof props.onMouseUp === 'function') {
    props.onMouseUp(e);
  }
};

// 捕获渲染错误
onErrorCaptured((err) => {
  console.error('ReaderContent 渲染错误：', err);
  hasError.value = true;
  errorMessage.value = '内容渲染出错，请重试';
  return true;
});
</script>

<template>
  <div class="reader-content-wrapper">
    <!-- 错误提示 -->
    <div v-if="hasError" class="error-container">
      <p class="error-text">{{ errorMessage }}</p>
      <button class="reload-btn" @click="hasError = false">重试</button>
    </div>

    <!-- 加载状态（文档加载 或 词性标注加载） -->
    <div v-else-if="loading || posTaggingLoading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>{{ loading ? '加载文档中...' : '词性标注接口响应中...（接口较慢，请勿刷新）' }}</p>
    </div>

    <!-- 核心内容渲染 -->
    <div v-else class="content-container">
      <div class="document-content" :style="contentStyle" v-html="processedContent" @mouseup="handleMouseUp"
        style="user-select: text !important; -webkit-user-select: text !important;"></div>
    </div>
  </div>
</template>

<style scoped>
.reader-content-wrapper {
  flex: 1;
  padding: 0;
  overflow: hidden;
  position: relative;
  min-height: calc(100vh - 60px);
  background: #fff9e6;
  /* 固定米黄色 */
}

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
  background: #fff;
  color: #e53935;
  cursor: pointer;
  transition: background 0.2s;
}

.reload-btn:hover {
  background: #ffebee;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
  color: #666;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #ff9800;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.content-container {
  position: relative;
  height: 100%;
  overflow-y: auto;
  padding: 20px;
  background: inherit;
}

.document-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  word-wrap: break-word;
  white-space: pre-wrap;
  color: #333;
  /* 确保词性标注的span不会挤在一起 */
  line-height: 2;
  font-size: 18px;
}

/* 滚动条美化 */
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

/* 词性标注的span样式优化（避免挤在一起） */
:deep(.document-content span) {
  margin: 0 1px;
  padding: 0 2px;
  box-sizing: border-box;
}
</style>

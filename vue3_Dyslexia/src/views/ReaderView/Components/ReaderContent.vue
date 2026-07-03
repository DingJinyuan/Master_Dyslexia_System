<script setup>
import { ref, watch, computed, onMounted, onErrorCaptured } from 'vue';

// 接收props（原有代码不变）
const props = defineProps({
  loading: { type: Boolean, default: false },
  content: { type: String, default: '' },
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
  isPlainText: { type: Boolean, default: true }
});

const hasError = ref(false);
const errorMessage = ref('');
const contentRef = ref(null);

// 原有方法不变
const processPlainText = (text) => {
  if (!text) return '';
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
    .replace(/\n/g, '<br>')
};

const processedContent = computed(() => {
  if (props.isPlainText) {
    return processPlainText(props.content);
  }
  return props.content;
});

watch(() => props.content, () => {
  hasError.value = false;
  errorMessage.value = '';
}, { immediate: true });

// ========== 仅新增/修改这部分背景相关逻辑 ==========
// 计算主题对应的背景和文字颜色
const themeStyle = computed(() => {
  const themeStyles = {
    warm: { background: '#fff9e6', color: '#92400e' },
    dark: { background: '#1f2937', color: 'white' },
    white: { background: '#ffffff', color: '#1f2937' },
    blue: { background: '#eff6ff', color: '#1e40af' }
  };
  return themeStyles[props.config.selectedTheme] || themeStyles.warm;
});

// 原有内容样式增加文字颜色绑定
const contentStyle = computed(() => {
  if (!props.config) return {};
  return {
    fontSize: `${props.config.fontSize || 20}px`,
    lineHeight: props.config.lineHeight || 1.8,
    letterSpacing: `${props.config.letterSpacing || 0}px`,
    fontFamily: props.config.selectedFont || 'system-ui',
    transition: 'all 0.3s ease',
    color: themeStyle.value.color // 仅新增这一行
  };
});

// 监听主题变化实时更新背景
watch(() => props.config.selectedTheme, () => {
  if (contentRef.value) {
    contentRef.value.style.background = themeStyle.value.background;
  }
}, { immediate: true });
// ========== 背景相关修改结束 ==========

onErrorCaptured((err, instance, info) => {
  console.error('ReaderContent 组件错误：', err, info);
  hasError.value = true;
  errorMessage.value = '内容渲染出错，请刷新重试';
  return true;
});

onMounted(() => {
  // 仅修改初始化背景逻辑
  if (contentRef.value && props.config) {
    contentRef.value.style.background = themeStyle.value.background;
  }
});
</script>

<template>
  <div class="reader-content-wrapper">
    <div v-if="hasError" class="error-container">
      <p class="error-text">{{ errorMessage }}</p>
      <button class="reload-btn" @click="hasError = false">重新加载</button>
    </div>

    <div v-else-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 仅新增ref绑定 -->
    <div v-else class="content-container" ref="contentRef">
      <div class="document-content" :style="contentStyle" v-html="processedContent"></div>
    </div>
  </div>
</template>

<!-- 样式完全不变 -->
<style scoped>
.reader-content-wrapper {
  flex: 1;
  padding: 0;
  overflow: hidden;
  position: relative;
  min-height: calc(100vh - 60px);
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
  background: white;
  color: #e53935;
  cursor: pointer;
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
  margin-bottom: 16px;
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
  transition: background 0.3s ease, color 0.3s ease;
}

.document-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

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

<script setup>
import { ref, watch, onMounted } from 'vue';
import FontSelector from '@/views/ReaderView/Components/FontSelector.vue';

const props = defineProps({
  config: {
    type: Object,
    required: true,
    default: () => ({
      selectedFont: 'system-ui',
      fontSize: 22,
      lineHeight: 2.2,
      letterSpacing: 1.5,
      selectedColor: '#ffeb3b',
      highlighted: false,
      enableRuler: false,
      enableFocus: false,
      rulerHeight: 28,
      focusHeight: 220
    })
  },
  isTextOptimized: {
    type: Boolean,
    default: false
  },
  // 新增：接收防抖状态，控制按钮禁用
  isGenerating: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits([
  'open-modal',
  'open-comic-modal',
  'optimize-text',
  'restore-text',
  'calculate-readability',
  'generate-summary' // 新增：触发生成摘要
]);

const readerPanelRef = ref(null);
const panelVisible = ref(false);
const CONTENT_MAX_WIDTH = 800;

// 字体列表
const fontList = [
  { key: 'system-ui', label: '默认字体' },
  { key: 'SimSun', label: '宋体' },
  { key: 'KaiTi', label: '楷体' },
  { key: 'Microsoft YaHei', label: '微软雅黑' },
  { key: 'Arial', label: 'Arial' },
  { key: 'Times New Roman', label: 'Times New Roman' },
  { key: 'Lexend', label: 'Lexend' },
  { key: 'Inclusive Sans', label: 'Inclusive Sans' },
  { key: 'Andika New Basic', label: 'Andika New Basic' }
];

// 阅读辅助工具
const readingRuler = ref(null);
const focusGuide = ref(null);

// 面板显示逻辑
const handleMouseMovePanel = (e) => {
  const screenWidth = window.innerWidth;
  const contentRight = (screenWidth - CONTENT_MAX_WIDTH) / 2 + CONTENT_MAX_WIDTH;

  if (e.clientX > contentRight && (screenWidth - e.clientX) < 100) {
    panelVisible.value = true;
  } else if (e.clientX < contentRight - 50) {
    panelVisible.value = false;
  }
};

// 阅读尺切换
const toggleRuler = () => {
  props.config.enableRuler = !props.config.enableRuler;
  if (readingRuler.value) {
    readingRuler.value.style.display = props.config.enableRuler ? 'block' : 'none';
  }
  if (props.config.enableRuler) {
    document.addEventListener('mousemove', (e) => {
      if (readingRuler.value) {
        readingRuler.value.style.top = `${e.clientY - 14}px`;
      }
    });
  }
};

// 焦点引导屏切换
const toggleFocus = () => {
  props.config.enableFocus = !props.config.enableFocus;
  if (focusGuide.value) {
    focusGuide.value.style.display = props.config.enableFocus ? 'block' : 'none';
  }
  if (props.config.enableFocus) {
    document.addEventListener('mousemove', (e) => {
      if (focusGuide.value) {
        focusGuide.value.style.setProperty('--y', `${e.clientY - 110}px`);
      }
    });
  }
};

// 监听工具配置变化
watch(() => props.config.rulerHeight, (val) => {
  if (readingRuler.value) readingRuler.value.style.height = `${val}px`;
});

watch(() => props.config.focusHeight, (val) => {
  if (focusGuide.value) focusGuide.value.style.setProperty('--focus-height', `${val}px`);
});

watch(panelVisible, (val) => {
  if (readerPanelRef.value) {
    readerPanelRef.value.style.transform = val ? 'translateX(0)' : 'translateX(100%)';
  }
});

// 加载远程字体
const loadFonts = () => {
  if (!document.querySelector('link[href*="fonts.googleapis.com/css2?family=Lexend"]')) {
    const link1 = document.createElement('link');
    link1.rel = 'preconnect';
    link1.href = 'https://fonts.googleapis.com';
    document.head.appendChild(link1);

    const link2 = document.createElement('link');
    link2.rel = 'preconnect';
    link2.href = 'https://fonts.gstatic.com';
    link2.crossOrigin = '';
    document.head.appendChild(link2);

    const link3 = document.createElement('link');
    link3.rel = 'stylesheet';
    link3.href = 'https://fonts.googleapis.com/css2?family=Lexend:wght@300..900&family=Inclusive+Sans:ital@0;1&family=Andika+New+Basic:ital,wght@0,400;0,700;1,400;1,700&display=swap';
    document.head.appendChild(link3);
  }
};

// 生命周期
onMounted(() => {
  document.addEventListener('mousemove', handleMouseMovePanel);
  loadFonts();
});
</script>

<template>
  <div class="reader-panel-container">
    <div class="reader-panel" ref="readerPanelRef">
      <div class="panel-header">🛠️ 阅读设置</div>

      <!-- 字体选择器 -->
      <FontSelector :config="config" :font-list="fontList" @config-change="() => { }" />

      <!-- 文本优化 -->
      <div class="panel-section">
        <div class="section-title">文本优化</div>
        <button class="func-btn" :class="{ active: isTextOptimized }"
          @click="isTextOptimized ? emit('restore-text') : emit('optimize-text')">
          {{ isTextOptimized ? '恢复原始文本' : '📝 优化文本（易读版）' }}
        </button>
      </div>

      <!-- 阅读辅助工具 -->
      <div class="panel-section">
        <div class="section-title">阅读辅助</div>

        <button class="tool-btn" :class="{ active: config.enableRuler }" @click="toggleRuler">
          📏 阅读障碍尺
        </button>
        <div class="tool-control" v-if="config.enableRuler">
          <span class="control-label">尺高度：{{ config.rulerHeight }}px</span>
          <input type="range" class="slider" min="10" max="100" v-model.number="config.rulerHeight">
        </div>

        <button class="tool-btn" :class="{ active: config.enableFocus }" @click="toggleFocus">
          🎯 焦点引导屏
        </button>
        <div class="tool-control" v-if="config.enableFocus">
          <span class="control-label">可视高度：{{ config.focusHeight }}px</span>
          <input type="range" class="slider" min="50" max="500" v-model.number="config.focusHeight">
        </div>

        <button class="func-btn" @click="emit('open-modal', 'guide')">📖 阅读指南</button>
        <button class="func-btn" @click="emit('calculate-readability')">📊 可读性评分</button>
        <!-- 生成摘要按钮：增加防抖禁用逻辑 -->
        <button class="func-btn" @click="emit('generate-summary')" :disabled="isGenerating"
          :style="isGenerating ? { opacity: 0.7, cursor: 'not-allowed' } : {}">
          📝 生成文本摘要
        </button>
      </div>

      <!-- 漫画生成 -->
      <div class="panel-section">
        <button class="comic-btn" @click="emit('open-comic-modal')">
          🎨 一键生成漫画解读
        </button>
      </div>
    </div>
  </div>

  <!-- 阅读辅助工具容器 -->
  <div class="reader-tools-container">
    <div ref="readingRuler" class="reading-ruler"></div>
    <div ref="focusGuide" class="focus-guide"></div>
  </div>
</template>

<style scoped>
/* 保留原有样式，无修改 */
.reader-panel-container {
  position: fixed;
  top: 0;
  right: 0;
  width: 100vw;
  height: 100vh;
  z-index: 90;
  pointer-events: none;
}

.reader-panel {
  pointer-events: auto;
  width: 320px;
  height: 100vh;
  background: white;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.1);
  padding: 24px;
  overflow-y: auto;
  position: absolute;
  top: 40px;
  right: 0;
  transform: translateX(100%);
  transition: transform 0.3s ease;
  color: #1f2937;
}

.panel-header {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 24px;
  color: #1f2937;
}

.panel-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 12px;
}

.func-btn,
.tool-btn,
.comic-btn {
  width: 100%;
  padding: 12px;
  margin: 8px 0;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  font-size: 14px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s;
}

.func-btn:hover,
.tool-btn:hover {
  background: #f9fafb;
}

.func-btn.active,
.tool-btn.active {
  border-color: #2563eb;
  background: #eff6ff;
  color: #2563eb;
  font-weight: 500;
}

.comic-btn {
  background: #f97316;
  color: white;
  border-color: #f97316;
}

.comic-btn:hover {
  background: #ea580c;
}

.tool-control {
  margin: 4px 0 12px;
  padding: 0 4px;
}

.control-label {
  font-size: 12px;
  color: #6b7280;
  display: block;
  margin-bottom: 4px;
}

.slider {
  width: 100%;
  height: 6px;
  -webkit-appearance: none;
  background: #e2e8f0;
  border-radius: 3px;
  outline: none;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #2563eb;
  border-radius: 50%;
  cursor: pointer;
}

.reader-tools-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 998;
}

.reading-ruler {
  position: fixed;
  left: 0;
  right: 0;
  height: 28px;
  background: rgba(255, 235, 59, 0.2);
  border: 1px solid rgba(255, 152, 0, 0.5);
  pointer-events: none;
  z-index: 999;
  display: none;
}

.focus-guide {
  position: fixed;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  display: none;
  z-index: 998;
  --y: 0px;
  --focus-height: 220px;
}

.focus-guide::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: var(--y);
  background: rgba(0, 0, 0, 0.7);
}

.focus-guide::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  height: calc(100vh - var(--y) - var(--focus-height));
  background: rgba(0, 0, 0, 0.7);
}

.reader-panel::-webkit-scrollbar {
  width: 4px;
}

.reader-panel::-webkit-scrollbar-track {
  background: #f3f4f6;
}

.reader-panel::-webkit-scrollbar-thumb {
  background: #d1d5db;
}
</style>

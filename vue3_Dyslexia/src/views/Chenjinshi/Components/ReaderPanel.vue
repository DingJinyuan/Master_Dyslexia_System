<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue';

// 引入字体选择组件
import FontSelector from '@/views/ReaderView/Components/FontSelector.vue';

// 接收属性
const props = defineProps({
  config: {
    type: Object,
    required: true,
    default: () => ({
      selectedFont: 'system-ui',
      fontSize: 22,
      lineHeight: 2.2,
      letterSpacing: 1.5,
      selectedTheme: 'warm',
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
  }
});

// 定义事件
const emit = defineEmits(['open-modal', 'open-comic-modal', 'optimize-text', 'restore-text']);

// 面板状态
const readerPanelRef = ref(null);
const panelContainerRef = ref(null);
const panelVisible = ref(false);
const CONTENT_MAX_WIDTH = 1000;

// 字体列表
const fontList = [
  { key: 'system-ui', label: '默认字体' },
  { key: 'SimSun', label: '宋体' },
  { key: 'KaiTi', label: '楷体' },
  { key: 'Microsoft YaHei', label: '微软雅黑' },
  { key: 'STSong', label: '宋体-繁' },
  { key: 'STKaiti', label: '楷体-繁' },
  { key: 'Arial', label: 'Arial' },
  { key: 'Times New Roman', label: 'Times New Roman' },
  { key: 'OpenDyslexic', label: 'OpenDyslexic' },
  { key: 'OpenDyslexic3', label: 'OpenDyslexic3' },
  { key: 'OpenDyslexicAlta', label: 'OpenDyslexicAlta' },
  { key: 'OpenDyslexicMono', label: 'OpenDyslexicMono' },
  { key: 'Lexend', label: 'Lexend' },
  { key: 'Inclusive Sans', label: 'Inclusive Sans' },
  { key: 'Andika New Basic', label: 'Andika New Basic' }
];

// 主题列表
const themeList = [
  { key: 'warm', label: '暖黄色', bg: '#fff9e6', color: '#92400e' },
  { key: 'dark', label: '护眼黑', bg: '#1f2937', color: 'white' },
  { key: 'white', label: '纯白色', bg: 'white', color: '#1f2937' },
  { key: 'blue', label: '天空蓝', bg: '#eff6ff', color: '#1e40af' }
];

// 工具引用
const readingRuler = ref(null);
const focusGuide = ref(null);

// 面板显隐逻辑（鼠标靠近右侧时显示）
const handleMouseMovePanel = (e) => {
  const screenWidth = window.innerWidth;
  const contentRight = (screenWidth - CONTENT_MAX_WIDTH) / 2 + CONTENT_MAX_WIDTH;
  if (e.clientX > contentRight && (screenWidth - e.clientX) < 100) {
    panelVisible.value = true;
  } else if (e.clientX < contentRight - 50) {
    panelVisible.value = false;
  }
};

// 切换主题
const changeTheme = (themeKey) => {
  props.config.selectedTheme = themeKey;
  const theme = themeList.find(t => t.key === themeKey);
  if (theme) {
    document.body.style.background = theme.bg;
    const el = document.querySelector('.document-content');
    if (el) el.style.color = theme.color;
  }
};

// 切换阅读障碍尺
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

// 切换焦点引导屏
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

// 监听配置变化
watch(() => props.config.rulerHeight, (val) => {
  if (readingRuler.value && props.config.enableRuler) {
    readingRuler.value.style.height = `${val}px`;
  }
});

watch(() => props.config.focusHeight, (val) => {
  if (focusGuide.value && props.config.enableFocus) {
    focusGuide.value.style.setProperty('--focus-height', `${val}px`);
  }
});

watch(panelVisible, (val) => {
  if (readerPanelRef.value) {
    readerPanelRef.value.style.transform = val ? 'translateX(0)' : 'translateX(100%)';
  }
});

// 加载特殊字体
const loadFonts = () => {
  // 加载OpenDyslexic字体（CDN）
  if (!document.querySelector('link[href*="fonts.cdnfonts.com/css/opendyslexic"]')) {
    const odLink = document.createElement('link');
    odLink.rel = 'stylesheet';
    odLink.href = 'https://fonts.cdnfonts.com/css/opendyslexic';
    document.head.appendChild(odLink);
  }

  // 加载Google Fonts
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
  changeTheme(props.config.selectedTheme);
  loadFonts();
});

onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMovePanel);
  const el = document.querySelector('.document-content');
  if (el) {
    el.style.fontFamily = '';
    el.style.color = '';
  }
  document.body.style.background = '';
});
</script>

<template>
  <!-- 工具栏容器 -->
  <div class="reader-panel-container" ref="panelContainerRef">
    <!-- 工具栏主体 -->
    <div class="reader-panel" ref="readerPanelRef">
      <div class="panel-header">🛠️ 沉浸式阅读助手</div>

      <!-- 字体选择 -->
      <div class="panel-section">
        <FontSelector :config="config" :font-list="fontList" />
      </div>

      <!-- 主题选择 -->
      <div class="panel-section">
        <div class="section-title">阅读主题</div>
        <div class="theme-buttons">
          <button v-for="theme in themeList" :key="theme.key" class="theme-btn"
            :class="{ active: config.selectedTheme === theme.key }"
            :style="{ background: theme.bg, color: theme.color }" @click="changeTheme(theme.key)">
            {{ theme.label }}
          </button>
        </div>
      </div>

      <!-- 文本优化 -->
      <div class="panel-section">
        <div class="section-title">文本优化</div>
        <button class="func-btn" :class="{ active: isTextOptimized }"
          @click="isTextOptimized ? emit('restore-text') : emit('optimize-text')">
          {{ isTextOptimized ? '恢复原始文本' : '📝 优化文本（易读版）' }}
        </button>
      </div>

      <!-- 阅读障碍辅助 -->
      <div class="panel-section">
        <div class="section-title">阅读障碍辅助</div>

        <!-- 阅读障碍尺 -->
        <button class="tool-btn" :class="{ active: config.enableRuler }" @click="toggleRuler">
          📏 阅读障碍尺
        </button>
        <div class="tool-control" v-if="config.enableRuler">
          <span class="control-label">尺高度：{{ config.rulerHeight }}px</span>
          <input type="range" class="slider" min="10" max="100" v-model.number="config.rulerHeight">
        </div>

        <!-- 焦点引导屏 -->
        <button class="tool-btn" :class="{ active: config.enableFocus }" @click="toggleFocus">
          🎯 焦点引导屏
        </button>
        <div class="tool-control" v-if="config.enableFocus">
          <span class="control-label">可视高度：{{ config.focusHeight }}px</span>
          <input type="range" class="slider" min="50" max="500" v-model.number="config.focusHeight">
        </div>

        <!-- 阅读指南 -->
        <button class="func-btn" @click="emit('open-modal', 'guide')">📖 阅读指南</button>
      </div>

      <!-- 漫画生成 -->
      <div class="panel-section">
        <button class="comic-btn" @click="emit('open-comic-modal')">
          🎨 一键生成漫画解读
        </button>
      </div>
    </div>
  </div>

  <!-- 辅助工具 DOM -->
  <div class="reader-tools-container">
    <div ref="readingRuler" class="reading-ruler"></div>
    <div ref="focusGuide" class="focus-guide"></div>
  </div>
</template>

<style scoped>
/* 工具栏容器 */
.reader-panel-container {
  position: fixed;
  top: 0;
  right: 0;
  width: 100vw;
  height: 100vh;
  z-index: 90;
  pointer-events: none;
}

/* 工具栏主体 */
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
  border-radius: 8px 0 0 8px;
}

/* 面板标题 */
.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  padding-bottom: 12px;
  border-bottom: 1px solid #f3f4f6;
}

/* 面板分区 */
.panel-section {
  margin-bottom: 24px;
}

/* 分区标题 */
.section-title {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 12px;
  font-weight: 500;
}

/* 主题按钮组 */
.theme-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 16px;
}

/* 主题按钮 */
.theme-btn {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.theme-btn.active {
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
  font-weight: 500;
}

/* 工具按钮 */
.tool-btn {
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
  display: flex;
  align-items: center;
  gap: 8px;
}

.tool-btn:hover {
  background: #f9fafb;
  border-color: #b9c0ca;
}

.tool-btn.active {
  border-color: #2563eb;
  background: #eff6ff;
  color: #2563eb;
  font-weight: 500;
}

/* 工具控制项 */
.tool-control {
  margin: 4px 0 12px;
  padding: 0 4px 0 12px;
}

/* 控制项标签 */
.control-label {
  font-size: 12px;
  color: #6b7280;
  display: block;
  margin-bottom: 4px;
}

/* 滑块样式 */
.slider {
  width: 100%;
  height: 6px;
  -webkit-appearance: none;
  background: #e2e8f0;
  border-radius: 3px;
  outline: none;
  margin-bottom: 16px;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #2563eb;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s;
}

.slider::-webkit-slider-thumb:hover {
  background: #1d4ed8;
  transform: scale(1.1);
}

/* 功能按钮 */
.func-btn {
  width: 100%;
  padding: 10px;
  margin-top: 8px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.func-btn:hover {
  background: #f3f4f6;
}

.func-btn.active {
  background: #dbeafe;
  border-color: #2563eb;
  color: #2563eb;
  font-weight: 500;
}

/* 漫画按钮 */
.comic-btn {
  width: 100%;
  padding: 12px;
  background: #fce7f3;
  color: #be185d;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  margin-top: 16px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
}

.comic-btn:hover {
  background: #fbcfe8;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(190, 24, 93, 0.15);
}

/* 辅助工具容器 */
.reader-tools-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 998;
}

/* 阅读障碍尺 */
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
  backdrop-filter: blur(1px);
}

/* 焦点引导屏 */
.focus-guide {
  position: fixed;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 998;
  display: none;
  background: linear-gradient(to bottom,
      rgba(0, 0, 0, 0.7) 0%,
      rgba(0, 0, 0, 0) var(--y),
      rgba(0, 0, 0, 0) calc(var(--y) + var(--focus-height)),
      rgba(0, 0, 0, 0.7) 100%);
}
</style>

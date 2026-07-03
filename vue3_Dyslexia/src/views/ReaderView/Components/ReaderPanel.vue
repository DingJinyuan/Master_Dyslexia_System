<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue';
import FontSelector from './FontSelector.vue';

const props = defineProps({
  config: {
    type: Object,
    required: true,
    default: () => ({
      selectedFont: 'system-ui',
      fontSize: 20,
      lineHeight: 1.8,
      letterSpacing: 0,
      selectedTheme: 'warm',
      selectedColor: '#ffeb3b',
      highlighted: false,
      enableRuler: false,
      enableFocus: false,
      enableScroll: false,
      rulerHeight: 28,
      focusHeight: 220,
      scrollSpeed: 1
    })
  }
});

const emit = defineEmits(['extract-keywords', 'clear-highlight', 'open-modal']);

const readerPanelRef = ref(null);
const panelContainerRef = ref(null);
const panelVisible = ref(false);
const CONTENT_MAX_WIDTH = 800;

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

const themeList = [
  { key: 'warm', label: '暖黄色', bg: '#fff9e6', color: '#92400e' },
  { key: 'dark', label: '护眼黑', bg: '#1f2937', color: 'white' },
  { key: 'white', label: '纯白色', bg: 'white', color: '#1f2937' },
  { key: 'blue', label: '天空蓝', bg: '#eff6ff', color: '#1e40af' }
];

const colorList = [
  '#ffeb3b', '#ff9800', '#f44336', '#e91e63',
  '#9c27b0', '#673ab7', '#2196f3', '#009688', '#4caf50'
];

const handleMouseMovePanel = (e) => {
  const screenWidth = window.innerWidth;
  const contentRight = (screenWidth - CONTENT_MAX_WIDTH) / 2 + CONTENT_MAX_WIDTH;
  if (e.clientX > contentRight && (screenWidth - e.clientX) < 100) {
    panelVisible.value = true;
  } else if (e.clientX < contentRight - 50) {
    panelVisible.value = false;
  }
};

// ========== 仅修改changeTheme方法 ==========
const changeTheme = (themeKey) => {
  // 原有逻辑保留，仅新增更新父容器背景的逻辑
  props.config.selectedTheme = themeKey;
  const theme = themeList.find(t => t.key === themeKey);
  if (theme) {
    document.body.style.background = theme.bg;
    const el = document.querySelector('.document-content');
    if (el) {
      el.style.color = theme.color;
      // 仅新增这一行：更新内容容器背景
      el.parentElement.style.background = theme.bg;
    }
    // 新增：更新根容器背景
    const rootEl = document.querySelector('.reader-container');
    if (rootEl) {
      rootEl.style.background = theme.bg;
    }
  }
};
// ========== 背景相关修改结束 ==========

const changeColor = (color) => {
  props.config.selectedColor = color;
  if (props.config.highlighted) {
    emit('extract-keywords');
  }
};

const readingRuler = ref(null);
const focusGuide = ref(null);
let scrollTimer = null;

const toggleRuler = () => {
  props.config.enableRuler = !props.config.enableRuler;
  if (readingRuler.value) {
    readingRuler.value.style.display = props.config.enableRuler ? 'block' : 'none';
  }
  if (props.config.enableRuler) {
    document.addEventListener('mousemove', e => {
      if (readingRuler.value) {
        readingRuler.value.style.top = e.clientY - 14 + 'px';
      }
    });
  }
};

const toggleFocus = () => {
  props.config.enableFocus = !props.config.enableFocus;
  if (focusGuide.value) {
    focusGuide.value.style.display = props.config.enableFocus ? 'block' : 'none';
  }
  if (props.config.enableFocus) {
    document.addEventListener('mousemove', e => {
      if (focusGuide.value) {
        focusGuide.value.style.setProperty('--y', e.clientY - 110 + 'px');
      }
    });
  }
};

const toggleScroll = () => {
  props.config.enableScroll = !props.config.enableScroll;
  if (scrollTimer) {
    clearInterval(scrollTimer);
    scrollTimer = null;
  }
  if (props.config.enableScroll) {
    const speed = props.config.scrollSpeed || 1;
    scrollTimer = setInterval(() => {
      window.scrollBy(0, speed);
    }, 60);
  }
};

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

watch(() => props.config.scrollSpeed, (val) => {
  if (props.config.enableScroll && scrollTimer) {
    clearInterval(scrollTimer);
    scrollTimer = setInterval(() => window.scrollBy(0, val || 1), 60);
  }
});

watch(panelVisible, (val) => {
  if (readerPanelRef.value) {
    readerPanelRef.value.style.transform = val ? 'translateX(0)' : 'translateX(100%)';
  }
});

onMounted(() => {
  document.addEventListener('mousemove', handleMouseMovePanel);
  changeTheme(props.config.selectedTheme);

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

  if (!document.querySelector('link[href*="fonts.cdnfonts.com/css/opendyslexic"]')) {
    const odLink = document.createElement('link');
    odLink.rel = 'stylesheet';
    odLink.href = 'https://fonts.cdnfonts.com/css/opendyslexic';
    document.head.appendChild(odLink);
  }
});

onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMovePanel);
  if (scrollTimer) clearInterval(scrollTimer);
  const el = document.querySelector('.document-content');
  if (el) {
    el.style.fontFamily = '';
    el.style.color = '';
  }
  document.body.style.background = '';
});
</script>

<template>
  <div class="reader-panel-container" ref="panelContainerRef">
    <div class="reader-panel" ref="readerPanelRef">
      <div class="panel-header">🛠️ 阅读助手</div>
      <FontSelector :config="config" :font-list="fontList" @config-change="() => { }" />
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
      <div class="panel-section">
        <div class="section-title">高亮颜色</div>
        <div class="highlight-color-buttons">
          <button v-for="color in colorList" :key="color" class="color-btn"
            :class="{ active: config.selectedColor === color }" :style="{ background: color }"
            @click="changeColor(color)" />
        </div>
        <button class="func-btn" @click="emit('extract-keywords'); config.highlighted = true">
          LLM关键词提取并高亮
        </button>
        <button class="func-btn" @click="emit('clear-highlight'); config.highlighted = false">
          清除高亮
        </button>
      </div>
      <div class="panel-section">
        <div class="section-title">阅读障碍辅助</div>
        <button class="tool-btn" :class="{ active: config.enableRuler }" @click="toggleRuler">
          📏 阅读障碍尺
        </button>
        <div class="tool-control">
          <span class="control-label">尺高度：{{ config.rulerHeight }}px</span>
          <input type="range" class="slider" min="10" max="100" v-model="config.rulerHeight">
        </div>
        <button class="tool-btn" :class="{ active: config.enableFocus }" @click="toggleFocus">
          🎯 焦点引导屏
        </button>
        <div class="tool-control">
          <span class="control-label">可视高度：{{ config.focusHeight }}px</span>
          <input type="range" class="slider" min="50" max="500" v-model="config.focusHeight">
        </div>
        <button class="tool-btn" :class="{ active: config.enableScroll }" @click="toggleScroll">
          ↕️ 自动滚动
        </button>
        <div class="tool-control">
          <span class="control-label">滚动速度：{{ config.scrollSpeed }}px/帧</span>
          <input type="range" class="slider" min="0.5" max="5" step="0.5" v-model="config.scrollSpeed">
        </div>
        <button class="func-btn" @click="emit('open-modal', 'guide')">阅读指南</button>
      </div>
      <button class="summary-btn" @click="emit('open-modal', 'summary')">📝 LLM内容摘要</button>
    </div>
  </div>
  <div class="reader-tools-container">
    <div ref="readingRuler" class="reading-ruler"></div>
    <div ref="focusGuide" class="focus-guide"></div>
  </div>
</template>

<style scoped>
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
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
  font-size: 16px;
  font-weight: 600;
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

.theme-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 16px;
}

.theme-btn {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.theme-btn.active {
  border-color: #2563eb;
  background: #eff6ff;
  color: #2563eb;
  font-weight: 500;
}

.highlight-color-buttons {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}

.color-btn {
  height: 36px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  cursor: pointer;
  position: relative;
}

.color-btn.active::after {
  content: "✓";
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-weight: bold;
  font-size: 16px;
}

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
}

.tool-btn.active {
  border-color: #2563eb;
  background: #eff6ff;
  color: #2563eb;
  font-weight: 500;
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
  margin-bottom: 16px;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #2563eb;
  border-radius: 50%;
  cursor: pointer;
}

.func-btn {
  width: 100%;
  padding: 10px;
  margin-top: 8px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  font-size: 14px;
  cursor: pointer;
}

.summary-btn {
  width: 100%;
  padding: 12px;
  background: #d1fae5;
  color: #065f46;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  margin-top: 8px;
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
</style>

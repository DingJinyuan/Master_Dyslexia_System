<script setup>
import { ref, watch, onMounted, nextTick } from 'vue';
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
  },
  // 文本优化加载状态
  textOptimizeLoading: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits([
  'open-modal',
  'optimize-text',
  'restore-text',
  'calculate-readability',
  'generate-summary', // 新增：触发生成摘要
  'generate-mindmap', // 新增：触发生成思维导图
]);

const readerPanelRef = ref(null);
const panelVisible = ref(true); // 默认展开，字体设置始终可见
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

// 词性标注颜色图例（与后端 NLP 服务一致）
const posLegend = [
  { label: '名词 / Noun', color: '#4A90D9', keys: 'n, NOUN' },
  { label: '动词 / Verb', color: '#E74C3C', keys: 'v, VERB' },
  { label: '形容词 / Adj.', color: '#27AE60', keys: 'a, ADJ' },
  { label: '副词 / Adv.', color: '#F39C12', keys: 'd, ADV' },
  { label: '代词 / Pron.', color: '#1ABC9C', keys: 'r, PRON' },
  { label: '数/量词 / Num.', color: '#9B59B6', keys: 'm, q, NUM' },
  { label: '介词/连词', color: '#95A5A6', keys: 'p, c, ADP, CONJ' },
  { label: '助词/标点', color: '#BDC3C7', keys: 'u, w, PUNCT' },
]
const showPosLegend = ref(false)

// 词性颜色显隐开关
const togglePosColors = () => {
  props.config.showPosColors = !props.config.showPosColors
}

// 面板显示逻辑 — 默认展开，点击切换
const togglePanel = () => {
  panelVisible.value = !panelVisible.value
  if (readerPanelRef.value) {
    readerPanelRef.value.style.transform = panelVisible.value ? 'translateX(0)' : 'translateX(100%)'
  }
}

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
  loadFonts();
  nextTick(() => {
    if (readerPanelRef.value) {
      readerPanelRef.value.style.transform = 'translateX(0)'
    }
  })
});
</script>

<template>
  <div class="reader-panel-container">
    <div class="panel-tab" @click="togglePanel" :title="panelVisible ? '收起面板' : '展开面板'">
      <span>{{ panelVisible ? '▶' : '◀' }}</span>
    </div>
    <div class="reader-panel" ref="readerPanelRef">
      <div class="panel-header">
        <span>🛠️ 阅读设置</span>
        <button class="panel-minimize" @click="togglePanel">−</button>
      </div>

      <!-- 字体选择器 -->
      <FontSelector :config="config" :font-list="fontList" @config-change="() => { }" />

      <!-- 阅读主题 -->
      <div class="panel-section">
        <div class="section-title">阅读主题</div>
        <div class="theme-buttons">
          <button v-for="t in [{k:'warm',l:'暖黄'},{k:'dark',l:'护眼黑'},{k:'white',l:'纯白'},{k:'blue',l:'天空蓝'}]" :key="t.k"
            class="theme-btn" :class="{ active: config.selectedTheme === t.k }"
            :style="{ background: {warm:'#fff9e6',dark:'#1f2937',white:'#fff',blue:'#eff6ff'}[t.k], color: {warm:'#92400e',dark:'#e5e7eb',white:'#1f2937',blue:'#1e40af'}[t.k] }"
            @click="config.selectedTheme = t.k">{{ t.l }}</button>
        </div>
      </div>

      <!-- 显示模式 -->
      <div class="panel-section">
        <div class="section-title">显示模式</div>
        <div class="display-mode-switch">
          <button class="mode-btn" :class="{ active: config.displayMode === 'mixed' }" @click="config.displayMode = 'mixed'">
            📄📷 图文共存
          </button>
          <button class="mode-btn" :class="{ active: config.displayMode === 'separated' }" @click="config.displayMode = 'separated'">
            📄↔📷 图文分离
          </button>
        </div>
        <div class="mode-hint">
          {{ config.displayMode === 'mixed' ? '图片嵌入文本中，图文一起阅读' : '图片收至左侧栏，鼠标移到左边缘查看' }}
        </div>
      </div>

      <!-- 词性颜色 -->
      <div class="panel-section">
        <div class="section-title">词性标注颜色</div>
        <button class="tool-btn" :class="{ active: config.showPosColors }" @click="togglePosColors">
          🎨 {{ config.showPosColors ? '点击隐藏颜色' : '点击显示颜色' }}
        </button>
        <button class="legend-toggle" @click="showPosLegend = !showPosLegend">
          📖 {{ showPosLegend ? '收起图例' : '查看颜色图例' }}
        </button>
        <!-- 颜色图例 -->
        <div v-if="showPosLegend" class="pos-legend">
          <div v-for="item in posLegend" :key="item.label" class="legend-item">
            <span class="legend-chip" :style="{ background: item.color }"></span>
            <span class="legend-label">{{ item.label }}</span>
            <span class="legend-keys">{{ item.keys }}</span>
          </div>
        </div>
      </div>

      <!-- 文本优化 -->
      <div class="panel-section">
        <div class="section-title">文本优化</div>
        <button class="func-btn" :class="{ active: isTextOptimized }"
          @click="isTextOptimized ? emit('restore-text') : emit('optimize-text')" :disabled="textOptimizeLoading">
          {{ textOptimizeLoading ? '⏳ AI 优化中...' : (isTextOptimized ? '🔄 恢复原始文本' : '📝 AI 优化文本（易读版）') }}
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

        <button class="tool-btn" :class="{ active: config.enableScroll }" @click="config.enableScroll = !config.enableScroll">
          ↕️ 自动滚动
        </button>
        <div class="tool-control" v-if="config.enableScroll">
          <span class="control-label">速度：{{ config.scrollSpeed }}px</span>
          <input type="range" class="slider" min="0.5" max="5" step="0.5" v-model.number="config.scrollSpeed">
        </div>

        <button class="func-btn" @click="emit('open-modal', 'guide')">📖 阅读指南</button>
        <button class="func-btn" @click="emit('calculate-readability')">📊 可读性评分</button>
        <!-- 生成摘要按钮：增加防抖禁用逻辑 -->
        <button class="func-btn" @click="emit('generate-summary')" :disabled="isGenerating"
          :style="isGenerating ? { opacity: 0.7, cursor: 'not-allowed' } : {}">
          📝 生成文本摘要
        </button>
        <button class="func-btn" @click="emit('generate-mindmap')">
          🧠 思维导图
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
.panel-tab {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 28px;
  height: 56px;
  background: white;
  border: 1px solid #e5e7eb;
  border-right: none;
  border-radius: 8px 0 0 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  pointer-events: auto;
  font-size: 14px;
  box-shadow: -2px 0 8px rgba(0,0,0,0.08);
  transition: all 0.2s;
  z-index: 91;
}
.panel-tab:hover { background: #eff6ff; border-color: #2563eb; }
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
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 24px;
  color: #1f2937;
}
.panel-minimize {
  width: 28px; height: 28px;
  border: none;
  background: #f3f4f6;
  border-radius: 6px;
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  transition: all 0.2s;
}
.panel-minimize:hover { background: #e5e7eb; color: #374151; }
.display-mode-switch { display: flex; gap: 6px; margin-bottom: 6px; }
.mode-btn {
  flex: 1;
  padding: 10px 8px;
  border: 2px solid #d1d5db;
  border-radius: 8px;
  background: white;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}
.mode-btn:hover { border-color: #2563eb; background: #f0f5ff; }
.mode-btn.active {
  border-color: #2563eb;
  background: #eff6ff;
  color: #2563eb;
  font-weight: 600;
  box-shadow: 0 0 0 1px #2563eb;
}
.mode-hint { font-size: 11px; color: #9ca3af; margin-bottom: 4px; padding: 0 4px; }
.theme-buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 4px; }
.theme-btn { padding: 8px 6px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 12px; cursor: pointer; transition: all 0.2s; }
.theme-btn.active { border-color: #2563eb; box-shadow: 0 0 0 1px #2563eb; font-weight: 600; }

.panel-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 12px;
}

.func-btn,
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

/* 词性颜色图例 */
.legend-toggle {
  width: 100%;
  padding: 8px;
  margin: 4px 0;
  border: 1px dashed #d1d5db;
  border-radius: 6px;
  background: #fafafa;
  font-size: 13px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}
.legend-toggle:hover {
  border-color: #2563eb;
  color: #2563eb;
  background: #eff6ff;
}
.pos-legend {
  margin-top: 8px;
  padding: 10px 12px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  font-size: 12px;
}
.legend-chip {
  width: 14px;
  height: 14px;
  border-radius: 3px;
  flex-shrink: 0;
  border: 1px solid rgba(0,0,0,0.1);
}
.legend-label {
  flex: 1;
  color: #374151;
  font-weight: 500;
}
.legend-keys {
  color: #9ca3af;
  font-size: 11px;
}
</style>

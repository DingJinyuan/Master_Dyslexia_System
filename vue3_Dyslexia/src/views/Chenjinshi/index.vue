<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

import { documentsDetailAPI } from '@/apis/documents.js'
import { documentsDetail_structuredAPI } from '@/apis/documents.js'

import ReaderContent from './Components/ReaderContent.vue'
import ReaderModal from './Components/ReaderModal.vue'
import ReaderPanel from './Components/ReaderPanel.vue'
import ComicPanel from './Components/ReaderCommic.vue'
import VoicePanel from './Components/VoicePanel.vue'

const route = useRoute()
// 修复1：给路由参数加默认值，避免 undefined
const documentId = ref(route.params.documents_id || 1)

const loading = ref(true)
const error = ref('')

const documentData = ref(null)
const structuredData = ref(null)
// 修复2：初始值设为占位符，确保渲染有内容
const originalText = ref('加载中...')
const originalTextContent = ref('')

const config = ref({
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

const modalState = ref({
  showGuide: false,
  showSummary: false
})

const isTextOptimized = ref(false)

// 漫画：只控制显示/隐藏，没有弹窗逻辑
const comicState = ref({
  visible: false,
  generating: false,
  list: []
})

const ttsState = ref({
  playing: false,
  showPanel: false,
  voiceType: 'female_soft',
  speed: 1.0,
  speedDisplay: '1.0',
  errorMessage: '',
  isPlaying: false
})

const tooltip = ref({
  show: false,
  word: '',
  pos: '',
  desc: '',
  left: 0,
  top: 0
})

let audio = null
let syncMarks = ref([])
let highlightTimer = null

// 加载文档
const loadDocumentData = async () => {
  try {
    loading.value = true
    error.value = ''
    console.log('【调试】加载文档ID：', documentId.value)

    const docRes = await documentsDetailAPI(documentId.value)
    documentData.value = docRes.data

    const structRes = await documentsDetail_structuredAPI(documentId.value)
    // ✅ 核心修复：接口返回的是 { data: 文档对象 }，所以要取 .data
    structuredData.value = structRes.data || structRes
    console.log('【调试】structuredData：', structuredData.value)

    let textContent = ''
    // 现在直接访问 structuredData.value.blocks
    if (Array.isArray(structuredData.value?.blocks)) {
      const textBlocks = structuredData.value.blocks
        .filter(block =>
          block.block_type === 'text' &&
          typeof block.text_content === 'string' &&
          block.text_content.trim() !== ''
        )
        .map(block => block.text_content)

      if (textBlocks.length > 0) {
        textContent = textBlocks.join('\n\n')
        console.log('【调试】提取到文本块：', textBlocks)
      } else {
        textContent = '接口返回了 blocks，但没有可显示的文本内容'
      }
    } else {
      textContent = `结构化数据格式异常，blocks 不是数组。当前 structuredData：${JSON.stringify(structuredData.value, null, 2)}`
    }

    if (!textContent || textContent.trim() === '') {
      textContent = '暂无可显示的文档内容，请检查文档解析结果'
    }

    originalText.value = textContent
    originalTextContent.value = textContent
    console.log('【调试】最终文本：', textContent)

  } catch (err) {
    error.value = `加载文档失败：${err.message || '未知错误'}`
    originalText.value = error.value
    console.error('【错误】', err)
  } finally {
    loading.value = false
  }
}
// 主题切换（保留背景设置，移除子组件样式操作）
const changeTheme = (newTheme) => {
  const themeMap = { warm: '#fff9e6', dark: '#1f2937', white: '#ffffff', blue: '#eff6ff' }
  document.body.style.background = themeMap[newTheme] || '#fff9e6'
}

// 划词逻辑（保持不变）
const handleMouseUp = () => {
  const selection = window.getSelection()
  const word = selection.toString().trim()
  if (!word || word.length >= 20) {
    tooltip.value.show = false
    return
  }
  const wordInfo = getWordDefinition(word)
  const rect = selection.getRangeAt(0).getBoundingClientRect()
  tooltip.value = {
    show: true,
    word,
    pos: wordInfo.pos,
    desc: wordInfo.desc,
    left: rect.left + window.scrollX,
    top: rect.bottom + window.scrollY + 10
  }
}

const getWordDefinition = (word) => {
  const dict = {
    "Reading": { pos: "n. 阅读", desc: "通过视觉获取文字信息并理解含义。" },
    "Power": { pos: "n. 力量；能力", desc: "体力、智力或影响力。" },
    "视野": { pos: "n. 视野", desc: "眼界与认知范围。" }
  }
  return dict[word] || { pos: "未知", desc: "暂无释义" }
}

// 语音面板逻辑（保持不变）
const toggleVoicePanel = (e) => {
  e.stopPropagation()
  ttsState.value.showPanel = !ttsState.value.showPanel
}

const onSpeedInput = () => {
  ttsState.value.speedDisplay = ttsState.value.speed
  if (audio && ttsState.value.isPlaying) {
    audio.playbackRate = parseFloat(ttsState.value.speed)
  }
}

// 高亮逻辑（增加内容校验）
const clearHighlights = () => {
  if (highlightTimer) clearInterval(highlightTimer)
  if (originalText.value && !originalText.value.includes('加载中') && !originalText.value.includes('失败')) {
    const el = document.querySelector('.document-content')
    if (el) el.innerHTML = originalText.value.replace(/\n/g, '<br><br>')
  }
}

const stopReading = () => {
  if (audio) {
    audio.pause()
    audio.currentTime = 0
  }
  ttsState.value.isPlaying = false
  ttsState.value.playing = false
  clearHighlights()
}

const syncWordHighlight = () => {
  highlightTimer = setInterval(() => {
    if (!ttsState.value.isPlaying || !audio) return
    const ms = audio.currentTime * 1000
    const mark = syncMarks.value.find(m => ms >= m.start_ms && ms <= m.end_ms)
    if (mark) {
      clearHighlights()
      const el = document.querySelector('.document-content')
      if (el) el.innerHTML = el.innerHTML.replaceAll(mark.word, `<span class="highlighted-word">${mark.word}</span>`)
    }
  }, 30)
}

const toggleStart = async () => {
  if (ttsState.value.isPlaying) {
    audio?.pause()
    ttsState.value.isPlaying = false
    ttsState.value.playing = false
  } else {
    if (!audio) {
      audio = new Audio('mock_audio/female_soft_1_0.mp3')
      audio.onended = stopReading
      syncMarks.value = [
        { index: 0, word: "Assignment", start_ms: 0, end_ms: 280 },
        { index: 1, word: "2", start_ms: 280, end_ms: 560 },
        { index: 2, word: "The", start_ms: 560, end_ms: 700 },
        { index: 3, word: "Power", start_ms: 700, end_ms: 950 },
        { index: 4, word: "of", start_ms: 950, end_ms: 1050 },
        { index: 5, word: "Reading", start_ms: 1050, end_ms: 1400 }
      ]
    }
    audio.playbackRate = parseFloat(ttsState.value.speed)
    await audio.play()
    ttsState.value.isPlaying = true
    ttsState.value.playing = true
    syncWordHighlight()
  }
}

// 文本优化（通过修改config让子组件响应）
const optimizeText = () => {
  isTextOptimized.value = true
  config.value.letterSpacing = 2
  config.value.wordSpacing = 1.8
  config.value.lineHeight = 2.5
}

const restoreText = () => {
  isTextOptimized.value = false
  config.value.letterSpacing = 1.5
  config.value.wordSpacing = 1.2
  config.value.lineHeight = 2.2
}

// 漫画逻辑（保持不变）
const generateComics = async () => {
  comicState.value.visible = true
  comicState.value.generating = true
  try {
    await new Promise(r => setTimeout(r, 3000))
    comicState.value.list = [
      { id: 1, imageUrl: 'https://picsum.photos/800/400?random=1', caption: '场景1：阅读开启知识' },
      { id: 2, imageUrl: 'https://picsum.photos/800/400?random=2', caption: '场景2：知识拓宽视野' },
      { id: 3, imageUrl: 'https://picsum.photos/800/400?random=3', caption: '场景3：沉浸式阅读' }
    ]
  } catch (err) {
    console.error(err)
  } finally {
    comicState.value.generating = false
  }
}

const regenerateComics = () => generateComics()

// 弹窗控制（保持不变）
const openModal = (type) => {
  if (type === 'guide') modalState.value.showGuide = true
  if (type === 'summary') modalState.value.showSummary = true
}
const closeModal = (type) => {
  if (type === 'guide') modalState.value.showGuide = false
  if (type === 'summary') modalState.value.showSummary = false
}

// 监听主题变化
watch(() => config.value.selectedTheme, changeTheme, { immediate: true })

// 监听路由参数变化（防止页面不刷新时参数更新）
watch(() => route.params.documents_id, (newVal) => {
  if (newVal) {
    documentId.value = newVal
    loadDocumentData() // 重新加载数据
  }
})

onMounted(async () => {
  // 优先加载数据
  await loadDocumentData()

  // 点击关闭tooltip/语音面板
  document.addEventListener('click', (e) => {
    if (tooltip.value.show && !e.target.closest('.word-tooltip')) tooltip.value.show = false
    if (ttsState.value.showPanel && !e.target.closest('.voice-panel') && e.target.id !== 'playBtn') {
      ttsState.value.showPanel = false
    }
  })
})

onUnmounted(() => {
  stopReading()
  if (highlightTimer) clearInterval(highlightTimer)
  document.body.style.background = ''
})
</script>

<template>
  <div class="immersive-reader" :class="config.selectedTheme">
    <!-- 顶部导航 -->
    <header class="reader-header">
      <div class="header-left">
        <button class="back-btn" @click="$router.back()">←</button>
        <h1 class="document-title">{{ documentData?.original_filename || '沉浸式阅读' }}</h1>
      </div>
      <div class="header-right">
        <button class="icon-btn" id="playBtn" :class="{ active: ttsState.playing }"
          @click="toggleVoicePanel">🎧</button>
        <VoicePanel :tts-state="ttsState" @toggle-start="toggleStart" @stop-reading="stopReading"
          @speed-input="onSpeedInput" />
        <button class="icon-btn" @click="openModal('guide')">❓</button>
      </div>
    </header>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载文档中...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <p class="error-text">{{ error }}</p>
      <button class="retry-btn" @click="loadDocumentData">重新加载</button>
    </div>

    <!-- 阅读主体（核心修复：调整布局，确保内容容器占满空间） -->
    <main v-else class="reading-container">
      <!-- 左侧漫画触发区 -->
      <div class="comic-hover-trigger" @mouseenter="comicState.visible = true" @mouseleave="comicState.visible = false">
        <ComicPanel :comics="comicState.list" :visible="comicState.visible" :generating="comicState.generating"
          @regenerate-comic="regenerateComics" />
      </div>

      <!-- 划词tooltip -->
      <div v-if="tooltip.show" class="word-tooltip" :style="{ left: `${tooltip.left}px`, top: `${tooltip.top}px` }">
        <div class="word">{{ tooltip.word }}</div>
        <span class="pos">{{ tooltip.pos }}</span>
        <span class="desc">{{ tooltip.desc }}</span>
      </div>

      <!-- 核心修复：移除loading绑定，确保内容始终渲染 + 增加key强制更新 -->
      <ReaderContent :key="documentId + (isTextOptimized ? 'optimized' : 'normal')" :content="originalText"
        :config="config" :is-plain-text="true" @mouseup="handleMouseUp" />
    </main>

    <!-- 右侧工具栏 -->
    <ReaderPanel :config="config" :is-text-optimized="isTextOptimized" @open-modal="openModal"
      @open-comic-modal="generateComics" @optimize-text="optimizeText" @restore-text="restoreText" />

    <!-- 弹窗 -->
    <ReaderModal :modal-state="modalState" @close-modal="closeModal">
      <template #summary-content>
        <p style="margin:16px 0;line-height:1.7;">
          {{ documentData?.summary || '暂无摘要' }}
        </p>
      </template>
    </ReaderModal>
  </div>
</template>

<style scoped>
.immersive-reader {
  min-height: 100vh;
  transition: background 0.3s;
  display: flex;
  flex-direction: column;
}

/* 主题背景 */
.immersive-reader.warm {
  background: #fff9e6;
}

.immersive-reader.dark {
  background: #1f2937;
}

.immersive-reader.white {
  background: #ffffff;
}

.immersive-reader.blue {
  background: #eff6ff;
}

/* 顶部导航 */
.reader-header {
  background: #fff;
  padding: 12px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
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
  cursor: pointer;
  border-radius: 8px;
}

.back-btn:hover {
  background: #f3f4f6;
}

.document-title {
  font-size: 18px;
  font-weight: 600;
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-right {
  display: flex;
  gap: 12px;
  position: relative;
}

.icon-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: #f9fafb;
  border-radius: 8px;
  cursor: pointer;
}

.icon-btn:hover {
  background: #e5e7eb;
}

.icon-btn.active {
  background: #2563eb;
  color: #fff;
}

/* 核心修复：阅读容器布局，确保占满剩余空间 */
.reading-container {
  flex: 1;
  position: relative;
  padding: 40px 24px;
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
  /* 修复flex布局导致的内容挤压 */
  display: block;
}

/* 漫画触发区 */
.comic-hover-trigger {
  position: fixed;
  left: 0;
  top: 80px;
  bottom: 0;
  width: 20px;
  z-index: 80;
}

.comic-hover-trigger:hover {
  width: 320px;
}

/* 加载/错误样式 */
.loading-container,
.error-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  100% {
    transform: rotate(360deg)
  }
}

.error-text {
  color: #ef4444;
  margin-bottom: 16px;
}

.retry-btn {
  padding: 8px 16px;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

/* 划词tooltip */
.word-tooltip {
  position: absolute;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  padding: 12px 16px;
  z-index: 10;
  min-width: 200px;
}

.word {
  font-weight: 600;
  margin-bottom: 4px;
}

.pos {
  color: #6b7280;
  margin-right: 8px;
}

.desc {
  color: #374151;
  line-height: 1.5;
}

/* 高亮文字样式 */
.highlighted-word {
  background: #ffeb3b;
  border-radius: 2px;
}
</style>

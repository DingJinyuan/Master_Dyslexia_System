<script setup>
// Vue3 setup语法糖中，defineProps/defineEmits 是内置宏，无需导入
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'

// 导入API
import { documentsDetailAPI, documentsDetail_structuredAPI } from '@/apis/documents.js'
import { wordLookupAPI, posTaggingAPI } from '@/apis/nlp.js'

// 导入组件
import ReaderHeader from './Components/ReaderHeader.vue'
import ReaderContent from './Components/ReaderContent.vue'
import ReaderModal from './Components/ReaderModal.vue'
import ReaderPanel from './Components/ReaderPanel.vue'
import ComicPanel from './Components/ReaderCommic.vue'
import VoicePanel from './Components/VoicePanel.vue'
import WordTooltip from './Components/ReaderWordTooltip.vue'

// 路由相关
const route = useRoute()
const router = useRouter()
const documentId = ref(route.params.documents_id || 1)

// 状态管理
const loading = ref(true)
const error = ref('')
const documentData = ref(null)
const structuredData = ref(null)
const originalText = ref('加载中...')
const taggedText = ref('加载中...')
// ✅ 新增：词性标注加载状态（区分文档加载和标注加载）
const posTaggingLoading = ref(false)
const posTaggingError = ref('')

// 配置项
const config = ref({
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

// 弹窗状态
const modalState = ref({
  showGuide: false,
  showSummary: false
})

// 文本优化
const isTextOptimized = ref(false)

// 漫画相关
const comicState = ref({
  visible: false,
  generating: false,
  list: []
})

// 语音朗读
const ttsState = ref({
  playing: false,
  showPanel: false,
  voiceType: 'female_soft',
  speed: 1.0,
  speedDisplay: '1.0',
  errorMessage: '',
  isPlaying: false
})

// 划词翻译
const tooltip = ref({
  visible: false,
  wordInfo: {},
  position: { left: 0, top: 0 }
})

// 朗读相关变量
let audio = null
let syncMarks = ref([])
let highlightTimer = null

// ✅ 重构：单独抽离词性标注逻辑，支持重试
// 重构：单独抽离词性标注逻辑，支持重试
const fetchPosTagging = async (textContent) => {
  if (!textContent || textContent.includes('异常') || textContent.includes('无可用')) {
    taggedText.value = textContent.replace(/\n/g, '<br><br>')
    return
  }

  posTaggingLoading.value = true
  posTaggingError.value = ''

  try {
    // 给接口请求加超时控制（10秒）
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 10000)

    // 调用词性标注API
    const posRes = await posTaggingAPI(textContent, {
      signal: controller.signal
    })

    clearTimeout(timeoutId)

    // ✅ 关键修改：放宽校验逻辑，只要有返回就渲染
    console.log('接口原始返回：', posRes) // 先看一眼真实结构
    if (posRes) {
      // 假设接口直接返回 tokens 数组，而不是 { data: { tokens } }
      const tokens = Array.isArray(posRes) ? posRes : posRes.data || posRes.tokens || []
      if (tokens.length > 0) {
        taggedText.value = convertPosTagsToHtml(tokens)
        posTaggingLoading.value = false // 成功后结束加载
        console.log('词性标注成功：', tokens)
      } else {
        throw new Error('接口返回了空的标注结果')
      }
    } else {
      throw new Error('接口返回为空')
    }
  } catch (posErr) {
    posTaggingError.value = posErr.message
    console.warn('词性标注接口调用提示：', posErr)

    // ✅ 只有真正的业务错误才降级，预检/超时不降级
    if (posErr.name !== 'AbortError' && !posErr.message.includes('preflight')) {
      taggedText.value = textContent.replace(/\n/g, '<br><br>')
      posTaggingLoading.value = false
    } else {
      // 超时/预检：继续等待，不结束加载
      taggedText.value = '词性标注接口响应中...（请勿刷新）'
    }
  }
}

// 加载文档核心逻辑
const loadDocumentData = async () => {
  try {
    loading.value = true
    error.value = ''

    // 1. 获取文档基础信息
    const docRes = await documentsDetailAPI(documentId.value)
    documentData.value = docRes.data

    // 2. 获取结构化文本内容
    const structRes = await documentsDetail_structuredAPI(documentId.value)
    structuredData.value = structRes.data || structRes

    // 提取纯文本
    let textContent = ''
    if (Array.isArray(structuredData.value?.blocks)) {
      const textBlocks = structuredData.value.blocks
        .filter(block =>
          block.block_type === 'text' &&
          typeof block.text_content === 'string' &&
          block.text_content.trim() !== ''
        )
        .map(block => block.text_content)

      textContent = textBlocks.length > 0 ? textBlocks.join('\n\n') : '无可用文本内容'
    } else {
      textContent = '文档格式异常'
    }

    originalText.value = textContent
    taggedText.value = '正在请求词性标注接口...'

    // 3. 调用词性标注（单独抽离，异步执行，不阻塞文档加载）
    await fetchPosTagging(textContent)

  } catch (err) {
    error.value = `加载失败：${err.message || '未知错误'}`
    originalText.value = error.value
    taggedText.value = error.value
  } finally {
    loading.value = false
  }
}

// 转换词性标注结果为带颜色的HTML
const convertPosTagsToHtml = (tokens) => {
  if (!tokens || tokens.length === 0) return ''

  let html = ''
  tokens.forEach(token => {
    html += `<span style="background-color: ${token.color || '#4A90D9'}30; padding: 0 2px; border-radius: 2px; margin: 0 1px;">${token.word}</span> `
  })
  return html
}

// 划词查询逻辑
const handleMouseUp = async (e) => {
  if (!e) return

  try {
    await nextTick()
    tooltip.value.visible = false

    const selection = window.getSelection()
    const word = selection.toString().trim()

    if (!word || word.length >= 20 || word.includes('\n')) return

    const res = await wordLookupAPI(word)
    if (res?.success) {
      const rect = selection.getRangeAt(0).getBoundingClientRect()
      tooltip.value = {
        visible: true,
        wordInfo: res,
        position: {
          left: rect.left + window.scrollX,
          top: rect.bottom + window.scrollY + 10
        }
      }
    }
  } catch (err) {
    tooltip.value.visible = false
  }
}

// 返回上一页
const handleBack = () => {
  if (route.query.from) {
    router.push(route.query.from)
  } else {
    router.go(-1)
  }
}

// 切换语音面板
const handleToggleVoice = () => {
  ttsState.value.showPanel = !ttsState.value.showPanel
}

// 打开指南弹窗
const handleOpenGuide = () => {
  modalState.value.showGuide = true
}

// 语音速度调整
const onSpeedInput = () => {
  ttsState.value.speedDisplay = ttsState.value.speed
  if (audio && ttsState.value.isPlaying) {
    audio.playbackRate = parseFloat(ttsState.value.speed)
  }
}

// 清空朗读高亮
const clearHighlights = () => {
  if (highlightTimer) clearInterval(highlightTimer)
  const el = document.querySelector('.document-content')
  if (el && taggedText.value) {
    el.innerHTML = taggedText.value
  }
}

// 停止朗读
const stopReading = () => {
  if (audio) {
    audio.pause()
    audio.currentTime = 0
  }
  ttsState.value.isPlaying = false
  ttsState.value.playing = false
  clearHighlights()
}

// 朗读同步高亮
const syncWordHighlight = () => {
  highlightTimer = setInterval(() => {
    if (!ttsState.value.isPlaying || !audio) return

    const ms = audio.currentTime * 1000
    const mark = syncMarks.value.find(m => ms >= m.start_ms && ms <= m.end_ms)

    if (mark) {
      clearHighlights()
      const el = document.querySelector('.document-content')
      if (el) {
        const highlightedHtml = taggedText.value.replace(
          new RegExp(`(${mark.word})`, 'g'),
          `<span style="background-color: #ffeb3b !important; padding: 0 2px; border-radius: 2px;">$1</span>`
        )
        el.innerHTML = highlightedHtml
      }
    }
  }, 30)
}

// 开始/暂停朗读
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
        { index: 0, word: "string", start_ms: 0, end_ms: 280 },
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

// 文本优化/恢复
const optimizeText = () => {
  isTextOptimized.value = true
  config.value.letterSpacing = 2
  config.value.lineHeight = 2.5
}

const restoreText = () => {
  isTextOptimized.value = false
  config.value.letterSpacing = 1.5
  config.value.lineHeight = 2.2
}

// 生成漫画
const generateComics = async () => {
  comicState.value.visible = true
  comicState.value.generating = true

  try {
    await new Promise(r => setTimeout(r, 2000))
    comicState.value.list = [
      { id: 1, imageUrl: 'https://picsum.photos/800/400?random=1', caption: '场景1' },
      { id: 2, imageUrl: 'https://picsum.photos/800/400?random=2', caption: '场景2' }
    ]
  } finally {
    comicState.value.generating = false
  }
}

const regenerateComics = () => generateComics()

// 弹窗控制
const openModal = (type) => {
  if (type === 'guide') modalState.value.showGuide = true
  if (type === 'summary') modalState.value.showSummary = true
}

const closeModal = (type) => {
  if (type === 'guide') modalState.value.showGuide = false
  if (type === 'summary') modalState.value.showSummary = false
}

// ✅ 监听词性标注加载状态，更新后强制重新渲染
watch([posTaggingLoading, taggedText], () => {
  // 触发组件重新渲染
  nextTick(() => {
    const contentEl = document.querySelector('.document-content')
    if (contentEl) {
      contentEl.innerHTML = taggedText.value
    }
  })
})

// 监听路由变化刷新文档
watch(() => route.params.documents_id, (newVal) => {
  if (newVal) {
    documentId.value = newVal
    loadDocumentData()
  }
})

// 生命周期
onMounted(async () => {
  await loadDocumentData()

  // 全局事件监听
  document.addEventListener('click', (e) => {
    if (tooltip.value.visible && !e.target.closest('.word-tooltip')) {
      tooltip.value.visible = false
    }
    if (ttsState.value.showPanel && !e.target.closest('.voice-panel') && e.target.id !== 'playBtn') {
      ttsState.value.showPanel = false
    }
  })

  document.addEventListener('mouseup', async (e) => {
    if (e.target.closest('.document-content')) {
      await handleMouseUp(e)
    }
  })
})

onUnmounted(() => {
  stopReading()
  if (highlightTimer) clearInterval(highlightTimer)
})
</script>

<template>
  <div class="immersive-reader">
    <!-- 头部组件 -->
    <ReaderHeader :document-title="documentData?.original_filename || '沉浸式阅读'" :is-playing="ttsState.playing"
      @back="handleBack" @toggle-voice="handleToggleVoice" @open-guide="handleOpenGuide" />

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

    <!-- 主内容区 -->
    <main v-else class="reading-container">
      <!-- 漫画面板触发区 -->
      <div class="comic-hover-trigger" @mouseenter="comicState.visible = true" @mouseleave="comicState.visible = false">
        <ComicPanel :comics="comicState.list" :visible="comicState.visible" :generating="comicState.generating"
          @regenerate-comic="regenerateComics" />
      </div>

      <!-- ✅ 增加词性标注加载状态提示 -->
      <div v-if="posTaggingLoading" class="pos-tagging-loading" style="text-align: center; padding: 20px; color: #666;">
        <div class="loading-spinner" style="margin: 0 auto;"></div>
        <p style="margin-top: 10px;">词性标注接口响应中...（接口较慢，请勿刷新）</p>
      </div>

      <!-- 核心阅读内容（词性标注后的文本） -->
      <ReaderContent
        :key="documentId + (isTextOptimized ? 'optimized' : 'normal') + (posTaggingLoading ? 'tagging' : 'tagged')"
        :content="taggedText" :config="config" :is-plain-text="false" :loading="loading"
        :posTaggingLoading="posTaggingLoading" @mouseup="handleMouseUp" />

      <!-- 划词翻译弹窗 -->
      <WordTooltip v-model:visible="tooltip.visible" :word-info="tooltip.wordInfo" :position="tooltip.position"
        :font-config="config" />
    </main>

    <!-- 右侧设置面板 -->
    <ReaderPanel :config="config" :is-text-optimized="isTextOptimized" @open-modal="openModal"
      @open-comic-modal="generateComics" @optimize-text="optimizeText" @restore-text="restoreText" />

    <!-- 弹窗组件 -->
    <ReaderModal :modal-state="modalState" @close-modal="closeModal">
      <template #summary-content>
        <p style="margin:16px 0;line-height:1.7;">
          {{ documentData?.summary || '暂无摘要' }}
        </p>
      </template>
    </ReaderModal>

    <!-- 语音朗读面板 -->
    <VoicePanel :tts-state="ttsState" @toggle-start="toggleStart" @stop-reading="stopReading"
      @speed-input="onSpeedInput" />
  </div>
</template>

<style scoped>
/* 全局容器 - 固定米黄色背景 */
.immersive-reader {
  min-height: 100vh;
  background: #fff9e6;
  display: flex;
  flex-direction: column;
}

/* 阅读内容容器 */
.reading-container {
  flex: 1;
  position: relative;
  padding: 40px 24px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

/* 漫画面板触发区 */
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

/* 加载/错误状态样式 */
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
    transform: rotate(360deg);
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

/* 词性标注加载提示 */
.pos-tagging-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
  background: rgba(255, 249, 230, 0.9);
  border-radius: 8px;
  width: 80%;
}

/* 词性标注文本样式 */
:deep(.document-content) {
  user-select: text !important;
  -webkit-user-select: text !important;
  cursor: text !important;
  line-height: 1.8;
  font-size: 18px;
  min-height: 60vh;
  padding: 20px 0;
}

:deep(.document-content span) {
  user-select: text !important;
  -webkit-user-select: text !important;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .reading-container {
    padding: 20px 16px;
  }

  .pos-tagging-loading {
    width: 90%;
  }
}
</style>

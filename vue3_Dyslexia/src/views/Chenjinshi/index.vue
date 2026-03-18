<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'

// 导入API（仅保留必要的）
import { documentsDetailAPI, documentsDetail_structuredAPI } from '@/apis/documents.js'
import { wordLookupAPI, posTaggingAPI, readabilityScoreAPI, summarizeTextAPI } from '@/apis/nlp.js'
import { ttsGenerateAPI } from '@/apis/tts.js'

// 导入组件（新增ReadabilityModal）
import ReaderHeader from './Components/ReaderHeader.vue'
import ReaderContent from './Components/ReaderContent.vue'
import ReaderModal from './Components/ReaderModal.vue'
import ReaderPanel from './Components/ReaderPanel.vue'
import ComicPanel from './Components/ReaderComic.vue'
import WordTooltip from './Components/ReaderWordTooltip.vue'
import VoicePanel from './Components/VoicePanel.vue'
import ReadabilityModal from './Components/ReadabilityModal.vue' // 新增
import SummaryModal from './Components/SummaryModal.vue'

// 路由
const route = useRoute()
const router = useRouter()
const documentId = ref(route.params.documents_id || 1)

// 核心状态
const loading = ref(true)
const error = ref('')
const documentData = ref(null)
const structuredData = ref(null)
const originalText = ref('加载中...')
const taggedText = ref('加载中...')
const posTaggingLoading = ref(false)

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

// 语音状态
const ttsState = ref({
  playing: false,
  showPanel: false,
  voiceType: 'youxiaomei',
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

// 可读性评分状态
const readabilityState = ref({
  visible: false,
  loading: false,
  error: '',
  result: null
})

// 摘要弹窗状态（适配返回字段+防抖）
const summaryState = ref({
  visible: false,
  loading: false,
  error: '',
  result: null,
  selectedLength: ''
})

// 防抖锁：防止重复请求
const isGenerating = ref(false)

// 朗读变量
let audio = null
let highlightTimer = null

// --- 核心方法 ---
// 加载文档
const loadDocumentData = async () => {
  try {
    loading.value = true
    error.value = ''
    const docRes = await documentsDetailAPI(documentId.value)
    documentData.value = docRes.data
    const structRes = await documentsDetail_structuredAPI(documentId.value)
    structuredData.value = structRes.data || structRes

    let textContent = ''
    if (Array.isArray(structuredData.value?.blocks)) {
      const textBlocks = structuredData.value.blocks
        .filter(block => block.block_type === 'text' && typeof block.text_content === 'string' && block.text_content.trim() !== '')
        .map(block => block.text_content)
      textContent = textBlocks.length > 0 ? textBlocks.join('\n\n') : '无可用文本内容'
    } else {
      textContent = '文档格式异常'
    }
    originalText.value = textContent
    taggedText.value = '正在请求词性标注接口...'
    await fetchPosTagging(textContent)
  } catch (err) {
    error.value = `加载失败：${err.message || '未知错误'}`
    originalText.value = error.value
    taggedText.value = error.value
  } finally {
    loading.value = false
  }
}

// 词性标注
const fetchPosTagging = async (textContent) => {
  if (!textContent || textContent.includes('异常') || textContent.includes('无可用')) {
    taggedText.value = textContent.replace(/\n/g, '<br><br>')
    return
  }
  posTaggingLoading.value = true
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 10000)
    const posRes = await posTaggingAPI(textContent, { signal: controller.signal })
    clearTimeout(timeoutId)
    const tokens = Array.isArray(posRes) ? posRes : posRes.data || posRes.tokens || []
    if (tokens.length > 0) {
      taggedText.value = convertPosTagsToHtml(tokens)
    } else {
      throw new Error('接口返回了空的标注结果')
    }
  } catch (posErr) {
    console.warn('词性标注接口调用提示：', posErr)
    taggedText.value = textContent.replace(/\n/g, '<br><br>')
  } finally {
    posTaggingLoading.value = false
  }
}

// 转换词性HTML
const convertPosTagsToHtml = (tokens) => {
  if (!tokens || tokens.length === 0) return ''
  let html = ''
  tokens.forEach(token => {
    html += `<span style="background-color: ${token.color || '#4A90D9'}30; padding: 0 2px; border-radius: 2px; margin: 0 1px;">${token.word}</span> `
  })
  return html
}

// 划词查询
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
        position: { left: rect.left + window.scrollX, top: rect.bottom + window.scrollY + 10 }
      }
    }
  } catch (err) {
    tooltip.value.visible = false
  }
}

// 语音朗读
const toggleStart = async () => {
  if (ttsState.value.isPlaying) {
    audio?.pause()
    ttsState.value.isPlaying = false
    ttsState.value.playing = false
    return
  }
  try {
    ttsState.value.errorMessage = ''
    if (!originalText.value || originalText.value.includes('加载中') || originalText.value.includes('无可用') || originalText.value.includes('文档格式异常')) {
      ttsState.value.errorMessage = '暂无可用文本用于朗读'
      return
    }
    const rateVal = ((ttsState.value.speed - 1) * 100).toFixed(0)
    const rate = rateVal === '0' ? '+0%' : (rateVal.startsWith('-') ? `${rateVal}%` : `+${rateVal}%`)
    ttsState.value.playing = true
    const res = await ttsGenerateAPI({
      text: originalText.value,
      voice: 'youxiaomei',
      voiceName: 'string',
      rate: rate,
      pitch: "+0Hz"
    })
    if (res && res.success) {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
      const audioPath = res.audioUrl.replace(/\\/g, '/')
      const audioUrl = audioPath.startsWith('http') ? audioPath : `${baseUrl}/${audioPath}`
      audio = new Audio(audioUrl)
      audio.playbackRate = parseFloat(ttsState.value.speed)
      audio.onended = stopReading
      audio.onerror = (e) => {
        ttsState.value.errorMessage = '音频播放失败，请检查文件是否存在'
        ttsState.value.isPlaying = false
        ttsState.value.playing = false
      }
      await audio.play()
      ttsState.value.isPlaying = true
      ttsState.value.playing = false
    } else {
      throw new Error(res?.message || '音频生成失败')
    }
  } catch (err) {
    ttsState.value.errorMessage = err.message || '朗读失败，请重试'
    ttsState.value.playing = false
    ttsState.value.isPlaying = false
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

// 清空高亮
const clearHighlights = () => {
  if (highlightTimer) clearInterval(highlightTimer)
  const el = document.querySelector('.document-content')
  if (el && taggedText.value) {
    el.innerHTML = taggedText.value
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

// 可读性评分
const calculateReadability = async () => {
  if (!originalText.value || originalText.value.includes('加载中') || originalText.value.includes('无可用') || originalText.value.includes('文档格式异常')) {
    readabilityState.value = {
      visible: true,
      loading: false,
      error: '暂无可用文本用于评分',
      result: null
    }
    return
  }

  readabilityState.value = {
    visible: true,
    loading: true,
    error: '',
    result: null
  }

  try {
    const resultData = await readabilityScoreAPI(originalText.value);
    readabilityState.value = {
      visible: true,
      loading: false,
      error: '',
      result: resultData
    };
  } catch (err) {
    const errMsg = err.response?.data?.detail?.[0]?.msg || err.message || '请求失败';
    readabilityState.value = {
      visible: true,
      loading: false,
      error: errMsg,
      result: null
    };
  }
};

// 生成文本摘要（适配返回+防抖）
const generateSummary = async (length) => {
  // 防抖：防止重复请求
  if (isGenerating.value) return
  isGenerating.value = true

  const originalTextVal = originalText.value.trim()

  // 文本校验
  if (!originalTextVal || originalTextVal.includes('加载中') || originalTextVal.includes('无可用') || originalTextVal.includes('文档格式异常')) {
    summaryState.value = {
      ...summaryState.value,
      loading: false,
      error: '暂无可用文本用于生成摘要',
      result: null
    }
    isGenerating.value = false
    return
  }

  // 打开弹窗 + 加载状态
  summaryState.value = {
    visible: true,
    loading: true,
    error: '',
    result: null,
    selectedLength: length
  }

  try {
    // 调用摘要接口（30秒超时）
    const resultData = await summarizeTextAPI(originalTextVal, length);
    console.log('摘要接口成功返回:', resultData);

    // 更新状态：展示结果
    summaryState.value = {
      ...summaryState.value,
      loading: false,
      result: resultData // 直接赋值返回的完整数据
    };
  } catch (err) {
    // 错误处理
    const errMsg = err.response?.data?.detail?.[0]?.msg || err.message || '生成摘要失败';
    summaryState.value = {
      ...summaryState.value,
      loading: false,
      error: errMsg,
      result: null
    };
  } finally {
    isGenerating.value = false // 解锁
  }
};

// 重置摘要状态
const resetSummary = () => {
  summaryState.value = {
    ...summaryState.value,
    loading: false,
    error: '',
    result: null,
    selectedLength: ''
  }
}

// 关闭摘要弹窗
const closeSummaryModal = () => {
  summaryState.value = {
    visible: false,
    loading: false,
    error: '',
    result: null,
    selectedLength: ''
  }
}

// 关闭可读性弹窗
const closeReadabilityModal = () => {
  readabilityState.value = {
    visible: false,
    loading: false,
    error: '',
    result: null
  }
}

// 弹窗控制
const openModal = (type) => {
  if (type === 'guide') modalState.value.showGuide = true
  if (type === 'summary') modalState.value.showSummary = true
}
const closeModal = (type) => {
  if (type === 'guide') modalState.value.showGuide = false
  if (type === 'summary') modalState.value.showSummary = false
}

// 监听
watch([posTaggingLoading, taggedText], () => {
  nextTick(() => {
    const el = document.querySelector('.document-content')
    if (el) el.innerHTML = taggedText.value
  })
})
watch(() => route.params.documents_id, (newVal) => {
  if (newVal) {
    documentId.value = newVal
    loadDocumentData()
  }
})

// 生命周期
onMounted(async () => {
  await loadDocumentData()
  document.addEventListener('click', (e) => {
    if (tooltip.value.visible && !e.target.closest('.word-tooltip')) tooltip.value.visible = false
    if (ttsState.value.showPanel && !e.target.closest('.voice-panel') && e.target.id !== 'playBtn') ttsState.value.showPanel = false
  })
  document.addEventListener('mouseup', async (e) => {
    if (e.target.closest('.document-content')) await handleMouseUp(e)
  })
})
onUnmounted(() => {
  stopReading()
  if (highlightTimer) clearInterval(highlightTimer)
  document.removeEventListener('click', () => { })
  document.removeEventListener('mouseup', () => { })
})
</script>

<template>
  <div class="immersive-reader">
    <!-- 头部 -->
    <ReaderHeader :document-title="documentData?.original_filename || '沉浸式阅读'" :is-playing="ttsState.playing"
      @back="() => router.go(-1)" @toggle-voice="() => ttsState.showPanel = !ttsState.showPanel"
      @open-guide="() => openModal('guide')" />

    <!-- 加载/错误状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载文档中...</p>
    </div>
    <div v-else-if="error" class="error-container">
      <p class="error-text">{{ error }}</p>
      <button class="retry-btn" @click="loadDocumentData">重新加载</button>
    </div>

    <!-- 主内容 -->
    <main v-else class="reading-container">
      <!-- 漫画面板 -->
      <div class="comic-hover-trigger" @mouseenter="comicState.visible = true" @mouseleave="comicState.visible = false">
        <ComicPanel :comics="comicState.list" :visible="comicState.visible" :generating="comicState.generating"
          @regenerate-comic="generateComics" />
      </div>

      <!-- 阅读内容 -->
      <ReaderContent :content="taggedText" :config="config" :is-plain-text="false" :loading="loading"
        :posTaggingLoading="posTaggingLoading" @mouseup="handleMouseUp" />

      <!-- 划词翻译 -->
      <WordTooltip v-model:visible="tooltip.visible" :word-info="tooltip.wordInfo" :position="tooltip.position"
        :font-config="config" />
    </main>

    <!-- 右侧面板（绑定生成摘要事件） -->
    <ReaderPanel :config="config" :is-text-optimized="isTextOptimized" @open-modal="openModal"
      @open-comic-modal="generateComics" @optimize-text="optimizeText" @restore-text="restoreText"
      @calculate-readability="calculateReadability" @generate-summary="() => summaryState.visible = true"
      :is-generating="isGenerating" /> <!-- 传递防抖状态 -->

    <!-- 通用弹窗 -->
    <ReaderModal :modal-state="modalState" @close-modal="closeModal">
      <template #summary-content>
        <p style="margin:16px 0;line-height:1.7;">
          {{ documentData?.summary || '暂无摘要' }}
        </p>
      </template>
    </ReaderModal>

    <!-- 语音面板 -->
    <VoicePanel :tts-state="ttsState" @toggle-start="toggleStart" @stop-reading="stopReading"
      @speed-input="() => ttsState.speedDisplay = ttsState.speed.toFixed(1)" />

    <!-- 可读性评分弹窗 -->
    <ReadabilityModal :visible="readabilityState.visible" :loading="readabilityState.loading"
      :error="readabilityState.error" :result="readabilityState.result" @close="closeReadabilityModal" />

    <!-- 文本摘要弹窗（核心） -->
    <SummaryModal :visible="summaryState.visible" :loading="summaryState.loading" :error="summaryState.error"
      :result="summaryState.result" :original-text="originalText.value" :selected-length="summaryState.selectedLength"
      @close="closeSummaryModal" @generate-summary="generateSummary" @reset-summary="resetSummary" />
  </div>
</template>

<style scoped>
.immersive-reader {
  min-height: 100vh;
  background: #fff9e6;
  display: flex;
  flex-direction: column;
  padding-top: 70px;
}

.reading-container {
  flex: 1;
  position: relative;
  padding: 40px 24px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

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
  transition: background 0.2s;
}

.retry-btn:hover {
  background: #1d4ed8;
}

@media (max-width: 768px) {
  .reading-container {
    padding: 20px 16px;
  }
}

@media (max-width: 480px) {
  .immersive-reader {
    padding-top: 60px;
  }

  .reading-container {
    padding: 16px 8px;
  }
}
</style>

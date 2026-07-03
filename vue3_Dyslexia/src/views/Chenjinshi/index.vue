<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'

// 导入API（仅保留必要的）
import { documentsDetailAPI, documentsDetail_structuredAPI } from '@/apis/documents.js'
import { wordLookupAPI, posTaggingAPI, readabilityScoreAPI, refineTextAPI } from '@/apis/nlp.js'
import { generateMindmapAPI } from '@/apis/mindmap.js'
import { ttsGenerateAPI, getTTSVoicesAPI } from '@/apis/tts.js'

// 导入组件（新增ReadabilityModal）
import ReaderHeader from './Components/ReaderHeader.vue'
import ReaderContent from './Components/ReaderContent.vue'
import ReaderModal from './Components/ReaderModal.vue'
import ReaderPanel from './Components/ReaderPanel.vue'
import WordTooltip from './Components/ReaderWordTooltip.vue'
import VoicePanel from './Components/VoicePanel.vue'
import ReadabilityModal from './Components/ReadabilityModal.vue' // 新增
import SummaryModal from './Components/SummaryModal.vue'
import MindMapModal from './Components/MindMapModal.vue'

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
  showPosColors: true,
  displayMode: 'mixed', // 'mixed' = 图文共存, 'separated' = 图文分离
  selectedTheme: 'warm',   // warm | dark | white | blue
  enableRuler: false,
  enableFocus: false,
  enableScroll: false,
  rulerHeight: 28,
  focusHeight: 220,
  scrollSpeed: 1
})

// 弹窗状态
const modalState = ref({
  showGuide: false
})

// 文本优化
const isTextOptimized = ref(false)
const refinedPlainText = ref('')

// 语音状态
const ttsState = ref({
  playing: false,
  showPanel: false,
  voiceType: 'youxiaomei',
  speed: 1.0,
  speedDisplay: '1.0',
  errorMessage: '',
  isPlaying: false,
})

// TTS 音色列表 & 选择
const voiceList = ref([])
const selectedVoice = ref('zh-CN-XiaoxiaoNeural')

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

// 思维导图状态
const mindmapState = ref({
  visible: false,
  loading: false,
  error: '',
  htmlUrl: '',
})

// 防抖锁：防止重复请求
const isGenerating = ref(false)

// 图片预览
const imagePreview = ref({ visible: false, url: '' })
const openImagePreview = (url) => { imagePreview.value = { visible: true, url } }
const closeImagePreview = () => { imagePreview.value = { visible: false, url: '' } }

// 侧栏开关
const imageSidebarOpen = ref(false)
const toggleImageSidebar = () => { imageSidebarOpen.value = !imageSidebarOpen.value }

// 朗读变量 + 结构化块缓存
let audio = null
let highlightTimer = null
const allBlocks = ref([]) // 所有结构化块（文本+图片）

// TTS 预热缓存 — 所有音色都预生成
const ttsPreWarmed = ref(false)
const preWarmedAudioMap = ref({})  // { voiceName: audioUrl }
const ttsPreWarming = ref(false)

// 文本优化 & 摘要 & 思维导图预热缓存
const refineCached = ref(null)   // full_refine 结果
const summaryCached = ref(null)  // summary 结果
const mindmapCached = ref(null)  // 思维导图 HTML URL
const cachePreWarming = ref(false)

// --- 核心方法 ---
// 加载文档（图文混排）
const loadDocumentData = async () => {
  try {
    loading.value = true
    error.value = ''
    const docRes = await documentsDetailAPI(documentId.value)
    documentData.value = docRes.data
    const structRes = await documentsDetail_structuredAPI(documentId.value)
    structuredData.value = structRes.data || structRes

    const blocks = structuredData.value?.blocks
    if (!Array.isArray(blocks) || blocks.length === 0) {
      originalText.value = '文档格式异常'
      taggedText.value = '文档格式异常'
      loading.value = false
      return
    }

    allBlocks.value = blocks

    // 提取纯文本（TTS、可读性评分用）
    const textOnly = blocks
      .filter(b => b.block_type === 'text' && b.text_content?.trim())
      .map(b => b.text_content)
      .join('\n\n')
    originalText.value = textOnly || '无可用文本内容'

    taggedText.value = '正在请求词性标注接口...'
    await fetchPosTagging(blocks)
  } catch (err) {
    error.value = `加载失败：${err.message || '未知错误'}`
    originalText.value = error.value
    taggedText.value = error.value
  } finally {
    loading.value = false
    // 后台预热：TTS + 文本优化 + 摘要
    preWarmTTS()
    preWarmRefine()
  }
}

// TTS 预热：为所有可选音色后台生成音频，切换声音秒开
const preWarmTTS = async () => {
  const text = originalText.value
  if (!text || text.includes('加载中') || text.includes('无可用') || text.includes('文档格式异常')) return
  ttsPreWarming.value = true
  ttsPreWarmed.value = false
  try {
    const voices = voiceList.value.length > 0 ? voiceList.value.map(v => v.name) : [selectedVoice.value]
    const results = await Promise.all(
      voices.map(voice =>
        ttsGenerateAPI({ text, voice, rate: '+0%', pitch: '+0Hz' }).catch(() => null)
      )
    )
    const map = {}
    voices.forEach((v, i) => {
      if (results[i]?.success) map[v] = resolveAudioUrl(results[i].audioUrl)
    })
    preWarmedAudioMap.value = map
    ttsPreWarmed.value = Object.keys(map).length > 0
  } catch (e) {
    console.warn('TTS 预热失败:', e)
  } finally {
    ttsPreWarming.value = false
  }
}

// 预热文本优化和摘要：后台生成缓存，点击秒开
const preWarmRefine = async () => {
  const text = originalText.value
  if (!text || text.includes('加载中') || text.includes('无可用') || text.includes('文档格式异常')) return
  if (text.length < 50) return
  cachePreWarming.value = true
  try {
    const [refineRes, summaryRes, mindmapRes] = await Promise.all([
      refineTextAPI({ original_text: text, mode: 'full_refine', max_iterations: 1 }).catch(() => null),
      refineTextAPI({ original_text: text, mode: 'summary', summary_length: '标准', max_iterations: 1 }).catch(() => null),
      generateMindmapAPI({ text, max_depth: 4 }).catch(() => null)
    ])
    if (refineRes?.refined_text) {
      refineCached.value = refineRes.refined_text
      refinedPlainText.value = refineRes.refined_text
    }
    if (summaryRes?.refined_text) summaryCached.value = summaryRes
    if (mindmapRes?.success) {
      const base = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
      const url = mindmapRes.html_url
      mindmapCached.value = url.startsWith('http') ? url : `${base}/${url.replace(/^\//, '')}`
    }
  } catch (e) {
    console.warn('预热失败:', e)
  } finally {
    cachePreWarming.value = false
  }
}

// 词性标注（逐文本块并行标注 → 图文混排）
const fetchPosTagging = async (blocks) => {
  const textIndices = []
  blocks.forEach((b, i) => {
    if (b.block_type === 'text' && b.text_content?.trim()) textIndices.push(i)
  })
  if (textIndices.length === 0) {
    taggedText.value = buildMixedHtml(blocks, {}, config.value.displayMode)
    return
  }
  posTaggingLoading.value = true
  try {
    const posResults = await Promise.all(
      textIndices.map(idx =>
        posTaggingAPI(blocks[idx].text_content).catch(() => null)
      )
    )
    let totalTokens = 0
    const blockTokens = {}
    textIndices.forEach((idx, i) => {
      const res = posResults[i]
      const tokens = Array.isArray(res) ? res : (res?.tokens || [])
      blockTokens[idx] = tokens
      totalTokens += tokens.length
    })
    taggedText.value = buildMixedHtml(blocks, blockTokens, config.value.displayMode)
  } catch (err) {
    taggedText.value = buildMixedHtml(blocks, {}, config.value.displayMode)
  } finally {
    posTaggingLoading.value = false
  }
}

// 转换词性HTML
const convertPosTagsToHtml = (tokens) => {
  if (!tokens || tokens.length === 0) return ''
  let html = ''
  tokens.forEach(token => {
    const color = token.color || '#4A90D9'
    html += `<span class="pos-token" style="background-color:${color}60;color:#333;padding:0 3px;border-radius:3px;">${token.word}</span> `
  })
  return html
}

// 图文混排 HTML 构建（font-size/line-height 从 .document-content 继承，不在 <p> 硬编码，保证滑块生效）
const buildMixedHtml = (blocks, blockTokens, displayMode = 'mixed') => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
  return blocks.map((block, idx) => {
    if (block.block_type === 'image' && block.image_url) {
      if (displayMode === 'separated') return '' // 图文分离模式不嵌入图片
      const imgUrl = block.image_url.startsWith('http')
        ? block.image_url
        : `${baseUrl}/${block.image_url.replace(/\\/g, '/')}`
      return `<figure class="image-block" style="text-align:center;margin:12px 0;">
        <img src="${imgUrl}" style="max-width:70%;max-height:300px;object-fit:contain;border-radius:8px;" alt="文档图片" loading="lazy" />
      </figure>`
    }
    if (block.block_type === 'text') {
      const tokens = blockTokens[idx]
      if (tokens && tokens.length > 0) {
        return `<p class="text-block">${convertPosTagsToHtml(tokens)}</p>`
      }
      const text = (block.text_content || '').replace(/\n/g, '<br>')
      return `<p class="text-block">${text}</p>`
    }
    return ''
  }).join('')
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

// 语音朗读（全文）
const toggleStart = async () => {
  if (ttsState.value.isPlaying) {
    audio?.pause()
    ttsState.value.isPlaying = false
    ttsState.value.playing = false
    return
  }
  try {
    ttsState.value.errorMessage = ''
    const text = originalText.value
    if (!text || text.includes('加载中') || text.includes('无可用') || text.includes('文档格式异常')) {
      ttsState.value.errorMessage = '暂无可用文本用于朗读'
      return
    }

    // 优先用预热音频（仅同音色+默认语速命中）
    const rateVal = ((ttsState.value.speed - 1) * 100).toFixed(0)
    const rate = rateVal === '0' ? '+0%' : (rateVal.startsWith('-') ? `${rateVal}%` : `+${rateVal}%`)

    const cachedUrl = preWarmedAudioMap.value[selectedVoice.value]
    if (ttsPreWarmed.value && rate === '+0%' && cachedUrl) {
      // 直接使用预热音频，秒开
      audio = new Audio(cachedUrl)
      audio.playbackRate = parseFloat(ttsState.value.speed)
      audio.onended = stopReading
      audio.onerror = () => {
        ttsState.value.errorMessage = '音频播放失败'
        ttsState.value.isPlaying = false
        ttsState.value.playing = false
      }
      await audio.play()
      ttsState.value.isPlaying = true
      ttsState.value.playing = false
      return
    }

    await playFullText(text, rate)
  } catch (err) {
    ttsState.value.errorMessage = err.message || '朗读失败，请重试'
    ttsState.value.playing = false
    ttsState.value.isPlaying = false
  }
}

const baseUrl = () => import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const resolveAudioUrl = (path) => {
  const p = path.replace(/\\/g, '/').replace(/^\/+/, '')
  return p.startsWith('http') ? p : `${baseUrl()}/${p}`
}

// 全文朗读
const playFullText = async (text, rate) => {
  ttsState.value.playing = true
  const res = await ttsGenerateAPI({ text, voice: selectedVoice.value, rate, pitch: '+0Hz' })
  if (!res?.success) throw new Error(res?.message || '音频生成失败')
  audio = new Audio(resolveAudioUrl(res.audioUrl))
  audio.playbackRate = parseFloat(ttsState.value.speed)
  audio.onended = stopReading
  audio.onerror = () => {
    ttsState.value.errorMessage = '音频播放失败'
    ttsState.value.isPlaying = false
    ttsState.value.playing = false
  }
  await audio.play()
  ttsState.value.isPlaying = true
  ttsState.value.playing = false
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

// 文本优化/恢复（调用后端 full_refine API）
const textOptimizeLoading = ref(false)
const cachedOriginalTagged = ref('') // 缓存原始词性标注结果，用于恢复

const optimizeText = async () => {
  const text = originalText.value
  if (!text || text.includes('加载中') || text.includes('无可用') || text.includes('文档格式异常')) return
  textOptimizeLoading.value = true
  try {
    cachedOriginalTagged.value = taggedText.value
    // 优先用缓存
    let refined = refineCached.value
    if (!refined) {
      const res = await refineTextAPI({ original_text: text, mode: 'full_refine', max_iterations: 1 })
      refined = res?.refined_text
    }
    if (refined) {
      refinedPlainText.value = refined
      taggedText.value = `<div class="refined-text">${refined.replace(/\n/g, '<br><br>')}</div>`
      isTextOptimized.value = true
    }
  } catch (err) {
    console.warn('文本优化失败:', err)
  } finally {
    textOptimizeLoading.value = false
  }
}

const restoreText = () => {
  if (cachedOriginalTagged.value) {
    taggedText.value = cachedOriginalTagged.value
  }
  refinedPlainText.value = ''
  isTextOptimized.value = false
}

// 可读性评分
const calculateReadability = async () => {
  // 优化后评简化版，未优化评原文
  const targetText = isTextOptimized.value && refinedPlainText.value
    ? refinedPlainText.value
    : originalText.value
  if (!targetText || targetText.includes('加载中') || targetText.includes('无可用') || targetText.includes('文档格式异常')) {
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
    const resultData = await readabilityScoreAPI(targetText);
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
    // 优先用缓存（仅"标准"长度命中缓存）
    let resultData = (length === '标准' && summaryCached.value) ? summaryCached.value : null
    if (!resultData) {
      resultData = await refineTextAPI({ original_text: originalTextVal, mode: 'summary', summary_length: length });
    }

    summaryState.value = {
      ...summaryState.value,
      loading: false,
      result: resultData
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

// 生成思维导图
const generateMindmap = async () => {
  // 防抖：防止重复请求
  if (mindmapState.value.loading) return

  const text = originalText.value
  if (!text || text.includes('加载中') || text.includes('无可用') || text.includes('文档格式异常')) {
    mindmapState.value = { visible: true, loading: false, error: '暂无可用文本用于生成思维导图', htmlUrl: '' }
    return
  }
  mindmapState.value = { visible: true, loading: true, error: '', htmlUrl: '' }
  try {
    // 优先用缓存
    if (mindmapCached.value) {
      mindmapState.value = { visible: true, loading: false, error: '', htmlUrl: mindmapCached.value }
      return
    }
    const res = await generateMindmapAPI({ text, max_depth: 4 })
    if (res?.success) {
      const backendBase = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
      const url = res.html_url
      const fullUrl = url.startsWith('http') ? url : `${backendBase}/${url.replace(/^\//, '')}`
      mindmapState.value = { visible: true, loading: false, error: '', htmlUrl: fullUrl }
    } else {
      mindmapState.value = { visible: true, loading: false, error: res?.error || '生成失败', htmlUrl: '' }
    }
  } catch (err) {
    const errMsg = err.response?.data?.detail || err.message || '思维导图生成失败'
    mindmapState.value = { visible: true, loading: false, error: errMsg, htmlUrl: '' }
  }
}

const closeMindmapModal = () => {
  mindmapState.value = { visible: false, loading: false, error: '', htmlUrl: '' }
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
}
const closeModal = (type) => {
  if (type === 'guide') modalState.value.showGuide = false
}

// 监听
watch([posTaggingLoading, taggedText], () => {
  nextTick(() => {
    const el = document.querySelector('.document-content')
    if (el) el.innerHTML = taggedText.value
  })
})
// 词性颜色显隐切换（纯 CSS，无需重建 HTML）
watch(() => config.value.showPosColors, (val) => {
  const el = document.querySelector('.document-content')
  if (el) el.classList.toggle('hide-pos-colors', !val)
})
watch(() => config.value.displayMode, () => {
  fetchPosTagging(allBlocks.value)
})

// 主题切换 — 用 CSS 变量穿透 scoped 样式
watch(() => config.value.selectedTheme, (val) => {
  const themes = { warm: { bg: '#fff9e6', text: '#1f2937' }, dark: { bg: '#1f2937', text: '#e5e7eb' }, white: { bg: '#ffffff', text: '#1f2937' }, blue: { bg: '#eff6ff', text: '#1e40af' } }
  const t = themes[val] || themes.warm
  const root = document.querySelector('.immersive-reader')
  if (root) {
    root.style.setProperty('--theme-bg', t.bg)
    root.style.setProperty('--theme-text', t.text)
    root.style.background = t.bg
  }
}, { immediate: true })

// 自动滚动
let scrollTimer = null
watch(() => config.value.enableScroll, (val) => {
  if (scrollTimer) { clearInterval(scrollTimer); scrollTimer = null }
  if (val) {
    scrollTimer = setInterval(() => {
      window.scrollBy(0, config.value.scrollSpeed || 1)
    }, 50)
  }
})
watch(() => config.value.scrollSpeed, (val) => {
  if (config.value.enableScroll && scrollTimer) {
    clearInterval(scrollTimer)
    scrollTimer = setInterval(() => window.scrollBy(0, val || 1), 50)
  }
})
watch(() => route.params.documents_id, (newVal) => {
  if (newVal) {
    documentId.value = newVal
    loadDocumentData()
  }
})

// 生命周期
onMounted(async () => {
  // 1. 先加载音色列表（预热需要音色数据）
  try {
    const res = await getTTSVoicesAPI()
    const allVoices = res?.voices || res?.data?.voices || []
    const edgeVoices = allVoices.filter(v => v.engine === 'edge-tts')
    const PICK = ['zh-CN-XiaoxiaoNeural','zh-CN-YunxiNeural','en-US-JennyNeural','en-US-GuyNeural']
    voiceList.value = edgeVoices.filter(v => PICK.includes(v.name))
    if (voiceList.value.length > 0) {
      selectedVoice.value = voiceList.value.find(v => (v.locale||'').startsWith('zh'))?.name || voiceList.value[0]?.name
    }
  } catch (e) { console.warn('获取音色列表失败:', e) }

  // 2. 加载文档（finally 中自动触发预热，此时 voiceList 已就绪）
  await loadDocumentData()

  document.addEventListener('click', (e) => {
    if (tooltip.value.visible && !e.target.closest('.word-tooltip')) tooltip.value.visible = false
    if (ttsState.value.showPanel && !e.target.closest('.voice-panel') && e.target.id !== 'playBtn') ttsState.value.showPanel = false
  })
  document.addEventListener('mouseup', async (e) => {
    if (e.target.closest('.document-content')) await handleMouseUp(e)
  })
  // 图片点击放大（事件委托）
  document.addEventListener('click', (e) => {
    const img = e.target.closest('.image-block img')
    if (img) openImagePreview(img.src)
  })
})
onUnmounted(() => {
  stopReading()
  if (highlightTimer) clearInterval(highlightTimer)
  if (scrollTimer) clearInterval(scrollTimer)
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
      <!-- 文档图片侧栏（仅图文分离模式，点击触发） -->
      <div v-if="config.displayMode === 'separated'" class="image-sidebar-container">
        <div class="image-sidebar-tab" @click="toggleImageSidebar" :title="imageSidebarOpen ? '收起图片栏' : '展开图片栏'">
          <span>{{ imageSidebarOpen ? '◀' : '📷' }}</span>
        </div>
        <div class="image-sidebar" :class="{ 'image-sidebar-open': imageSidebarOpen }">
          <div class="image-sidebar-header">
            <span>📷 文档图片</span>
            <button class="image-sidebar-close" @click="imageSidebarOpen = false">✕</button>
          </div>
          <div
            v-for="(block, idx) in allBlocks.filter(b => b.block_type === 'image')"
            :key="idx"
            class="image-sidebar-item"
            @click="openImagePreview(block.image_url.startsWith('http') ? block.image_url : baseUrl() + '/' + block.image_url.replace(/\\/g, '/'))"
          >
            <img
              :src="block.image_url.startsWith('http') ? block.image_url : baseUrl() + '/' + block.image_url.replace(/\\/g, '/')"
              :alt="'第' + block.page + '页图片'"
              loading="lazy"
            />
            <span>第{{ block.page }}页</span>
          </div>
          <div v-if="!allBlocks.some(b => b.block_type === 'image')" class="image-sidebar-empty">
            暂无图片
          </div>
        </div>
      </div>

      <!-- 阅读内容 -->
      <ReaderContent :content="taggedText" :config="config" :is-plain-text="false" :loading="loading"
        :posTaggingLoading="posTaggingLoading" @mouseup="handleMouseUp" />

      <!-- 划词翻译 -->
      <WordTooltip v-model:visible="tooltip.visible" :word-info="tooltip.wordInfo" :position="tooltip.position"
        :font-config="config" />
    </main>

    <!-- 右侧面板（绑定生成摘要事件） -->
    <ReaderPanel :config="config" :is-text-optimized="isTextOptimized" :text-optimize-loading="textOptimizeLoading"
      @open-modal="openModal" @optimize-text="optimizeText"
      @restore-text="restoreText" @calculate-readability="calculateReadability"
      @generate-summary="() => summaryState.visible = true"
      @generate-mindmap="generateMindmap"
      :is-generating="isGenerating" />

    <!-- 阅读指南弹窗 -->
    <ReaderModal :modal-state="modalState" @close-modal="closeModal" />

    <!-- 语音面板 -->
    <VoicePanel :tts-state="ttsState" :voice-list="voiceList" :selected-voice="selectedVoice"
      :tts-pre-warming="ttsPreWarming" :tts-pre-warmed="ttsPreWarmed"
      @toggle-start="toggleStart" @stop-reading="stopReading"
      @speed-input="() => ttsState.speedDisplay = ttsState.speed.toFixed(1)"
      @update:selected-voice="(v) => selectedVoice = v"
      />

    <!-- 可读性评分弹窗 -->
    <ReadabilityModal :visible="readabilityState.visible" :loading="readabilityState.loading"
      :error="readabilityState.error" :result="readabilityState.result" @close="closeReadabilityModal" />

    <!-- 文本摘要弹窗（核心） -->
    <SummaryModal :visible="summaryState.visible" :loading="summaryState.loading" :error="summaryState.error"
      :result="summaryState.result" :original-text="originalText" :selected-length="summaryState.selectedLength"
      @close="closeSummaryModal" @generate-summary="generateSummary" @reset-summary="resetSummary" />

    <!-- 思维导图弹窗 -->
    <MindMapModal
      :visible="mindmapState.visible"
      :loading="mindmapState.loading"
      :error="mindmapState.error"
      :html-url="mindmapState.htmlUrl"
      @update:visible="closeMindmapModal"
      @retry="generateMindmap"
    />

    <!-- 图片全屏预览 -->
    <teleport to="body">
      <div v-if="imagePreview.visible" class="image-preview-overlay" @click="closeImagePreview">
        <img :src="imagePreview.url" class="image-preview-img" @click.stop />
        <button class="image-preview-close" @click="closeImagePreview">✕</button>
      </div>
    </teleport>
  </div>
</template>

<style scoped>
/* 图片全屏预览 */
.image-preview-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  cursor: zoom-out;
}
.image-preview-img {
  max-width: 90vw;
  max-height: 90vh;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.5);
}
.image-preview-close {
  position: absolute;
  top: 20px;
  right: 24px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 24px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}
.image-preview-close:hover {
  background: rgba(255, 255, 255, 0.4);
}

.immersive-reader {
  min-height: 100vh;
  background: #fff9e6;
  display: flex;
  flex-direction: column;
  padding-top: 70px;
  transition: background 0.3s ease;
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

/* 图片侧栏容器 + 触发标签 */
.image-sidebar-container {
  position: fixed;
  left: 0;
  top: 80px;
  bottom: 0;
  z-index: 85;
  pointer-events: none;
}
.image-sidebar-tab {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 60px;
  background: white;
  border: 1px solid #e5e7eb;
  border-left: none;
  border-radius: 0 8px 8px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  pointer-events: auto;
  font-size: 16px;
  box-shadow: 2px 0 8px rgba(0,0,0,0.08);
  transition: all 0.2s;
  z-index: 86;
}
.image-sidebar-tab:hover {
  background: #eff6ff;
  border-color: #2563eb;
}
.image-sidebar {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 360px;
  background: white;
  box-shadow: 4px 0 24px rgba(0,0,0,0.1);
  border-right: 1px solid #e5e7eb;
  overflow-y: auto;
  padding: 24px;
  transform: translateX(-100%);
  transition: transform 0.3s ease;
  pointer-events: auto;
  direction: rtl;
}
.image-sidebar > * { direction: ltr; }
.image-sidebar.image-sidebar-open { transform: translateX(0); }
.image-sidebar::-webkit-scrollbar { width: 6px; }
.image-sidebar::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 3px; }
.image-sidebar::-webkit-scrollbar-thumb { background: #ccc; border-radius: 3px; }
.image-sidebar::-webkit-scrollbar-thumb:hover { background: #999; }
.image-sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
}
.image-sidebar-close {
  width: 28px; height: 28px;
  border: none;
  background: #f3f4f6;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  transition: all 0.2s;
}
.image-sidebar-close:hover { background: #fee2e2; color: #ef4444; }
.image-sidebar-item {
  margin-bottom: 8px;
  cursor: pointer;
  border-radius: 6px;
  overflow: hidden;
  border: 2px solid transparent;
  transition: border-color 0.2s;
}
.image-sidebar-item:hover { border-color: #2563eb; }
.image-sidebar-item img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 4px;
}
.image-sidebar-item span {
  display: block;
  font-size: 10px;
  color: #9ca3af;
  text-align: center;
  padding: 2px 0;
  white-space: nowrap;
  overflow: hidden;
}
.image-sidebar-empty {
  font-size: 11px;
  color: #d1d5db;
  text-align: center;
  padding: 16px 0;
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

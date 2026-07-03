<template>
  <Teleport to="body">
    <div v-if="visible" class="word-tooltip" :style="tooltipStyle" @mouseenter="stopHide" @mouseleave="startHide">
      <!-- 单词标题 + 音标 -->
      <div class="tooltip-header">
        <span class="word">{{ word }}</span>
        <span class="phonetic" v-if="phonetic">{{ phonetic }}</span>
      </div>

      <!-- 词性 + 释义 -->
      <div class="tooltip-body" v-for="(meaning, idx) in meanings" :key="idx">
        <span class="pos">{{ meaning.partOfSpeech }}</span>
        <div class="definitions">
          <div v-for="(def, defIdx) in meaning.definitions" :key="defIdx" class="definition">
            <p>{{ def.definition }}</p>
            <p class="example" v-if="def.example">例：{{ def.example }}</p>
          </div>
        </div>
      </div>

      <!-- 同义词 -->
      <div class="tooltip-footer" v-if="synonyms.length">
        <span class="label">同义词：</span>
        <span class="synonyms">{{ synonyms.join('，') }}</span>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch, onUnmounted, computed } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  wordInfo: {
    type: Object,
    default: () => ({})
  },
  position: {
    type: Object,
    default: () => ({ left: 0, top: 0 })
  },
  // 新增：接收阅读文本的字体配置（从父组件传递）
  fontConfig: {
    type: Object,
    default: () => ({
      selectedFont: 'system-ui',
      fontSize: 22,
      lineHeight: 2.2,
      letterSpacing: 1.5,
      selectedTheme: 'warm'
    })
  }
})

// 定义emit
const emit = defineEmits(['update:visible'])

// 解构数据
const word = ref('')
const phonetic = ref('')
const meanings = ref([])
const synonyms = ref([])

// 自动隐藏定时器
let hideTimer = null

// 解析单词信息
const parseWordInfo = (info) => {
  if (!info.success) return

  word.value = info.word || ''
  phonetic.value = info.phonetic || ''
  meanings.value = info.meanings || []

  // 收集所有同义词
  const syns = []
  meanings.value.forEach(meaning => {
    if (Array.isArray(meaning.synonyms)) {
      syns.push(...meaning.synonyms)
    }
  })
  synonyms.value = [...new Set(syns)].slice(0, 5) // 去重 + 最多显示5个
}

// 延迟隐藏
const startHide = () => {
  hideTimer = setTimeout(() => {
    emit('update:visible', false)
  }, 1000)
}

// 停止隐藏
const stopHide = () => {
  clearTimeout(hideTimer)
}

// 新增：动态计算tooltip样式（和阅读文本字体统一，字号放大）
const tooltipStyle = computed(() => {
  // 主题颜色映射（和阅读文本一致）
  const themeColorMap = {
    warm: '#92400e',
    dark: 'white',
    white: '#1f2937',
    blue: '#1e40af'
  }

  // 基础样式 + 位置
  return {
    // 位置
    left: `${props.position.left}px`,
    top: `${props.position.top}px`,
    // 字体样式（和阅读文本统一，字号放大1.2倍）
    fontFamily: props.fontConfig.selectedFont || 'system-ui',
    color: themeColorMap[props.fontConfig.selectedTheme] || '#92400e',
    letterSpacing: `${props.fontConfig.letterSpacing || 1.5}px`,
    // 字号放大（阅读文本字号*1.2，最小16px，最大20px）
    fontSize: `${Math.min(Math.max(props.fontConfig.fontSize * 1.2, 16), 20)}px`,
    lineHeight: props.fontConfig.lineHeight || 2.2
  }
})

// 监听props变化
watch(() => props.wordInfo, parseWordInfo, { immediate: true })
watch(() => props.visible, (val) => {
  if (val) {
    stopHide() // 显示时清除隐藏定时器
  } else {
    clearTimeout(hideTimer) // 隐藏时清空定时器
  }
})

// 组件卸载时清空定时器
onUnmounted(() => {
  clearTimeout(hideTimer)
})
</script>

<style scoped>
/* 基础样式：移除固定字号，由动态样式控制 */
.word-tooltip {
  position: absolute;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.18);
  padding: 20px;
  /* 加大内边距，更舒适 */
  z-index: 9999;
  min-width: 320px;
  /* 加宽tooltip */
  max-width: 450px;
  max-height: 450px;
  overflow-y: auto;
  /* 移除固定font-size，由动态样式控制 */
  transition: all 0.2s ease;
}

.tooltip-header {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

/* 单词标题：在基础字号上再放大1.1倍 */
.word {
  font-size: 1.1em;
  font-weight: 600;
  display: inline-block;
  margin-right: 8px;
}

/* 音标：字号稍小，保持样式统一 */
.phonetic {
  color: #6b7280;
  font-style: italic;
  font-size: 0.9em;
}

.tooltip-body {
  margin: 12px 0;
}

/* 词性标签：样式优化，字号适配 */
.pos {
  display: inline-block;
  padding: 4px 10px;
  background: #eff6ff;
  color: #2563eb;
  border-radius: 6px;
  font-size: 0.9em;
  margin-right: 8px;
  margin-bottom: 6px;
}

.definitions {
  margin-left: 4px;
}

.definition {
  margin: 8px 0;
  line-height: 1.6;
}

/* 例句：字号稍小，样式统一 */
.example {
  margin: 6px 0 0 0;
  color: #6b7280;
  font-style: italic;
  font-size: 0.9em;
}

.tooltip-footer {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.label {
  color: #6b7280;
  font-size: 0.9em;
}

.synonyms {
  color: #2563eb;
  margin-left: 6px;
  font-size: 0.95em;
}

/* 滚动条优化 */
.word-tooltip::-webkit-scrollbar {
  width: 6px;
}

.word-tooltip::-webkit-scrollbar-track {
  background: #f5f5f5;
  border-radius: 3px;
}

.word-tooltip::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}
</style>

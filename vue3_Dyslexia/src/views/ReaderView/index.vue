<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

// 引入组件（原有代码不变）
import ReaderHeader from './Components/ReaderHeader.vue';
import ReaderContent from './Components/ReaderContent.vue';
import ReaderPanel from './Components/ReaderPanel.vue';
import ReaderModal from './Components/ReaderModal.vue';
import ImagePanel from './Components/ReaderImagePanel.vue';

import { documentsDetailAPI, documentsDetail_structuredAPI } from '@/apis/documents';

// 路由实例（原有代码不变）
const router = useRouter();
const route = useRoute();

// 响应式数据（原有代码不变）
const loading = ref(false);
const documentInfo = ref({
  id: 0,
  original_filename: '001.pdf',
  file_type: 'pdf',
  extracted_text: '',
  blocks: []
});
const documentContent = ref('');
const documentImages = ref([]);

// 样式配置（原有代码不变）
const readerConfig = ref({
  fontSize: 20,
  lineHeight: 1.8,
  letterSpacing: 0,
  selectedFont: 'system-ui',
  selectedTheme: 'warm',
  selectedColor: '#ffeb3b',
  enableRuler: false,
  enableFocus: false,
  enableScroll: false,
  highlighted: false
});

// ========== 仅新增这一行：根据主题获取背景色 ==========
const getThemeBackground = () => {
  const themeMap = {
    warm: '#fff9e6',
    dark: '#1f2937',
    white: '#ffffff',
    blue: '#eff6ff'
  };
  return themeMap[readerConfig.value.selectedTheme] || '#fff9e6';
};
// ========== 背景相关新增结束 ==========

// 其余原有代码完全不变（左侧图片列、弹窗、工具函数、初始化等）
const imagePanelVisible = ref(false);
const CONTENT_MAX_WIDTH = 800;
const modalState = ref({
  showSummary: false,
  showGuide: false,
  showImage: false
});
const imageModalData = ref({
  url: '',
  caption: ''
});
const summaryContent = ref('暂无摘要，请先导入文档');

const escapeRegExp = (str) => {
  if (!str || typeof str !== 'string') return '';
  return str.replace(/[\\^$.*+?|()[\]{}]/g, '\\$&');
};

const processDocumentBlocks = (blocks) => {
  if (!blocks || blocks.length === 0) {
    documentContent.value = '';
    documentImages.value = [];
    return;
  }
  const sortedBlocks = [...blocks].sort((a, b) => a.block_order - b.block_order);
  let plainText = '';
  const images = [];
  const backendBaseUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
  sortedBlocks.forEach((block, index) => {
    if (block.block_type === 'text' && block.text_content && block.text_content.trim()) {
      plainText += block.text_content.trim() + '\n\n';
    } else if (block.block_type === 'image' && block.image_url) {
      let imageUrl = block.image_url;
      imageUrl = imageUrl.replace(/\\/g, '/');
      if (!imageUrl.startsWith('http')) {
        if (imageUrl.startsWith('/')) {
          imageUrl = imageUrl.substring(1);
        }
        imageUrl = `${backendBaseUrl}/${imageUrl}`;
      }
      images.push({
        id: index + 1,
        url: imageUrl,
        caption: block.image_caption || `图片 ${index + 1}`
      });
    }
  });
  documentContent.value = plainText.trim();
  documentImages.value = images;
};

const openImageModal = (url, caption) => {
  imageModalData.value = { url, caption };
  modalState.value.showImage = true;
};

const closeImageModal = () => {
  modalState.value.showImage = false;
  imageModalData.value = { url: '', caption: '' };
};

const handleMouseMoveImagePanel = (e) => {
  const screenWidth = window.innerWidth;
  const contentLeft = (screenWidth - CONTENT_MAX_WIDTH) / 2;
  if (e.clientX < contentLeft && e.clientX < 100) {
    imagePanelVisible.value = true;
  } else if (e.clientX > contentLeft + 50) {
    imagePanelVisible.value = false;
  }
};

const initDocument = async () => {
  try {
    loading.value = true;
    const documentId = route.params.documents_id || route.query.id;
    if (!documentId) {
      throw new Error('缺少文档ID，请检查路由参数');
    }
    const structuredDoc = await documentsDetail_structuredAPI(documentId);
    documentInfo.value = {
      id: structuredDoc.id,
      original_filename: structuredDoc.original_filename,
      file_type: structuredDoc.file_type,
      extracted_text: '',
      blocks: structuredDoc.blocks || []
    };
    if (structuredDoc.blocks && structuredDoc.blocks.length > 0) {
      processDocumentBlocks(structuredDoc.blocks);
      generateSummary();
    } else {
      const docDetail = await documentsDetailAPI(documentId);
      documentContent.value = docDetail.extracted_text || '';
      generateSummary();
    }
  } catch (error) {
    let errorMsg = '加载文档失败，请稍后重试';
    if (error.response) {
      errorMsg = `请求错误 [${error.response.status}]：${error.response.data?.detail || '服务器返回异常'}`;
    } else if (error.message) {
      errorMsg = error.message;
    }
    alert(errorMsg);
    documentContent.value = '';
  } finally {
    loading.value = false;
  }
};

const generateSummary = () => {
  if (!documentContent.value) {
    summaryContent.value = '暂无摘要：文档中未提取到文本内容';
    return;
  }
  const text = documentContent.value.substring(0, 300);
  const cleanText = text.replace(/\n+/g, ' ').trim();
  summaryContent.value = `本文主要内容：${cleanText}${cleanText.length >= 300 ? '……' : ''}\n\n（完整摘要可通过LLM接口生成）`;
};

const methods = {
  handleBack: () => router.back(),
  extractKeywords: () => {
    if (!documentContent.value) {
      alert('暂无文档内容可高亮');
      return;
    }
    const originalText = documentContent.value;
    const text = originalText.toLowerCase();
    const keywords = [];
    if (text) {
      const wordMatches = text.match(/[\u4e00-\u9fa5a-zA-Z0-9]{2,}/g) || [];
      const wordCount = {};
      wordMatches.forEach(word => {
        if (word.length >= 2) {
          wordCount[word] = (wordCount[word] || 0) + 1;
        }
      });
      const sortedWords = Object.entries(wordCount)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 6);
      sortedWords.forEach(([word]) => keywords.push(word));
    }
    if (keywords.length === 0) {
      keywords.push('blockchain', 'defi', 'multi-chain', 'finance', 'layerzero', 'cosmos');
    }
    let highlightedText = originalText;
    keywords.forEach(k => {
      try {
        const escapedKey = escapeRegExp(k);
        if (!escapedKey) return;
        const reg = new RegExp(`(${escapedKey})`, 'gi');
        highlightedText = highlightedText.replace(
          reg,
          `<span style="background:${readerConfig.value.selectedColor};padding:0 2px;border-radius:2px;">$1</span>`
        );
      } catch (e) {
        return;
      }
    });
    documentContent.value = highlightedText;
    readerConfig.value.highlighted = true;
    alert(`已高亮 ${keywords.filter(k => originalText.includes(k)).length} 个关键词！`);
  },
  clearHighlight: () => {
    if (documentInfo.value.blocks.length > 0) {
      processDocumentBlocks(documentInfo.value.blocks);
    }
    readerConfig.value.highlighted = false;
  },
  togglePanel: (panelRef) => {
    if (panelRef) {
      const isVisible = panelRef.style.transform !== 'translateX(100%)';
      panelRef.style.transform = isVisible ? 'translateX(100%)' : 'translateX(0)';
    }
  },
  openModal: (type) => {
    if (type === 'summary') {
      modalState.value.showSummary = true;
    } else if (type === 'guide') {
      modalState.value.showGuide = true;
    }
  },
  closeModal: (type) => {
    if (type === 'summary') {
      modalState.value.showSummary = false;
    } else if (type === 'guide') {
      modalState.value.showGuide = false;
    }
  },
  openImageModal,
  closeImageModal
};

watch(
  () => route.params.documents_id || route.query.id,
  async () => {
    try {
      await initDocument();
    } catch (e) {
      console.error('路由变化处理失败：', e);
    }
  },
  { immediate: true, flush: 'post' }
);

onMounted(() => {
  document.addEventListener('mousemove', handleMouseMoveImagePanel);
});

onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMoveImagePanel);
  if (readerConfig.value.enableScroll) {
    const scrollTimer = window.scrollTimer;
    if (scrollTimer) clearInterval(scrollTimer);
  }
});
</script>

<template>
  <!-- 仅新增:style绑定背景色 -->
  <div class="reader-container" :style="{ background: getThemeBackground() }">
    <ImagePanel :images="documentImages" :visible="imagePanelVisible" @open-image="methods.openImageModal" />
    <ReaderHeader :title="documentInfo.original_filename || '文档阅读'" :document-id="documentInfo.id"
      @back="methods.handleBack" />
    <ReaderContent :loading="loading" :content="documentContent" :config="readerConfig" is-plain-text="true" />
    <ReaderPanel :config="readerConfig" @extract-keywords="methods.extractKeywords"
      @clear-highlight="methods.clearHighlight" @open-modal="methods.openModal" />
    <ReaderModal :modal-state="modalState" @close-modal="methods.closeModal">
      <template #summary-content>
        <p style="margin:16px 0;line-height:1.7;white-space: pre-line;">
          {{ summaryContent }}
        </p>
      </template>
    </ReaderModal>
    <div v-if="modalState.showImage" class="image-modal-overlay" @click="methods.closeImageModal">
      <div class="image-modal-content" @click.stop>
        <button class="image-modal-close" @click="methods.closeImageModal">×</button>
        <img :src="imageModalData.url" :alt="imageModalData.caption" class="modal-image" />
        <p v-if="imageModalData.caption" class="modal-image-caption">{{ imageModalData.caption }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.reader-container {
  /* 仅修改：去掉固定背景色，改为动态绑定 */
  background: transparent;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  transition: background 0.3s ease;
  margin-top: 40px;
  position: relative;
}

/* 其余样式完全不变 */
:deep(body) {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.image-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-modal-content {
  max-width: 90%;
  max-height: 90%;
  position: relative;
}

.modal-image {
  max-width: 100%;
  max-height: 80vh;
  border-radius: 8px;
}

.modal-image-caption {
  color: white;
  text-align: center;
  margin-top: 8px;
  font-size: 14px;
}

.image-modal-close {
  position: absolute;
  top: -20px;
  right: -20px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: white;
  color: black;
  border: none;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>

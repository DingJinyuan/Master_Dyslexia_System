<template>
  <div class="recent-section">
    <div class="recent-header">
      <h2>阅读历史</h2>
      <div class="header-right">
        <span class="doc-count" v-if="!loading">共 {{ total }} 篇</span>
        <button v-if="hasMore" class="expand-btn-inline" @click="showAllModal = true">展开更多</button>
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载阅读记录...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="bookList.length === 0" class="empty-state">
      <p>暂无阅读记录</p>
      <p class="empty-hint">上传文档后即可开始阅读</p>
    </div>

    <!-- 文档列表（最多展示 6 本） -->
    <div v-else>
      <div class="recent-grid">
        <div v-for="doc in displayedBooks" :key="doc.id" class="book-card"
          @click="openDocument(doc.id)"
          @mouseenter="handleHover" @mouseleave="handleLeave">
          <div class="book-icon" :style="{ background: getIconBg(doc.id) }">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
              stroke="white" width="28" height="28">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H7.125A3.375 3.375 0 003.75 5.625v12.75a3.375 3.375 0 003.375 3.375h1.5a1.125 1.125 0 011.125 1.125v1.5a3.375 3.375 0 003.375 3.375h1.5a3.375 3.375 0 003.375-3.375V14.25z" />
            </svg>
            <span class="doc-type">{{ getFileType(doc.original_filename) }}</span>
          </div>
          <div class="book-info">
            <div class="book-title">{{ doc.original_filename || '未命名文档' }}</div>
            <div class="book-meta">{{ formatDate(doc.created_at) }}</div>
          </div>
        </div>
      </div>

    </div>

    <!-- 全部文档弹窗 -->
    <teleport to="body">
      <div v-if="showAllModal" class="all-docs-overlay" @click.self="showAllModal = false">
        <div class="all-docs-modal">
          <div class="all-docs-header">
            <h3>全部文档 ({{ bookList.length }})</h3>
            <button class="all-docs-close" @click="showAllModal = false">✕</button>
          </div>
          <div class="all-docs-grid">
            <div v-for="doc in bookList" :key="doc.id" class="book-card"
              @click="openDocument(doc.id); showAllModal = false"
              @mouseenter="handleHover" @mouseleave="handleLeave">
              <div class="book-icon" :style="{ background: getIconBg(doc.id) }">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                  stroke="white" width="28" height="28">
                  <path stroke-linecap="round" stroke-linejoin="round"
                    d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H7.125A3.375 3.375 0 003.75 5.625v12.75a3.375 3.375 0 003.375 3.375h1.5a1.125 1.125 0 011.125 1.125v1.5a3.375 3.375 0 003.375 3.375h1.5a3.375 3.375 0 003.375-3.375V14.25z" />
                </svg>
                <span class="doc-type">{{ getFileType(doc.original_filename) }}</span>
              </div>
              <div class="book-info">
                <div class="book-title">{{ doc.original_filename || '未命名文档' }}</div>
                <div class="book-meta">{{ formatDate(doc.created_at) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { documentsListAPI } from '@/apis/documents.js'

const emit = defineEmits(['cardHover', 'cardLeave'])
const handleHover = () => emit('cardHover')
const handleLeave = () => emit('cardLeave')

const router = useRouter()
const bookList = ref([])
const total = ref(0)
const loading = ref(true)
const showAllModal = ref(false)

const DISPLAY_LIMIT = 4
const displayedBooks = computed(() => bookList.value.slice(0, DISPLAY_LIMIT))
const hasMore = computed(() => bookList.value.length > DISPLAY_LIMIT)

// 渐变色池
const gradients = [
  'linear-gradient(135deg, #fb923c, #f97316)',
  'linear-gradient(135deg, #10b981, #059669)',
  'linear-gradient(135deg, #9333ea, #7e22ce)',
  'linear-gradient(135deg, #3b82f6, #2563eb)',
  'linear-gradient(135deg, #ec4899, #db2777)',
  'linear-gradient(135deg, #f59e0b, #d97706)',
]
const getIconBg = (id) => gradients[id % gradients.length]
const getFileType = (filename) => {
  if (!filename) return ''
  const ext = filename.split('.').pop()?.toLowerCase()
  return ext?.toUpperCase() || ''
}
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now - d
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days} 天前`
  return d.toLocaleDateString('zh-CN')
}

const openDocument = (id) => {
  router.push(`/chenjinshi/${id}`)
}

onMounted(async () => {
  try {
    const res = await documentsListAPI(1, 100)
    bookList.value = res?.items || []
    total.value = res?.total || bookList.value.length
  } catch (err) {
    console.warn('加载文档列表失败:', err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.recent-section {
  display: flex;
  flex-direction: column;
}
.recent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.recent-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  letter-spacing: -0.3px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.doc-count {
  font-size: 0.9rem;
  color: #6b7280;
}
.expand-btn-inline {
  padding: 6px 16px;
  background: white;
  border: 1.5px solid #d1d5db;
  border-radius: 8px;
  font-size: 13px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}
.expand-btn-inline:hover {
  border-color: #9333ea;
  color: #9333ea;
  background: #faf5ff;
}
.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: #6b7280;
}
.empty-hint {
  font-size: 0.85rem;
  margin-top: 4px;
  color: #9ca3af;
}
.spinner {
  width: 30px; height: 30px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #9333ea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}
@keyframes spin { 100% { transform: rotate(360deg); } }
.recent-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 20px;
  width: 100%;
}
.book-card {
  background-color: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: all 0.3s ease;
  cursor: pointer;
}
.book-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
}
.book-icon {
  width: 40px; height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: white;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex-direction: column;
}
.doc-type {
  font-size: 8px;
  font-weight: 700;
  margin-top: 2px;
}
.book-info { width: 100%; }
.book-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 6px;
  color: #1f2937;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-all;
}
.book-meta {
  font-size: 0.85rem;
  color: #6b7280;
}

/* 全部文档弹窗 */
.all-docs-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
}
.all-docs-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  width: 70%;
  max-width: 900px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}
.all-docs-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 12px;
  border-bottom: 1px solid #f3f4f6;
}
.all-docs-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}
.all-docs-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #f3f4f6;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  transition: all 0.2s;
}
.all-docs-close:hover {
  background: #fee2e2;
  color: #ef4444;
}
.all-docs-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding: 20px 24px;
  overflow-y: auto;
  overflow-x: hidden;
  max-height: calc(85vh - 72px);
}
</style>

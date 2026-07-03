<script setup>
defineProps({
  visible: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  htmlUrl: { type: String, default: '' },
})

defineEmits(['update:visible', 'retry'])
</script>

<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    title="🧠 思维导图"
    width="90%"
    align-center
    destroy-on-close
  >
    <!-- 加载状态 -->
    <div v-if="loading" class="mindmap-loading">
      <div class="loading-spinner"></div>
      <p>AI 正在分析文档结构，生成思维导图...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="mindmap-error">
      <p class="error-text">{{ error }}</p>
      <button class="retry-btn" @click="$emit('retry')">🔄 重试</button>
    </div>

    <!-- 导图 iframe -->
    <iframe
      v-else-if="htmlUrl"
      :src="htmlUrl"
      class="mindmap-iframe"
      frameborder="0"
    />

    <!-- 空状态 -->
    <div v-else class="mindmap-empty">
      <p>暂无思维导图数据</p>
    </div>

    <template #footer>
      <el-button @click="$emit('update:visible', false)">关闭</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.mindmap-iframe {
  width: 100%;
  height: 80vh;
  border: none;
  border-radius: 8px;
  background: #fff;
}

.mindmap-loading,
.mindmap-error,
.mindmap-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  text-align: center;
  color: #6b7280;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

.error-text {
  color: #ef4444;
  margin-bottom: 16px;
  max-width: 500px;
}

.retry-btn {
  padding: 8px 20px;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.retry-btn:hover {
  background: #1d4ed8;
}
</style>

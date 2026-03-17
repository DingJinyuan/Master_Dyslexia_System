<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import CharacterGroup from './Components/CharacterGroup.vue';
// 导入上传接口
import { documentsUploadAPI } from '@/apis/documents';

const router = useRouter();
const dropAreaRef = ref(null);
const fileInputRef = ref(null);
const isSmiling = ref(false);
const isDraggingOver = ref(false);
const isUploading = ref(false); // 上传状态

// 返回首页
const handleBack = () => {
  router.push('/');
};

// 小人hover事件
const handleCharHover = () => {
  isSmiling.value = true;
};

const handleCharLeave = () => {
  isSmiling.value = false;
};

// 拖放事件
const handleDragEnter = (e) => {
  e.preventDefault();
  isDraggingOver.value = true;
  isSmiling.value = true;
};

const handleDragOver = (e) => {
  e.preventDefault();
  isDraggingOver.value = true;
};

const handleDragLeave = () => {
  isDraggingOver.value = false;
  if (!document.querySelector('.char:hover')) {
    isSmiling.value = false;
  }
};


// 上传成功后的跳转逻辑
const uploadFile = async (file) => {
  try {
    isUploading.value = true;
    const formData = new FormData();
    formData.append('file', file);

    // 调用上传接口
    const response = await documentsUploadAPI(formData);
    //console.log("接口返回内容：", response);

    // 关键1：严格校验 id 存在性
    if (!response || !response.id) {
      throw new Error('接口未返回有效的文档ID');
    }
    const documentsId = response.id; // 拿到正确的 ID（8）

    // 关键2：规范跳转（和路由定义的参数名 documents_id 严格匹配）
    router.push({
      path: `/reader_view/${documentsId}`,
      // 或用命名路由（推荐，更稳定）
      // name: 'ReaderView',
      // params: { documents_id: documentsId }
    });

  } catch (error) {
    //console.error('上传/跳转失败详情：', error);
    const errorMsg = error.response?.data?.detail || error.message || '上传失败，请重试';
    alert('上传失败：' + errorMsg);
  } finally {
    isUploading.value = false;
  }
};

// 拖放上传（保留）
const handleDrop = (e) => {
  e.preventDefault();
  const file = e.dataTransfer.files[0];
  uploadFile(file);
};

// 修复：选择文件上传（核心修改）
const selectFile = () => {
  if (isUploading.value) return;

  // 方案：不提前重置，改为选择后再重置，避免清空未触发的change事件
  // 直接触发输入框点击，确保DOM已挂载
  if (fileInputRef.value) {
    // 强制聚焦并触发点击，解决层级问题
    fileInputRef.value.click();
  }
};

// 修复：文件选择change事件
const handleFileChange = (e) => {
  // 立即获取文件，避免DOM刷新丢失
  const file = e.target.files[0];
  if (file) {
    // 先重置输入框（避免重复选择同一文件不触发），再上传
    e.target.value = '';
    uploadFile(file);
  }
};
</script>

<template>
  <div class="upload-page">
    <div class="scene">
      <!-- 引入小人组件 -->
      <CharacterGroup @charHover="handleCharHover" @charLeave="handleCharLeave" />

      <!-- 主卡片 -->
      <div class="main-box">
        <div class="header">
          <button class="back-btn" @click="handleBack" :disabled="isUploading">
            ←
          </button>
          <div class="title">导入本地文档</div>
        </div>

        <div class="content">
          <div class="drop-area" ref="dropAreaRef" @dragenter="handleDragEnter" @dragover="handleDragOver"
            @dragleave="handleDragLeave" @drop="handleDrop" @mouseenter="isSmiling = true"
            @mouseleave="isSmiling = false" :class="{ dragover: isDraggingOver }">
            <div class="drop-icon">☁️</div>
            <div class="drop-title">
              {{ isUploading ? '正在上传...' : '把文件拖到这里' }}
            </div>
            <div class="drop-desc">
              {{ isUploading ? '请稍候...' : '支持 PDF、电子书、文本文件' }}
            </div>
          </div>

          <div class="divider">或者</div>

          <!-- 修复：将文件输入框移到按钮外部，避免层级冲突 -->
          <div class="upload-btn-wrapper">
            <button class="primary-btn" @click="selectFile" @mouseenter="isSmiling = true"
              @mouseleave="isSmiling = false" :disabled="isUploading">
              {{ isUploading ? '上传中...' : '📄 从文件夹中选取文件' }}
            </button>
            <!-- 独立的文件输入框，避免被按钮覆盖 -->
            <input type="file" ref="fileInputRef" class="file-input" accept=".pdf,.txt,.epub"
              @change="handleFileChange" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: system-ui, -apple-system, sans-serif;
}

.upload-page {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #f9f7ff, #e2e8ff);
  display: flex;
  align-items: center;
  justify-content: center;
}

.scene {
  width: 1000px;
  height: 650px;
  position: relative;
}

/* 主盒子 */
.main-box {
  width: 100%;
  height: 100%;
  background: #fff;
  border-radius: 32px;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 28px 40px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  gap: 20px;
}

/* 返回按钮 */
.back-btn {
  width: 50px;
  height: 50px;
  border-radius: 14px;
  border: none;
  background: #f3f4f6;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.back-btn:hover:not(:disabled) {
  background: #e5e7eb;
}

.back-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.title {
  font-size: 22px;
  font-weight: 600;
  color: #111;
}

.content {
  flex: 1;
  padding: 60px 50px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 32px;
}

.drop-area {
  width: 100%;
  max-width: 700px;
  height: 300px;
  border: 2px dashed #93c5fd;
  border-radius: 20px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.drop-area.dragover {
  border-color: #3b82f6;
  background: #eff6ff;
  transform: scale(1.02);
}

.drop-icon {
  width: 80px;
  height: 80px;
  background: #3b82f6;
  border-radius: 50%;
  color: white;
  font-size: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drop-title {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
}

.drop-desc {
  color: #64748b;
}

.divider {
  width: 100%;
  max-width: 700px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #94a3b8;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #e2e8f0;
}

/* 修复：新增按钮包裹层，分离按钮和输入框 */
.upload-btn-wrapper {
  position: relative;
  display: inline-block;
}

.primary-btn {
  padding: 18px 36px;
  background: #9333ea;
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 18px;
  cursor: pointer;
  transition: background 0.2s;
  /* 移除relative，避免层级覆盖 */
}

.primary-btn:hover:not(:disabled) {
  background: #7e22ce;
}

.primary-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  background: #a855f7;
}

/* 修复：重新定位文件输入框 */
.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 10;
  /* 确保输入框在最上层，能接收到点击 */
}
</style>

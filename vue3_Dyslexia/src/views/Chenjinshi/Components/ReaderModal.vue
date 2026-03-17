<script setup>
import { ref, defineProps, defineEmits } from 'vue';

// 接收属性
const props = defineProps({
  modalState: {
    type: Object,
    required: true,
    default: () => ({
      showGuide: false,
      showSummary: false
    })
  }
});

// 定义事件
const emit = defineEmits(['close-modal']);

// 指南内容
const guideContent = `• 阅读障碍尺：跟随鼠标，帮助聚焦单行文字
• 焦点引导屏：屏蔽干扰，专注中间阅读区域
• 文本优化：增大文字间距，提升阅读舒适度
• 划词释义：选中单词自动显示释义
• TTS语音：支持多音色、可调速的文字朗读
• 漫画解读：AI将文档内容生成漫画场景`;
</script>

<template>
  <!-- 摘要弹窗 -->
  <teleport to="body">
    <div class="modal" v-if="modalState.showSummary" @click.self="emit('close-modal', 'summary')">
      <div class="modal-content">
        <h3>📝 LLM智能摘要</h3>
        <!-- 插槽：自定义摘要内容 -->
        <slot name="summary-content">
          <p style="margin:16px 0;line-height:1.7;white-space: pre-line;">
            暂无摘要数据
          </p>
        </slot>
        <button class="func-btn" @click="emit('close-modal', 'summary')">关闭</button>
      </div>
    </div>
  </teleport>

  <!-- 阅读指南弹窗 -->
  <teleport to="body">
    <div class="modal" v-if="modalState.showGuide" @click.self="emit('close-modal', 'guide')">
      <div class="modal-content">
        <h3>📖 沉浸式阅读指南</h3>
        <p style="margin:16px 0;line-height:1.8;white-space: pre-line;">
          {{ guideContent }}
        </p>
        <button class="func-btn" @click="emit('close-modal', 'guide')">关闭</button>
      </div>
    </div>
  </teleport>
</template>

<style scoped>
/* 弹窗遮罩 */
.modal {
  position: fixed;
  left: 0;
  top: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(2px);
}

/* 弹窗内容 */
.modal-content {
  background: #fff;
  width: 90%;
  max-width: 600px;
  padding: 24px;
  border-radius: 12px;
  position: relative;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

/* 弹窗标题 */
.modal-content h3 {
  margin: 0 0 16px 0;
  color: #1f2937;
  font-size: 18px;
  font-weight: 600;
}

/* 功能按钮 */
.func-btn {
  width: 100%;
  padding: 10px;
  margin-top: 8px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.func-btn:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}
</style>

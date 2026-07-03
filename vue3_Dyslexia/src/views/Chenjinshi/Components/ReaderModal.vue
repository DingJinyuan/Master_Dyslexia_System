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
const guideContent = `📖 显示模式
• 图文共存：图片嵌入文本中，图文一起阅读，左侧不触发图片栏
• 图文分离：文字与图片分开，鼠标移到屏幕左边缘可展开图片栏查看文档插图

🎨 词性标注
• 自动识别文本中每个词汇的词性（名词/动词/形容词等），用不同颜色高亮显示
• 可在右侧面板开启/关闭词性颜色，也可查看完整颜色图例

📏 阅读障碍尺
• 开启后跟随鼠标显示一条水平横线，帮助聚焦当前行
• 尺的高度可在右侧面板调节（10-100px）

🎯 焦点引导屏
• 遮罩除中间区域外的上下部分，减少周围文字干扰
• 可视区域高度可在右侧面板调节（50-500px）

📝 AI 文本优化
• 通过多轮 AI 迭代改写文本，优化句长和词汇难度，让阅读更轻松
• 点击"恢复原始文本"可随时还原

🔍 划词翻译
• 在文本中选中任意单词或短语，自动弹出释义、音标、例句和同义词
• 支持中文和英文词汇查询

🔊 TTS 语音朗读
• 支持多种音色（中文/英文/其他语言），语速 0.5x - 2.0x 可调
• 朗读过程中自动高亮当前句子并跟随滚动

📊 可读性评分
• 分析文本难度，计算综合评分、语言类型、易读等级和详细文本统计

📝 AI 文本摘要
• 调用多轮 AI 迭代生成摘要，支持简短/标准/详细三种长度
• 保留核心关键词和关键信息

🧠 思维导图
• 基于文本内容自动生成结构化思维导图，帮助梳理文档脉络

🖼️ 图片查看
• 点击文本中的图片可全屏放大预览
• 图文分离模式下，鼠标移到屏幕左边缘可浏览所有文档图片`;
</script>

<template>
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

<script setup>
import { ref, watch, computed, onMounted, onUnmounted, onErrorCaptured } from 'vue';



const props = defineProps({
    modalState: {
        type: Object,
        required: true
    }
});

const emit = defineEmits(['close-modal']);

// 指南内容
const guideContent = `• 阅读障碍尺：跟随鼠标，帮助聚焦单行文字
• 焦点引导屏：屏蔽干扰，专注中间阅读区域
• 自动滚动：无需手动翻页，自动匀速阅读
• LLM关键词：AI自动提取核心词汇并高亮`;
</script>

<template>
    <!-- 摘要弹窗 -->
    <teleport to="body">
        <div class="modal" v-if="modalState.showSummary" @click.self="emit('close-modal', 'summary')">
            <div class="modal-content">
                <h3>LLM智能摘要</h3>
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
                <h3>阅读指南</h3>
                <p style="margin:16px 0;line-height:1.8;white-space: pre-line;">
                    {{ guideContent }}
                </p>
                <button class="func-btn" @click="emit('close-modal', 'guide')">关闭</button>
            </div>
        </div>
    </teleport>
</template>

<style scoped>
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
}

.modal-content {
    background: #fff;
    width: 90%;
    max-width: 600px;
    padding: 24px;
    border-radius: 12px;
    position: relative;
}

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
}
</style>
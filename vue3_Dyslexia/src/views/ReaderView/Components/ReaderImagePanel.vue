<script setup>
import { ref, defineProps, defineEmits } from 'vue';

// 接收属性
const props = defineProps({
    images: {
        type: Array,
        default: () => []
    },
    visible: {
        type: Boolean,
        default: false
    }
});

// 定义事件
const emit = defineEmits(['open-image']);

// 打开图片弹窗
const handleOpenImage = (url, caption) => {
    emit('open-image', url, caption);
};
</script>

<template>
    <div class="image-panel-container">
        <!-- 图片列主体（宽度加宽到360px，滚动条在左侧） -->
        <div class="image-panel" :style="{ transform: visible ? 'translateX(0)' : 'translateX(-100%)' }">
            <div class="panel-header">🖼️ 文档图片</div>

            <!-- 无图片提示 -->
            <div v-if="images.length === 0" class="no-images">
                暂无图片
            </div>

            <!-- 图片列表 -->
            <div v-else class="images-list">
                <div v-for="image in images" :key="image.id" class="image-item"
                    @click="handleOpenImage(image.url, image.caption)">
                    <img :src="image.url" :alt="image.caption" class="image-thumbnail" loading="lazy"
                        onerror="this.onerror=null; this.src='./static/default-image.png';">
                    <p class="image-caption">{{ image.caption }}</p>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* 容器样式 */
.image-panel-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 90;
    pointer-events: none;
}

/* 图片列主体（宽度加宽到360px） */
.image-panel {
    pointer-events: auto;
    width: 360px;
    /* 加宽：从280px → 360px */
    height: 100vh;
    background: white;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.1);
    padding: 24px;
    overflow-y: auto;
    position: absolute;
    top: 40px;
    left: 0;
    transform: translateX(-100%);
    transition: transform 0.3s ease;

    /* 核心：滚动条移到左侧 */
    direction: rtl;
    /* 反向排版 */
    padding-left: 12px;
    /* 给滚动条留空间 */
}

/* 滚动条样式（左侧） */
.image-panel::-webkit-scrollbar {
    width: 6px;
    height: 6px;
    margin-left: 10px;
}

.image-panel::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
}

.image-panel::-webkit-scrollbar-thumb {
    background: #ccc;
    border-radius: 3px;
}

.image-panel::-webkit-scrollbar-thumb:hover {
    background: #999;
}

/* 内部内容恢复正向排版 */
.image-panel>* {
    direction: ltr;
}

/* 无图片提示 */
.no-images {
    text-align: center;
    padding: 20px;
    color: #666;
    font-size: 14px;
}

/* 图片列表 */
.images-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin-top: 16px;
}

/* 图片项 */
.image-item {
    cursor: pointer;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #eee;
    transition: box-shadow 0.2s;
}

.image-item:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 图片缩略图（适配加宽的容器） */
.image-thumbnail {
    width: 100%;
    height: 180px;
    /* 缩略图加高，适配宽容器 */
    object-fit: cover;
}

/* 图片标题 */
.image-caption {
    padding: 8px;
    font-size: 12px;
    color: #666;
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* 面板标题 */
.panel-header {
    font-size: 16px;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 8px;
}
</style>
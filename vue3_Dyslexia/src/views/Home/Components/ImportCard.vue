<template>
    <div class="import-card-container">
        <!-- 添加点击事件跳转 -->
        <div class="import-card" @mouseenter="handleHover" @mouseleave="handleLeave" @click="goToUploadPage">
            <div class="import-icon">
                <div class="plus">+</div>
            </div>
            <h3>导入新文档</h3>
            <p>支持 PDF, TXT, EPUB 等格式</p>
        </div>
    </div>
</template>

<script setup>
// 引入路由
import { useRouter } from 'vue-router';

// 定义事件，供父组件同步小人表情
const emit = defineEmits(['cardHover', 'cardLeave'])

// 获取路由实例
const router = useRouter();

const handleHover = () => emit('cardHover')
const handleLeave = () => emit('cardLeave')

// 新增：跳转到upload页面
const goToUploadPage = () => {
    router.push('/upload');
}
</script>

<style scoped>
.import-card-container {
    display: flex;
    flex-direction: column;
    gap: 0;
}

.import-card {
    background-color: #fffaf5;
    border: none;
    border-radius: 24px;
    padding: 100px 32px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    cursor: pointer;
    /* 保持指针样式 */
    transition: all 0.3s ease;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.import-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
}

.import-icon {
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, #fb923c, #f97316);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 24px;
    box-shadow: 0 4px 16px rgba(251, 146, 60, 0.3);
}

.import-icon .plus {
    width: 36px;
    height: 36px;
    background-color: white;
    border-radius: 50%;
    color: #fb923c;
    font-size: 22px;
    font-weight: bold;
    display: flex;
    align-items: center;
    justify-content: center;
}

.import-card h3 {
    font-size: 1.35rem;
    font-weight: 600;
    margin-bottom: 12px;
    color: #1f2937;
    letter-spacing: -0.3px;
}

.import-card p {
    color: #6b7280;
    font-size: 1.05rem;
    line-height: 1.5;
}
</style>
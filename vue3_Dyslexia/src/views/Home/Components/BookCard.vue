<template>
    <div class="book-card" @mouseenter="$emit('cardHover')" @mouseleave="$emit('cardLeave')">
        <div class="book-icon" :style="{ background: book.iconBg }">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="white"
                width="28" height="28">
                <path :d="book.iconSvg" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <span v-if="book.iconText" style="font-size: 12px; font-weight: 600; margin-top: 4px;">
                {{ book.iconText }}
            </span>
        </div>
        <div class="book-info">
            <div class="book-title">{{ book.title }}</div>
            <div class="book-progress">{{ book.progressText }}</div>
            <div class="progress-bar">
                <div class="progress-fill" :style="{ width: book.progress + '%' }"></div>
            </div>
        </div>
    </div>
</template>

<script setup>
const props = defineProps({
    book: {
        type: Object,
        required: true
    }
})
defineEmits(['cardHover', 'cardLeave'])
</script>

<style scoped>
/* 这里放原 .book-card 的样式 */
.book-card {
    background-color: white;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    display: flex;
    flex-direction: column;
    gap: 12px;
    transition: all 0.3s ease;
}

.book-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
}

.book-icon {
    width: 40px;
    height: 40px;
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

.book-info {
    width: 100%;
}

.book-title {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 6px;
    color: #1f2937;
}

.book-progress {
    font-size: 0.85rem;
    color: #6b7280;
    margin-bottom: 6px;
}

.progress-bar {
    width: 100%;
    height: 6px;
    background-color: #e2e8f0;
    border-radius: 12px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(135deg, #9333ea, #7e22ce);
    border-radius: 12px;
    transition: width 0.5s ease;
}
</style>
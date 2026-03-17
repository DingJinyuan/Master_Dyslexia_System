<template>
    <div class="recent-section">
        <div class="recent-header">
            <h2>最近在读</h2>
            <a href="#all" class="view-all" @mouseenter="handleHover" @mouseleave="handleLeave">
                查看全部
            </a>
        </div>
        <div class="recent-grid">
            <!-- 直接循环渲染书籍卡片，不再使用组件标签 -->
            <div v-for="(book, index) in bookList" :key="index" class="book-card" @mouseenter="handleHover"
                @mouseleave="handleLeave">
                <div class="book-icon" :style="{ background: book.iconBg }">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                        stroke="white" width="28" height="28">
                        <path v-html="book.iconSvg" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                    <span v-if="book.iconText" style="font-size: 12px; font-weight: 600; margin-top: 4px;">{{
                        book.iconText }}</span>
                </div>
                <div class="book-info">
                    <div class="book-title">{{ book.title }}</div>
                    <div class="book-progress">{{ book.progressText }}</div>
                    <div class="progress-bar">
                        <div class="progress-fill" :style="{ width: book.progress + '%' }"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
// 定义事件，供父组件同步小人表情
const emit = defineEmits(['cardHover', 'cardLeave'])
const handleHover = () => emit('cardHover')
const handleLeave = () => emit('cardLeave')

// 书籍数据（可抽离到单独的data文件）
const bookList = [
    {
        title: "平凡的世界",
        progress: 45,
        progressText: "已阅读 45%",
        iconBg: "linear-gradient(135deg, #fb923c, #f97316)",
        iconSvg: `<path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-2.485 0-4.5 1.507-4.5 3.75v8.25c0 1.194.885 2.243 2.065 2.455C3.389 18.725 4.16 19 5 19s1.611-.275 2.435-.545c1.18-.212 2.065-1.26 2.065-2.455V7.5h-2.25v8.25c0 .54-.398.992-.9.992s-.9-.453-.9-.992V7.5H6v8.25c0 .54-.398.992-.9.992s-.9-.453-.9-.992V7.5c0-1.243 2.015-2.25 4.5-2.25 1.105 0 2.145.296 3.042.808m0 0l3.042-.808c2.485 0 4.5 1.007 4.5 3.25v8.25c0 1.194-.885 2.243-2.065 2.455C16.611 18.725 15.84 19 15 19s-1.611-.275-2.435-.545c-1.18-.212-2.065-1.26-2.065-2.455V7.5h2.25v8.25c0 .54.398.992.9.992s.9-.453.9-.992V7.5h1.5v8.25c0 .54.398.992.9.992s.9-.453.9-.992V7.5c0-1.243-2.015-2.25-4.5-2.25z" />`,
        iconText: ""
    },
    {
        title: "2026年度计划方案",
        progress: 0,
        progressText: "未开始",
        iconBg: "linear-gradient(135deg, #10b981, #059669)",
        iconSvg: `<path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H7.125A3.375 3.375 0 003.75 5.625v12.75a3.375 3.375 0 003.375 3.375h1.5a1.125 1.125 0 011.125 1.125v1.5a3.375 3.375 0 003.375 3.375h1.5a3.375 3.375 0 003.375-3.375V14.25zm-1.5-9.75a1.125 1.125 0 11-2.25 0 1.125 1.125 0 012.25 0zM12 18.75a1.125 1.125 0 11-2.25 0 1.125 1.125 0 012.25 0z" />`,
        iconText: "PDF"
    },
    {
        title: "老人与海",
        progress: 88,
        progressText: "已阅读 88%",
        iconBg: "linear-gradient(135deg, #9333ea, #7e22ce)",
        iconSvg: `<path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-2.485 0-4.5 1.507-4.5 3.75v8.25c0 1.194.885 2.243 2.065 2.455C3.389 18.725 4.16 19 5 19s1.611-.275 2.435-.545c1.18-.212 2.065-1.26 2.065-2.455V7.5h-2.25v8.25c0 .54-.398.992-.9.992s-.9-.453-.9-.992V7.5H6v8.25c0 .54-.398.992-.9.992s-.9-.453-.9-.992V7.5c0-1.243 2.015-2.25 4.5-2.25 1.105 0 2.145.296 3.042.808m0 0l3.042-.808c2.485 0 4.5 1.007 4.5 3.25v8.25c0 1.194-.885 2.243-2.065 2.455C16.611 18.725 15.84 19 15 19s-1.611-.275-2.435-.545c-1.18-.212-2.065-1.26-2.065-2.455V7.5h2.25v8.25c0 .54.398.992.9.992s.9-.453.9-.992V7.5h1.5v8.25c0 .54.398.992.9.992s.9-.453.9-.992V7.5c0-1.243-2.015-2.25-4.5-2.25z" />`,
        iconText: ""
    },
    {
        title: "活着",
        progress: 60,
        progressText: "已阅读 60%",
        iconBg: "linear-gradient(135deg, #3b82f6, #2563eb)",
        iconSvg: `<path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-2.485 0-4.5 1.507-4.5 3.75v8.25c0 1.194.885 2.243 2.065 2.455C3.389 18.725 4.16 19 5 19s1.611-.275 2.435-.545c1.18-.212 2.065-1.26 2.065-2.455V7.5h2.25v8.25c0 .54-.398.992.9.992s.9-.453.9-.992V7.5h1.5v8.25c0 .54.398.992.9.992s.9-.453.9-.992V7.5c0-1.243-2.015-2.25-4.5-2.25z" />`,
        iconText: ""
    },
    {
        title: "百年孤独",
        progress: 20,
        progressText: "已阅读 20%",
        iconBg: "linear-gradient(135deg, #ec4899, #db2777)",
        iconSvg: `<path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-2.485 0-4.5 1.507-4.5 3.75v8.25c0 1.194.885 2.243 2.065 2.455C3.389 18.725 4.16 19 5 19s1.611-.275 2.435-.545c1.18-.212 2.065-1.26 2.065-2.455V7.5h2.25v8.25c0 .54-.398.992.9.992s.9-.453.9-.992V7.5h1.5v8.25c0 .54.398.992.9.992s.9-.453.9-.992V7.5c0-1.243-2.015-2.25-4.5-2.25z" />`,
        iconText: ""
    },
    {
        title: "人类简史",
        progress: 30,
        progressText: "已阅读 30%",
        iconBg: "linear-gradient(135deg, #f59e0b, #d97706)",
        iconSvg: `<path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-2.485 0-4.5 1.507-4.5 3.75v8.25c0 1.194.885 2.243 2.065 2.455C3.389 18.725 4.16 19 5 19s1.611-.275 2.435-.545c1.18-.212 2.065-1.26 2.065-2.455V7.5h2.25v8.25c0 .54-.398.992.9.992s.9-.453.9-.992V7.5h1.5v8.25c0 .54.398.992.9.992s.9-.453.9-.992V7.5c0-1.243-2.015-2.25-4.5-2.25z" />`,
        iconText: ""
    }
]
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

.view-all {
    color: #9333ea;
    text-decoration: none;
    font-size: 1rem;
    font-weight: 500;
    border: 2px solid #d1d5db;
    padding: 8px 16px;
    border-radius: 20px;
    transition: all 0.25s;
}

.view-all:hover {
    background-color: #9333ea;
    color: white;
    border-color: #9333ea;
    transform: translateY(-2px);
    box-shadow: 0 8px 15px rgba(147, 51, 234, 0.2);
}

.recent-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(2, 1fr);
    gap: 16px;
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
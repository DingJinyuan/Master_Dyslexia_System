<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue';

const emits = defineEmits(['charHover', 'charLeave']);

const isSmiling = ref(false);
const pupilStyle = reactive({
    transform: 'translate(-50%, -50%)'
});

// 鼠标移动处理（眼球跟随 + 身体晃动）
const handleMouseMove = (e) => {
    const xRatio = (e.clientX / window.innerWidth - 0.5) * 2;
    const yRatio = (e.clientY / window.innerHeight - 0.5) * 2;

    // 1. 眼球跟随
    const dx = xRatio * 3;
    const dy = yRatio * 3;
    pupilStyle.transform = `translate(-50%, -50%) translate(${dx}px, ${dy}px)`;

    // 2. 身体左右晃动
    const chars = document.querySelectorAll('.char');
    chars.forEach((char, index) => {
        // 每个小人晃动幅度略有不同，更自然
        const shakeAmt = xRatio * (1.5 + index * 0.2);
        char.style.transform = `rotate(${shakeAmt}deg)`;
    });
};

// 小人hover事件
const handleCharMouseEnter = () => {
    isSmiling.value = true;
    emits('charHover');
};

const handleCharMouseLeave = () => {
    isSmiling.value = false;
    emits('charLeave');
};

// 生命周期
onMounted(() => {
    window.addEventListener('mousemove', handleMouseMove);
});

onUnmounted(() => {
    window.removeEventListener('mousemove', handleMouseMove);
});
</script>

<template>
    <div class="char-group">
        <div class="char char-orange" @mouseenter="handleCharMouseEnter" @mouseleave="handleCharMouseLeave">
            <div class="char-body">
                <div class="char-eye left">
                    <div class="char-pupil" :style="pupilStyle"></div>
                </div>
                <div class="char-eye right">
                    <div class="char-pupil" :style="pupilStyle"></div>
                </div>
                <div class="char-mouth" :class="{ smile: isSmiling }"></div>
            </div>
        </div>
        <div class="char char-purple" @mouseenter="handleCharMouseEnter" @mouseleave="handleCharMouseLeave">
            <div class="char-body">
                <div class="char-eye left">
                    <div class="char-pupil" :style="pupilStyle"></div>
                </div>
                <div class="char-eye right">
                    <div class="char-pupil" :style="pupilStyle"></div>
                </div>
                <div class="char-mouth" :class="{ smile: isSmiling }"></div>
            </div>
        </div>
        <div class="char char-black" @mouseenter="handleCharMouseEnter" @mouseleave="handleCharMouseLeave">
            <div class="char-body">
                <div class="char-eye left">
                    <div class="char-pupil" :style="pupilStyle"></div>
                </div>
                <div class="char-eye right">
                    <div class="char-pupil" :style="pupilStyle"></div>
                </div>
                <div class="char-mouth" :class="{ smile: isSmiling }"></div>
            </div>
        </div>
        <div class="char char-yellow" @mouseenter="handleCharMouseEnter" @mouseleave="handleCharMouseLeave">
            <div class="char-body">
                <div class="char-eye left">
                    <div class="char-pupil" :style="pupilStyle"></div>
                </div>
                <div class="char-eye right">
                    <div class="char-pupil" :style="pupilStyle"></div>
                </div>
                <div class="char-mouth" :class="{ smile: isSmiling }"></div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.char-group {
    position: absolute;
    top: -30px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 14px;
    z-index: 99;
}

.char {
    width: 60px;
    height: 70px;
    transition: transform 0.15s ease;
    /* 晃动过渡效果 */
    transform-origin: bottom center;
    /* 以底部为旋转中心 */
}

.char-body {
    width: 100%;
    height: 100%;
    border-radius: 30px 30px 12px 12px;
    position: relative;
}

.char-orange .char-body {
    background: #fb923c;
}

.char-purple .char-body {
    background: #9333ea;
}

.char-black .char-body {
    background: #1f2937;
}

.char-yellow .char-body {
    background: #fbbf24;
}

.char-eye {
    position: absolute;
    top: 24%;
    width: 10px;
    height: 10px;
    background: #fff;
    border-radius: 50%;
    border: 2px solid #222;
}

.char-eye.left {
    left: 22%;
}

.char-eye.right {
    right: 22%;
}

.char-pupil {
    width: 5px;
    height: 5px;
    background: #111;
    border-radius: 50%;
    position: absolute;
    top: 50%;
    left: 50%;
    transition: transform 0.12s ease;
}

.char-black .char-pupil {
    background: #fff;
}

.char-mouth {
    position: absolute;
    bottom: 28%;
    left: 50%;
    transform: translateX(-50%);
    width: 14px;
    height: 7px;
    background: #111;
    border-radius: 0 0 10px 10px;
    opacity: 0;
    transition: opacity 0.2s;
}

.char-black .char-mouth {
    background: #fff;
}

.char-mouth.smile {
    opacity: 1;
}
</style>
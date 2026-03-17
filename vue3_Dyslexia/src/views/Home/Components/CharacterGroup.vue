<template>
    <div class="char-container">
        <div class="char char-orange" @mouseenter="handleCharMouseEnter" @mouseleave="handleCharMouseLeave">
            <div class="char-body">
                <div class="char-eye left">
                    <div class="char-pupil"></div>
                </div>
                <div class="char-eye right">
                    <div class="char-pupil"></div>
                </div>
                <div class="char-mouth"></div>
            </div>
        </div>
        <div class="char char-purple" @mouseenter="handleCharMouseEnter" @mouseleave="handleCharMouseLeave">
            <div class="char-body">
                <div class="char-eye left">
                    <div class="char-pupil"></div>
                </div>
                <div class="char-eye right">
                    <div class="char-pupil"></div>
                </div>
                <div class="char-mouth"></div>
            </div>
        </div>
        <div class="char char-black" @mouseenter="handleCharMouseEnter" @mouseleave="handleCharMouseLeave">
            <div class="char-body">
                <div class="char-eye left">
                    <div class="char-pupil"></div>
                </div>
                <div class="char-eye right">
                    <div class="char-pupil"></div>
                </div>
                <div class="char-mouth"></div>
            </div>
        </div>
        <div class="char char-yellow" @mouseenter="handleCharMouseEnter" @mouseleave="handleCharMouseLeave">
            <div class="char-body">
                <div class="char-eye left">
                    <div class="char-pupil"></div>
                </div>
                <div class="char-eye right">
                    <div class="char-pupil"></div>
                </div>
                <div class="char-mouth"></div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'

// 定义事件，供父组件监听交互状态
const emit = defineEmits(['charHover', 'charLeave'])

let mouseMoveHandler = null

// 小人鼠标进入
const handleCharMouseEnter = (e) => {
    const char = e.currentTarget
    char.classList.add('smile')
    char.style.transform = 'scale(1.15) translateY(-5px) rotate(0deg)'
    emit('charHover')
}

// 小人鼠标离开
const handleCharMouseLeave = (e) => {
    const char = e.currentTarget
    char.classList.remove('smile')
    const xRatio = (window.event.clientX / window.innerWidth - 0.5) * 2
    const index = Array.from(document.querySelectorAll('.char')).indexOf(char)
    const shakeAmt = xRatio * (3 + index * 0.5)
    char.style.transform = `rotate(${shakeAmt}deg)`
    emit('charLeave')
}

// 鼠标移动时眼球跟随+小人晃动
const initMouseMove = () => {
    mouseMoveHandler = (e) => {
        const xRatio = (e.clientX / window.innerWidth - 0.5) * 2
        const yRatio = (e.clientY / window.innerHeight - 0.5) * 2

        // 眼球跟随
        document.querySelectorAll('.char-pupil').forEach(pupil => {
            const dx = xRatio * 3
            const dy = yRatio * 3
            pupil.style.transform = `translate(-50%, -50%) translate(${dx}px, ${dy}px)`
        })

        // 小人晃动
        document.querySelectorAll('.char').forEach((char, index) => {
            if (!char.matches(':hover')) {
                const shakeAmt = xRatio * (3 + index * 0.5)
                char.style.transform = `rotate(${shakeAmt}deg)`
            }
        })
    }
    document.addEventListener('mousemove', mouseMoveHandler)
}

onMounted(() => initMouseMove())
onUnmounted(() => {
    if (mouseMoveHandler) document.removeEventListener('mousemove', mouseMoveHandler)
})
</script>

<style scoped>
.char-container {
    position: absolute;
    top: 10px;
    left: 40%;
    transform: translateX(-50%);
    display: flex;
    justify-content: center;
    gap: 15px;
    z-index: 20;
}

.char {
    width: 60px;
    height: 70px;
    position: relative;
    transition: all 0.3s ease;
    transform-origin: bottom center;
}

.char:hover {
    transform: scale(1.15) translateY(-5px);
}

.char-body {
    width: 100%;
    height: 100%;
    border-radius: 30px 30px 12px 12px;
    position: relative;
}

/* 小人高光 */
.char-body::after {
    content: '';
    position: absolute;
    background: rgba(255, 255, 255, 0.25);
    border-radius: 50%;
}

.char-orange .char-body::after {
    width: 20px;
    height: 15px;
    top: 8px;
    left: 15px;
}

.char-purple .char-body::after {
    width: 18px;
    height: 13px;
    top: 10px;
    left: 12px;
}

.char-black .char-body::after {
    width: 15px;
    height: 12px;
    top: 12px;
    left: 10px;
}

.char-yellow .char-body::after {
    width: 19px;
    height: 14px;
    top: 9px;
    left: 14px;
}

/* 眼睛/瞳孔/嘴巴 */
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
    transform: translate(-50%, -50%);
    transition: transform 0.18s ease-out;
}

.char-black .char-pupil {
    background: white;
    border: 1px solid #111;
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
    transition: opacity 0.2s ease;
}

.char-black .char-mouth {
    background: white;
}

.char.smile .char-mouth {
    opacity: 1;
    transform: translateX(-50%) scale(1.1);
}

/* 小人颜色 */
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
</style>
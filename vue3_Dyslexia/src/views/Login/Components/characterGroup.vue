<template>
    <div class="characters" ref="characterAreaRef" @click.stop="stopClick ? true : null">
        <!-- 橙色角色 -->
        <div class="blob-wrapper" :ref="setBlobWrapperRef">
            <div class="blob orange" :class="{ active: isEmotionActive }">
                <!-- 根据父组件传递的emotionType判断显示O嘴/笑脸 -->
                <div class="mouth o-mouth" v-if="emotionType === 'o-mouth'"></div>
                <div class="mouth smiling-mouth" v-else-if="emotionType === 'smiling'"></div>
                <div class="eyes">
                    <div class="eye">
                        <div class="pupil" :ref="setPupilRef"></div>
                    </div>
                    <div class="eye">
                        <div class="pupil" :ref="setPupilRef"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 紫色角色 -->
        <div class="blob-wrapper" :ref="setBlobWrapperRef">
            <div class="blob purple" :class="{ active: isEmotionActive }">
                <div class="mouth o-mouth" v-if="emotionType === 'o-mouth'"></div>
                <div class="mouth smiling-mouth" v-else-if="emotionType === 'smiling'"></div>
                <div class="eyes">
                    <div class="eye">
                        <div class="pupil" :ref="setPupilRef"></div>
                    </div>
                    <div class="eye">
                        <div class="pupil" :ref="setPupilRef"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 黑色角色 -->
        <div class="blob-wrapper" :ref="setBlobWrapperRef">
            <div class="blob black" :class="{ active: isEmotionActive }">
                <div class="mouth o-mouth" v-if="emotionType === 'o-mouth'"></div>
                <div class="mouth smiling-mouth" v-else-if="emotionType === 'smiling'"></div>
                <div class="eyes">
                    <div class="eye">
                        <div class="pupil" :ref="setPupilRef"></div>
                    </div>
                    <div class="eye">
                        <div class="pupil" :ref="setPupilRef"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 黄色角色 -->
        <div class="blob-wrapper" :ref="setBlobWrapperRef">
            <div class="blob yellow" :class="{ active: isEmotionActive }">
                <div class="mouth o-mouth" v-if="emotionType === 'o-mouth'"></div>
                <div class="mouth smiling-mouth" v-else-if="emotionType === 'smiling'"></div>
                <div class="eyes">
                    <div class="eye">
                        <div class="pupil" :ref="setPupilRef"></div>
                    </div>
                    <div class="eye">
                        <div class="pupil" :ref="setPupilRef"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { defineProps, ref, onMounted, onUnmounted, nextTick } from 'vue'

// 定义Props：接收父组件传递的表情类型和激活状态
const props = defineProps({
    emotionType: { // 表情类型：o-mouth/O嘴，smiling/笑脸
        type: String,
        default: 'smiling',
        validator: (val) => ['o-mouth', 'smiling'].includes(val) // 限制只能传这两个值
    },
    isEmotionActive: { // 是否显示嘴巴
        type: Boolean,
        default: false
    },
    stopClick: {
        type: Boolean,
        default: false
    }
})

// 子组件内部DOM引用
const characterAreaRef = ref(null)
const pupils = ref([])
const blobWrappers = ref([])

// 函数式ref收集
const setPupilRef = (el) => {
    if (el && !pupils.value.includes(el)) pupils.value.push(el)
}
const setBlobWrapperRef = (el) => {
    if (el && !blobWrappers.value.includes(el)) blobWrappers.value.push(el)
}

// 鼠标移动逻辑：眼球跟随 + 角色晃动
const handleMouseMove = (e) => {
    if (!pupils.value.length || !blobWrappers.value.length) return

    const pupilFollow = 15
    const bodySway = 5
    const bodyTilt = 3

    const mx = (e.clientX / window.innerWidth - 0.5) * 2
    const my = (e.clientY / window.innerHeight - 0.5) * 2

    // 眼球跟随
    pupils.value.forEach(p => {
        p.style.transform = `translate(-50%, -50%) translate(${mx * pupilFollow}px, ${my * pupilFollow}px)`
    })

    // 角色晃动
    blobWrappers.value.forEach(w => {
        w.style.transform = `
            translateY(${my * bodySway}px)
            rotate(${mx * bodyTilt}deg)
        `
        w.style.transition = 'transform 0.1s ease-out'
    })
}

// 生命周期
onMounted(() => {
    nextTick(() => {
        pupils.value = Array.from(document.querySelectorAll('.pupil'))
        blobWrappers.value = Array.from(document.querySelectorAll('.blob-wrapper'))
    })
    document.addEventListener('mousemove', handleMouseMove)
})

onUnmounted(() => {
    document.removeEventListener('mousemove', handleMouseMove)
})
</script>

<style scoped>
/* 角色区域基础样式 */
.characters {
    flex: 1;
    background: #fffaf5;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    padding: 60px 30px 100px 30px;
}

/* 角色容器 */
.blob-wrapper {
    position: relative;
    margin: 0 5px;
    z-index: 1;
}

.blob-wrapper:nth-child(1) {
    width: 190px;
    height: 130px;
}

.blob-wrapper:nth-child(2) {
    width: 150px;
    height: 210px;
}

.blob-wrapper:nth-child(3) {
    width: 120px;
    height: 310px;
}

.blob-wrapper:nth-child(4) {
    width: 170px;
    height: 190px;
}

/* 角色身体基础样式 */
.blob {
    width: 100%;
    height: 100%;
    position: relative;
    transition: all 0.3s ease;
}

/* 嘴巴基础样式 - 默认隐藏 */
.mouth {
    position: absolute;
    left: 50%;
    top: 65%;
    transform: translateX(-50%);
    opacity: 0;
    transition: opacity 0.3s ease, transform 0.3s ease;
    background: #111;
}

/* 激活状态显示嘴巴 */
.blob.active .mouth {
    opacity: 1;
    transform: translateX(-50%) scale(1.15);
}

/* 1. O型嘴样式（圆形） */
.o-mouth {
    width: 28px;
    height: 28px;
    border-radius: 50%;
}

/* 2. 笑脸样式（下弧形） */
.smiling-mouth {
    width: 32px;
    height: 16px;
    border-radius: 0 0 16px 16px;
}

/* 眼睛基础样式 */
.eyes {
    position: absolute;
    display: flex;
    pointer-events: none;
    top: 22%;
    left: 50%;
    transform: translateX(-50%);
    z-index: 2;
}

.eye {
    background: white;
    border-radius: 50%;
    position: relative;
    overflow: hidden;
    border: 2px solid #111;
}

.pupil {
    background: #111;
    border-radius: 50%;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    transition: transform 0.1s ease-out;
}

/* 各角色颜色/尺寸 */
.blob.orange {
    background: #fb923c;
    border-radius: 40px 40px 20px 20px;
}

.blob.purple {
    background: #9333ea;
    border-radius: 70px 70px 30px 30px;
}

.blob.black {
    background: #1f2937;
    border-radius: 30px 30px 15px 15px;
}

.blob.yellow {
    background: #fbbf24;
    border-radius: 80px 80px 35px 35px;
}

/* 高光效果 */
.blob::after {
    content: '';
    position: absolute;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    filter: blur(2px);
}

.blob.orange::after {
    width: 60px;
    height: 45px;
    top: 20px;
    left: 45px;
}

.blob.purple::after {
    width: 45px;
    height: 60px;
    top: 30px;
    left: 30px;
}

.blob.black::after {
    width: 35px;
    height: 75px;
    top: 35px;
    left: 20px;
}

.blob.yellow::after {
    width: 50px;
    height: 45px;
    top: 30px;
    left: 35px;
}

/* 眼睛/瞳孔尺寸 */
.blob.orange .eyes {
    gap: 18px;
    top: 25%;
}

.blob.orange .eye {
    width: 30px;
    height: 30px;
}

.blob.orange .pupil {
    width: 13px;
    height: 13px;
}

.blob.purple .eyes {
    gap: 18px;
    top: 20%;
}

.blob.purple .eye {
    width: 28px;
    height: 28px;
}

.blob.purple .pupil {
    width: 12px;
    height: 12px;
}

.blob.black .eyes {
    gap: 16px;
    top: 18%;
}

.blob.black .eye {
    width: 26px;
    height: 26px;
    border-color: #374151;
}

.blob.black .pupil {
    width: 12px;
    height: 12px;
    background: #f3f4f6;
    border: 1px solid #111;
}

.blob.yellow .eyes {
    gap: 18px;
    top: 22%;
}

.blob.yellow .eye {
    width: 28px;
    height: 28px;
    border-color: #d97706;
}

.blob.yellow .pupil {
    width: 12px;
    height: 12px;
}
</style>
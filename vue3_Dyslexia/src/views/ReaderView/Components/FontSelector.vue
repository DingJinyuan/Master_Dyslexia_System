<script setup>
import { defineProps, defineEmits, ref, watch } from 'vue';

const props = defineProps({
    config: {
        type: Object,
        required: true
    },
    fontList: {
        type: Array,
        required: true
    }
});

const emit = defineEmits(['config-change']);
const showFontOptions = ref(false);

const getFontFamily = (fontKey) => {
    switch (fontKey) {
        case 'OpenDyslexic':
            return '"OpenDyslexic", sans-serif';
        case 'OpenDyslexic3':
            return '"OpenDyslexic3", sans-serif';
        case 'OpenDyslexicAlta':
            return '"OpenDyslexicAlta", sans-serif';
        case 'OpenDyslexicMono':
            return '"OpenDyslexicMono", sans-serif';
        case 'Lexend':
            return '"Lexend", sans-serif';
        case 'Inclusive Sans':
            return '"Inclusive Sans", sans-serif';
        case 'Andika New Basic':
            return '"Andika New Basic", sans-serif';
        default:
            return fontKey;
    }
};

const changeFont = (fontKey) => {
    props.config.selectedFont = fontKey;
    const el = document.querySelector('.document-content');
    if (el) el.style.fontFamily = getFontFamily(fontKey);
    emit('config-change', props.config);
};

const changeFontSize = (size) => {
    props.config.fontSize = size;
    const el = document.querySelector('.document-content');
    if (el) el.style.fontSize = `${size}px`;
    emit('config-change', props.config);
};

const changeLineHeight = (height) => {
    props.config.lineHeight = height;
    const el = document.querySelector('.document-content');
    if (el) el.style.lineHeight = height;
    emit('config-change', props.config);
};

const changeLetterSpacing = (spacing) => {
    props.config.letterSpacing = spacing;
    const el = document.querySelector('.document-content');
    if (el) el.style.letterSpacing = `${spacing}px`;
    emit('config-change', props.config);
};

watch(() => props.config.selectedFont, (val) => {
    const el = document.querySelector('.document-content');
    if (el) el.style.fontFamily = getFontFamily(val);
}, { immediate: true });

watch(() => props.config.fontSize, (val) => {
    const el = document.querySelector('.document-content');
    if (el) el.style.fontSize = `${val}px`;
}, { immediate: true });

watch(() => props.config.lineHeight, (val) => {
    const el = document.querySelector('.document-content');
    if (el) el.style.lineHeight = val;
}, { immediate: true });

watch(() => props.config.letterSpacing, (val) => {
    const el = document.querySelector('.document-content');
    if (el) el.style.letterSpacing = `${val}px`;
}, { immediate: true });
</script>

<template>
    <div class="font-settings-container">
        <div class="font-switch-wrapper"
            style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span class="section-title" style="margin-bottom: 0;">字体设置</span>
            <button
                style="padding: 4px 12px; border: 1px solid #d1d5db; border-radius: 6px; background: #fff; cursor: pointer; font-size: 12px;"
                @click="showFontOptions = !showFontOptions">
                {{ showFontOptions ? '收起' : '展开' }}
            </button>
        </div>

        <div v-if="showFontOptions">
            <!-- 单行横向滚动 -->
            <div class="font-select-buttons">
                <button v-for="font in fontList" :key="font.key" class="font-btn"
                    :class="{ active: config.selectedFont === font.key }"
                    :style="{ fontFamily: getFontFamily(font.key) }" @click="changeFont(font.key)">
                    {{ font.label }}
                </button>
            </div>

            <div class="font-size-control">
                <span class="font-size-label">文字大小</span>
                <span class="font-size-value">{{ config.fontSize }}px</span>
            </div>
            <input type="range" class="slider" min="14" max="48" v-model.number="config.fontSize"
                @input="changeFontSize(config.fontSize)">

            <div class="section-title">行间距</div>
            <input type="range" class="slider" min="1.2" max="3.0" step="0.1" v-model.number="config.lineHeight"
                @input="changeLineHeight(config.lineHeight)">

            <div class="section-title">字间距</div>
            <input type="range" class="slider" min="0" max="4" step="0.1" v-model.number="config.letterSpacing"
                @input="changeLetterSpacing(config.letterSpacing)">
        </div>
    </div>
</template>

<style scoped>
.font-settings-container {
    width: 100%;
    margin-bottom: 24px;
}

.section-title {
    font-size: 14px;
    color: #6b7280;
    margin-bottom: 12px;
}

/* 单行横向滚动 */
.font-select-buttons {
    display: flex;
    flex-wrap: nowrap;
    overflow-x: auto;
    gap: 8px;
    padding-bottom: 8px;
    margin-bottom: 16px;
}

.font-select-buttons::-webkit-scrollbar {
    height: 4px;
}

.font-select-buttons::-webkit-scrollbar-thumb {
    background: #ccc;
    border-radius: 2px;
}

.font-btn {
    padding: 8px 12px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    font-size: 14px;
    cursor: pointer;
    white-space: nowrap;
}

.font-btn.active {
    border-color: #2563eb;
    background: #eff6ff;
    color: #2563eb;
    font-weight: 500;
}

.font-size-control {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
}

.font-size-label {
    font-size: 14px;
    color: #4b5563;
}

.font-size-value {
    font-size: 14px;
    font-weight: 600;
    color: #2563eb;
}

.slider {
    width: 100%;
    height: 6px;
    -webkit-appearance: none;
    background: #e2e8f0;
    border-radius: 3px;
    outline: none;
    margin-bottom: 16px;
}

.slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 16px;
    height: 16px;
    background: #2563eb;
    border-radius: 50%;
    cursor: pointer;
}

:deep(.font-btn[style*="OpenDyslexic"]) {
    font-family: "OpenDyslexic", sans-serif !important;
}

:deep(.font-btn[style*="Lexend"]) {
    font-family: "Lexend", sans-serif !important;
}

:deep(.font-btn[style*="Inclusive Sans"]) {
    font-family: "Inclusive Sans", sans-serif !important;
}

:deep(.font-btn[style*="Andika New Basic"]) {
    font-family: "Andika New Basic", sans-serif !important;
}
</style>
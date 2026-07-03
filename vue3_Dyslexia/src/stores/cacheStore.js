import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCacheStore = defineStore('cache', () => {
  // { [docId]: { refine, summary, mindmap, tts: { voiceName: url } } }
  const docCache = ref({})

  const getDocCache = (docId) => docCache.value[docId] || {}

  const setRefine = (docId, text) => {
    if (!docCache.value[docId]) docCache.value[docId] = {}
    docCache.value[docId].refine = text
  }

  const setSummary = (docId, data) => {
    if (!docCache.value[docId]) docCache.value[docId] = {}
    docCache.value[docId].summary = data
  }

  const setMindmap = (docId, url) => {
    if (!docCache.value[docId]) docCache.value[docId] = {}
    docCache.value[docId].mindmap = url
  }

  const setTTS = (docId, voiceName, url) => {
    if (!docCache.value[docId]) docCache.value[docId] = {}
    if (!docCache.value[docId].tts) docCache.value[docId].tts = {}
    docCache.value[docId].tts[voiceName] = url
  }

  const getTTS = (docId, voiceName) => {
    return docCache.value[docId]?.tts?.[voiceName] || null
  }

  const clearAll = () => { docCache.value = {} }

  return { docCache, getDocCache, setRefine, setSummary, setMindmap, setTTS, getTTS, clearAll }
}, { persist: true })

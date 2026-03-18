import httpInstance from '@/utils/http'

// 词性标注
export const posTaggingAPI = (text) => {
  return httpInstance({
    url: 'nlp/pos-tagging',
    method: 'POST',
    data: { text },
  })
}

// 划词翻译（只保留POST）
export const wordLookupAPI = (word) => {
  return httpInstance({
    url: 'nlp/word-lookup',
    method: 'POST',
    data: { word },
  })
}

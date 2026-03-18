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

//可读性评分

export const readabilityScoreAPI = (text) => {
  return httpInstance({
    url: 'readability',
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded', // 修正为表单编码
    },
    data: new URLSearchParams({ text }), // 使用URLSearchParams提交
  })
}

/**
 * 文本总结 + 可读性评分接口
 * @param {string} originalText - 需要总结的原文（必填）
 * @param {string} summaryLength - 总结长度：简短/标准/详细（可选，默认标准）
 * @returns {Promise<Object>} 包含总结文本和可读性评分的响应数据
 */
export const summarizeTextAPI = (originalText, summaryLength = '标准') => {
  return httpInstance({
    url: 'summarize', // 匹配目标接口路径
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded', // Form提交格式
    },
    // 按接口要求构造Form数据
    data: new URLSearchParams({
      originalText: originalText, // 接口要求的参数名（必填）
      summaryLength: summaryLength, // 可选参数
    }),
  })
}

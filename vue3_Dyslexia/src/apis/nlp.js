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
 * 文本精炼接口（多 Agent 迭代：全文改写 / 摘要）
 * @param {Object} data - 请求参数
 * @param {string} data.original_text - 需要处理的原文
 * @param {string} data.mode - 模式：'full_refine'（全文改写）| 'summary'（摘要）
 * @param {string} [data.summary_length='标准'] - 摘要长度：简短/标准/详细
 * @param {number} [data.max_iterations=3] - 最大迭代轮次（1-5）
 * @param {number|null} [data.pass_threshold=null] - 合格阈值，null 时自动选择
 * @returns {Promise<Object>} RefineResponse: success, mode, lang, refined_text, iterations, origin_score, final_score, improvement, score_history
 */
export const refineTextAPI = (data) => {
  return httpInstance({
    url: 'refine',
    method: 'POST',
    data: {
      original_text: data.original_text,
      mode: data.mode,
      summary_length: data.summary_length || '标准',
      max_iterations: data.max_iterations || 3,
      pass_threshold: data.pass_threshold || null,
    },
  })
}

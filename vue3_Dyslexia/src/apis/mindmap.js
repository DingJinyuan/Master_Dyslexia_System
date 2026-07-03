import httpInstance from '@/utils/http'

/**
 * 生成思维导图（LLM 大纲提取 + MCP HTML 渲染）
 * @param {Object} data - 请求参数
 * @param {string} data.text - 文档全文
 * @param {number} [data.max_depth=4] - 导图最大层级（2-6）
 * @returns {Promise<Object>} { success, markdown, html_url, error }
 */
export const generateMindmapAPI = (data) => {
  return httpInstance({
    url: 'mindmap/generate',
    method: 'POST',
    data: {
      text: data.text,
      max_depth: data.max_depth || 4,
    },
  })
}

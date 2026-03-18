import httpInstance from '@/utils/http'

/**
 * 文本转语音接口（仅保留核心参数，语音写死 youxiaomei）
 * @param {Object} data - 请求参数
 * @param {string} data.text - 要转换的文本
 * @param {string} [data.rate='+0%'] - 语速（如 "+0%"）
 * @param {string} [data.pitch='+0Hz'] - 音调（如 "+0Hz"）
 */
export const ttsGenerateAPI = (data) => {
  // 强制写死语音参数，覆盖传入值
  const requestData = {
    text: data.text,
    voice: 'youxiaomei', // 固定为有道有小美
    voiceName: 'string', // 固定值
    rate: data.rate || '+0%', // 保留语速自定义
    pitch: data.pitch || '+0Hz', // 保留音调自定义
  }

  return httpInstance({
    url: 'tts',
    method: 'POST',
    data: requestData,
  })
}

/**
 * 逐句转语音接口（支持高亮跟随）
 * @param {Object} data - 请求参数
 */
export const ttsSentencesAPI = (data) => {
  const requestData = {
    text: data.text,
    voice: 'youxiaomei',
    voiceName: 'string',
    rate: data.rate || '+0%',
  }

  return httpInstance({
    url: 'tts/sentences',
    method: 'POST',
    data: requestData,
  })
}

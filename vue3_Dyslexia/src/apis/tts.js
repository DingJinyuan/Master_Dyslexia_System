import httpInstance from '@/utils/http'

/**
 * 获取可用 TTS 音色列表
 * @returns {Promise<Object>} { voices: [{ name, locale, gender, friendlyName, engine }] }
 */
export const getTTSVoicesAPI = () => {
  return httpInstance({
    url: 'tts/voices',
    method: 'GET',
  })
}

/**
 * 全文 TTS 语音合成
 * @param {Object} data - 请求参数（全部透传，不再硬编码）
 * @param {string} data.text - 要转换的文本
 * @param {string} [data.voice] - 音色名称
 * @param {string} [data.rate='+0%'] - 语速
 * @param {string} [data.pitch='+0Hz'] - 音调
 */
export const ttsGenerateAPI = (data) => {
  return httpInstance({
    url: 'tts',
    method: 'POST',
    data: {
      text: data.text,
      voice: data.voice,
      voiceName: data.voiceName,
      rate: data.rate || '+0%',
      pitch: data.pitch || '+0Hz',
    },
  })
}

/**
 * 逐句 TTS 语音合成（支持高亮跟随）
 * @param {Object} data - 请求参数
 */
export const ttsSentencesAPI = (data) => {
  return httpInstance({
    url: 'tts/sentences',
    method: 'POST',
    data: {
      text: data.text,
      voice: data.voice,
      voiceName: data.voiceName,
      rate: data.rate || '+0%',
    },
  })
}

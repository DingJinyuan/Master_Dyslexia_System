import httpInstance from '@/utils/http'

export const audio_tts_API = (audio_data) => {
  return httpInstance({
    url: '/audio/tts',
    method: 'POST',
    data: audio_data,
  })
}

export const audio_tracks_API = (track_id) => {
  return httpInstance({
    url: '/audio/tracks/{track_id}',
    method: 'GET',
  })
}

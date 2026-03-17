import httpInstance from '@/utils/http'

export const documentsUploadAPI = (file) => {
  return httpInstance({
    url: '/documents/upload',
    method: 'POST',
    data: file,
  })
}

export const documentsDetailAPI = (documents_id) => {
  return httpInstance({
    url: `/documents/${documents_id}`,
    method: 'GET',
  })
}

export const documentsDetail_structuredAPI = (documents_id) => {
  return httpInstance({
    url: `/documents/${documents_id}/structured`,
    method: 'GET',
  })
}

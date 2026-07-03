import httpInstance from '@/utils/http'

// 文档列表（历史记录）
export const documentsListAPI = (page = 1, page_size = 20) => {
  return httpInstance({
    url: '/documents',
    method: 'GET',
    params: { page, page_size },
  })
}

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

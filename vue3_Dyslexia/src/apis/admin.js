import httpInstance from '@/utils/http'

export const approval_requestAPI = () => {
  return httpInstance({
    url: 'admin/approval-requests',
    method: 'get',
  })
}

export const approval_requestAPI_reject = (request_id) => {
  return httpInstance({
    url: `admin/approval-requests/${request_id}/reject`,
    method: 'post',
  })
}

export const approval_requestAPI_approve = (request_id) => {
  return httpInstance({
    url: `admin/approval-requests/${request_id}/approve`,
    method: 'post',
  })
}

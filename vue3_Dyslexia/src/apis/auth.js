import httpInstance from '@/utils/http'

export const loginAPI = (username, password) => {
  // 1. 构建 x-www-form-urlencoded 格式的参数（关键）
  const formData = new URLSearchParams()
  formData.append('grant_type', 'password') // 固定值 "password"，不是变量！
  formData.append('username', username) // 用户名
  formData.append('password', password) // 密码

  return httpInstance({
    url: '/auth/login',
    method: 'POST',
    data: formData, // 传 formData 而非 JSON
    // 2. 显式指定请求头（确保后端按表单解析）
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })
}

export const registerAPI = (email, username, password) => {
  return httpInstance({
    url: '/auth/register',
    method: 'POST',
    data: {
      email,
      username,
      password,
    },
  })
}

export const password_changeAPI = (PasswordChange) => {
  return httpInstance({
    url: '/auth/password-change-request',
    method: 'POST',
    data: PasswordChange,
  })
}

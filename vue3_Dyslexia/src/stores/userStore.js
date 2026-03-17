// 管理用户数据相关 - 仅保留用户信息核心功能
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { loginAPI } from '@/apis/auth'

export const useUserStore = defineStore(
  'user',
  () => {
    // 核心：存储用户信息的响应式变量
    const userInfo = ref({})

    // 登录：仅获取并存储用户信息
    const getUserInfo = async (username, password) => {
      try {
        const res = await loginAPI(username, password)
        // 将接口返回的用户信息存入userInfo（如用户名、token等）
        userInfo.value =
          {
            username: username, // 保存输入的用户名
            password: password,
            token: res.access_token, // 保存接口返回的token
          } || {}
        return userInfo.value // 返回用户信息，方便组件使用
      } catch (error) {
        console.error('登录失败：', error)
        userInfo.value = {} // 登录失败清空信息
        throw new Error('登录失败，请检查账号密码') // 抛出错误供组件捕获
      }
    }

    // 退出：仅清空用户信息
    const clearUserInfo = () => {
      userInfo.value = {}
    }

    // 仅暴露用户信息相关的变量和方法
    return {
      userInfo, // 存储的用户信息
      getUserInfo, // 登录获取用户信息
      clearUserInfo, // 退出清空用户信息
    }
  },
  {
    // 仅持久化用户信息，保证刷新不丢失
    persist: true,
  },
)

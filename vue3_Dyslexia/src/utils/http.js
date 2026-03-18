import 'element-plus/theme-chalk/el-message.css'
import { ElMessage } from 'element-plus'
//axios 基础封装
import axios from 'axios'
import { useUserStore } from '@/stores/userStore'
import router from '@/router'

const httpInstance = axios.create({
  //配置基地址
  baseURL: 'http://localhost:8000/api/v1',
  //配置超时时间
  timeout: 30000,
})
// axios请求拦截器 --请求发送到服务器之前执行的逻辑，可对请求参数、请求头做统一处理
httpInstance.interceptors.request.use(
  (config) => {
    //1.pinia获取token数据
    const useStore = useUserStore()
    const token = useStore.userInfo.token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    //后端要求拼接token数据

    return config
  },
  (e) => Promise.reject(e),
)

// axios响应式拦截器 --服务器返回响应之后执行的逻辑，可对响应数据、错误做统一处理。
httpInstance.interceptors.response.use(
  (res) => res.data,
  (e) => {
    const useStore = useUserStore()
    //错误提示统一
    ElMessage({
      type: 'warning',
      message: e.response.data.message,
    })
    //401token失效处理
    //清楚本地用户数据
    if (e.response.status === 401) {
      useStore.clearUserInfo()
      router.push('/login')
    }
    //跳转到登录页
    return Promise.reject(e)
  },
)

export default httpInstance

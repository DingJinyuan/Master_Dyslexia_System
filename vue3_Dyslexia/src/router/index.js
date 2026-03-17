import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login'
import Home from '@/views/Home'
import Upload from '@/views/Upload'
//import ForgetPassword from '@/views/Login/ForgetPassword'
import Register from '@/views/Login/Register'
import ReaderView from '@/views/ReaderView'
import Chenjinshi from '@/views/Chenjinshi'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  // path和component对应关系的位置
  routes: [
    {
      path: '/',
      component: Home,
    },
    {
      path: '/login',
      component: Login,
    },
    {
      path: '/register',
      component: Register,
    },
    {
      path: '/upload',
      component: Upload,
    },
    {
      path: '/reader_view/:documents_id',
      component: ReaderView,
    },
    {
      path: '/chenjinshi/:documents_id',
      component: Chenjinshi,
    },
  ],
  scrollBehavior() {
    return {
      top: 0,
    }
  },
})

export default router

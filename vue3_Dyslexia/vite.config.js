import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
//引入插件
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    AutoImport({
      resolvers: [
        ElementPlusResolver({
          importStyle: 'sass', // 关键！告诉插件加载SCSS而非默认CSS
        }),
      ],
    }),
    // 新增：Components 插件配置
    Components({
      resolvers: [
        ElementPlusResolver({
          importStyle: 'sass', // 关键配置，缺一不可
        }),
      ],
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
    // 关键：添加.vue扩展名到自动解析列表
    extensions: ['.vue', '.ts', '.js'],
  },
  css: {
    preprocessorOptions: {
      scss: {
        // 导入自定义SCSS变量文件
        additionalData: `@use "@/styles/element/index.scss" as *;\n
        @use "@/styles/var.scss" as *;\n
        `,
      },
    },
  },
})

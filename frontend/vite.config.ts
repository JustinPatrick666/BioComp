import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      'vue': 'vue/dist/vue.esm-bundler.js'
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // 不重写路径，保持/api前缀
        // rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/test_data': {
        target: 'http://localhost:5174',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/test_data/, '../test_data')
      }
    }
  },
  optimizeDeps: {
    include: ['hammerjs', 'cornerstone-core']
  }
})

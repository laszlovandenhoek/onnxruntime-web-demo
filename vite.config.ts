import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [
    vue()
  ],
  resolve: {
    alias: {
      '@': '/src'
    }
  },
  css: {
    postcss: {
      plugins: [
        require('autoprefixer')
      ]
    },
    preprocessorOptions: {
      sass: {
        additionalData: ['@import "vuetify/styles"', ''].join('\n')
      }
    }
  }
}) 
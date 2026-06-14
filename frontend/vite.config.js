import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import path from 'path'
import viteCompression from 'vite-plugin-compression'
import { visualizer } from 'rollup-plugin-visualizer'
import { createHtmlPlugin } from 'vite-plugin-html'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    viteCompression({
      algorithm: 'gzip',
      threshold: 1024,
      deleteOriginFile: false,
      minRatio: 0.8
    }),
    visualizer({
      open: false,
      gzipSize: true,
      brotliSize: true
    }),
    createHtmlPlugin({
      minify: true,
      inject: {
        data: {
          title: '云南省AI择校平台',
          injectScript: `<script>
            (function() {
              const storage = window.localStorage || { getItem: () => null };
              const token = storage.getItem('token');
              if (token) {
                document.cookie = 'auth_token=' + token + '; path=/';
              }
            })();
          </script>`
        }
      }
    }),
    AutoImport({
      resolvers: [ElementPlusResolver()],
      imports: ['vue', 'vue-router', 'pinia'],
      dts: 'src/auto-imports.d.ts',
      eslintrc: {
        enabled: false
      }
    }),
    Components({
      resolvers: [ElementPlusResolver({
        importStyle: false
      })],
      dts: 'src/components.d.ts'
    })
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    },
    extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.vue'],
    dedupe: ['vue']
  },
  server: {
    port: 3000,
    host: '0.0.0.0',
    open: false,
    hmr: {
      port: 3000,
      overlay: false
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path,
        timeout: 30000
      },
      '/ai': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ai/, '/api'),
        timeout: 60000
      }
    },
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.warn', 'console.error', 'console.debug'],
        passes: 2
      },
      mangle: {
        safari10: true
      }
    },
    rollupOptions: {
      output: {
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: '[ext]/[name]-[hash].[ext]',
        manualChunks: {
          'element-plus': ['element-plus'],
          'echarts': ['echarts', 'vue-echarts'],
          'marked': ['marked'],
          'axios': ['axios'],
          'pinia': ['pinia']
        },
        compact: true,
        plugins: []
      },
      treeshake: {
        moduleSideEffects: 'no-external',
        propertyReadSideEffects: false,
        tryCatchDeoptimization: false
      }
    },
    assetsInlineLimit: 4096,
    cssCodeSplit: true,
    reportCompressedSize: true,
    chunkSizeWarningLimit: 200,
    commonjsOptions: {
      transformMixedEsModules: true
    }
  },
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'axios', 'element-plus'],
    exclude: [],
    esbuildOptions: {
      target: 'es2020',
      supported: { 'top-level-await': true },
      treeShaking: true
    }
  },
  base: process.env.NODE_ENV === 'production' ? '/' : '/',
  esbuild: {
    drop: ['console', 'debugger'],
    pure: ['console.log', 'console.warn', 'console.error']
  }
})